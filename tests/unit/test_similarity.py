#!/usr/bin/env python3
"""
Unit Tests for Similarity Calculation Module
Tests similarity algorithms, SimilarCardPair, and SimilarityCalculator
"""

import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.anki_differ.core.similarity import (
    SimilarityConfig, SimilarityResult, SimilarCardPair, SimilarityCalculator,
    MatchType, SimilarityAlgorithm, create_similarity_calculator,
    find_best_matches, group_similar_cards
)
from src.anki_differ.core.card import Card


class TestSimilarityConfig:
    """Test SimilarityConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SimilarityConfig()
        assert config.algorithm == SimilarityAlgorithm.SEQUENCE_MATCHER
        assert config.exact_threshold == 1.0
        assert config.similar_threshold == 0.8
        assert config.partial_threshold == 0.5
        assert config.question_weight == 0.6
        assert config.answer_weight == 0.4
        assert config.case_sensitive is False
        assert config.ignore_html is True
        assert config.ignore_punctuation is True
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = SimilarityConfig(
            algorithm=SimilarityAlgorithm.JACCARD,
            similar_threshold=0.7,
            question_weight=0.8,
            answer_weight=0.2
        )
        assert config.algorithm == SimilarityAlgorithm.JACCARD
        assert config.similar_threshold == 0.7
        assert config.question_weight == 0.8
        assert config.answer_weight == 0.2
    
    def test_invalid_threshold_values(self):
        """Test validation of threshold values"""
        with pytest.raises(ValueError, match="exact_threshold must be between 0.0 and 1.0"):
            SimilarityConfig(exact_threshold=1.5)
        
        with pytest.raises(ValueError, match="similar_threshold must be between 0.0 and 1.0"):
            SimilarityConfig(similar_threshold=-0.1)
        
        with pytest.raises(ValueError, match="partial_threshold must be between 0.0 and 1.0"):
            SimilarityConfig(partial_threshold=2.0)
    
    def test_invalid_weight_values(self):
        """Test validation of weight values"""
        with pytest.raises(ValueError, match="question_weight must be between 0.0 and 1.0"):
            SimilarityConfig(question_weight=1.5)
        
        with pytest.raises(ValueError, match="answer_weight must be between 0.0 and 1.0"):
            SimilarityConfig(answer_weight=-0.1)
        
        with pytest.raises(ValueError, match="question_weight \\+ answer_weight must equal 1.0"):
            SimilarityConfig(question_weight=0.3, answer_weight=0.5)


class TestSimilarityResult:
    """Test SimilarityResult class"""
    
    def test_create_result(self):
        """Test creating a similarity result"""
        result = SimilarityResult(
            question_similarity=0.8,
            answer_similarity=0.6,
            overall_similarity=0.7,
            match_type=MatchType.SIMILAR,
            confidence=0.75,
            algorithm_data={"test": "data"}
        )
        
        assert result.question_similarity == 0.8
        assert result.answer_similarity == 0.6
        assert result.overall_similarity == 0.7
        assert result.match_type == MatchType.SIMILAR
        assert result.confidence == 0.75
        assert result.algorithm_data == {"test": "data"}
    
    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = SimilarityResult(
            question_similarity=0.8,
            answer_similarity=0.6,
            overall_similarity=0.7,
            match_type=MatchType.SIMILAR,
            confidence=0.75
        )
        
        result_dict = result.to_dict()
        expected = {
            'question_similarity': 0.8,
            'answer_similarity': 0.6,
            'overall_similarity': 0.7,
            'match_type': 'similar',
            'confidence': 0.75,
            'algorithm_data': {}
        }
        
        assert result_dict == expected


class TestSimilarCardPair:
    """Test SimilarCardPair class"""
    
    def test_create_pair(self):
        """Test creating a similar card pair"""
        card1 = Card("What is Python?", "A programming language")
        card2 = Card("What is Python?", "A programming language")
        result = SimilarityResult(0.9, 0.9, 0.9, MatchType.SIMILAR, 0.85)
        
        pair = SimilarCardPair(card1, card2, result)
        
        assert pair.card1 == card1
        assert pair.card2 == card2
        assert pair.similarity_result == result
        assert pair.user_action is None
        assert pair.notes == ""
    
    def test_pair_sets_match_ids(self):
        """Test that creating a pair sets match IDs on both cards"""
        card1 = Card("Question 1", "Answer 1")
        card2 = Card("Question 2", "Answer 2")
        result = SimilarityResult(0.8, 0.7, 0.75, MatchType.SIMILAR, 0.8)
        
        pair = SimilarCardPair(card1, card2, result)
        
        assert card1.similarity.match_id is not None
        assert card2.similarity.match_id is not None
        assert card1.similarity.match_id == card2.similarity.match_id
        assert card1.similarity.similarity_score == 0.75
        assert card2.similarity.similarity_score == 0.75
    
    def test_pair_methods(self):
        """Test pair utility methods"""
        card1 = Card("Question", "Answer")
        card2 = Card("Question", "Answer")
        result = SimilarityResult(0.9, 0.9, 0.9, MatchType.SIMILAR, 0.85)
        
        pair = SimilarCardPair(card1, card2, result)
        
        assert pair.get_match_type() == MatchType.SIMILAR
        assert pair.get_similarity_score() == 0.9
        assert pair.get_confidence() == 0.85
        assert pair.is_high_quality_match() is True
    
    def test_low_quality_match(self):
        """Test low quality match detection"""
        card1 = Card("Question", "Answer")
        card2 = Card("Question", "Answer")
        result = SimilarityResult(0.6, 0.5, 0.55, MatchType.PARTIAL, 0.6)
        
        pair = SimilarCardPair(card1, card2, result)
        
        assert pair.is_high_quality_match() is False
    
    def test_user_actions(self):
        """Test user action methods"""
        card1 = Card("Question", "Answer")
        card2 = Card("Question", "Answer")
        result = SimilarityResult(0.8, 0.7, 0.75, MatchType.SIMILAR, 0.8)
        
        pair = SimilarCardPair(card1, card2, result)
        
        pair.accept_match("Good match")
        assert pair.user_action == "accept"
        assert pair.notes == "Good match"
        
        pair.reject_match("False positive")
        assert pair.user_action == "reject"
        assert pair.notes == "False positive"
    
    def test_to_dict(self):
        """Test converting pair to dictionary"""
        card1 = Card("Question", "Answer")
        card2 = Card("Question", "Answer")
        result = SimilarityResult(0.8, 0.7, 0.75, MatchType.SIMILAR, 0.8)
        
        pair = SimilarCardPair(card1, card2, result)
        pair.accept_match("Test")
        
        pair_dict = pair.to_dict()
        
        assert 'card1' in pair_dict
        assert 'card2' in pair_dict
        assert 'similarity_result' in pair_dict
        assert pair_dict['user_action'] == 'accept'
        assert pair_dict['notes'] == 'Test'


class TestSimilarityCalculator:
    """Test SimilarityCalculator class"""
    
    def test_default_calculator(self):
        """Test creating calculator with default config"""
        calculator = SimilarityCalculator()
        assert calculator.config.algorithm == SimilarityAlgorithm.SEQUENCE_MATCHER
        assert calculator.config.similar_threshold == 0.8
    
    def test_custom_config_calculator(self):
        """Test creating calculator with custom config"""
        config = SimilarityConfig(algorithm=SimilarityAlgorithm.JACCARD)
        calculator = SimilarityCalculator(config)
        assert calculator.config.algorithm == SimilarityAlgorithm.JACCARD
    
    def test_identical_cards(self):
        """Test similarity calculation for identical cards"""
        calculator = SimilarityCalculator()
        card1 = Card("What is Python?", "A programming language")
        card2 = Card("What is Python?", "A programming language")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.question_similarity == 1.0
        assert result.answer_similarity == 1.0
        assert result.overall_similarity == 1.0
        assert result.match_type == MatchType.EXACT
        assert result.confidence > 0.9
    
    def test_completely_different_cards(self):
        """Test similarity calculation for completely different cards"""
        calculator = SimilarityCalculator()
        card1 = Card("What is Python?", "A programming language")
        card2 = Card("What is the capital of France?", "Paris")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.question_similarity < 0.6  # Adjusted for "what is" overlap
        assert result.answer_similarity < 0.3
        assert result.overall_similarity < 0.5
        assert result.match_type == MatchType.DIFFERENT
    
    def test_similar_cards(self):
        """Test similarity calculation for similar cards"""
        calculator = SimilarityCalculator()
        card1 = Card("What is Python?", "A programming language")
        card2 = Card("What is Python?", "A programming language used for development")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.question_similarity == 1.0
        assert 0.5 < result.answer_similarity < 1.0
        assert result.overall_similarity > 0.7
        assert result.match_type in [MatchType.SIMILAR, MatchType.EXACT]
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        config = SimilarityConfig(ignore_html=True, ignore_punctuation=True, case_sensitive=False)
        calculator = SimilarityCalculator(config)
        
        text = "<b>Hello, World!</b>"
        processed = calculator._preprocess_text(text)
        
        assert processed == "hello world"
    
    def test_case_sensitive_processing(self):
        """Test case sensitive text processing"""
        config = SimilarityConfig(case_sensitive=True)
        calculator = SimilarityCalculator(config)
        
        text = "Hello World"
        processed = calculator._preprocess_text(text)
        
        assert processed == "Hello World"
    
    def test_html_preservation(self):
        """Test HTML tag preservation"""
        config = SimilarityConfig(ignore_html=False, ignore_punctuation=False)
        calculator = SimilarityCalculator(config)
        
        text = "<b>Hello</b>"
        processed = calculator._preprocess_text(text)
        
        assert "<b>" in processed
        assert "</b>" in processed
    
    def test_find_similar_pairs(self):
        """Test finding similar pairs between card lists"""
        calculator = SimilarityCalculator()
        
        cards1 = [
            Card("What is Python?", "A programming language"),
            Card("What is Java?", "A programming language")
        ]
        
        cards2 = [
            Card("What is Python?", "A programming language"),
            Card("What is C++?", "A programming language")
        ]
        
        pairs = calculator.find_similar_pairs(cards1, cards2, min_similarity=0.5)
        
        assert len(pairs) >= 1
        assert all(isinstance(pair, SimilarCardPair) for pair in pairs)
        assert pairs[0].similarity_result.overall_similarity >= 0.5
    
    def test_different_algorithms(self):
        """Test different similarity algorithms"""
        algorithms = [
            SimilarityAlgorithm.SEQUENCE_MATCHER,
            SimilarityAlgorithm.JACCARD,
            SimilarityAlgorithm.COSINE,
            SimilarityAlgorithm.LEVENSHTEIN,
            SimilarityAlgorithm.COMBINED
        ]
        
        card1 = Card("What is Python?", "A programming language")
        card2 = Card("What is Python?", "A programming language")
        
        for algorithm in algorithms:
            config = SimilarityConfig(algorithm=algorithm)
            calculator = SimilarityCalculator(config)
            
            result = calculator.calculate_similarity(card1, card2)
            
            assert -1e-10 <= result.overall_similarity <= 1.0 + 1e-10
            # Should be exact or very close to exact (some algorithms may have floating point precision issues)
            assert result.overall_similarity > 0.99
    
    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation"""
        calculator = SimilarityCalculator()
        
        # Test identical texts
        assert calculator._jaccard_similarity("hello world", "hello world") == 1.0
        
        # Test completely different texts
        assert calculator._jaccard_similarity("hello", "goodbye") == 0.0
        
        # Test partial overlap
        similarity = calculator._jaccard_similarity("hello world", "hello universe")
        assert 0.0 < similarity < 1.0
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        calculator = SimilarityCalculator()
        
        # Test identical texts
        assert abs(calculator._cosine_similarity("hello world", "hello world") - 1.0) < 1e-10
        
        # Test empty texts
        assert calculator._cosine_similarity("", "") == 1.0
        assert calculator._cosine_similarity("hello", "") == 0.0
        
        # Test partial overlap
        similarity = calculator._cosine_similarity("hello world", "hello universe")
        assert 0.0 < similarity < 1.0
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation"""
        calculator = SimilarityCalculator()
        
        # Test identical strings
        assert calculator._levenshtein_distance("hello", "hello") == 0
        
        # Test completely different strings
        distance = calculator._levenshtein_distance("hello", "world")
        assert distance > 0
        
        # Test one character difference
        assert calculator._levenshtein_distance("hello", "hallo") == 1
    
    def test_levenshtein_similarity(self):
        """Test Levenshtein similarity calculation"""
        calculator = SimilarityCalculator()
        
        # Test identical strings
        assert calculator._levenshtein_similarity("hello", "hello") == 1.0
        
        # Test empty strings
        assert calculator._levenshtein_similarity("", "") == 1.0
        
        # Test partial similarity
        similarity = calculator._levenshtein_similarity("hello", "hallo")
        assert 0.0 < similarity < 1.0
    
    def test_combined_similarity(self):
        """Test combined similarity algorithm"""
        calculator = SimilarityCalculator()
        
        # Test identical texts
        similarity = calculator._combined_similarity("hello world", "hello world")
        assert abs(similarity - 1.0) < 1e-10
        
        # Test different texts
        similarity = calculator._combined_similarity("hello", "goodbye")
        assert 0.0 <= similarity <= 1.0
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        calculator = SimilarityCalculator()
        
        # High confidence when both similarities are high and balanced
        confidence = calculator._calculate_confidence(0.9, 0.9, 0.9)
        assert confidence > 0.8
        
        # Lower confidence when similarities are unbalanced
        confidence = calculator._calculate_confidence(0.9, 0.1, 0.5)
        assert confidence < 0.8
    
    def test_match_type_determination(self):
        """Test match type determination"""
        config = SimilarityConfig(
            exact_threshold=1.0,
            similar_threshold=0.8,
            partial_threshold=0.5
        )
        calculator = SimilarityCalculator(config)
        
        assert calculator._determine_match_type(1.0) == MatchType.EXACT
        assert calculator._determine_match_type(0.9) == MatchType.SIMILAR
        assert calculator._determine_match_type(0.6) == MatchType.PARTIAL
        assert calculator._determine_match_type(0.3) == MatchType.DIFFERENT


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_similarity_calculator(self):
        """Test create_similarity_calculator function"""
        calculator = create_similarity_calculator(
            algorithm="jaccard",
            similar_threshold=0.7,
            question_weight=0.8
        )
        
        assert calculator.config.algorithm == SimilarityAlgorithm.JACCARD
        assert calculator.config.similar_threshold == 0.7
        assert calculator.config.question_weight == 0.8
        assert abs(calculator.config.answer_weight - 0.2) < 1e-10
    
    def test_find_best_matches(self):
        """Test find_best_matches function"""
        cards1 = [
            Card("What is Python?", "A programming language"),
            Card("What is Java?", "A programming language")
        ]
        
        cards2 = [
            Card("What is Python?", "A programming language"),
            Card("What is JavaScript?", "A programming language")
        ]
        
        matches = find_best_matches(cards1, cards2, max_matches=5)
        
        assert len(matches) <= 5
        assert all(isinstance(match, SimilarCardPair) for match in matches)
        if matches:
            assert matches[0].similarity_result.overall_similarity >= 0.5
    
    def test_group_similar_cards(self):
        """Test group_similar_cards function"""
        cards = [
            Card("What is Python?", "A programming language"),
            Card("What is Python?", "A programming language"),  # Duplicate
            Card("What is Java?", "A programming language"),
            Card("What is the capital of France?", "Paris")
        ]
        
        groups = group_similar_cards(cards, similarity_threshold=0.8)
        
        assert len(groups) >= 2  # At least the Python group and others
        assert all(isinstance(group, list) for group in groups)
        assert all(len(group) >= 1 for group in groups)
        
        # Check that all cards are in exactly one group
        all_cards_in_groups = [card for group in groups for card in group]
        assert len(all_cards_in_groups) == len(cards)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_card_content(self):
        """Test similarity calculation with empty card content"""
        calculator = SimilarityCalculator()
        
        card1 = Card("", "")
        card2 = Card("", "")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.question_similarity == 1.0
        assert result.answer_similarity == 1.0
        assert result.overall_similarity == 1.0
        assert result.match_type == MatchType.EXACT
    
    def test_one_empty_card(self):
        """Test similarity calculation with one empty card"""
        calculator = SimilarityCalculator()
        
        card1 = Card("Question", "Answer")
        card2 = Card("", "")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.question_similarity == 0.0
        assert result.answer_similarity == 0.0
        assert result.overall_similarity == 0.0
        assert result.match_type == MatchType.DIFFERENT
    
    def test_very_long_content(self):
        """Test similarity calculation with very long content"""
        calculator = SimilarityCalculator()
        
        long_text = "This is a very long text. " * 100
        
        card1 = Card(long_text, long_text)
        card2 = Card(long_text, long_text)
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.overall_similarity == 1.0
        assert result.match_type == MatchType.EXACT
    
    def test_special_characters(self):
        """Test similarity calculation with special characters"""
        calculator = SimilarityCalculator()
        
        card1 = Card("What is ∑(n=1 to ∞) 1/n²?", "π²/6")
        card2 = Card("What is ∑(n=1 to ∞) 1/n²?", "π²/6")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.overall_similarity == 1.0
        assert result.match_type == MatchType.EXACT
    
    def test_html_content(self):
        """Test similarity calculation with HTML content"""
        config = SimilarityConfig(ignore_html=True)
        calculator = SimilarityCalculator(config)
        
        card1 = Card("<b>What is Python?</b>", "<i>A programming language</i>")
        card2 = Card("What is Python?", "A programming language")
        
        result = calculator.calculate_similarity(card1, card2)
        
        assert result.overall_similarity == 1.0
        assert result.match_type == MatchType.EXACT
    
    def test_find_pairs_empty_lists(self):
        """Test finding pairs with empty card lists"""
        calculator = SimilarityCalculator()
        
        pairs = calculator.find_similar_pairs([], [], min_similarity=0.5)
        assert pairs == []
        
        cards = [Card("Question", "Answer")]
        pairs = calculator.find_similar_pairs(cards, [], min_similarity=0.5)
        assert pairs == []
        
        pairs = calculator.find_similar_pairs([], cards, min_similarity=0.5)
        assert pairs == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])