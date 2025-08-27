import json
import os
from typing import Dict, Tuple, List, Optional
import random
from sentence_transformers import util
from .model_singleton import model

class IntentClassifier:
    def __init__(
        self,
        patterns_file: str = 'app/data/chat_patterns.json',
        casual_threshold: float = 0.65  # 降低阈值从0.75到0.65
    ):
        """初始化意图分类器"""
        self.casual_threshold = casual_threshold
        
        # 加载对话模式
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns = json.load(f)
            
        # 预计算所有casual patterns的embeddings（只在初始化时显示进度条）
        self.casual_texts = []
        for category, patterns in self.patterns['casual_patterns'].items():
            self.casual_texts.extend(patterns)
        self.casual_embeddings = model.encode_texts(self.casual_texts, show_progress_bar=True)
        
    def classify(self, query: str) -> Tuple[str, float, Dict[str, any]]:
        """对输入文本进行分类"""
        # 计算查询文本的embedding（不显示进度条）
        query_embedding = model.encode_text(query, show_progress_bar=False)
        
        # 计算与所有casual patterns的相似度
        similarities = util.pytorch_cos_sim(query_embedding, self.casual_embeddings)[0]
        max_similarity = float(similarities.max())
        
        # 如果相似度超过阈值，判定为casual对话
        if max_similarity >= self.casual_threshold:
            # 找出最相似的pattern
            max_idx = int(similarities.argmax())
            matched_text = self.casual_texts[max_idx]
            
            # 确定category
            for category, patterns in self.patterns['casual_patterns'].items():
                if matched_text in patterns:
                    # 随机选择一个对应的回复
                    response = random.choice(self.patterns['casual_responses'][category])
                    return 'casual', max_similarity, {
                        'category': category,
                        'response': response,
                        'matched_pattern': matched_text
                    }
                    
        # 默认返回search类型
        return 'search', 1.0 - max_similarity, {}