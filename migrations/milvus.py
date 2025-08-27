# create_collection_in_q3demo.py
# pip install pymilvus
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

HOST, PORT = "127.0.0.1", "19530"
DB_NAME = "q3demo"          # 你的数据库名
USING = "q3"                # 连接别名（随便起）
COLLECTION = "faq_qa"    # 集合名
EMBED_DIM = 384             # 文本向量维度（按你的嵌入模型来）

INDEX_PARAMS = {
    "index_type": "HNSW",
    "metric_type": "COSINE",          # 若未做归一化可改为 "L2"
    "params": {"M": 16, "efConstruction": 200}
}

# 1) 连接到 q3demo 数据库
connections.connect(alias=USING, host=HOST, port=PORT, db_name=DB_NAME)

# 2) 在 q3demo 中建集合（等同“建表”）
if not utility.has_collection(COLLECTION, using=USING):
    fields = [
        FieldSchema(name="id",        dtype=DataType.INT64,  is_primary=True, auto_id=True),
        FieldSchema(name="faq_uuid",  dtype=DataType.VARCHAR, max_length=36),     # 与 MySQL UUID 对齐
        FieldSchema(name="category",  dtype=DataType.VARCHAR, max_length=64),     # 业务分类
        FieldSchema(name="question",  dtype=DataType.VARCHAR, max_length=1024),   # 标准问
        FieldSchema(name="answer",    dtype=DataType.VARCHAR, max_length=16384),  # 答案内容
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBED_DIM)
    ]
    schema = CollectionSchema(fields, description="FAQ semantic index")
    col = Collection(name=COLLECTION, schema=schema, shards_num=2, using=USING)
else:
    col = Collection(name=COLLECTION, using=USING)

# 3) 为向量字段建索引并加载
col.create_index(field_name="embedding", index_params=INDEX_PARAMS)
col.load()
print(f"[OK] Collection `{DB_NAME}.{COLLECTION}` is ready.")
