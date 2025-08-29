import json
import os

class EmotionAnalyzer:
    def __init__(self):
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """Load emotion rules from the JSON file"""
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'rules', 'emotion_urgency_rules.json')
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['emotion_rules']
    
    def analyze_emotion(self, text: str) -> str:
        """
        Analyze the emotion of the input text.
        Returns: 'positive', 'negative', or 'neutral'
        Priority: If explicit emotions (positive/negative) exist, ignore neutral words.
        """
        # Clean and prepare text
        text = text.lower()
        # Remove punctuation from text for word matching
        import string
        cleaned_text = text.translate(str.maketrans('', '', string.punctuation))
        words = cleaned_text.split()
        
        print(f"Analyzing text: {text}")
        print(f"Cleaned text: {cleaned_text}")
        print(f"Words: {words}")
        print(f"Negative keywords: {self.rules['negative']}")
        
        # First check for explicit emotions (positive/negative)
        negative_matches = [keyword for keyword in self.rules['negative'] 
                          if keyword.lower() in words or 
                          (' ' in keyword and keyword.lower() in cleaned_text)]
        
        positive_matches = [keyword for keyword in self.rules['positive']
                          if keyword.lower() in words or 
                          (' ' in keyword and keyword.lower() in cleaned_text)]
        
        print(f"Negative matches found: {negative_matches}")
        print(f"Positive matches found: {positive_matches}")
        
        # If we have explicit emotions, return them (negative takes priority if both exist)
        if negative_matches:
            print("Returning negative due to matches:", negative_matches)
            return 'negative'
        if positive_matches:
            print("Returning positive due to matches:", positive_matches)
            return 'positive'
            
        # Only check neutral words if no explicit emotions were found
        neutral_matches = [keyword for keyword in self.rules['neutral']
                         if keyword.lower() in words or 
                         (' ' in keyword and keyword.lower() in cleaned_text)]
        
        print(f"Neutral matches found: {neutral_matches}")
        return 'neutral'
