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
        """
        text = text.lower()
        
        # Count matches for each urgency level
        urgency_scores = {
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        # Count phrase occurrences for each urgency level
        for level, phrases in self.rules.items():
            for phrase in phrases:
                if phrase.lower() in text:
                    urgency_scores[level] += 1
        
        # If no urgency indicators are found, return low
        if all(score == 0 for score in urgency_scores.values()):
            return 'low'
        
        # Return the urgency level with the highest score
        return max(urgency_scores.items(), key=lambda x: x[1])[0]
