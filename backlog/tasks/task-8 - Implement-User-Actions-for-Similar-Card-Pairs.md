---
id: task-8
title: Implement User Actions for Similar Card Pairs
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [medium-priority, ui-interaction]
dependencies: [task-7]
---

## Description
Implement user actions (keep left, keep right, keep both) for similar card pairs, including form handling and session state management.

## Requirements
- Handle "keep left" action (select card from first export)
- Handle "keep right" action (select card from second export)
- Handle "keep both" action (include both cards in result)
- Update session state based on user selections
- Provide visual feedback for user actions

## Sub-tasks
- [ ] Implement form handlers for user actions
- [ ] Update session state for each action type
- [ ] Add visual feedback for selected actions
- [ ] Handle bulk actions (select all, deselect all)
- [ ] Implement undo functionality
- [ ] Add validation for user selections
- [ ] Test all action types with various card pairs

## Dependencies
- task-7 (/similar_cards route implementation)

## Files to Create/Modify
- `src/anki_differ/web/app.py` (action handlers)
- `templates/similar_cards.html` (form integration)
- `static/js/similar_cards.js` (client-side interactions)
- `tests/integration/test_similar_cards_actions.py` (new test file)

## Acceptance Criteria
- All user actions work correctly
- Session state updates appropriately
- Visual feedback for user selections
- Bulk actions implemented
- Undo functionality works
- Input validation prevents invalid states
- Integration tests pass