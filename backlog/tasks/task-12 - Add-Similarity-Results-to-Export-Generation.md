---
id: task-12
title: Add Similarity Results to Export Generation Logic
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [low-priority, export]
dependencies: [task-11]
---

## Description
Integrate similarity results into the export generation logic, ensuring user selections for similar cards are properly included in the final merged export file.

## Requirements
- Include similarity-based selections in export generation
- Handle different user actions (keep left, keep right, keep both)
- Maintain proper Anki export format
- Ensure no duplicate cards in final export
- Preserve card metadata and formatting

## Sub-tasks
- [ ] Integrate similarity selections into export generation
- [ ] Handle "keep left" selections in export
- [ ] Handle "keep right" selections in export
- [ ] Handle "keep both" selections in export
- [ ] Prevent duplicate cards in final export
- [ ] Preserve card metadata and formatting
- [ ] Test export generation with similarity data
- [ ] Validate generated exports can be imported to Anki

## Dependencies
- task-11 (Updated comparison_data.json structure)

## Files to Create/Modify
- `src/anki_differ/core/merge.py` (export generation logic)
- `src/anki_differ/web/app.py` (export route updates)
- `tests/integration/test_similarity_export.py` (new test file)

## Acceptance Criteria
- Similarity selections included in export generation
- All user action types handled correctly
- No duplicate cards in final export
- Anki export format maintained
- Generated exports import successfully to Anki
- Integration tests pass