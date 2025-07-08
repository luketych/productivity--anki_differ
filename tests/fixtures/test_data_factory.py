#!/usr/bin/env python3
"""
Test Data Factory for Anki Diff Tool
Provides consistent, configurable test data for all testing scenarios
"""

import json
import tempfile
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DatasetSize(Enum):
    TINY = "tiny"        # 1-2 cards per category
    SMALL = "small"      # 3-5 cards per category  
    MEDIUM = "medium"    # 10-20 cards per category
    LARGE = "large"      # 100+ cards per category

class ScenarioType(Enum):
    NORMAL = "normal"               # Typical mix of all card types
    IDENTICAL_ONLY = "identical"    # Only identical cards
    DIFFERENT_ONLY = "different"    # Only different cards
    UNIQUE_ONLY = "unique"         # Only unique cards
    NO_OVERLAP = "no_overlap"      # No shared questions
    EDGE_CASES = "edge_cases"      # Special characters, HTML, etc.

@dataclass
class TestCard:
    question: str
    answer: str
    selected: bool = True

@dataclass
class TestDifferentCard:
    question: str
    file1_answer: str
    file2_answer: str
    selected: str = "file1"

@dataclass
class TestDataset:
    identical_cards: List[TestCard]
    different_cards: List[TestDifferentCard]
    unique_file1: List[TestCard]
    unique_file2: List[TestCard]
    file1_name: str = "Test File 1"
    file2_name: str = "Test File 2"
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {"separator": "tab", "html": "true"}

class TestDataFactory:
    """Factory class for generating test data scenarios"""
    
    @staticmethod
    def create_dataset(size: DatasetSize, scenario: ScenarioType = ScenarioType.NORMAL) -> TestDataset:
        """Create a test dataset based on size and scenario"""
        
        if scenario == ScenarioType.NORMAL:
            return TestDataFactory._create_normal_dataset(size)
        elif scenario == ScenarioType.IDENTICAL_ONLY:
            return TestDataFactory._create_identical_only_dataset(size)
        elif scenario == ScenarioType.DIFFERENT_ONLY:
            return TestDataFactory._create_different_only_dataset(size)
        elif scenario == ScenarioType.UNIQUE_ONLY:
            return TestDataFactory._create_unique_only_dataset(size)
        elif scenario == ScenarioType.NO_OVERLAP:
            return TestDataFactory._create_no_overlap_dataset(size)
        elif scenario == ScenarioType.EDGE_CASES:
            return TestDataFactory._create_edge_cases_dataset(size)
        else:
            raise ValueError(f"Unknown scenario type: {scenario}")
    
    @staticmethod
    def _get_card_counts(size: DatasetSize) -> Tuple[int, int, int, int]:
        """Get card counts for each category based on size"""
        counts = {
            DatasetSize.TINY: (1, 1, 1, 1),
            DatasetSize.SMALL: (3, 2, 4, 5),
            DatasetSize.MEDIUM: (15, 8, 12, 18),
            DatasetSize.LARGE: (150, 50, 75, 100)
        }
        return counts[size]
    
    @staticmethod
    def _create_normal_dataset(size: DatasetSize) -> TestDataset:
        """Create a normal mixed dataset"""
        identical_count, different_count, unique1_count, unique2_count = TestDataFactory._get_card_counts(size)
        
        # Identical cards
        identical_cards = [
            TestCard(f"What is {i} + {i}?", str(i * 2))
            for i in range(1, identical_count + 1)
        ]
        
        # Different cards
        different_cards = [
            TestDifferentCard(
                f"Programming question {i}?",
                f"Answer from file1 {i}",
                f"Answer from file2 {i}"
            ) for i in range(1, different_count + 1)
        ]
        
        # Unique cards file1
        unique_file1 = [
            TestCard(f"File1 unique question {i}?", f"File1 unique answer {i}")
            for i in range(1, unique1_count + 1)
        ]
        
        # Unique cards file2
        unique_file2 = [
            TestCard(f"File2 unique question {i}?", f"File2 unique answer {i}")
            for i in range(1, unique2_count + 1)
        ]
        
        return TestDataset(identical_cards, different_cards, unique_file1, unique_file2)
    
    @staticmethod
    def _create_identical_only_dataset(size: DatasetSize) -> TestDataset:
        """Create dataset with only identical cards"""
        identical_count, _, _, _ = TestDataFactory._get_card_counts(size)
        
        identical_cards = [
            TestCard(f"Identical question {i}?", f"Identical answer {i}")
            for i in range(1, identical_count + 1)
        ]
        
        return TestDataset(identical_cards, [], [], [])
    
    @staticmethod
    def _create_different_only_dataset(size: DatasetSize) -> TestDataset:
        """Create dataset with only different cards"""
        _, different_count, _, _ = TestDataFactory._get_card_counts(size)
        
        different_cards = [
            TestDifferentCard(
                f"Conflict question {i}?",
                f"File1 perspective {i}",
                f"File2 perspective {i}"
            ) for i in range(1, different_count + 1)
        ]
        
        return TestDataset([], different_cards, [], [])
    
    @staticmethod
    def _create_unique_only_dataset(size: DatasetSize) -> TestDataset:
        """Create dataset with only unique cards"""
        _, _, unique1_count, unique2_count = TestDataFactory._get_card_counts(size)
        
        unique_file1 = [
            TestCard(f"Only in file1 {i}?", f"File1 exclusive {i}")
            for i in range(1, unique1_count + 1)
        ]
        
        unique_file2 = [
            TestCard(f"Only in file2 {i}?", f"File2 exclusive {i}")
            for i in range(1, unique2_count + 1)
        ]
        
        return TestDataset([], [], unique_file1, unique_file2)
    
    @staticmethod
    def _create_no_overlap_dataset(size: DatasetSize) -> TestDataset:
        """Create dataset with no overlapping questions"""
        _, _, unique1_count, unique2_count = TestDataFactory._get_card_counts(size)
        
        # All cards are unique to their respective files
        unique_file1 = [
            TestCard(f"File1 question {i}?", f"File1 answer {i}")
            for i in range(1, unique1_count + 1)
        ]
        
        unique_file2 = [
            TestCard(f"File2 question {i}?", f"File2 answer {i}")
            for i in range(1, unique2_count + 1)
        ]
        
        return TestDataset([], [], unique_file1, unique_file2)
    
    @staticmethod
    def _create_edge_cases_dataset(size: DatasetSize) -> TestDataset:
        """Create dataset with edge cases and special characters"""
        
        # Edge case cards with special characters, HTML, unicode
        identical_cards = [
            TestCard("What is <b>HTML</b> formatting?", "<i>Markup language</i>"),
            TestCard("Unicode test: 你好?", "Hello in Chinese: 你好"),
            TestCard("Special chars: !@#$%^&*()?", "Symbols: !@#$%^&*()"),
            TestCard("Multi-line\nquestion?", "Multi-line\nanswer"),
            TestCard("", "Empty question test"),  # Edge case: empty question
        ]
        
        different_cards = [
            TestDifferentCard(
                "HTML difference test?",
                "<b>Bold formatting</b>",
                "<i>Italic formatting</i>"
            ),
            TestDifferentCard(
                "Unicode difference: 日本語?",
                "Japanese: 日本語",
                "Nihongo: にほんご"
            )
        ]
        
        unique_file1 = [
            TestCard("Very long question that might cause display issues and should be tested for UI wrapping and proper handling of extensive text content?", "Very long answer that should also be tested for proper display and wrapping behavior in the user interface"),
            TestCard("Tab\tcharacter\ttest?", "Answer\twith\ttabs"),
        ]
        
        unique_file2 = [
            TestCard("Newline\ncharacter\ntest?", "Answer\nwith\nnewlines"),
            TestCard("Quote \"test\" with 'mixed' quotes?", "Answer with \"quotes\" and 'apostrophes'"),
        ]
        
        return TestDataset(identical_cards, different_cards, unique_file1, unique_file2)
    
    @staticmethod
    def dataset_to_comparison_data(dataset: TestDataset) -> Dict:
        """Convert TestDataset to comparison_data.json format"""
        
        data = {
            "headers": dataset.headers,
            "file1_name": dataset.file1_name,
            "file2_name": dataset.file2_name,
            "file1_path": "/tmp/test_file1.txt",
            "file2_path": "/tmp/test_file2.txt",
            "identical_cards": [
                {
                    "question": card.question,
                    "answer": card.answer,
                    "selected": "file1"
                } for card in dataset.identical_cards
            ],
            "different_cards": [
                {
                    "question": card.question,
                    "file1_answer": card.file1_answer,
                    "file2_answer": card.file2_answer,
                    "selected": card.selected
                } for card in dataset.different_cards
            ],
            "unique_file1": [
                {
                    "question": card.question,
                    "answer": card.answer,
                    "selected": card.selected
                } for card in dataset.unique_file1
            ],
            "unique_file2": [
                {
                    "question": card.question,
                    "answer": card.answer,
                    "selected": card.selected
                } for card in dataset.unique_file2
            ],
            "stats": {
                "file1_total": len(dataset.identical_cards) + len(dataset.different_cards) + len(dataset.unique_file1),
                "file2_total": len(dataset.identical_cards) + len(dataset.different_cards) + len(dataset.unique_file2),
                "identical": len(dataset.identical_cards),
                "different": len(dataset.different_cards),
                "only_file1": len(dataset.unique_file1),
                "only_file2": len(dataset.unique_file2)
            }
        }
        
        return data
    
    @staticmethod
    def dataset_to_anki_files(dataset: TestDataset) -> Tuple[str, str]:
        """Convert TestDataset to Anki export file format"""
        
        # File 1 content
        file1_lines = []
        for key, value in dataset.headers.items():
            file1_lines.append(f"#{key}:{value}")
        
        # Add identical cards
        for card in dataset.identical_cards:
            file1_lines.append(f"{card.question}\t{card.answer}")
        
        # Add different cards (file1 answers)
        for card in dataset.different_cards:
            file1_lines.append(f"{card.question}\t{card.file1_answer}")
        
        # Add unique file1 cards
        for card in dataset.unique_file1:
            file1_lines.append(f"{card.question}\t{card.answer}")
        
        file1_content = "\n".join(file1_lines)
        
        # File 2 content
        file2_lines = []
        for key, value in dataset.headers.items():
            file2_lines.append(f"#{key}:{value}")
        
        # Add identical cards
        for card in dataset.identical_cards:
            file2_lines.append(f"{card.question}\t{card.answer}")
        
        # Add different cards (file2 answers)
        for card in dataset.different_cards:
            file2_lines.append(f"{card.question}\t{card.file2_answer}")
        
        # Add unique file2 cards
        for card in dataset.unique_file2:
            file2_lines.append(f"{card.question}\t{card.answer}")
        
        file2_content = "\n".join(file2_lines)
        
        return file1_content, file2_content
    
    @staticmethod
    def create_temp_files(dataset: TestDataset) -> Tuple[str, str]:
        """Create temporary Anki export files from dataset"""
        
        file1_content, file2_content = TestDataFactory.dataset_to_anki_files(dataset)
        
        # Create temporary files
        file1_fd, file1_path = tempfile.mkstemp(suffix='.txt', prefix='anki_test1_')
        file2_fd, file2_path = tempfile.mkstemp(suffix='.txt', prefix='anki_test2_')
        
        try:
            with os.fdopen(file1_fd, 'w', encoding='utf-8') as f:
                f.write(file1_content)
            
            with os.fdopen(file2_fd, 'w', encoding='utf-8') as f:
                f.write(file2_content)
            
            return file1_path, file2_path
        
        except Exception:
            # Cleanup on error
            try:
                os.unlink(file1_path)
                os.unlink(file2_path)
            except:
                pass
            raise

# Predefined test datasets for common scenarios
class TestFixtures:
    """Predefined test fixtures for common testing scenarios"""
    
    @staticmethod
    def tiny_normal():
        return TestDataFactory.create_dataset(DatasetSize.TINY, ScenarioType.NORMAL)
    
    @staticmethod
    def small_normal():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.NORMAL)
    
    @staticmethod
    def medium_normal():
        return TestDataFactory.create_dataset(DatasetSize.MEDIUM, ScenarioType.NORMAL)
    
    @staticmethod
    def edge_cases():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.EDGE_CASES)
    
    @staticmethod
    def no_overlap():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.NO_OVERLAP)
    
    @staticmethod
    def identical_only():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.IDENTICAL_ONLY)
    
    @staticmethod
    def different_only():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.DIFFERENT_ONLY)
    
    @staticmethod
    def unique_only():
        return TestDataFactory.create_dataset(DatasetSize.SMALL, ScenarioType.UNIQUE_ONLY)

if __name__ == "__main__":
    # Demo usage
    print("🧪 Test Data Factory Demo")
    print("=" * 40)
    
    # Create different datasets
    datasets = [
        ("Tiny Normal", TestFixtures.tiny_normal()),
        ("Small Normal", TestFixtures.small_normal()),
        ("Edge Cases", TestFixtures.edge_cases()),
        ("No Overlap", TestFixtures.no_overlap()),
    ]
    
    for name, dataset in datasets:
        print(f"\n📊 {name}:")
        print(f"  Identical: {len(dataset.identical_cards)}")
        print(f"  Different: {len(dataset.different_cards)}")
        print(f"  Unique File1: {len(dataset.unique_file1)}")
        print(f"  Unique File2: {len(dataset.unique_file2)}")
        
        # Show sample data
        if dataset.identical_cards:
            print(f"  Sample identical: {dataset.identical_cards[0].question}")
        if dataset.different_cards:
            print(f"  Sample different: {dataset.different_cards[0].question}")
    
    print(f"\n✅ Test Data Factory ready for use!")