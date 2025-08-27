"""
NLP module tests for intent classification.
"""
import pytest
from app.nlp.intent_classifier import IntentClassifier, TextPreprocessor


class TestTextPreprocessor:
    """Test text preprocessing functionality."""
    
    def setUp(self):
        self.preprocessor = TextPreprocessor()
    
    def test_basic_preprocessing(self):
        preprocessor = TextPreprocessor()
        
        # Test basic cleaning
        result = preprocessor.preprocess("  Hello, World!  ")
        assert result == "hello world"
        
        # Test punctuation removal
        result = preprocessor.preprocess("What's your price?")
        assert result == "whats your price"
        
        # Test whitespace normalization
        result = preprocessor.preprocess("hello    world")
        assert result == "hello world"
    
    def test_tokenization(self):
        preprocessor = TextPreprocessor()
        
        tokens = preprocessor.tokenize("hello world")
        assert tokens == ["hello", "world"]


class TestIntentClassifier:
    """Test intent classification functionality."""
    
    def setUp(self):
        self.classifier = IntentClassifier()
    
    def test_greeting_classification(self):
        classifier = IntentClassifier()
        
        # Test various greeting patterns
        greet_inputs = ["hello", "hi", "good morning", "hey there"]
        
        for input_text in greet_inputs:
            intent, confidence, slots = classifier.classify(input_text)
            assert intent == "greet"
            assert confidence > 0.6  # Should have reasonable confidence
    
    def test_faq_hours_classification(self):
        classifier = IntentClassifier()
        
        # Test business hours queries
        hours_inputs = [
            "what are your hours",
            "when are you open",
            "business hours",
            "what time do you close"
        ]
        
        for input_text in hours_inputs:
            intent, confidence, slots = classifier.classify(input_text)
            assert intent == "faq_hours"
            assert confidence > 0.6
    
    def test_faq_price_classification(self):
        classifier = IntentClassifier()
        
        # Test pricing queries
        price_inputs = [
            "how much does it cost",
            "what are your prices",
            "pricing information",
            "how expensive"
        ]
        
        for input_text in price_inputs:
            intent, confidence, slots = classifier.classify(input_text)
            assert intent == "faq_price"
            assert confidence > 0.6
    
    def test_fallback_classification(self):
        classifier = IntentClassifier()
        
        # Test unrecognized input
        fallback_inputs = [
            "xyz random text",
            "completely unrelated query",
            "asdfghjkl"
        ]
        
        for input_text in fallback_inputs:
            intent, confidence, slots = classifier.classify(input_text)
            assert intent == "fallback"
    
    def test_confidence_threshold(self):
        classifier = IntentClassifier()
        
        # Test that low confidence inputs fall back to fallback intent
        intent, confidence, slots = classifier.classify("somewhat similar to greeting but not really")
        
        # Should either classify correctly with good confidence or fallback
        if intent != "fallback":
            assert confidence >= classifier.intent_config.confidence_threshold
