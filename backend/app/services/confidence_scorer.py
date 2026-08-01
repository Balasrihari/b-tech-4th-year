"""Confidence Scoring Service for AI Answers"""
from typing import List, Dict, Any, Optional
from loguru import logger
import re


class ConfidenceScorer:
    """Service for calculating confidence scores for AI answers"""
    
    def __init__(self):
        self.weights = {
            'retrieval_quality': 0.4,
            'answer_length': 0.1,
            'citation_quality': 0.2,
            'specificity': 0.2,
            'coherence': 0.1
        }
    
    def calculate_confidence(
        self,
        answer: str,
        retrieved_docs: List[Dict[str, Any]] = None,
        query: str = None
    ) -> Dict[str, Any]:
        """
        Calculate confidence score for an AI answer
        
        Args:
            answer: AI-generated answer
            retrieved_docs: Retrieved documents used for the answer
            query: Original query
            
        Returns:
            Dictionary with confidence score and breakdown
        """
        try:
            scores = {}
            
            # Calculate individual scores
            scores['retrieval_quality'] = self._score_retrieval_quality(retrieved_docs)
            scores['answer_length'] = self._score_answer_length(answer)
            scores['citation_quality'] = self._score_citation_quality(answer)
            scores['specificity'] = self._score_specificity(answer, query)
            scores['coherence'] = self._score_coherence(answer)
            
            # Calculate weighted average
            total_score = sum(
                scores[key] * self.weights[key]
                for key in self.weights
            )
            
            # Normalize to 0-100
            confidence = min(max(total_score * 100, 0), 100)
            
            result = {
                'confidence': round(confidence, 2),
                'breakdown': scores,
                'level': self._get_confidence_level(confidence)
            }
            
            logger.info(f"Calculated confidence score: {confidence:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Confidence scoring failed: {e}")
            return {
                'confidence': 50.0,
                'breakdown': {},
                'level': 'medium',
                'error': str(e)
            }
    
    def _score_retrieval_quality(self, retrieved_docs: List[Dict[str, Any]]) -> float:
        """Score based on retrieval quality"""
        if not retrieved_docs:
            return 0.0
        
        # Average retrieval score
        scores = [doc.get('score', doc.get('rerank_score', 0.5)) for doc in retrieved_docs]
        avg_score = sum(scores) / len(scores)
        
        return min(max(avg_score, 0), 1)
    
    def _score_answer_length(self, answer: str) -> float:
        """Score based on answer length (not too short, not too long)"""
        word_count = len(answer.split())
        
        # Ideal range: 20-200 words
        if word_count < 10:
            return 0.3  # Too short
        elif word_count < 20:
            return 0.7  # Short but acceptable
        elif word_count <= 200:
            return 1.0  # Ideal
        elif word_count <= 500:
            return 0.8  # Long but acceptable
        else:
            return 0.5  # Too long
    
    def _score_citation_quality(self, answer: str) -> float:
        """Score based on citation presence and quality"""
        # Check for citation patterns
        citation_patterns = [
            r'\[.*?\]',  # [1], [source], etc.
            r'\(.*?\d+.*?\)',  # (Smith, 2020), etc.
            r'source:',  # source: ...
            r'according to',  # according to ...
            r'based on',  # based on ...
        ]
        
        has_citation = any(re.search(pattern, answer, re.IGNORECASE) for pattern in citation_patterns)
        
        if has_citation:
            # Count citations
            citation_count = sum(len(re.findall(pattern, answer, re.IGNORECASE)) for pattern in citation_patterns)
            
            if citation_count >= 3:
                return 1.0  # Good citation density
            elif citation_count >= 1:
                return 0.8  # Some citations
            else:
                return 0.5  # Weak citations
        else:
            return 0.3  # No citations
    
    def _score_specificity(self, answer: str, query: str = None) -> float:
        """Score based on answer specificity"""
        if not query:
            return 0.7  # Default if no query
        
        # Check if answer contains query terms
        query_terms = set(query.lower().split())
        answer_lower = answer.lower()
        
        matched_terms = sum(1 for term in query_terms if term in answer_lower)
        specificity = matched_terms / len(query_terms) if query_terms else 0
        
        # Boost for specific details (numbers, dates, names)
        has_numbers = bool(re.search(r'\d+', answer))
        has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+\b', answer))
        
        detail_score = 0.5
        if has_numbers:
            detail_score += 0.2
        if has_proper_nouns:
            detail_score += 0.2
        
        return min(max((specificity * 0.6) + (detail_score * 0.4), 0), 1)
    
    def _score_coherence(self, answer: str) -> float:
        """Score based on answer coherence"""
        # Check for coherence indicators
        coherence_indicators = [
            r'\bhowever\b',
            r'\btherefore\b',
            r'\bmoreover\b',
            r'\bfurthermore\b',
            r'\bconsequently\b',
            r'\bthus\b',
            r'\bhence\b'
        ]
        
        has_transitions = any(re.search(pattern, answer, re.IGNORECASE) for pattern in coherence_indicators)
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', answer)
        valid_sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 3]
        
        if len(valid_sentences) == 0:
            return 0.3
        
        # Check for sentence variety
        avg_sentence_length = sum(len(s.split()) for s in valid_sentences) / len(valid_sentences)
        
        coherence_score = 0.5
        if has_transitions:
            coherence_score += 0.3
        if 5 <= avg_sentence_length <= 25:  # Reasonable sentence length
            coherence_score += 0.2
        
        return min(max(coherence_score, 0), 1)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level label"""
        if confidence >= 80:
            return 'high'
        elif confidence >= 60:
            return 'medium'
        elif confidence >= 40:
            return 'low'
        else:
            return 'very_low'
    
    def batch_calculate_confidence(
        self,
        answers: List[str],
        retrieved_docs_list: List[List[Dict[str, Any]]] = None,
        queries: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate confidence scores for multiple answers
        
        Args:
            answers: List of AI-generated answers
            retrieved_docs_list: List of retrieved documents for each answer
            queries: List of original queries
            
        Returns:
            List of confidence score dictionaries
        """
        results = []
        
        for i, answer in enumerate(answers):
            docs = retrieved_docs_list[i] if retrieved_docs_list and i < len(retrieved_docs_list) else None
            query = queries[i] if queries and i < len(queries) else None
            
            confidence = self.calculate_confidence(answer, docs, query)
            results.append(confidence)
        
        return results
    
    def get_confidence_explanation(self, confidence_result: Dict[str, Any]) -> str:
        """
        Get human-readable explanation of confidence score
        
        Args:
            confidence_result: Confidence result from calculate_confidence
            
        Returns:
            Human-readable explanation
        """
        confidence = confidence_result.get('confidence', 0)
        breakdown = confidence_result.get('breakdown', {})
        level = confidence_result.get('level', 'unknown')
        
        explanation = f"Confidence: {confidence}% ({level.upper()})\n\n"
        explanation += "Score breakdown:\n"
        
        for factor, score in breakdown.items():
            explanation += f"- {factor}: {score * 100:.1f}%\n"
        
        # Add recommendations
        explanation += "\nRecommendations:\n"
        
        if breakdown.get('retrieval_quality', 0) < 0.5:
            explanation += "- Improve document retrieval quality\n"
        if breakdown.get('citation_quality', 0) < 0.5:
            explanation += "- Add more citations to support the answer\n"
        if breakdown.get('specificity', 0) < 0.5:
            explanation += "- Include more specific details and examples\n"
        if breakdown.get('coherence', 0) < 0.5:
            explanation += "- Improve answer structure and transitions\n"
        
        return explanation


# Global confidence scorer instance
confidence_scorer = ConfidenceScorer()
