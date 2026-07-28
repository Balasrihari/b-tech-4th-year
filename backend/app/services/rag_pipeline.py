"""
Advanced RAG Pipeline
Implements query rewriting, BM25, vector search, hybrid retrieval, reranking, context compression, and citations
"""
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
import numpy as np
from app.services.embedding_service import EmbeddingService
import re


class RAGPipeline:
    """Advanced RAG pipeline with multiple retrieval strategies"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.bm25_index = None
        self.documents = []
        self.document_ids = []
    
    def build_bm25_index(self, chunks: List[str], document_ids: List[str]) -> None:
        """Build BM25 index for keyword search"""
        # Tokenize documents
        tokenized_corpus = [self._tokenize(doc) for doc in chunks]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        self.documents = chunks
        self.document_ids = document_ids
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())
        return tokens
    
    def rewrite_query(self, query: str) -> str:
        """Rewrite query for better retrieval"""
        # Simple query expansion - remove stop words and normalize
        query = query.lower().strip()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
                     'during', 'before', 'after', 'above', 'below', 'between', 'under',
                     'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
                     'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
                     'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                     'very', 'just', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
                     'those', 'am', 'it', 'its'}
        
        words = query.split()
        filtered_words = [w for w in words if w not in stop_words]
        rewritten_query = ' '.join(filtered_words)
        
        return rewritten_query if rewritten_query else query
    
    def bm25_search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search using BM25 keyword matching"""
        if not self.bm25_index:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]
        
        return results
    
    def vector_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search using vector embeddings"""
        results = self.embedding_service.query_embeddings(
            collection_name="documents",
            query_text=query,
            n_results=top_k
        )
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> List[Dict]:
        """Hybrid search combining BM25 and vector search"""
        # Get BM25 results
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        bm25_scores = {idx: score for idx, score in bm25_results}
        
        # Get vector results
        vector_results = self.vector_search(query, top_k=top_k * 2)
        
        # Combine scores
        combined_scores = {}
        
        # Normalize BM25 scores
        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            for idx, score in bm25_scores.items():
                combined_scores[idx] = alpha * (score / max_bm25)
        
        # Add vector scores
        if vector_results and vector_results.get('distances'):
            max_vector = max(vector_results['distances'][0]) if vector_results['distances'][0] else 1
            for i, (doc_id, distance) in enumerate(zip(
                vector_results.get('ids', [[]])[0],
                vector_results.get('distances', [[]])[0]
            )):
                # Extract document index from ID (format: doc_X_chunk_Y)
                if isinstance(doc_id, str):
                    chunk_idx = int(doc_id.split('_chunk_')[1])
                    vector_score = (1 - distance / max_vector) if max_vector > 0 else 0
                    if chunk_idx in combined_scores:
                        combined_scores[chunk_idx] += (1 - alpha) * vector_score
                    else:
                        combined_scores[chunk_idx] = (1 - alpha) * vector_score
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top-k results with documents
        final_results = []
        for idx, score in sorted_results[:top_k]:
            if idx < len(self.documents):
                final_results.append({
                    'chunk_index': idx,
                    'document_id': self.document_ids[idx] if idx < len(self.document_ids) else None,
                    'text': self.documents[idx],
                    'score': score
                })
        
        return final_results
    
    def rerank_results(self, query: str, results: List[Dict], top_k: int = 3) -> List[Dict]:
        """Rerank results based on relevance to query"""
        if not results:
            return results
        
        # Simple reranking based on keyword overlap
        query_tokens = set(self._tokenize(query))
        
        for result in results:
            doc_tokens = set(self._tokenize(result['text']))
            
            # Calculate Jaccard similarity
            intersection = len(query_tokens & doc_tokens)
            union = len(query_tokens | doc_tokens)
            jaccard = intersection / union if union > 0 else 0
            
            # Update score with reranking factor
            result['reranked_score'] = result['score'] * 0.7 + jaccard * 0.3
        
        # Sort by reranked score
        reranked = sorted(results, key=lambda x: x['reranked_score'], reverse=True)
        
        return reranked[:top_k]
    
    def compress_context(self, results: List[Dict], max_tokens: int = 1000) -> str:
        """Compress retrieved context to fit within token limit"""
        if not results:
            return ""
        
        context_parts = []
        total_tokens = 0
        
        for result in results:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(result['text']) // 4
            
            if total_tokens + estimated_tokens <= max_tokens:
                context_parts.append(result['text'])
                total_tokens += estimated_tokens
            else:
                # Truncate to fit remaining space
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 0:
                    truncated_text = result['text'][:remaining_tokens * 4]
                    context_parts.append(truncated_text)
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def generate_citations(self, results: List[Dict]) -> List[Dict]:
        """Generate citations for retrieved documents"""
        citations = []
        
        for i, result in enumerate(results):
            citation = {
                'index': i + 1,
                'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                'document_id': result.get('document_id'),
                'chunk_index': result.get('chunk_index'),
                'score': result.get('score', 0)
            }
            citations.append(citation)
        
        return citations
    
    def retrieve(self, query: str, top_k: int = 5, use_hybrid: bool = True, 
                rerank: bool = True, compress: bool = True) -> Dict:
        """Complete RAG retrieval pipeline"""
        # Rewrite query
        rewritten_query = self.rewrite_query(query)
        
        # Retrieve documents
        if use_hybrid:
            results = self.hybrid_search(rewritten_query, top_k=top_k * 2)
        else:
            results = self.vector_search(rewritten_query, top_k=top_k * 2)
        
        # Convert vector results to standard format
        if not use_hybrid and results and results.get('documents'):
            results = [
                {
                    'chunk_index': i,
                    'document_id': results.get('ids', [[]])[0][i] if i < len(results.get('ids', [[]])[0]) else None,
                    'text': results.get('documents', [[]])[0][i] if i < len(results.get('documents', [[]])[0]) else None,
                    'score': 1 - results.get('distances', [[]])[0][i] if i < len(results.get('distances', [[]])[0]) else 0
                }
                for i in range(min(len(results.get('documents', [[]])[0]), top_k * 2))
            ]
        
        # Rerank results
        if rerank:
            results = self.rerank_results(rewritten_query, results, top_k=top_k)
        else:
            results = results[:top_k]
        
        # Compress context
        if compress:
            context = self.compress_context(results, max_tokens=1000)
        else:
            context = "\n\n---\n\n".join([r['text'] for r in results])
        
        # Generate citations
        citations = self.generate_citations(results)
        
        return {
            'query': query,
            'rewritten_query': rewritten_query,
            'context': context,
            'citations': citations,
            'results': results
        }
