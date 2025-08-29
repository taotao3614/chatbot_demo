import json
import os

class UrgencyAnalyzer:
    def __init__(self):
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """Load urgency rules from the JSON file"""
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'rules', 'emotion_urgency_rules.json')
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['urgency_rules']
    
    def analyze_urgency(self, text: str) -> str:
        """
        Analyze the urgency level of the input text.
        Returns: 'high', 'medium', or 'low'
        Priority: If multiple urgency levels are found, higher urgency takes precedence.
        """
        # Clean and prepare text
        text = text.lower()
        # Remove punctuation from text for better matching
        import string
        cleaned_text = text.translate(str.maketrans('', '', string.punctuation))
        
        print(f"Analyzing urgency - Original text: {text}")
        print(f"Analyzing urgency - Cleaned text: {cleaned_text}")
        
        # First check for high urgency indicators
        high_matches = [phrase for phrase in self.rules['high']
                       if phrase.lower() in cleaned_text]
        if high_matches:
            print(f"Found high urgency indicators: {high_matches}")
            return 'high'
            
        # Then check for medium urgency
        medium_matches = [phrase for phrase in self.rules['medium']
                         if phrase.lower() in cleaned_text]
        if medium_matches:
            print(f"Found medium urgency indicators: {medium_matches}")
            return 'medium'
            
        # Finally check for low urgency
        low_matches = [phrase for phrase in self.rules['low']
                      if phrase.lower() in cleaned_text]
        if low_matches:
            print(f"Found low urgency indicators: {low_matches}")
            return 'low'
            
        # If no urgency indicators are found, return low
        print("No urgency indicators found, defaulting to low")
        return 'low'
