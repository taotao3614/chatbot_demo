import logging
from typing import List, Dict, Tuple, Optional
from pymilvus import Collection, connections
from .model_singleton import model

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(
        self,
        milvus_host: str = "127.0.0.1",
        milvus_port: str = "19530",
        milvus_db: str = "q3demo",
        milvus_alias: str = "q3",
        collection_name: str = "faq_qa",
        similarity_threshold: float = 0.6,  # 降低阈值
        top_k: int = 3
    ):
        """初始化语义搜索类"""
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.milvus_alias = milvus_alias
        self.collection_name = collection_name
        
        # 连接Milvus
        connections.connect(
            alias=milvus_alias,
            host=milvus_host,
            port=milvus_port,
            db_name=milvus_db
        )
        self.collection = Collection(collection_name, using=milvus_alias)
        self.collection.load()  # 加载集合到内存
        
    def search(self, query: str) -> Tuple[bool, Optional[Dict], float]:
        """搜索最相似的FAQ"""
        # 生成查询向量（不显示进度条）
        query_embedding = model.encode_text(query, show_progress_bar=False)
        
        # 在Milvus中搜索
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        results = self.collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=self.top_k,
            output_fields=["faq_uuid", "category", "question", "answer"]
        )

        # 检查最佳匹配的相似度得分
        if not results or not results[0]:
            logger.info(f"No results found for query: {query}")
            return False, None, 0.0
            
        best_match = results[0][0]  # 第一个查询的第一个结果
        similarity_score = float(best_match.score)
        
        # 限制相似度分数在合理范围内（处理浮点数精度问题）
        similarity_score = max(0.0, min(1.0, similarity_score))
        
        # 添加调试日志
        logger.info(f"Query: '{query}' | Best match: '{best_match.entity.get('question')}' | Score: {similarity_score:.3f} | Threshold: {self.similarity_threshold}")
        
        # 如果相似度低于阈值，视为未找到匹配
        if similarity_score < self.similarity_threshold:
            logger.info(f"Score {similarity_score:.3f} below threshold {self.similarity_threshold}")
            return False, None, similarity_score
            
        # 返回最佳匹配的FAQ信息
        matched_faq = {
            "faq_uuid": best_match.entity.get('faq_uuid'),
            "category": best_match.entity.get('category'),
            "question": best_match.entity.get('question'),
            "answer": best_match.entity.get('answer'),
            "similarity": similarity_score
        }
        
        logger.info(f"FAQ match found: {matched_faq['question']}")
        return True, matched_faq, similarity_score
        
    def close(self):
        """关闭Milvus连接"""
        if hasattr(self, 'collection'):
            self.collection.release()  # 释放集合
        connections.disconnect(self.milvus_alias)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()