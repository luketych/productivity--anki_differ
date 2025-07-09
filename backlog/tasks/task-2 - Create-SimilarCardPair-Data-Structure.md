---
id: task-2
title: Create SimilarCardPair Data Structure
status: Completed
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [high-priority, data-structure]
dependencies: [task-1]
---

## Description
Create a new SimilarCardPair data structure to represent pairs of similar cards and implement the similarity calculation module.

## Requirements
- Design SimilarCardPair class to hold card pairs with similarity metrics
- Include similarity score, confidence level, and match type
- Implement similarity calculation methods
- Support different similarity algorithms

## Sub-tasks
- [x] Design SimilarCardPair class structure
- [x] Implement similarity score calculation
- [x] Add confidence level metrics
- [x] Support different match types (exact, similar, partial)
- [x] Create similarity calculation module
- [x] Add unit tests for similarity calculations

## Implementation Summary
- Created comprehensive similarity module (`src/anki_differ/core/similarity.py`)
- Implemented `SimilarCardPair` class with similarity metrics and user actions
- Added `SimilarityCalculator` with 5 different algorithms (SequenceMatcher, Jaccard, Cosine, Levenshtein, Combined)
- Created configurable similarity scoring with thresholds and weights
- Added confidence calculation based on balance between question/answer similarity
- Implemented match types: EXACT, SIMILAR, PARTIAL, DIFFERENT
- Created comprehensive unit tests (38 tests) covering all functionality
- All tests pass, confirming robust implementation

## Dependencies
- task-1 (Card data structure extension)

## Files to Create/Modify
- `src/anki_differ/core/similarity.py` (new file)
- `src/anki_differ/core/diff.py` (integration)
- `tests/unit/test_similarity.py` (new test file)

## Acceptance Criteria
- SimilarCardPair class properly represents card pairs
- Similarity calculation is accurate and configurable
- Different match types are supported
- Comprehensive unit tests pass
- Integration with existing Card structure works