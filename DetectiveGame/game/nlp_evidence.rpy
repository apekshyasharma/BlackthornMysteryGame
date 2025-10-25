# NLP Evidence similarity checking system

init -10 python:
    import requests
    
    # Threshold for determining if evidence items are similar enough
    SIMILARITY_THRESHOLD = 0.6
    
    def check_similarity(text1, text2):
        """
        Check semantic similarity between two texts using NLP API.
        Falls back to difflib if API is unavailable.
        """
        try:
            import requests
            import json
            
            # Call the Flask NLP service for similarity scoring
            response = requests.post("http://127.0.0.1:5000/similarity", 
                json={"text1": text1, "text2": text2}, timeout=2)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("similarity", 0.0)
            else:
                # API error - use fallback
                return fallback_similarity(text1, text2)
                
        except Exception as e:
            # Log the exception but don't crash
            renpy.log(f"NLP API error: {str(e)}. Using fallback.")
            return fallback_similarity(text1, text2)
    
    def fallback_similarity(text1, text2):
        """Fallback similarity using difflib when API is unavailable"""
        # Convert to lowercase for better matching
        t1, t2 = text1.lower(), text2.lower()
        # Calculate similarity ratio using SequenceMatcher
        ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
        # Scale up slightly as difflib tends to be stricter than semantic similarity
        scaled_ratio = min(1.0, ratio * 1.3)
        return scaled_ratio

    def _basic_similarity(text1, text2):
        """
        Calculate a basic similarity score using Levenshtein distance.
        This is a fallback if the Flask API is unavailable.
        """
        # If texts are identical, return 1.0
        if text1 == text2:
            return 1.0
            
        # Simple word overlap as fallback
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
            
        # Calculate Jaccard similarity
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total
    
    def _norm(text):
        """
        Normalize input text with lemmatization if spaCy is available.
        Falls back to basic normalization if spaCy isn't available.
        """
        import re
        
        # First, apply basic normalization (lowercase + regex)
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        
        # Try to use spaCy for lemmatization if available
        try:
            import spacy
            
            # Load the English model 
            if not hasattr(renpy.store, "_nlp_model"):
                renpy.store._nlp_model = spacy.load("en_core_web_sm")
            
            # Process the text with spaCy
            doc = renpy.store._nlp_model(text)
            
            # Replace each token with its lemma
            lemmatized_text = " ".join([token.lemma_ for token in doc])
            return lemmatized_text
        except:
            # If spaCy is unavailable, return the basic normalized text
            return text
