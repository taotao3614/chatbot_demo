"""
FAQ Clustering using BERTopic

This script clusters FAQ questions using BERTopic and writes results to MySQL database.

Requirements:
    pip install bertopic pandas numpy sentence-transformers pymysql scikit-learn
"""
import os
import re
import json
import warnings
import pandas as pd
import numpy as np
import random
import uuid

from typing import List, Dict
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import pymysql
from bs4 import BeautifulSoup

# Configuration
CONFIG = {
    # 文件和目录配置
    "input_file": "migrations/faq.json",
    "output_dir": "data/processed/bertopic",
    "model_dir": "artifacts/bertopic/model",
    
    # 模型配置
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "nr_topics": 10,          # 期望的主题数量
    "random_state": 42,       # 随机种子
    
    # 主题大小限制
    "min_topic_size": 0.05,   # 最小主题占比 (5%)
    "max_topic_size": 0.60,   # 最大主题占比 (60%)
    
    # 词汇和短语配置
    "ngram_range": (1, 1),    # 词组长度范围 (min, max)
    "top_n_words": 1,         # 用于生成主题名称的词数
    "min_word_score": 0.1,    # 词语最小重要性分数
    
    # Database configs
    "mysql": {
        "host": "localhost",
        "port": 3307,
        "user": "root",
        "password": "root",
        "database": "q3demo"
    }
}

# Low information words that should trigger fallback to phrase names
LOW_INFO_WORDS = [
    'issue', 'account', 'help', 'question', 'support', 'problem', 'can', 'what', 'how',
    'do', 'does', 'is', 'are', 'was', 'were', 'will', 'would', 'could', 'should',
    'have', 'has', 'had', 'having', 'get', 'getting', 'got', 'i', 'you', 'he', 'she',
    'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
]

def setup_dirs() -> None:
    """Create necessary directories if they don't exist."""
    for path in [CONFIG['output_dir'], CONFIG['model_dir']]:
        os.makedirs(path, exist_ok=True)

def preprocess_text(text: str) -> str:
    """Clean and normalize text."""
    if pd.isna(text):
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove HTML if BeautifulSoup is available
    try:
        text = BeautifulSoup(text, "html.parser").get_text()
    except:
        pass
    
    # Convert to lowercase and normalize whitespace
    text = re.sub(r'\s+', ' ', text.lower().strip())
    
    return text

def load_and_preprocess_data() -> pd.DataFrame:
    """Load and preprocess the FAQ data from JSON file."""
    print("Loading and preprocessing data...")
    
    # Read JSON file
    with open(CONFIG['input_file'], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert JSON to DataFrame
    df = pd.DataFrame(data)
    
    # Ensure required columns exist
    if 'question' not in df.columns:
        raise ValueError("Input file must contain 'question' field")
    
    # Remove UUID generation - let MySQL handle it
    
    # Preprocess questions
    df['question_clean'] = df['question'].apply(preprocess_text)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['question_clean'])
    
    # Remove empty questions
    df = df[df['question_clean'].str.len() > 0]
    
    print(f"Loaded {len(df)} questions with fields: {', '.join(df.columns)}")
    
    return df

def create_bertopic_model(data_size: int) -> BERTopic:
    """Initialize and configure BERTopic model."""
    # Configure CountVectorizer with dynamic parameters based on data size
    min_df = 1 if data_size < 100 else 2
    max_df = min(0.95, max(0.5, 1.0 - 10/data_size))  # Dynamic max_df
    
    # Custom stop words to keep important business terms
    custom_stop_words = [
        'a', 'an', 'the', 'this', 'that', 'these', 'those',
        'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
        'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
    ]
    
    vectorizer = CountVectorizer(
        ngram_range=CONFIG['ngram_range'],  # 使用配置的词组长度范围
        stop_words='english',               # 使用英语停用词
        min_df=min_df,
        max_df=max_df
    )
    
    # Initialize embedding model
    embedding_model = SentenceTransformer(CONFIG['embedding_model'])
    
    # Create BERTopic model with correct parameters
    topic_model = BERTopic(
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        nr_topics=CONFIG['nr_topics'],
        min_topic_size=max(2, data_size // 20)  # Dynamic min topic size
    )
    
    return topic_model

def validate_clustering(df: pd.DataFrame, topics_df: pd.DataFrame) -> List[str]:
    """Validate clustering results and return warnings."""
    warnings_list = []
    
    # Check number of topics
    n_topics = len(topics_df)
    if not (5 <= n_topics <= 7):
        warnings_list.append(f"Number of topics ({n_topics}) outside desired range [5,7]")
    
    # Check topic distribution
    for _, row in topics_df.iterrows():
        topic_size = row['count'] / len(df)
        if topic_size < CONFIG['min_topic_size']:
            warnings_list.append(f"Topic {row['topic_name']} too small ({topic_size:.1%})")
        elif topic_size > CONFIG['max_topic_size']:
            warnings_list.append(f"Topic {row['topic_name']} too large ({topic_size:.1%})")
    
    return warnings_list

def generate_topic_name(topic_words: List[tuple]) -> str:
    """Generate topic name from top words with improved readability."""
    if not topic_words:
        return "other"
    
    # Extract words and scores from tuples
    words_with_scores = [(word, score) for word, score in topic_words[:CONFIG['top_n_words']]]
    
    # Filter out low information words but keep their scores for reference
    filtered_words = [(w, s) for w, s in words_with_scores if w not in LOW_INFO_WORDS]
    
    if not filtered_words:
        # If all words are low information, use original words
        filtered_words = words_with_scores
    
    # 只选择得分最高且超过阈值的词
    significant_words = [w for w, s in filtered_words if s > CONFIG['min_word_score']]
    
    if significant_words:
        return significant_words[0]  # 返回得分最高的词
    elif filtered_words:
        return filtered_words[0][0]  # 如果没有显著性词，返回第一个词
    else:
        return "other"

def create_mysql_table():
    """Create MySQL table if it doesn't exist."""
    conn = pymysql.connect(**CONFIG['mysql'])
    cursor = conn.cursor()
    
    try:
        # Create table based on qs.sql structure with auto-generated UUID
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS faq_qa (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
            uuid VARCHAR(36) NOT NULL,
            category VARCHAR(64) NOT NULL,
            question TEXT NOT NULL,
            answer MEDIUMTEXT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_uuid (uuid),
            KEY idx_category (category),
            FULLTEXT KEY ft_q (question, answer)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("MySQL table created/verified successfully")
        
        # Show table structure for verification
        cursor.execute("DESCRIBE faq_qa")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
        
    finally:
        cursor.close()
        conn.close()

def insert_data_to_mysql(assignments_df: pd.DataFrame) -> None:
    """Insert clustered data into MySQL."""
    conn = pymysql.connect(**CONFIG['mysql'])
    cursor = conn.cursor()
    
    try:
        # Clear existing data (optional - remove if you want to keep existing data)
        # cursor.execute("DELETE FROM faq_qa")
        
        # Insert new data with generated UUID string
        insert_query = """
        INSERT INTO faq_qa (uuid, category, question, answer) 
        VALUES (%s, %s, %s, %s)
        """
        
        for _, row in assignments_df.iterrows():
            # Generate UUID string (36 chars, with hyphens)
            uuid_str = str(uuid.uuid4())
            cursor.execute(insert_query, (
                uuid_str,
                row['topic_name'],
                row['question'],
                row.get('answer', 'No answer provided')  # Use default text if no answer
            ))
        
        conn.commit()
        print(f"Inserted {len(assignments_df)} rows in MySQL")
        
        # Test query to verify data insertion
        cursor.execute("SELECT uuid, category, question FROM faq_qa ORDER BY id DESC LIMIT 3")
        results = cursor.fetchall()
        print("\nSample inserted data:")
        for result in results:
            print(f"UUID: {result[0]}, Category: {result[1]}, Question: {result[2][:50]}...")
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main execution flow."""
    # Set random seeds for reproducibility
    random.seed(CONFIG['random_state'])
    np.random.seed(CONFIG['random_state'])
    
    setup_dirs()
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    print(f"Loaded {len(df)} unique questions")
    
    # Create and fit model
    model = create_bertopic_model(len(df))
    topics, probs = model.fit_transform(df['question_clean'])
    
    # Get topic information
    topic_info = model.get_topic_info()
    
    # Generate topic names and create topics DataFrame
    topics_df = pd.DataFrame({
        'topic_id': topic_info['Topic'],
        'count': topic_info['Count']
    })
    
    # Add topic names using custom logic
    topics_df['top_words'] = [model.get_topic(i) for i in topics_df['topic_id']]
    topics_df['topic_name'] = topics_df['top_words'].apply(generate_topic_name)
    
    # Create assignments DataFrame
    assignments_df = df.copy()
    assignments_df['topic_id'] = topics
    assignments_df['prob'] = probs
    assignments_df = assignments_df.merge(
        topics_df[['topic_id', 'topic_name']],
        on='topic_id',
        how='left'
    )
    
    # Handle outliers (topic -1)
    assignments_df['topic_name'] = assignments_df['topic_name'].fillna('other')
    
    # Validate results
    validation_warnings = validate_clustering(df, topics_df[topics_df['topic_id'] != -1])
    for warning in validation_warnings:
        print(f"Warning: {warning}")
    
    # Save results
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    
    assignments_df.to_csv(
        f"{CONFIG['output_dir']}/assignments.csv",
        index=False
    )
    
    topics_df.to_csv(
        f"{CONFIG['output_dir']}/topics.csv",
        index=False
    )
    
    # Save model
    try:
        model.save(CONFIG['model_dir'])
        print("Model saved successfully")
    except Exception as e:
        print(f"Warning: Could not save model: {e}")
    
    # Print sample for manual validation (5 questions per topic)
    print("\nSample questions per topic for manual validation:")
    for topic_id in topics_df['topic_id']:
        if topic_id == -1:  # Skip outliers
            continue
        topic_questions = assignments_df[assignments_df['topic_id'] == topic_id]
        topic_name = topics_df[topics_df['topic_id'] == topic_id]['topic_name'].iloc[0]
        print(f"\nTopic: {topic_name} (ID: {topic_id})")
        sample_size = min(5, len(topic_questions))
        for i, (_, row) in enumerate(topic_questions.sample(sample_size).iterrows()):
            print(f"  {i+1}. {row['question']}")
    
    # Create MySQL table and insert data
    create_mysql_table()
    insert_data_to_mysql(assignments_df)
    
    print("\nClustering completed successfully!")
    print(f"Total questions processed: {len(assignments_df)}")
    print(f"Number of topics generated: {len(topics_df[topics_df['topic_id'] != -1])}")

if __name__ == "__main__":
    main()