#!/usr/bin/env python3
"""
Unit tests for text similarity algorithms
Tests the text processing and similarity calculation functionality
"""

import pytest
import unittest
from unittest.mock import Mock, patch

from src.anki_differ.core.similarity import (
    SimilarityCalculator, SimilarityConfig, SimilarityResult, SimilarCardPair,
    MatchType, SimilarityAlgorithm, create_similarity_calculator
)
from src.anki_differ.core.text_processing import (
    TextProcessor, ContentType, preprocess_card_text, extract_card_keywords
)
from src.anki_differ.core.card import Card


class TestTextProcessor(unittest.TestCase):
    """Test text processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = TextProcessor()
        self.case_sensitive_processor = TextProcessor(case_sensitive=True)
        
    def test_basic_text_processing(self):
        """Test basic text processing"""
        text = "Hello World! This is a test."
        result = self.processor.process_text(text)
        self.assertEqual(result, "hello world this is a test")
    
    def test_html_content_processing(self):
        """Test HTML content processing"""
        html_text = "<p>Hello <b>World</b>!</p><br/>This is a test."
        result = self.processor.process_text(html_text, ContentType.HTML)
        self.assertEqual(result, "hello world this is a test")
    
    def test_cloze_content_processing(self):
        """Test Anki cloze deletion processing"""
        cloze_text = "The capital of {{c1::France}} is {{c2::Paris::city}}."
        result = self.processor.process_text(cloze_text, ContentType.CLOZE)
        self.assertEqual(result, "the capital of france is paris")
    
    def test_markdown_content_processing(self):
        """Test markdown content processing"""
        markdown_text = "# Header\n**Bold text** and *italic text*\n`code`"
        result = self.processor.process_text(markdown_text, ContentType.MARKDOWN)
        self.assertEqual(result, "header bold text and italic text code")
    
    def test_mixed_content_processing(self):
        """Test mixed content processing"""
        mixed_text = "<p>The capital of {{c1::France}} is **Paris**.</p>"
        result = self.processor.process_text(mixed_text, ContentType.MIXED)
        self.assertEqual(result, "the capital of france is paris")
    
    def test_case_sensitive_processing(self):
        """Test case sensitive processing"""
        text = "Hello World"
        result = self.case_sensitive_processor.process_text(text)
        self.assertEqual(result, "Hello World")
    
    def test_punctuation_handling(self):
        """Test punctuation handling"""
        text = "Hello, World! How are you?"
        result = self.processor.process_text(text)
        self.assertEqual(result, "hello world how are you")
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization"""
        text = "Hello    World\n\nThis  is   a    test."
        result = self.processor.process_text(text)
        self.assertEqual(result, "hello world this is a test")
    
    def test_html_entity_decoding(self):
        """Test HTML entity decoding"""
        text = "&lt;Hello&gt; &amp; &quot;World&quot;"
        result = self.processor.process_text(text)
        self.assertEqual(result, "hello world")
    
    def test_content_type_detection(self):
        """Test content type detection"""
        html_text = "<p>Hello World</p>"
        cloze_text = "The capital of {{c1::France}} is Paris."
        markdown_text = "# Header\n**Bold text**"
        plain_text = "Hello World"
        
        self.assertEqual(self.processor.detect_content_type(html_text), ContentType.HTML)
        self.assertEqual(self.processor.detect_content_type(cloze_text), ContentType.CLOZE)
        self.assertEqual(self.processor.detect_content_type(markdown_text), ContentType.MARKDOWN)
        self.assertEqual(self.processor.detect_content_type(plain_text), ContentType.PLAIN_TEXT)
    
    def test_keyword_extraction(self):
        """Test keyword extraction"""
        text = "This is a test of keyword extraction with some common words."
        keywords = self.processor.extract_keywords(text)
        expected = ["test", "keyword", "extraction", "some", "common", "words"]
        self.assertEqual(keywords, expected)
    
    def test_text_stats(self):
        """Test text statistics"""
        text = "<p>Hello World</p>"
        stats = self.processor.get_text_stats(text)
        
        self.assertEqual(stats['original_length'], 18)
        self.assertEqual(stats['word_count'], 2)
        self.assertEqual(stats['unique_words'], 2)
        self.assertTrue(stats['has_html'])
        self.assertFalse(stats['has_cloze'])


class TestSimilarityCalculator(unittest.TestCase):
    """Test similarity calculation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = SimilarityCalculator()
        self.card1 = Card("What is the capital of France?", "Paris")
        self.card2 = Card("What is the capital of France?", "Paris")
        self.card3 = Card("What is the capital of Germany?", "Berlin")
        self.card4 = Card("Capital of France?", "Paris")
        
    def test_identical_cards_similarity(self):
        """Test similarity between identical cards"""
        result = self.calculator.calculate_similarity(self.card1, self.card2)
        self.assertEqual(result.overall_similarity, 1.0)
        self.assertEqual(result.match_type, MatchType.EXACT)
    
    def test_different_cards_similarity(self):
        """Test similarity between different cards"""
        result = self.calculator.calculate_similarity(self.card1, self.card3)
        self.assertLess(result.overall_similarity, 0.8)
        self.assertIn(result.match_type, [MatchType.PARTIAL, MatchType.DIFFERENT])
    
    def test_similar_cards_similarity(self):
        """Test similarity between similar cards"""
        result = self.calculator.calculate_similarity(self.card1, self.card4)
        self.assertGreater(result.overall_similarity, 0.7)
        self.assertIn(result.match_type, [MatchType.SIMILAR, MatchType.EXACT])
    
    def test_html_cards_similarity(self):
        """Test similarity with HTML content"""
        html_card1 = Card("<p>What is the capital of <b>France</b>?</p>", "<i>Paris</i>")
        html_card2 = Card("What is the capital of France?", "Paris")
        
        result = self.calculator.calculate_similarity(html_card1, html_card2)
        self.assertGreater(result.overall_similarity, 0.9)
    
    def test_cloze_cards_similarity(self):
        """Test similarity with cloze deletion cards"""
        cloze_card1 = Card("The capital of {{c1::France}} is {{c2::Paris}}.", "")
        cloze_card2 = Card("The capital of France is Paris.", "")
        
        result = self.calculator.calculate_similarity(cloze_card1, cloze_card2)
        self.assertGreater(result.overall_similarity, 0.9)
    
    def test_case_insensitive_similarity(self):
        """Test case insensitive similarity"""
        card_lower = Card("what is the capital of france?", "paris")
        card_upper = Card("WHAT IS THE CAPITAL OF FRANCE?", "PARIS")
        
        result = self.calculator.calculate_similarity(card_lower, card_upper)
        self.assertEqual(result.overall_similarity, 1.0)
    
    def test_punctuation_ignored_similarity(self):
        """Test punctuation ignored similarity"""
        card_with_punct = Card("What is the capital of France?", "Paris!")
        card_without_punct = Card("What is the capital of France", "Paris")
        
        result = self.calculator.calculate_similarity(card_with_punct, card_without_punct)
        self.assertEqual(result.overall_similarity, 1.0)
    
    def test_different_algorithms(self):
        """Test different similarity algorithms"""
        algorithms = [
            SimilarityAlgorithm.SEQUENCE_MATCHER,
            SimilarityAlgorithm.JACCARD,
            SimilarityAlgorithm.COSINE,
            SimilarityAlgorithm.LEVENSHTEIN,
            SimilarityAlgorithm.COMBINED
        ]
        
        for algorithm in algorithms:
            config = SimilarityConfig(algorithm=algorithm)
            calculator = SimilarityCalculator(config)
            result = calculator.calculate_similarity(self.card1, self.card2)
            self.assertEqual(result.overall_similarity, 1.0)
    
    def test_configurable_thresholds(self):
        """Test configurable similarity thresholds"""
        config = SimilarityConfig(
            similar_threshold=0.9,
            partial_threshold=0.7
        )
        calculator = SimilarityCalculator(config)
        
        # Test with cards that have medium similarity
        result = calculator.calculate_similarity(self.card1, self.card4)
        # Match type should be determined by the configured thresholds
        self.assertIsInstance(result.match_type, MatchType)
    
    def test_weight_configuration(self):
        """Test question and answer weight configuration"""
        config1 = SimilarityConfig(question_weight=0.8, answer_weight=0.2)
        config2 = SimilarityConfig(question_weight=0.2, answer_weight=0.8)
        
        calculator1 = SimilarityCalculator(config1)
        calculator2 = SimilarityCalculator(config2)
        
        # Cards with same question, different answers
        card_a = Card("What is the capital?", "Paris")
        card_b = Card("What is the capital?", "Berlin")
        
        result1 = calculator1.calculate_similarity(card_a, card_b)
        result2 = calculator2.calculate_similarity(card_a, card_b)
        
        # Question-weighted should be higher
        self.assertGreater(result1.overall_similarity, result2.overall_similarity)
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        result = self.calculator.calculate_similarity(self.card1, self.card2)
        self.assertIsInstance(result.confidence, float)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
    
    def test_empty_cards_similarity(self):
        """Test similarity with empty cards"""
        empty_card1 = Card("", "")
        empty_card2 = Card("", "")
        normal_card = Card("Question", "Answer")
        
        # Two empty cards should be identical
        result1 = self.calculator.calculate_similarity(empty_card1, empty_card2)
        self.assertEqual(result1.overall_similarity, 1.0)
        
        # Empty card vs normal card should be different
        result2 = self.calculator.calculate_similarity(empty_card1, normal_card)
        self.assertEqual(result2.overall_similarity, 0.0)
    
    def test_early_stopping_optimization(self):
        """Test early stopping optimization"""
        config = SimilarityConfig(early_stop_threshold=0.5)
        calculator = SimilarityCalculator(config)
        
        # Cards with very different questions should trigger early stopping
        very_different_card = Card("Completely different question about astronomy", "Answer")
        
        result = calculator.calculate_similarity(self.card1, very_different_card)
        
        # Should have early stop flag in algorithm data
        if result.overall_similarity < 0.5:
            self.assertTrue(result.algorithm_data.get('early_stop', False))
    
    def test_caching_functionality(self):
        """Test caching functionality"""
        config = SimilarityConfig(enable_caching=True)
        calculator = SimilarityCalculator(config)
        
        # First calculation
        result1 = calculator.calculate_similarity(self.card1, self.card2)
        
        # Second calculation should use cache
        result2 = calculator.calculate_similarity(self.card1, self.card2)
        
        # Results should be identical
        self.assertEqual(result1.overall_similarity, result2.overall_similarity)
    
    def test_find_similar_pairs(self):
        """Test finding similar pairs"""
        cards1 = [self.card1, self.card3]
        cards2 = [self.card2, self.card4]
        
        pairs = self.calculator.find_similar_pairs(cards1, cards2, min_similarity=0.5)
        
        # Should find at least the identical pair
        self.assertGreater(len(pairs), 0)
        self.assertIsInstance(pairs[0], SimilarCardPair)
    
    def test_performance_with_large_text(self):
        """Test performance with large text content"""
        large_text = "This is a very long text " * 1000
        large_card1 = Card(large_text, "Answer")
        large_card2 = Card(large_text, "Answer")
        
        # Should still work efficiently
        result = self.calculator.calculate_similarity(large_card1, large_card2)
        self.assertEqual(result.overall_similarity, 1.0)


class TestSimilarCardPair(unittest.TestCase):
    """Test SimilarCardPair functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.card1 = Card("Question 1", "Answer 1")
        self.card2 = Card("Question 2", "Answer 2")
        self.similarity_result = SimilarityResult(
            question_similarity=0.8,
            answer_similarity=0.9,
            overall_similarity=0.85,
            match_type=MatchType.SIMILAR,
            confidence=0.85
        )
        self.pair = SimilarCardPair(self.card1, self.card2, self.similarity_result)
    
    def test_pair_creation(self):
        """Test SimilarCardPair creation"""
        self.assertEqual(self.pair.card1, self.card1)
        self.assertEqual(self.pair.card2, self.card2)
        self.assertEqual(self.pair.similarity_result, self.similarity_result)
    
    def test_match_type_getter(self):
        """Test match type getter"""
        self.assertEqual(self.pair.get_match_type(), MatchType.SIMILAR)
    
    def test_similarity_score_getter(self):
        """Test similarity score getter"""
        self.assertEqual(self.pair.get_similarity_score(), 0.85)
    
    def test_confidence_getter(self):
        """Test confidence getter"""
        self.assertEqual(self.pair.get_confidence(), 0.85)
    
    def test_high_quality_match(self):
        """Test high quality match detection"""
        # Current similarity (0.85) and confidence (0.85) should make this a high quality match
        self.assertTrue(self.pair.is_high_quality_match())
    
    def test_user_actions(self):
        """Test user action functionality"""
        # Test accept
        self.pair.accept_match("Good match")
        self.assertEqual(self.pair.user_action, "accept")
        self.assertEqual(self.pair.notes, "Good match")
        
        # Test reject
        self.pair.reject_match("Not a good match")
        self.assertEqual(self.pair.user_action, "reject")
        self.assertEqual(self.pair.notes, "Not a good match")
    
    def test_serialization(self):
        """Test dictionary serialization"""
        pair_dict = self.pair.to_dict()
        
        self.assertIn('card1', pair_dict)
        self.assertIn('card2', pair_dict)
        self.assertIn('similarity_result', pair_dict)
        self.assertIn('user_action', pair_dict)
        self.assertIn('notes', pair_dict)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_create_similarity_calculator(self):
        """Test create_similarity_calculator utility"""
        calculator = create_similarity_calculator(
            algorithm="jaccard",
            similar_threshold=0.9,
            question_weight=0.7
        )
        
        self.assertEqual(calculator.config.algorithm, SimilarityAlgorithm.JACCARD)
        self.assertEqual(calculator.config.similar_threshold, 0.9)
        self.assertEqual(calculator.config.question_weight, 0.7)
    
    def test_preprocess_card_text(self):
        """Test preprocess_card_text utility"""
        text = "<p>Hello <b>World</b>!</p>"
        result = preprocess_card_text(text)
        self.assertEqual(result, "hello world")
    
    def test_extract_card_keywords(self):
        """Test extract_card_keywords utility"""
        text = "This is a test of keyword extraction."
        keywords = extract_card_keywords(text)
        self.assertIn("test", keywords)
        self.assertIn("keyword", keywords)
        self.assertIn("extraction", keywords)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = SimilarityCalculator()
    
    def test_invalid_configuration(self):
        """Test invalid configuration handling"""
        with self.assertRaises(ValueError):
            SimilarityConfig(exact_threshold=1.5)
        
        with self.assertRaises(ValueError):
            SimilarityConfig(question_weight=0.8, answer_weight=0.3)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        card1 = Card("What is é + ñ?", "Special chars: àáâãäåæçèéêë")
        card2 = Card("What is é + ñ?", "Special chars: àáâãäåæçèéêë")
        
        result = self.calculator.calculate_similarity(card1, card2)
        self.assertEqual(result.overall_similarity, 1.0)
    
    def test_unicode_handling(self):
        """Test Unicode text handling"""
        card1 = Card("What is 你好?", "世界")
        card2 = Card("What is 你好?", "世界")
        
        result = self.calculator.calculate_similarity(card1, card2)
        self.assertEqual(result.overall_similarity, 1.0)
    
    def test_very_long_text(self):
        """Test very long text handling"""
        long_text = "word " * 10000
        card1 = Card(long_text, "answer")
        card2 = Card(long_text, "answer")
        
        result = self.calculator.calculate_similarity(card1, card2)
        self.assertEqual(result.overall_similarity, 1.0)
    
    def test_whitespace_only_text(self):
        """Test whitespace-only text"""
        card1 = Card("   \n\t   ", "   ")
        card2 = Card("", "")
        
        result = self.calculator.calculate_similarity(card1, card2)
        self.assertEqual(result.overall_similarity, 1.0)


if __name__ == '__main__':
    unittest.main()