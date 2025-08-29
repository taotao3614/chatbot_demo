# Chatbot Test Conversations

## Test Description
This document contains test conversations covering:
- FAQ intent recognition
- Emotion analysis (positive/negative/neutral)
- Urgency detection (high/medium/low)

## 1. Basic FAQ Testing

### Scenario 1: Payment Methods (Neutral Emotion, Low Urgency)
```
User: What payment methods do you accept for online orders?
Expected:
- Emotion: neutral (using "what" - neutral word)
- Urgency: low
- Should contain: Information about credit cards, debit cards, and PayPal
```

### Scenario 2: Order Tracking (Neutral Emotion, Medium Urgency)
```
User: I need to track my order soon, how can I do that?
Expected:
- Emotion: neutral (using "need" - neutral word)
- Urgency: medium (using "soon" - medium urgency word)
- Should contain: Instructions about logging into account and order history
```

## 2. Urgent Scenarios

### Scenario 3: Order Cancellation (Negative Emotion, High Urgency)
```
User: This is terrible! I need to cancel my order immediately, it's urgent!
Expected:
- Emotion: negative (using "terrible" - negative word)
- Urgency: high (using "immediately", "urgent" - high urgency words)
- Should contain: Order cancellation process
```

## 3. Positive Feedback

### Scenario 5: Satisfaction (Positive Emotion, Low Urgency)
```
User: Thank you for the excellent service! I would like to know about your loyalty program.
Expected:
- Emotion: positive (using "thank", "excellent" - positive words)
- Urgency: low (using "would like" - low urgency phrase)
- Should contain: Loyalty program details
```

## 4. Complex Scenarios

### Scenario 7: Damaged Package (Negative Emotion, High Urgency)
```
User: My package arrived completely damaged, this is horrible! I need immediately assistance!
Expected:
- Emotion: negative (using "horrible" - negative word)
- Urgency: high (using "immediate" - high urgency word)
- Should contain: Damaged goods handling process
```

## Test Guidelines

### Emotion Keywords
- Positive: thank, thanks, great, good, excellent, wonderful
- Negative: bad, terrible, awful, horrible, angry
- Neutral: what, how, when, where, which

### Urgency Keywords
- High: immediately, urgent, emergency, asap, right now
- Medium: soon, important, needed, should
- Low: maybe, sometime, when possible

### Testing Tips
1. Execute each test scenario in order
2. Record system responses
3. Compare expected vs actual results
4. Focus on emotion and urgency detection accuracy
5. Verify answer relevance and completeness