#!/usr/bin/env python3
"""
Similarity calculation module for Anki Diff Tool
Provides similarity matching between cards with configurable algorithms and thresholds
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any, Callable
from enum import Enum
import re
import difflib
import json
import math
from collections import Counter

from .card import Card


class MatchType(Enum):
    """Type of similarity match between cards"""
    EXACT = "exact"           # Identical question and answer
    SIMILAR = "similar"       # High similarity but not identical
    PARTIAL = "partial"       # Some similarity but below high threshold
    DIFFERENT = "different"   # No meaningful similarity


class SimilarityAlgorithm(Enum):
    """Available similarity calculation algorithms"""
    SEQUENCE_MATCHER = "sequence_matcher"     # Python's difflib SequenceMatcher
    JACCARD = "jaccard"                      # Jaccard similarity coefficient
    COSINE = "cosine"                        # Cosine similarity
    LEVENSHTEIN = "levenshtein"              # Levenshtein distance
    COMBINED = "combined"                     # Weighted combination of algorithms


@dataclass
class SimilarityConfig:
    """Configuration for similarity calculations"""
    algorithm: SimilarityAlgorithm = SimilarityAlgorithm.SEQUENCE_MATCHER
    exact_threshold: float = 1.0        # Threshold for exact match
    similar_threshold: float = 0.8      # Threshold for similar match
    partial_threshold: float = 0.5      # Threshold for partial match
    question_weight: float = 0.6        # Weight for question similarity
    answer_weight: float = 0.4          # Weight for answer similarity
    case_sensitive: bool = False        # Whether to consider case
    ignore_html: bool = True           # Whether to strip HTML tags
    ignore_punctuation: bool = True     # Whether to ignore punctuation
    
    def __post_init__(self):
        """Validate configuration values"""
        if not (0.0 <= self.exact_threshold <= 1.0):
            raise ValueError("exact_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.similar_threshold <= 1.0):
            raise ValueError("similar_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.partial_threshold <= 1.0):
            raise ValueError("partial_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.question_weight <= 1.0):
            raise ValueError("question_weight must be between 0.0 and 1.0")
        if not (0.0 <= self.answer_weight <= 1.0):
            raise ValueError("answer_weight must be between 0.0 and 1.0")
        if abs(self.question_weight + self.answer_weight - 1.0) > 0.001:
            raise ValueError("question_weight + answer_weight must equal 1.0")


@dataclass
class SimilarityResult:
    """Result of similarity calculation between two cards"""
    question_similarity: float
    answer_similarity: float
    overall_similarity: float
    match_type: MatchType
    confidence: float
    algorithm_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'question_similarity': self.question_similarity,
            'answer_similarity': self.answer_similarity,
            'overall_similarity': self.overall_similarity,
            'match_type': self.match_type.value,
            'confidence': self.confidence,
            'algorithm_data': self.algorithm_data
        }


@dataclass
class SimilarCardPair:
    """Represents a pair of similar cards with similarity metrics"""
    card1: Card
    card2: Card
    similarity_result: SimilarityResult
    user_action: Optional[str] = None  # User decision: "accept", "reject", "pending"
    notes: str = ""
    
    def __post_init__(self):
        """Initialize pair with match IDs"""
        pair_id = f"pair_{hash((self.card1.to_tuple(), self.card2.to_tuple()))}"
        self.card1.set_similarity_match(
            match_id=pair_id,
            score=self.similarity_result.overall_similarity,
            algorithm_data=self.similarity_result.algorithm_data
        )
        self.card2.set_similarity_match(
            match_id=pair_id,
            score=self.similarity_result.overall_similarity,
            algorithm_data=self.similarity_result.algorithm_data
        )
    
    def get_match_type(self) -> MatchType:
        """Get the match type for this pair"""
        return self.similarity_result.match_type
    
    def get_similarity_score(self) -> float:
        """Get the overall similarity score"""
        return self.similarity_result.overall_similarity
    
    def get_confidence(self) -> float:
        """Get the confidence level of the match"""
        return self.similarity_result.confidence
    
    def is_high_quality_match(self) -> bool:
        """Check if this is a high-quality match (high similarity + confidence)"""
        return (self.similarity_result.overall_similarity > 0.8 and 
                self.similarity_result.confidence > 0.8)
    
    def accept_match(self, notes: str = "") -> None:
        """Accept this similarity match"""
        self.user_action = "accept"
        self.notes = notes
    
    def reject_match(self, notes: str = "") -> None:
        """Reject this similarity match"""
        self.user_action = "reject"
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'card1': self.card1.to_dict(),
            'card2': self.card2.to_dict(),
            'similarity_result': self.similarity_result.to_dict(),
            'user_action': self.user_action,
            'notes': self.notes
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"SimilarCardPair(similarity={self.similarity_result.overall_similarity:.3f}, type={self.similarity_result.match_type.value})"


class SimilarityCalculator:
    """Main class for calculating similarity between cards"""
    
    def __init__(self, config: Optional[SimilarityConfig] = None):
        """Initialize calculator with configuration"""
        self.config = config or SimilarityConfig()
        self._algorithm_map = {
            SimilarityAlgorithm.SEQUENCE_MATCHER: self._sequence_matcher_similarity,
            SimilarityAlgorithm.JACCARD: self._jaccard_similarity,
            SimilarityAlgorithm.COSINE: self._cosine_similarity,
            SimilarityAlgorithm.LEVENSHTEIN: self._levenshtein_similarity,
            SimilarityAlgorithm.COMBINED: self._combined_similarity
        }
    
    def calculate_similarity(self, card1: Card, card2: Card) -> SimilarityResult:
        """Calculate similarity between two cards"""
        # Preprocess text
        q1 = self._preprocess_text(card1.question)
        a1 = self._preprocess_text(card1.answer)
        q2 = self._preprocess_text(card2.question)
        a2 = self._preprocess_text(card2.answer)
        
        # Calculate similarities using selected algorithm
        algorithm_func = self._algorithm_map[self.config.algorithm]
        question_sim = algorithm_func(q1, q2)
        answer_sim = algorithm_func(a1, a2)
        
        # Calculate overall similarity
        overall_sim = (question_sim * self.config.question_weight + 
                      answer_sim * self.config.answer_weight)
        
        # Determine match type
        match_type = self._determine_match_type(overall_sim)
        
        # Calculate confidence
        confidence = self._calculate_confidence(question_sim, answer_sim, overall_sim)
        
        # Create algorithm data
        algorithm_data = {
            'algorithm': self.config.algorithm.value,
            'question_processed': q1,
            'answer_processed': a1,
            'question_processed_2': q2,
            'answer_processed_2': a2,
            'weights': {
                'question': self.config.question_weight,
                'answer': self.config.answer_weight
            }
        }
        
        return SimilarityResult(
            question_similarity=question_sim,
            answer_similarity=answer_sim,
            overall_similarity=overall_sim,
            match_type=match_type,
            confidence=confidence,
            algorithm_data=algorithm_data
        )
    
    def find_similar_pairs(self, cards1: List[Card], cards2: List[Card], 
                          min_similarity: float = 0.5) -> List[SimilarCardPair]:
        """Find all similar pairs between two lists of cards"""
        pairs = []
        
        for card1 in cards1:
            for card2 in cards2:
                result = self.calculate_similarity(card1, card2)
                if result.overall_similarity >= min_similarity:
                    pairs.append(SimilarCardPair(card1, card2, result))
        
        # Sort by similarity score (descending)
        pairs.sort(key=lambda p: p.similarity_result.overall_similarity, reverse=True)
        
        return pairs
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text according to configuration"""
        if not text:
            return ""
        
        processed = text
        
        # Remove HTML tags if configured
        if self.config.ignore_html:
            processed = re.sub(r'<[^>]+>', '', processed)
        
        # Remove punctuation if configured
        if self.config.ignore_punctuation:
            processed = re.sub(r'[^\w\s]', '', processed)
        
        # Handle case sensitivity
        if not self.config.case_sensitive:
            processed = processed.lower()
        
        # Normalize whitespace
        processed = ' '.join(processed.split())
        
        return processed
    
    def _determine_match_type(self, similarity: float) -> MatchType:
        """Determine match type based on similarity score"""
        if similarity >= self.config.exact_threshold:
            return MatchType.EXACT
        elif similarity >= self.config.similar_threshold:
            return MatchType.SIMILAR
        elif similarity >= self.config.partial_threshold:
            return MatchType.PARTIAL
        else:
            return MatchType.DIFFERENT
    
    def _calculate_confidence(self, question_sim: float, answer_sim: float, 
                            overall_sim: float) -> float:
        """Calculate confidence level of the similarity match"""
        # Confidence is higher when both question and answer similarities are high
        # and when they are close to each other (not one very high, one very low)
        min_sim = min(question_sim, answer_sim)
        max_sim = max(question_sim, answer_sim)
        
        # Penalize large differences between question and answer similarity
        balance_factor = 1.0 - abs(question_sim - answer_sim)
        
        # Confidence is combination of overall similarity and balance
        confidence = (overall_sim * 0.7 + balance_factor * 0.3)
        
        return max(0.0, min(1.0, confidence))
    
    def _sequence_matcher_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using Python's difflib SequenceMatcher"""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity coefficient"""
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity"""
        words1 = text1.split()
        words2 = text2.split()
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        # Create word frequency vectors
        all_words = set(words1) | set(words2)
        vec1 = [words1.count(word) for word in all_words]
        vec2 = [words2.count(word) for word in all_words]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on Levenshtein distance"""
        if not text1 and not text2:
            return 1.0
        
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        distance = self._levenshtein_distance(text1, text2)
        return 1.0 - (distance / max_len)
    
    def _levenshtein_distance(self, text1: str, text2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(text1) < len(text2):
            return self._levenshtein_distance(text2, text1)
        
        if len(text2) == 0:
            return len(text1)
        
        previous_row = list(range(len(text2) + 1))
        for i, c1 in enumerate(text1):
            current_row = [i + 1]
            for j, c2 in enumerate(text2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _combined_similarity(self, text1: str, text2: str) -> float:
        """Calculate combined similarity using multiple algorithms"""
        # Use different algorithms with different weights
        seq_sim = self._sequence_matcher_similarity(text1, text2)
        jaccard_sim = self._jaccard_similarity(text1, text2)
        cosine_sim = self._cosine_similarity(text1, text2)
        levenshtein_sim = self._levenshtein_similarity(text1, text2)
        
        # Weighted combination
        combined = (seq_sim * 0.4 + 
                   jaccard_sim * 0.3 + 
                   cosine_sim * 0.2 + 
                   levenshtein_sim * 0.1)
        
        return combined


# Utility functions
def create_similarity_calculator(algorithm: str = "sequence_matcher", 
                               similar_threshold: float = 0.8,
                               partial_threshold: float = 0.5,
                               question_weight: float = 0.6) -> SimilarityCalculator:
    """Create a similarity calculator with common configuration"""
    config = SimilarityConfig(
        algorithm=SimilarityAlgorithm(algorithm),
        similar_threshold=similar_threshold,
        partial_threshold=partial_threshold,
        question_weight=question_weight,
        answer_weight=1.0 - question_weight
    )
    return SimilarityCalculator(config)


def find_best_matches(cards1: List[Card], cards2: List[Card], 
                     max_matches: int = 10) -> List[SimilarCardPair]:
    """Find the best similarity matches between two card lists"""
    calculator = create_similarity_calculator()
    all_pairs = calculator.find_similar_pairs(cards1, cards2, min_similarity=0.5)
    
    # Return top matches
    return all_pairs[:max_matches]


def group_similar_cards(cards: List[Card], similarity_threshold: float = 0.8) -> List[List[Card]]:
    """Group cards that are similar to each other"""
    calculator = create_similarity_calculator()
    groups = []
    used_indices = set()
    
    for i, card1 in enumerate(cards):
        if i in used_indices:
            continue
        
        group = [card1]
        used_indices.add(i)
        
        for j, card2 in enumerate(cards[i+1:], i+1):
            if j in used_indices:
                continue
            
            result = calculator.calculate_similarity(card1, card2)
            if result.overall_similarity >= similarity_threshold:
                group.append(card2)
                used_indices.add(j)
        
        groups.append(group)
    
    return groups