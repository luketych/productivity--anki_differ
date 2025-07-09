---
id: task-5
title: Add Similarity Calculation to Comparison Workflow
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [medium-priority, integration]
dependencies: [task-4]
---

## Description
Integrate similarity calculation into the main comparison workflow, ensuring similar cards are identified and processed alongside existing comparison logic.

## Requirements
- Integrate similarity matching with existing diff workflow
- Maintain compatibility with current comparison functionality
- Store similarity results for web interface access
- Handle performance impact on large datasets

## Sub-tasks
- [ ] Integrate similarity calculation into main comparison workflow
- [ ] Update comparison result data structure
- [ ] Ensure compatibility with existing diff functionality
- [ ] Add similarity results to session storage
- [ ] Test integration with existing comparison features
- [ ] Performance testing with large datasets

## Dependencies
- task-4 (Optimal card pairing algorithm)

## Files to Create/Modify
- `src/anki_differ/core/diff.py` (main integration)
- `src/anki_differ/web/app.py` (session storage)
- `tests/integration/test_similarity_workflow.py` (new test file)

## Acceptance Criteria
- Similarity calculation integrated into main workflow
- Existing comparison functionality unaffected
- Similarity results available for web interface
- Performance impact minimized
- Integration tests pass