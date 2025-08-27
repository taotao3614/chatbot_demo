from typing import Dict, Any
from app.nlp.semantic_search import SemanticSearch
from app.nlp.intent_classifier import IntentClassifier

class ResponsePolicy:
    def __init__(self):
        """初始化响应策略"""
        self.semantic_search = SemanticSearch()  # 使用默认配置
        self.intent_classifier = IntentClassifier()  # 意图分类器
        
    def get_response(self, query: str) -> Dict[str, Any]:
        """获取响应
        
        Args:
            query: 用户问题
            
        Returns:
            Dict包含：
            - response: 回复内容
            - confidence: 置信度
            - need_human: 是否需要人工介入
            - source: 回复来源 ('casual', 'faq', 'human')
        """
        # 首先进行意图分类
        intent_type, confidence, slots = self.intent_classifier.classify(query)
        
        # 如果是日常对话，直接返回预设回复
        if intent_type == 'casual':
            return {
                "response": slots.get('response', 'Hello!'),
                "confidence": confidence,
                "need_human": False,
                "source": "casual",
                "metadata": {
                    "category": slots.get('category', 'unknown')
                }
            }
            
        # 如果是需要查库的对话，进行语义搜索
        found, faq_match, similarity = self.semantic_search.search(query)
        
        if found:
            return {
                "response": faq_match["answer"],
                "confidence": similarity,
                "need_human": False,
                "source": "faq",
                "metadata": {
                    "faq_uuid": faq_match["faq_uuid"],
                    "category": faq_match["category"],
                    "matched_question": faq_match["question"]
                }
            }
            
        # 如果没有找到合适的答案，转人工处理
        return {
            "response": "I apologize, but I need to escalate this to a human agent for better assistance.",
            "confidence": 0.0,
            "need_human": True,
            "source": "human",
            "metadata": {}
        }
        
    def close(self):
        """清理资源"""
        if hasattr(self, 'semantic_search'):
            self.semantic_search.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()