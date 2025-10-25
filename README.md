# Blackthorn Mystery Solver 

An immersive detective deduction visual novel that uses NLP and AI-driven responses for interactive interrogations, evidence reasoning, and dynamic narrative flow.

---

##  Vision

Blackthorn Mystery Solver demonstrates how NLP and AI can transform traditional visual novels from linear, static experiences into dynamic, real-life-like deduction adventures, letting players reason like a true detective.

---

##  Features

- Dynamic story progression driven by your dialogue and choices
- NLP-powered conversations with suspects and witnesses
- Emotion- and context-aware character responses
- Immersive art and sound design
- Adaptive narrative that reacts to your investigative style

---

##  Tech Stack

- Backend & AI: Python, Flask, Sentence-Transformers (spaCy/NLTK optional)
- Game Engine: Ren’Py (recommended) or PyGame
- Optional APIs: OpenAI API for advanced dialogue/reasoning
- Version Control: Git & GitHub

---

##  Architecture

- Game client (Ren’Py): DetectiveGame/
- NLP microservice (Flask + Sentence-Transformers): nlp_service/
- Communication:
  - Evidence matching via HTTP: http://127.0.0.1:5000
  - Interrogation intent matching supports direct import fallback

Key files:
- Evidence system: DetectiveGame/game/clues/evidence_system.rpy
- Interrogation flow and responses: DetectiveGame/game/story/interrogation.rpy
- Characters: DetectiveGame/game/characters/characters.rpy
- BGM routing: DetectiveGame/game/audio/bgm.rpy
- Entry points: DetectiveGame/game/script.rpy and story/*.rpy
- NLP API service: nlp_service/nlp_service.py
- Deployment helpers: nlp_service/.render.yaml, nlp_service/Procfile

---

##  Quick Start

```bash
# 1) Clone
git clone https://github.com/apekshyasharma/BlackthornMysterySolver.git
cd BlackthornMysterySolver

# 2) Start NLP service
cd nlp_service
pip install -r requirements.txt
python nlp_service.py
# Service listens on http://127.0.0.1:5000

# 3) Launch the game in Ren'Py
# Open DetectiveGame/ in Ren’Py Launcher (Ren’Py 8 recommended) and Run
```

---

## 🧩 Installation (detailed)

NLP service (Python 3.10+):

```bash
cd nlp_service
# Option A: pip
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Option B: conda
conda env create -f environment.yml
conda activate blackthorn_env
```

Run:

```bash
python nlp_service.py
# Or production-ish:
waitress-serve --listen=0.0.0.0:5000 nlp_service:app
```

Health checks:

```bash
curl -s http://127.0.0.1:5000/
curl -s http://127.0.0.1:5000/healthz
curl -s http://127.0.0.1:5000/readyz
```

Game (Ren’Py):

- Open DetectiveGame/ in the Ren’Py Launcher.
- Entry flow: start → prologue → evidence → interrogation → accusation → ending.
  - Entry: DetectiveGame/game/script.rpy → story/prologue.rpy
  - Evidence: story/evidence_collection.rpy
  - Interrogation: story/interrogation.rpy
  - Endings: story/ending.rpy

Tip: Keep the NLP service running at 127.0.0.1:5000.

---

## ⚙️ Configuration

NLP service (environment variables):

- BLACKTHORN_NLP_MODEL: sentence-transformers model (default: all-MiniLM-L6-v2)
- BLACKTHORN_NLP_MODEL_DIR: local model dir override
- BLACKTHORN_NLP_MAX_BODY, BLACKTHORN_NLP_MAX_TEXT_LEN, BLACKTHORN_NLP_MAX_CANDIDATES
- BLACKTHORN_NLP_THREADS, PORT (default 5000)
- CORS:
  - BLACKTHORN_NLP_CORS (e.g., "*")
  - BLACKTHORN_NLP_CORS_HEADERS, BLACKTHORN_NLP_CORS_METHODS, BLACKTHORN_NLP_CORS_CREDENTIALS

Game-side constants (Evidence system):
- NLP_BEST_MATCH_URL in DetectiveGame/game/clues/evidence_system.rpy (default http://127.0.0.1:5000/best_match)
- EVIDENCE_SIM_THRESHOLD in the same file (default 0.65)

---

##  NLP API

Base URL: http://127.0.0.1:5000

- GET /, /healthz, /readyz

- POST /similarity
  Request:
  ```json
  { "text1": "broken glass", "text2": "glass shards" }
  ```
  Response:
  ```json
  { "similarity": 0.82 }
  ```

- POST /best_match
  Request:
  ```json
  { "text": "bloody cloth", "candidates": ["glass", "letter", "handkerchief"] }
  ```
  Response:
  ```json
  {
    "best_text": "handkerchief",
    "best_score": 0.91,
    "scores": { "glass": 0.11, "letter": 0.07, "handkerchief": 0.91 }
  }
  ```

- POST /intent_best_match
  Request:
  ```json
  {
    "text": "where were you last night",
    "intents": [
      { "id": "alibi", "canonical": "ask about alibi", "synonyms": ["where were you", "do you have an alibi"] },
      { "id": "motive", "canonical": "ask about motive", "synonyms": ["why would you kill him"] }
    ],
    "threshold": 0.35
  }
  ```
  Response:
  ```json
  { "best_id": "alibi", "best_text": "where were you", "best_score": 0.88, "matched": true }
  ```

---

##  In-Game NLP Integration

Evidence matching (DetectiveGame/game/clues/evidence_system.rpy):
- 3-stage validation in check_evidence_input:
  1) NLP HTTP /best_match score ≥ EVIDENCE_SIM_THRESHOLD
  2) Exact match against EVIDENCE_SYNONYMS
  3) Fuzzy fallback (difflib ratio ≥ 0.8)

Interrogation (DetectiveGame/game/story/interrogation.rpy):
- Intent set: INTERROGATION_INTENTS (alibi, evidence, motive, relationships, accusation)
- Sanitization and relevance filters for smalltalk/emoji
- Classifier:
  - Primary: best_intent import (NLP), with a local difflib fallback
  - Wrapper get_question_category restricts to valid categories and applies thresholds
- Accusation parsing get_accused_suspect maps free text to suspects with synonyms and similarity checks

---

##  Testing

- Unit tests (service): add tests under nlp_service/tests/
- Manual checks:
  - Validate /best_match with evidence synonyms
  - Try multiple interrogation phrasings and confirm categories map as expected

---

##  Deployment (NLP Service)

Render.com example (nlp_service/.render.yaml):

```yaml
services:
  - type: web
    name: blackthorn-nlp
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: waitress-serve --listen=0.0.0.0:$PORT nlp_service:app
    autoDeploy: true
```

Procfile: nlp_service/Procfile

---

##  Extending

- Add evidence synonyms:
  - Update EVIDENCE_SYNONYMS in DetectiveGame/game/clues/evidence_system.rpy
- Tune thresholds:
  - EVIDENCE_SIM_THRESHOLD and interrogation thresholds in get_question_category
- Expand interrogation coverage:
  - Add phrases to INTERROGATION_INTENTS and responses in SUSPECT_RESPONSES

---

##  Troubleshooting

- Evidence matching fails:
  - Ensure NLP service is running at 127.0.0.1:5000
  - Verify NLP_BEST_MATCH_URL and check nlp_service/logs/nlp_service.log
- Health checks fail:
  - Verify BLACKTHORN_NLP_MODEL or BLACKTHORN_NLP_MODEL_DIR availability
- CORS/405/404 errors:
  - Configure BLACKTHORN_NLP_CORS for your origin
- Ren’Py cache/state issues:
  - Fully exit and relaunch the project to clear compiled state

---

##  Contributing

I’d love your help in making **Blackthorn Mystery Solver** even better!  

- **Report bugs:** Open an issue with a clear description or screenshots.  
- **Suggest features:** Share ideas to improve gameplay, AI interactions, or story.  
- **Submit PRs:**  
  - Fork the repo and create a feature branch.  
  - Keep commits clear and concise.  
  - Include screenshots or clips if relevant.  

Thanks for helping make the game more engaging for everyone!  

---

##  License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.  
You’re free to use, modify, and share the code as long as the original copyright and license are included.

---

## 📞 Contact

- **Developer:** Apekshya Sharma  
- **GitHub:** [https://github.com/apekshyasharma](https://github.com/apekshyasharma)  
- **Email:** apekshyasharma2308@gmail.com  

Feel free to reach out with questions, feedback, or ideas for the game!
