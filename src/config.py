"""
Configuration management for GDPR RAG system
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict, Optional
import yaml
from pathlib import Path


class OllamaConfig(BaseSettings):
    base_url: str = "http://localhost:11434"
    model: str = "llama2"
    embedding_model: str = "llama2"
    temperature: float = 0.1
    top_k: int = 40
    top_p: float = 0.9


class EmbeddingsConfig(BaseSettings):
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32


class FAISSConfig(BaseSettings):
    index_type: str = "HNSW"
    dimension: int = 384
    hnsw_m: int = 32
    hnsw_ef_construction: int = 200
    hnsw_ef_search: int = 128
    store_path: str = "vectorstore/gdpr_faiss_index"


class TextProcessingConfig(BaseSettings):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    preserve_structure: bool = True
    min_chunk_size: int = 100
    languages: List[str] = ["en", "de", "fr", "es", "it"]


class RetrievalConfig(BaseSettings):
    top_k: int = 5
    score_threshold: float = 0.7
    rerank: bool = True
    filter_by: List[str] = ["source_type", "language", "article_number", "violation_category"]


class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        self.ollama = OllamaConfig(**config_dict.get('ollama', {}))
        self.embeddings = EmbeddingsConfig(**config_dict.get('embeddings', {}))
        self.faiss = FAISSConfig(**config_dict.get('faiss', {}))
        self.text_processing = TextProcessingConfig(**config_dict.get('text_processing', {}))
        self.retrieval = RetrievalConfig(**config_dict.get('retrieval', {}))
        
        self.data_sources = config_dict.get('data_sources', {})
        self.risk_assessment = config_dict.get('risk_assessment', {})
        self.prompts = config_dict.get('prompts', {})
        self.logging = config_dict.get('logging', {})
        self.performance = config_dict.get('performance', {})
    
    def get(self, key: str, default=None):
        """Get configuration value by key"""
        return getattr(self, key, default)
