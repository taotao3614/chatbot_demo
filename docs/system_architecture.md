# Chatbot System Architecture

This document describes the architecture of our chatbot system, including the online QA process, data storage, and data processing pipelines.

## System Flow Diagram

```mermaid
flowchart TD
 subgraph subGraph0["Online QA Process"]
    direction TB
        B{"Empty Input?"}
        A["User Input"]
        C["Return Welcome Message"]
        D["Create/Get Session"]
        E["Intent Classification"]
        F{"Is Casual Chat?"}
        G["Return Preset Reply<br>1.1 自然な会話が可能なチャットボット"]
        H["Semantic FAQ Search"]
        H1["Generate Query Vector"]
        H2["Vector Similarity Search"]
        I{"Similarity > Threshold?"}
        J["Return FAQ Answer<br>1.1 よくある質問（FAQ）への自動回答"]
        K["Mark for Human Support<br>1.1 複雑な問い合わせの人間担当者への適切なエスカレーション"]
        L["Emotion Analysis<br>2.1 感情分析"]
        M["Urgency Analysis<br>2.1 緊急度・重要度の自動判定"]
        N["Update Session State<br>1.1 会話履歴の構造化された保存"]
        O["Record Conversation Turn"]
        P["Return Response"]
        Q["Record Feedback<br>1.2 ユーザーフィードバックの収集と反映<br>2.1 感情分析による顧客満足度の把握"]
  end
 subgraph subGraph1["Storage Layer"]
    direction LR
        MYSQL[("MySQL DB")]
        MDB[("Milvus Vector DB")]
  end
 subgraph subGraph2["FAQ Pipeline"]
    direction TB
        SYNC1["Periodic Sync Task"]
        SYNC2["Batch Vectorization"]
        SYNC3["Update Vector DB<br>1.2 会話パターンの学習による回答精度向上"]
  end
 subgraph subGraph3["Conversation Pipeline"]
    direction TB
        CLEAN1["Periodic Data Analysis"]
        CLEAN2["Filter Quality Conversations"]
        CLEAN3["Process Feedback Data"]
        CLEAN4{"Quality Assessment"}
        CLEAN5["Generate FAQ Entries<br>1.2 未知の質問パターンの検出と学習データ化"]
        CLEAN6["Archive"]
  end
 subgraph subGraph4["Data Processing"]
    direction TB
        subGraph2
        subGraph3
        DASH["Dashboard<br>2.1 感情分析による顧客満足度の把握"]
  end

 subgraph subGraph5["Customer Insight Analysis Future"]
    direction TB
        TOPIC1["BERTopic Clustering<br>2.1 会話から顧客の課題・ニーズを自動抽出"]
        RULE1["Rule-based Analysis<br>2.1 緊急度・重要度の自動判定"]
        MODEL1["ML Model Training<br>2.1 感情分析・緊急度判定の精度向上"]
        DATA1["Data Collection & Labeling"]
        
        TOPIC1 --> MODEL1
        RULE1 --> MODEL1
        DATA1 --> MODEL1
        MODEL1 --> RULE1
  end

    A --> B
    B -- Yes --> C
    B -- No --> D
    D --> E
    E --> F
    F -- Yes --> G
    F -- No --> H
    H --> H1
    H1 --> H2
    H2 --> I & MDB
    I -- Yes --> J
    I -- No --> K
    G --> L
    J --> L
    K --> L
    L --> M
    M --> N
    N --> O & MYSQL
    O --> P
    P --> Q
    SYNC1 -- Read --> MYSQL
    SYNC1 --> SYNC2
    SYNC2 --> SYNC3
    SYNC3 --> MDB
    CLEAN1 -- Read --> MYSQL
    CLEAN1 --> CLEAN2
    CLEAN2 --> CLEAN3
    CLEAN3 --> CLEAN4
    CLEAN4 -- Pass --> CLEAN5
    CLEAN5 -- Update --> MYSQL
    CLEAN4 -- Fail --> CLEAN6
    Q --> MYSQL
    MYSQL --> DASH

    %% Future connections
    Q -.- TOPIC1
    Q -.- DATA1
    L -.- DATA1
    M -.- DATA1
    MYSQL -.- TOPIC1
```

## Architecture Components

### Online QA Process
- Natural Conversation (1.1 自然な会話が可能なチャットボット)
- FAQ Auto-response (1.1 よくある質問（FAQ）への自動回答)
- Human Support Escalation (1.1 複雑な問い合わせの人間担当者への適切なエスカレーション)
- Emotion Analysis (2.1 感情分析)
- Urgency Assessment (2.1 緊急度・重要度の自動判定)
- Structured Conversation History (1.1 会話履歴の構造化された保存)
- User Feedback Collection (1.2 ユーザーフィードバックの収集と反映)
- Customer Satisfaction Analysis (2.1 感情分析による顧客満足度の把握)

### Storage Layer
- MySQL Database
  - FAQ data and conversation history
  - Session and feedback management
  - Analytics and monitoring data
- Milvus Vector Database
  - Semantic vectors for enhanced search
  - Real-time query matching

### Data Processing
- FAQ Pipeline
  - Periodic data synchronization
  - Vector database updates (1.2 会話パターンの学習による回答精度向上)
  - Pattern learning and optimization
- Conversation Pipeline
  - Quality conversation filtering
  - Feedback data processing
  - New pattern detection (1.2 未知の質問パターンの検出と学習データ化)
  - Knowledge base enhancement
- Dashboard
  - System performance monitoring
  - Customer satisfaction tracking (2.1 感情分析による顧客満足度の把握)

### Customer Insight Analysis (Future Enhancement)
- Automated Issue Extraction (2.1 会話から顧客の課題・ニーズを自動抽出)
  - BERTopic clustering implementation
  - Category-based issue classification
  - Continuous pattern learning
- Hybrid Analysis System
  - Rule-based initial analysis (2.1 緊急度・重要度の自動判定)
  - ML model enhancement (2.1 感情分析・緊急度判定の精度向上)
  - Continuous model training
- Data Pipeline
  - Structured data collection
  - Quality assessment and labeling
  - Model performance monitoring

## Color Coding
- Orange: MySQL Database
- Blue: Milvus Vector Database
- Green: FAQ Update Process
- Yellow: Conversation Processing