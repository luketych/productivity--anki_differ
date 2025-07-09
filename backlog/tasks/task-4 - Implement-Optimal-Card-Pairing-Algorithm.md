---
id: task-4
title: Implement Optimal Card Pairing Algorithm
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [medium-priority, algorithm]
dependencies: [task-3]
---

## Description
Implement optimal card pairing algorithm (Hungarian or greedy matching) to find the best matches between similar cards from different exports.

## Requirements
- Choose between Hungarian algorithm (optimal) or greedy matching (faster)
- Ensure each card is matched at most once
- Handle edge cases (unequal numbers of cards, no matches)
- Support similarity threshold filtering

## Sub-tasks
- [ ] Research and choose optimal matching algorithm
- [ ] Implement card pairing algorithm
- [ ] Handle edge cases (no matches, unequal card counts)
- [ ] Add threshold filtering for matches
- [ ] Optimize algorithm performance
- [ ] Create unit tests for pairing logic

## Dependencies
- task-3 (Text similarity algorithm)

## Files to Create/Modify
- `src/anki_differ/core/matching.py` (new file)
- `src/anki_differ/core/similarity.py` (integration)
- `tests/unit/test_matching.py` (new test file)

## Acceptance Criteria
- Optimal or near-optimal card pairing
- Each card matched at most once
- Edge cases handled gracefully
- Performance acceptable for large datasets
- Comprehensive unit tests pass