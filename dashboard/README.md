# Chatbot Analytics Dashboard

A real-time analytics dashboard for monitoring chatbot performance metrics.

## Features

- Real-time KPI monitoring
- Message volume heatmap (7x24)
- Daily message trends
- Sentiment and urgency analysis
- Top problem intents tracking
- Auto-refresh every 5 minutes

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your database configuration:
```
DATABASE_URL=mysql+pymysql://user:password@localhost/q3demo
```

4. Run the dashboard:
```bash
uvicorn main:app --reload
```

5. Access the dashboard at http://localhost:8088

## Data Refresh

- The dashboard automatically refreshes every 5 minutes
- All metrics show data from the last 7 days
- Time zone is displayed in local time (JST)

## Metrics Definitions

- Total Messages: All messages in the last 7 days
- Unique Users: Distinct users (by session) in the last 7 days
- Avg Messages/Session: Average number of messages per user session
- Negative Sentiment %: Percentage of messages with negative sentiment
- High Urgency %: Percentage of messages marked as high urgency
- High Urgency & Negative: Count of messages that are both high urgency and negative
