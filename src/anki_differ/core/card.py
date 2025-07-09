#!/usr/bin/env python3
"""
Card data structure for Anki Diff Tool
Provides a structured representation of Anki cards with similarity metadata support

## Overview
The Card class extends the original tuple-based card representation with:
- Similarity metadata for matching cards across different exports
- Backward compatibility with existing tuple-based functions
- Support for JSON serialization for web interface

## Similarity Matching Features
- similarity_score: Numerical similarity score (0.0-1.0)
- match_id: Reference to the matched card
- status: Current state of similarity matching (unmatched, matched, rejected, etc.)
- algorithm_data: Additional data from similarity algorithms

## Usage Examples
```python
# Create a basic card
card = Card(question="What is 2+2?", answer="4")

# Set similarity match
card.set_similarity_match(match_id="card123", score=0.95)

# Convert to legacy tuple format
tuple_format = card.to_tuple()

# Convert from legacy tuple format
card_from_tuple = Card.from_tuple(("Question", "Answer"))
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
import json


class SimilarityStatus(Enum):
    """Status of similarity matching for a card"""
    UNMATCHED = "unmatched"
    MATCHED = "matched"
    REJECTED = "rejected"
    REVIEWED = "reviewed"
    PENDING = "pending"


@dataclass
class SimilarityMetadata:
    """Metadata about similarity matching for a card"""
    similarity_score: float = 0.0
    match_id: Optional[str] = None
    status: SimilarityStatus = SimilarityStatus.UNMATCHED
    algorithm_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'similarity_score': self.similarity_score,
            'match_id': self.match_id,
            'status': self.status.value,
            'algorithm_data': self.algorithm_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimilarityMetadata':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            similarity_score=data.get('similarity_score', 0.0),
            match_id=data.get('match_id'),
            status=SimilarityStatus(data.get('status', SimilarityStatus.UNMATCHED.value)),
            algorithm_data=data.get('algorithm_data', {})
        )


@dataclass
class Card:
    """
    Structured representation of an Anki card with similarity metadata support
    
    This class maintains backward compatibility with the existing tuple format
    while adding support for similarity matching functionality.
    """
    question: str
    answer: str
    similarity: Optional[SimilarityMetadata] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize similarity metadata if not provided"""
        if self.similarity is None:
            self.similarity = SimilarityMetadata()
    
    def to_tuple(self) -> Tuple[str, str]:
        """Convert to tuple format for backward compatibility"""
        return (self.question, self.answer)
    
    @classmethod
    def from_tuple(cls, card_tuple: Tuple[str, str]) -> 'Card':
        """Create Card from tuple format for backward compatibility"""
        return cls(question=card_tuple[0], answer=card_tuple[1])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'question': self.question,
            'answer': self.answer,
            'metadata': self.metadata
        }
        if self.similarity:
            result['similarity'] = self.similarity.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """Create Card from dictionary (JSON deserialization)"""
        similarity = None
        if 'similarity' in data:
            similarity = SimilarityMetadata.from_dict(data['similarity'])
        
        return cls(
            question=data['question'],
            answer=data['answer'],
            similarity=similarity,
            metadata=data.get('metadata', {})
        )
    
    def set_similarity_match(self, match_id: str, score: float, 
                           status: SimilarityStatus = SimilarityStatus.MATCHED,
                           algorithm_data: Optional[Dict[str, Any]] = None) -> None:
        """Set similarity match information"""
        if self.similarity is None:
            self.similarity = SimilarityMetadata()
        
        self.similarity.match_id = match_id
        self.similarity.similarity_score = score
        self.similarity.status = status
        if algorithm_data:
            self.similarity.algorithm_data = algorithm_data
    
    def get_similarity_score(self) -> float:
        """Get similarity score, default to 0.0 if not set"""
        return self.similarity.similarity_score if self.similarity else 0.0
    
    def is_similar_to(self, other_card: 'Card', threshold: float = 0.8) -> bool:
        """Check if this card is similar to another card based on threshold"""
        if self.similarity and self.similarity.match_id:
            # If we have a match_id, check if it matches the other card
            return self.similarity.match_id == str(hash(other_card.to_tuple()))
        return False
    
    def __str__(self) -> str:
        """String representation"""
        return f"Card(q='{self.question[:50]}...', a='{self.answer[:50]}...', score={self.get_similarity_score():.2f})"
    
    def __repr__(self) -> str:
        """Repr representation"""
        return f"Card(question='{self.question}', answer='{self.answer}', similarity={self.similarity})"


# Utility functions for backward compatibility
def cards_to_tuples(cards: List[Card]) -> List[Tuple[str, str]]:
    """Convert list of Cards to list of tuples for backward compatibility"""
    return [card.to_tuple() for card in cards]


def tuples_to_cards(tuples: List[Tuple[str, str]]) -> List[Card]:
    """Convert list of tuples to list of Cards for backward compatibility"""
    return [Card.from_tuple(t) for t in tuples]


def cards_to_json(cards: List[Card]) -> str:
    """Convert list of Cards to JSON string"""
    return json.dumps([card.to_dict() for card in cards], indent=2)


def cards_from_json(json_str: str) -> List[Card]:
    """Create list of Cards from JSON string"""
    data = json.loads(json_str)
    return [Card.from_dict(item) for item in data]


# Legacy format conversion functions
def convert_web_card_to_card(web_card: Dict[str, Any], card_type: str) -> Card:
    """Convert web interface card format to Card object"""
    if card_type == "identical":
        return Card(
            question=web_card["question"],
            answer=web_card["answer"],
            metadata={"selected": web_card.get("selected", "file1"), "type": "identical"}
        )
    elif card_type == "different":
        return Card(
            question=web_card["question"],
            answer=web_card["file1_answer"],  # Default to file1 answer
            metadata={
                "file1_answer": web_card["file1_answer"],
                "file2_answer": web_card["file2_answer"],
                "selected": web_card.get("selected", "file1"),
                "type": "different"
            }
        )
    elif card_type in ["unique_file1", "unique_file2"]:
        return Card(
            question=web_card["question"],
            answer=web_card["answer"],
            metadata={"selected": web_card.get("selected", True), "type": card_type}
        )
    else:
        raise ValueError(f"Unknown card type: {card_type}")


def convert_card_to_web_card(card: Card) -> Dict[str, Any]:
    """Convert Card object to web interface card format"""
    card_type = card.metadata.get("type", "unknown")
    
    if card_type == "identical":
        return {
            "question": card.question,
            "answer": card.answer,
            "selected": card.metadata.get("selected", "file1")
        }
    elif card_type == "different":
        return {
            "question": card.question,
            "file1_answer": card.metadata.get("file1_answer", card.answer),
            "file2_answer": card.metadata.get("file2_answer", ""),
            "selected": card.metadata.get("selected", "file1")
        }
    elif card_type in ["unique_file1", "unique_file2"]:
        return {
            "question": card.question,
            "answer": card.answer,
            "selected": card.metadata.get("selected", True)
        }
    else:
        # Default format
        return {
            "question": card.question,
            "answer": card.answer,
            "selected": True
        }