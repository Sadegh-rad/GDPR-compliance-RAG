"""
RAG System - Retrieval-Augmented Generation for GDPR Compliance
Integrates FAISS vector store with Ollama for intelligent Q&A
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List, Optional
from loguru import logger
import json

try:
    import ollama
except ImportError:
    logger.error("Ollama package not installed. Install with: pip install ollama")
    raise

from vectorstore.faiss_store import FAISSVectorStore


class GDPRRAGSystem:
    """RAG system for GDPR compliance questions and analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ollama_config = config.get('ollama', {})
        self.retrieval_config = config.get('retrieval', {})
        self.prompts = config.get('prompts', {})
        
        # Initialize Ollama client
        self.base_url = self.ollama_config.get('base_url', 'http://localhost:11434')
        self.model = self.ollama_config.get('model', 'gpt-oss:latest')
        self.temperature = self.ollama_config.get('temperature', 0.1)
        
        logger.info(f"Initializing RAG system with Ollama model: {self.model}")
        
        # Initialize vector store
        self.vector_store = FAISSVectorStore(config)
        
        # Load existing index
        if not self.vector_store.load_index():
            logger.warning("No existing index found. Please build the index first.")
        
        # Initialize reranker if enabled
        self.reranker = None
        if self.retrieval_config.get('rerank', False):
            try:
                from sentence_transformers import CrossEncoder
                model_name = self.retrieval_config.get('rerank_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
                logger.info(f"Loading reranker model: {model_name}")
                self.reranker = CrossEncoder(model_name, max_length=512)
                logger.info("✓ Reranker loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load reranker: {e}. Continuing without reranking.")
    
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context from vector store with optional reranking
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filters: Metadata filters
        
        Returns:
            List of relevant documents with metadata (reranked if enabled)
        """
        if top_k is None:
            top_k = self.retrieval_config.get('top_k', 5)
        
        logger.info(f"Retrieving context for query: '{query[:100]}...'")
        
        # Retrieve more candidates if reranking is enabled
        retrieve_k = top_k * 2 if self.reranker else top_k
        
        results = self.vector_store.search(
            query=query,
            top_k=retrieve_k,
            filter_metadata=filters
        )
        
        # Filter by score threshold (PERMISSIVE - we'll rerank to find quality)
        score_threshold = self.retrieval_config.get('score_threshold', 0.7)
        filtered_results = [r for r in results if r['score'] >= score_threshold]
        
        # Apply reranking if enabled - THIS IS WHERE QUALITY COMES FROM
        if self.reranker and filtered_results:
            logger.info(f"Reranking {len(filtered_results)} candidates...")
            
            # Prepare query-document pairs for reranking
            pairs = [(query, doc['text'][:512]) for doc in filtered_results]  # Limit to 512 chars for cross-encoder
            
            # Get reranking scores (raw logits from cross-encoder)
            rerank_scores = self.reranker.predict(pairs)
            
            # Normalize scores using MIN-MAX scaling instead of sigmoid
            # Legal text cross-encoder gives very negative logits (-20 to -5)
            # Sigmoid doesn't work well - use min-max normalization instead
            import numpy as np
            rerank_scores = np.array(rerank_scores)
            
            # Min-max normalization to 0-1 range
            min_score = rerank_scores.min()
            max_score = rerank_scores.max()
            
            if max_score > min_score:
                # Normalize to 0-1 based on this batch's range
                normalized_scores = (rerank_scores - min_score) / (max_score - min_score)
            else:
                # All scores are the same - assign 0.5
                normalized_scores = np.full_like(rerank_scores, 0.5)
            
            # Add normalized rerank scores
            for doc, raw_score, norm_score in zip(filtered_results, rerank_scores, normalized_scores):
                doc['rerank_score_raw'] = float(raw_score)
                doc['rerank_score'] = float(norm_score)
                # IMPORTANT: Use rerank score as primary - it's more accurate than vector similarity
                # The RELATIVE ordering matters more than absolute scores
                doc['combined_score'] = doc['rerank_score']
                doc['quality_tier'] = self._classify_quality_tier(doc['rerank_score'])
            
            # Sort by rerank score (higher is better) - TOP results are highest quality
            filtered_results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Keep only top_k after reranking - these are the BEST results
            rerank_top_k = self.retrieval_config.get('rerank_top_k', top_k)
            filtered_results = filtered_results[:rerank_top_k]
            
            # Log accuracy improvement with quality analysis
            avg_rerank = sum(d['rerank_score'] for d in filtered_results) / len(filtered_results)
            top_score = filtered_results[0]['rerank_score'] if filtered_results else 0
            quality_tiers = {}
            for doc in filtered_results:
                tier = doc['quality_tier']
                quality_tiers[tier] = quality_tiers.get(tier, 0) + 1
            
            logger.info(f"✓ Reranking complete. Top result: {top_score:.1%}, Avg: {avg_rerank:.1%}")
            logger.info(f"  Quality distribution: {quality_tiers}")
            logger.info(f"  → Using top {len(filtered_results)} HIGHEST QUALITY results (relative ranking)")
        
        logger.info(f"Retrieved {len(filtered_results)} relevant documents (threshold: {score_threshold})")
        
        return filtered_results
    
    def _classify_quality_tier(self, rerank_score: float) -> str:
        """
        Classify rerank score into quality tier for legal text
        Legal text has different score distributions than web search
        Thresholds calibrated based on actual MS-MARCO cross-encoder behavior on GDPR text
        
        Args:
            rerank_score: Normalized rerank score (0-1)
        
        Returns:
            Quality tier: 'Excellent', 'Good', 'Fair', 'Marginal'
        """
        # Adjusted thresholds based on observed legal text scores (typically 0.25-0.55)
        if rerank_score >= 0.45:
            return 'Excellent'  # Top tier - very rare for legal text
        elif rerank_score >= 0.38:
            return 'Good'       # High quality - best matches
        elif rerank_score >= 0.30:
            return 'Fair'       # Acceptable - still relevant
        else:
            return 'Marginal'   # Low confidence - may not be relevant
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            retrieved_docs: List of retrieved documents
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc['metadata']
            text = doc['text']
            
            # Format with source information
            source_info = f"[Source {i}: {metadata.get('source', 'Unknown')}"
            
            if metadata.get('article_number'):
                source_info += f", Article {metadata['article_number']}"
            elif metadata.get('section_title'):
                source_info += f", {metadata['section_title']}"
            
            source_info += "]"
            
            context_parts.append(f"{source_info}\n{text}\n")
        
        return "\n---\n".join(context_parts)
    
    def generate_response(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        custom_prompt_template: Optional[str] = None
    ) -> Dict:
        """
        Generate response using Ollama with improved prompting
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: System prompt (overrides default)
            custom_prompt_template: Custom prompt template
        
        Returns:
            Dictionary with response and metadata
        """
        # Prepare system prompt
        if system_prompt is None:
            system_prompt = self.prompts.get('system_prompt', 
                'You are a GDPR compliance expert. Provide accurate answers based on the context.')
        
        # Prepare user prompt with enhanced template
        if custom_prompt_template:
            user_prompt = custom_prompt_template.format(context=context, query=query)
        else:
            # Use enhanced query prompt from config or default
            query_template = self.prompts.get('query_prompt', """Based on the following context from GDPR regulations, guidelines, and case law, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer citing specific GDPR articles, recitals, or guidelines where applicable.""")
            
            user_prompt = query_template.format(context=context, query=query)
        
        try:
            logger.info("Generating response with Ollama...")
            
            # Get options from config with anti-hallucination settings
            options = {
                'temperature': self.temperature,
                'top_k': self.ollama_config.get('top_k', 40),
                'top_p': self.ollama_config.get('top_p', 0.9),
            }
            
            # Add optional parameters including num_predict for response length
            for param in ['num_ctx', 'num_predict', 'repeat_penalty', 'presence_penalty', 'frequency_penalty']:
                if param in self.ollama_config:
                    options[param] = self.ollama_config[param]
            
            logger.info(f"Ollama options: {options}")
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options=options
            )
            
            answer = response['message']['content']
            
            # Log if response is empty or too short
            if not answer or len(answer.strip()) < 10:
                logger.warning(f"LLM returned empty or very short response! Length: {len(answer)}")
                logger.warning(f"Prompt length: {len(user_prompt)} chars")
                logger.warning(f"Model: {self.model}")
            else:
                logger.info(f"Response generated successfully ({len(answer)} chars)")
            
            return {
                'answer': answer,
                'model': self.model,
                'context_used': context,
                'metadata': {
                    'total_tokens': response.get('total_duration', 0),
                    'prompt_tokens': response.get('prompt_eval_count', 0),
                    'completion_tokens': response.get('eval_count', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'answer': f"Error generating response: {str(e)}",
                'error': True
            }
    
    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Dict:
        """
        Main query method - retrieves context and generates answer
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            filters: Metadata filters for retrieval
            return_sources: Whether to return source documents
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info(f"\n{'='*60}\nProcessing query: {query}\n{'='*60}")
        
        # Retrieve relevant context
        retrieved_docs = self.retrieve_context(query, top_k=top_k, filters=filters)
        
        if not retrieved_docs:
            return {
                'answer': "I couldn't find relevant information in the GDPR database to answer your question.",
                'sources': [],
                'query': query
            }
        
        # Format context
        context = self.format_context(retrieved_docs)
        
        # Generate response
        response = self.generate_response(query, context)
        
        # Prepare result
        result = {
            'query': query,
            'answer': response['answer'],
            'model': response.get('model'),
            'metadata': response.get('metadata', {})
        }
        
        if return_sources:
            result['sources'] = [
                {
                    'text': doc['text'][:500] + '...' if len(doc['text']) > 500 else doc['text'],
                    'source': doc['metadata'].get('source'),
                    'document_type': doc['metadata'].get('document_type'),
                    'article_number': doc['metadata'].get('article_number'),
                    'url': doc['metadata'].get('url'),
                    'score': doc['score']
                }
                for doc in retrieved_docs
            ]
        
        return result
    
    def ask(self, query: str, **kwargs) -> str:
        """
        Simple ask method that returns just the answer
        
        Args:
            query: User query
            **kwargs: Additional arguments passed to query()
        
        Returns:
            Answer string
        """
        result = self.query(query, **kwargs)
        return result['answer']
    
    def batch_query(self, queries: List[str], **kwargs) -> List[Dict]:
        """
        Process multiple queries
        
        Args:
            queries: List of queries
            **kwargs: Additional arguments passed to query()
        
        Returns:
            List of results
        """
        results = []
        
        for i, query in enumerate(queries, 1):
            logger.info(f"Processing query {i}/{len(queries)}")
            result = self.query(query, **kwargs)
            results.append(result)
        
        return results
    
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """
        Simple LLM generation for remediation engine (acts as LLM client)
        
        Args:
            prompt: Full prompt to send to LLM
            temperature: Temperature for generation
            max_tokens: Max tokens to generate
        
        Returns:
            Generated text
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_k': 40,
                    'top_p': 0.9,
                },
            )
            
            return response.get('response', '')
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Simple retrieval interface for remediation engine
        
        Args:
            query: Query text
            top_k: Number of results
        
        Returns:
            List of retrieved documents
        """
        return self.retrieve_context(query, top_k=top_k)
    
    def get_system_info(self) -> Dict:
        """Get information about the RAG system"""
        info = {
            'ollama_model': self.model,
            'ollama_base_url': self.base_url,
            'vector_store_stats': self.vector_store.get_statistics() if self.vector_store.index else {},
            'retrieval_config': self.retrieval_config
        }
        
        return info


if __name__ == "__main__":
    import yaml
    
    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize RAG system
    rag = GDPRRAGSystem(config)
    
    # Example queries
    example_queries = [
        "What are the rights of data subjects under GDPR?",
        "What is the maximum fine for GDPR violations?",
        "When is a Data Protection Impact Assessment required?",
        "What are the lawful bases for processing personal data?"
    ]
    
    print("\n" + "="*80)
    print("GDPR RAG System - Example Queries")
    print("="*80 + "\n")
    
    for query in example_queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        result = rag.query(query, top_k=3)
        
        print(f"\nAnswer:\n{result['answer']}\n")
        
        if result.get('sources'):
            print(f"\nSources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['source']} - {source['document_type']}")
                if source.get('article_number'):
                    print(f"   Article {source['article_number']}")
                print(f"   Score: {source['score']:.3f}")
        
        print("\n" + "="*80 + "\n")
