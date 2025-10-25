from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
import re
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

app = Flask(__name__)

# Security/size limits
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("BLACKTHORN_NLP_MAX_BODY", str(512 * 1024)))  # default 512KB
MAX_TEXT_LEN = int(os.getenv("BLACKTHORN_NLP_MAX_TEXT_LEN", "512"))
MAX_CANDIDATES = int(os.getenv("BLACKTHORN_NLP_MAX_CANDIDATES", "256"))

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", os.getenv("BLACKTHORN_NLP_PORT", "5000")))
THREADS = int(os.getenv("BLACKTHORN_NLP_THREADS", "4"))

# Structured rotating logs
try:
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "nlp_service.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
except Exception:
    app.logger.warning("Failed to initialize file logger; using stderr.")

# Optional CORS (set env BLACKTHORN_NLP_CORS="*" or "https://a.com,https://b.com")
_cors = os.getenv("BLACKTHORN_NLP_CORS", "").strip()
CORS_HEADERS = os.getenv("BLACKTHORN_NLP_CORS_HEADERS", "Content-Type, Authorization")
CORS_METHODS = os.getenv("BLACKTHORN_NLP_CORS_METHODS", "GET,POST,OPTIONS")
CORS_CREDENTIALS = os.getenv("BLACKTHORN_NLP_CORS_CREDENTIALS", "false").lower() in ("1", "true", "yes")
_origins_list = []

if _cors:
    try:
        from flask_cors import CORS
        origins = "*" if _cors == "*" else [o.strip() for o in _cors.split(",") if o.strip()]
        CORS(app, resources={r"/*": {
            "origins": origins,
            "supports_credentials": CORS_CREDENTIALS,
            "methods": [m.strip() for m in CORS_METHODS.split(",") if m.strip()],
            "allow_headers": [h.strip() for h in CORS_HEADERS.split(",") if h.strip()],
        }})
        _origins_list = [] if origins == "*" else origins
        app.logger.info(f"CORS enabled via flask-cors for: {origins}")
    except Exception:
        # Fallback: manual header injection
        _origins_list = [] if _cors == "*" else [o.strip() for o in _cors.split(",") if o.strip()]
        app.logger.warning("flask-cors not installed; using manual CORS headers.")

def _add_cors_headers(resp):
    # Only add if configured
    if not _cors:
        return resp
    origin = request.headers.get("Origin", "")
    if _cors == "*":
        resp.headers["Access-Control-Allow-Origin"] = "*"
    else:
        if origin and origin in _origins_list:
            resp.headers["Access-Control-Allow-Origin"] = origin
            # Let caches know response varies by Origin
            resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = CORS_METHODS
    resp.headers["Access-Control-Allow-Headers"] = CORS_HEADERS
    if CORS_CREDENTIALS:
        resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers.setdefault("Access-Control-Max-Age", "600")
    return resp

@app.before_request
def _handle_preflight():
    # Gracefully handle preflight requests even if flask-cors is missing.
    if request.method == "OPTIONS":
        resp = app.make_response(("", 204))
        return _add_cors_headers(resp)
    return None

@app.after_request
def _ensure_cors_headers(resp):
    # Ensure CORS headers are present on all responses, including errors.
    return _add_cors_headers(resp)

# Model loading with env/bundled fallback
try:
    _model_name = os.getenv("BLACKTHORN_NLP_MODEL", "all-MiniLM-L6-v2")
    _model_dir = os.getenv("BLACKTHORN_NLP_MODEL_DIR", "").strip()
    if _model_dir and Path(_model_dir).exists():
        model = SentenceTransformer(_model_dir)
        app.logger.info(f"Loaded model from directory: {_model_dir}")
    else:
        bundled = Path(__file__).parent / "model" / _model_name
        if bundled.exists():
            model = SentenceTransformer(str(bundled))
            app.logger.info(f"Loaded bundled model: {bundled}")
        else:
            model = SentenceTransformer(_model_name)
            app.logger.info(f"Loaded hub model: {_model_name}")
except Exception:
    app.logger.exception("Failed to load SentenceTransformer model.")
    raise

# Filler phrases to strip from user inputs
FILLER_PATTERNS = [
    r"\bi think\b", r"\bmaybe\b", r"\bkind of\b", r"\blocks like\b", r"\blooks like\b",
    r"\bi guess\b", r"\bsort of\b", r"\bseems like\b", r"\bi found\b",
    r"\bi think i found\b", r"\bi believe\b", r"\bit might be\b",
]

def _clip(s: str) -> str:
    return (s or "")[:MAX_TEXT_LEN]

def preprocess_text(text: str) -> str:
    """
    Lowercase, remove filler words, strip punctuation, and collapse whitespace.
    Used by both evidence collection and interrogation helpers.
    """
    if not text:
        return ""
    s = _clip(text).lower().strip()
    for pat in FILLER_PATTERNS:
        s = re.sub(pat, " ", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# -------------------------
# Interrogation-only
# -------------------------
def check_similarity(text1: str, text2: str) -> float:
    """
    Cosine similarity between two phrases using the shared model.
    """
    q = preprocess_text(text1 or "")
    c = preprocess_text(text2 or "")
    if not q or not c:
        return 0.0
    emb1 = model.encode(q, convert_to_tensor=True)
    emb2 = model.encode(c, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2)[0][0])

def best_intent(user_text: str, intents: list, threshold: float = 0.35):
    """
    Best-matching intent across canonical+synonyms.
    Returns dict with best_id/best_text/best_score/matched.
    """
    q = preprocess_text(user_text or "")
    if not q or not intents:
        return {"best_id": "", "best_text": "", "best_score": 0.0, "matched": False}

    candidates = []
    for it in intents[:64]:
        if not isinstance(it, dict):
            continue
        cid = it.get("id") or it.get("name") or ""
        if not cid:
            continue
        canon = it.get("canonical") or ""
        syns = list(it.get("synonyms") or [])[:64]
        pool = ([canon] if canon else []) + syns
        for cand in pool:
            if cand:
                candidates.append((cid, cand))

    if not candidates:
        return {"best_id": "", "best_text": "", "best_score": 0.0, "matched": False}

    proc_texts = [preprocess_text(cand) for _, cand in candidates]
    q_emb = model.encode(q, convert_to_tensor=True)
    c_embs = model.encode(proc_texts, convert_to_tensor=True)
    sims = util.cos_sim(q_emb, c_embs)[0]
    scores = [float(s) for s in sims]
    best_idx = max(range(len(scores)), key=lambda i: scores[i])
    best_score = scores[best_idx]
    best_id, best_text = candidates[best_idx]

    app.logger.info(f"[Interrogation] Best intent '{best_id}' via '{best_text}' ({best_score:.4f}) for '{q}'")
    return {
        "best_id": best_id,
        "best_text": best_text,
        "best_score": best_score,
        "matched": best_score >= threshold,
    }

# -------------------------
# Health/info
# -------------------------
@app.get("/")
def info():
    return jsonify({
        "name": "Blackthorn NLP Service",
        "model": os.getenv("BLACKTHORN_NLP_MODEL", "all-MiniLM-L6-v2"),
        "host": HOST, "port": PORT
    })

@app.get("/healthz")
def healthz():
    try:
        _ = model.encode(["ok"], convert_to_tensor=False)
        return jsonify({"status": "ok"}), 200
    except Exception:
        app.logger.exception("Health check failed.")
        return jsonify({"status": "error"}), 500

@app.get("/readyz")
def readyz():
    return healthz()

@app.errorhandler(405)
def _method_not_allowed(e):
    resp = jsonify({"error": "method not allowed"})
    resp.status_code = 405
    return _add_cors_headers(resp)

@app.errorhandler(404)
def _not_found(e):
    resp = jsonify({"error": "not found"})
    resp.status_code = 404
    return _add_cors_headers(resp)

# -------------------------
# Evidence endpoints
# -------------------------
@app.route("/similarity", methods=["POST", "OPTIONS"])
def similarity():
    try:
        data = request.get_json(silent=True) or {}
        text1 = _clip(data.get("text1", ""))
        text2 = _clip(data.get("text2", ""))
        q = preprocess_text(text1)
        c = preprocess_text(text2)
        emb1 = model.encode(q, convert_to_tensor=True)
        emb2 = model.encode(c, convert_to_tensor=True)
        sim = float(util.cos_sim(emb1, emb2)[0][0])
        app.logger.info(f"Similarity: '{q}' vs '{c}' -> {sim:.4f}")
        return jsonify({"similarity": sim})
    except Exception:
        app.logger.exception("Error in /similarity")
        return jsonify({"error": "internal error"}), 500

@app.route("/best_match", methods=["POST", "OPTIONS"])
def best_match():
    """
    Given user text and a list of candidates, return best match and scores.
    """
    try:
        data = request.get_json(silent=True) or {}
        user_text = _clip(data.get("text", ""))
        candidates = data.get("candidates", []) or []
        if not isinstance(candidates, list):
            return jsonify({"error": "candidates must be a list"}), 400
        candidates = [ _clip(str(c)) for c in candidates if isinstance(c, (str, bytes)) ][:MAX_CANDIDATES]

        q = preprocess_text(user_text)
        if not q or not candidates:
            return jsonify({"best_text": "", "best_score": 0.0, "scores": []})

        processed = [preprocess_text(c) for c in candidates]
        original_by_index = candidates

        q_emb = model.encode(q, convert_to_tensor=True)
        c_embs = model.encode(processed, convert_to_tensor=True)
        sims = util.cos_sim(q_emb, c_embs)[0]
        scores = [float(s) for s in sims]
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        best_score = scores[best_idx]
        best_text = original_by_index[best_idx]

        app.logger.info(f"Best match -> '{best_text}' ({best_score:.4f}) for input '{q}'")
        return jsonify({
            "best_text": best_text,
            "best_score": best_score,
            "scores": [{"candidate": original_by_index[i], "score": scores[i]} for i in range(len(scores))]
        })
    except Exception:
        app.logger.exception("Error in /best_match")
        return jsonify({"error": "internal error"}), 500

# -------------------------
# Interrogation endpoint
# -------------------------
@app.route("/intent_best_match", methods=["POST", "OPTIONS"])
def intent_best_match():
    try:
        data = request.get_json(silent=True) or {}
        text = _clip(data.get("text", ""))
        intents = data.get("intents", []) or []
        threshold = float(data.get("threshold", 0.35))
        if not isinstance(intents, list):
            return jsonify({"error": "intents must be a list"}), 400
        safe_intents = []
        for it in intents[:64]:
            if not isinstance(it, dict):
                continue
            syns = [ _clip(str(s)) for s in (it.get("synonyms") or []) if isinstance(s, (str, bytes)) ][:64]
            safe_intents.append({
                "id": str(it.get("id", "")) or str(it.get("name", "")),
                "canonical": _clip(str(it.get("canonical", ""))),
                "synonyms": syns,
            })
        result = best_intent(text, safe_intents, threshold=threshold)
        return jsonify(result)
    except Exception:
        app.logger.exception("Error in /intent_best_match")
        return jsonify({"error": "internal error"}), 500

if __name__ == "__main__":
    try:
        from waitress import serve
        PORT = int(os.getenv("PORT", os.getenv("BLACKTHORN_NLP_PORT", "5000")))
        HOST = "0.0.0.0"
        app.logger.info(f"Starting waitress on {HOST}:{PORT} (threads={THREADS})")
        serve(app, host=HOST, port=PORT, threads=THREADS)
    except Exception:
        app.logger.warning("Waitress unavailable; falling back to Flask dev server.")
        app.run(host=HOST, port=PORT, debug=False)

