import os
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables
load_dotenv()

app = FastAPI(title="Chatbot Analytics Dashboard")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Database connection
DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3307/q3demo")
engine = create_engine(DB_URL)

def get_date_range():
    """Get the date range for the last 7 days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date

@app.get("/")
async def dashboard(request: Request):
    """Render the main dashboard page"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/api/kpi")
async def get_kpi_data():
    """Get KPI data for the dashboard"""
    start_date, end_date = get_date_range()
    
    with engine.connect() as conn:
        # Total messages
        total_messages = pd.read_sql(
            text("""
                SELECT COUNT(*) as total
                FROM conversation_turns
                WHERE create_time BETWEEN :start AND :end
            """),
            conn,
            params={"start": start_date, "end": end_date}
        ).iloc[0]["total"]

        # Unique users (sessions)
        unique_users = pd.read_sql(
            text("""
                SELECT COUNT(DISTINCT session_id) as total
                FROM sessions
                WHERE create_time BETWEEN :start AND :end
            """),
            conn,
            params={"start": start_date, "end": end_date}
        ).iloc[0]["total"]

        # Average messages per session
        avg_messages = pd.read_sql(
            text("""
                SELECT AVG(message_count) as avg_messages
                FROM (
                    SELECT session_id, COUNT(*) as message_count
                    FROM conversation_turns
                    WHERE create_time BETWEEN :start AND :end
                    GROUP BY session_id
                ) t
            """),
            conn,
            params={"start": start_date, "end": end_date}
        ).iloc[0]["avg_messages"]

        # Emotion and urgency stats
        emotion_urgency = pd.read_sql(
            text("""
                SELECT 
                    COUNT(CASE WHEN emotion = 'negative' THEN 1 END) * 100.0 / COUNT(*) as negative_ratio,
                    COUNT(CASE WHEN urgency = 'high' THEN 1 END) * 100.0 / COUNT(*) as high_urgency_ratio,
                    COUNT(CASE WHEN emotion = 'negative' AND urgency = 'high' THEN 1 END) as high_urgency_negative
                FROM conversation_turns
                WHERE create_time BETWEEN :start AND :end
            """),
            conn,
            params={"start": start_date, "end": end_date}
        ).iloc[0]

    return {
        "total_messages": int(total_messages),
        "unique_users": int(unique_users),
        "avg_messages_per_session": round(float(avg_messages), 2),
        "negative_ratio": round(float(emotion_urgency["negative_ratio"]), 2),
        "high_urgency_ratio": round(float(emotion_urgency["high_urgency_ratio"]), 2),
        "high_urgency_negative": int(emotion_urgency["high_urgency_negative"])
    }

@app.get("/api/hourly_heatmap")
async def get_hourly_heatmap():
    """Get hourly message distribution for heatmap"""
    start_date, end_date = get_date_range()
    
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT 
                    DATE(create_time) as date,
                    HOUR(create_time) as hour,
                    COUNT(*) as message_count
                FROM conversation_turns
                WHERE create_time BETWEEN :start AND :end
                GROUP BY DATE(create_time), HOUR(create_time)
                ORDER BY date, hour
            """),
            conn,
            params={"start": start_date, "end": end_date}
        )
    
    # Pivot the data for heatmap format
    pivot_df = df.pivot(index='hour', columns='date', values='message_count').fillna(0)
    return pivot_df.to_dict()

@app.get("/api/daily_trend")
async def get_daily_trend():
    """Get daily message trend with emotion breakdown"""
    start_date, end_date = get_date_range()
    
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT 
                    DATE(create_time) as date,
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN emotion = 'negative' THEN 1 END) as negative_messages
                FROM conversation_turns
                WHERE create_time BETWEEN :start AND :end
                GROUP BY DATE(create_time)
                ORDER BY date
            """),
            conn,
            params={"start": start_date, "end": end_date}
        )
    
    return df.to_dict(orient='records')

@app.get("/api/top_intents")
async def get_top_intents():
    """Get top intents that led to escalation or negative feedback"""
    start_date, end_date = get_date_range()
    
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT 
                    intent,
                    COUNT(*) as count,
                    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
                FROM conversation_turns
                WHERE 
                    create_time BETWEEN :start AND :end
                    AND (emotion = 'negative' OR urgency = 'high')
                GROUP BY intent
                ORDER BY count DESC
                LIMIT 10
            """),
            conn,
            params={"start": start_date, "end": end_date}
        )
    
    return df.to_dict(orient='records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8088)
