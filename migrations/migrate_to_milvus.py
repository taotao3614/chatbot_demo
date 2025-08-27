import pymysql
from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# MySQL配置
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "q3demo",
    "charset": "utf8mb4",
    "port": 3307
}

# Milvus配置（与milvus.py保持一致）
MILVUS_HOST = "127.0.0.1"
MILVUS_PORT = "19530"
MILVUS_DB = "q3demo"
MILVUS_ALIAS = "q3"
COLLECTION_NAME = "faq_qa"
BATCH_SIZE = 100  # 每批处理的数据量

def init_connections():
    """初始化MySQL和Milvus连接"""
    # 连接MySQL
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    
    # 连接Milvus
    connections.connect(
        alias=MILVUS_ALIAS,
        host=MILVUS_HOST,
        port=MILVUS_PORT,
        db_name=MILVUS_DB
    )
    collection = Collection(name=COLLECTION_NAME, using=MILVUS_ALIAS)
    collection.load()  # 加载集合到内存
    
    return mysql_conn, collection

def get_total_records(cursor):
    """获取总记录数"""
    cursor.execute("SELECT COUNT(*) FROM faq_qa")
    return cursor.fetchone()[0]

def batch_generate_embeddings(model, texts):
    """批量生成文本嵌入向量"""
    return model.encode(texts, show_progress_bar=False)

def main():
    # 初始化sentence transformer模型
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 建立连接
    print("Connecting to databases...")
    mysql_conn, collection = init_connections()
    cursor = mysql_conn.cursor()
    
    try:
        # 获取总记录数用于进度显示
        total_records = get_total_records(cursor)
        print(f"Total records to migrate: {total_records}")
        
        # 分批读取MySQL数据
        offset = 0
        with tqdm(total=total_records, desc="Migrating data") as pbar:
            while True:
                # 读取一批数据
                cursor.execute("""
                    SELECT uuid, category, question, answer 
                    FROM faq_qa 
                    LIMIT %s OFFSET %s
                """, (BATCH_SIZE, offset))
                
                records = cursor.fetchall()
                if not records:
                    break
                
                # 准备数据
                questions = [record[2] for record in records]  # 使用question生成embedding
                embeddings = batch_generate_embeddings(model, questions)
                
                # 逐条插入Milvus
                for i, record in enumerate(records):
                    entities = {
                        "faq_uuid": str(record[0]),    # 确保UUID是字符串
                        "category": str(record[1]),    # 确保category是字符串
                        "question": str(record[2]),    # 确保question是字符串
                        "answer": str(record[3]),      # 确保answer是字符串
                        "embedding": embeddings[i].tolist()  # 对应的embedding
                    }
                    # 插入单条数据
                    collection.insert(entities)
                
                # 更新进度
                offset += len(records)
                pbar.update(len(records))
        
        # 创建索引（如果还没创建）
        print("Creating index if not exists...")
        collection.flush()  # 确保数据持久化
        print(f"Successfully migrated {offset} records to Milvus!")
        
    finally:
        # 清理连接
        cursor.close()
        mysql_conn.close()
        connections.disconnect(MILVUS_ALIAS)

if __name__ == "__main__":
    main()
