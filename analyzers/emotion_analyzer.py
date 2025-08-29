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
        """
        text = text.lower()
        
        # Count matches for each emotion category
        emotion_scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        # Count word occurrences for each emotion
        words = text.lower().split()
        for emotion, keywords in self.rules.items():
            for keyword in keywords:
                # 使用精确匹配而不是子字符串匹配
                if keyword.lower() in words:
                    emotion_scores[emotion] += 1
                # 检查词组（包含空格的关键词）
                elif ' ' in keyword and keyword.lower() in text:
                    emotion_scores[emotion] += 1
        
        # If no emotion is detected, return neutral
        if all(score == 0 for score in emotion_scores.values()):
            return 'neutral'
        
        # Return the emotion with the highest score
        return max(emotion_scores.items(), key=lambda x: x[1])[0]
