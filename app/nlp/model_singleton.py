"""
Model singleton to avoid multiple model loads
"""
import os
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ModelSingleton:
    _instance = None
    _model = None
    _pid = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        current_pid = os.getpid()
        
        # 如果是新进程或模型未初始化，则加载模型
        if cls._pid != current_pid or cls._model is None:
            logger.info(f"Initializing model for process {current_pid}")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            cls._pid = current_pid
        
        return cls._model
    
    @classmethod 
    def encode_text(cls, text: str, show_progress_bar: bool = False):
        """编码文本，默认不显示进度条"""
        model = cls.get_model()
        return model.encode(text, show_progress_bar=show_progress_bar)
    
    @classmethod
    def encode_texts(cls, texts: list, show_progress_bar: bool = False):
        """批量编码文本，默认不显示进度条"""
        model = cls.get_model()
        return model.encode(texts, show_progress_bar=show_progress_bar)

# Global instance
model = ModelSingleton()