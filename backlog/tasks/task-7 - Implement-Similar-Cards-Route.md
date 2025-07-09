---
id: task-7
title: Implement /similar_cards Route
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [medium-priority, backend]
dependencies: [task-6]
---

## Description
Implement the /similar_cards route in app.py with threshold configuration, displaying similar card pairs and handling user interactions.

## Requirements
- Create /similar_cards route in Flask app
- Support configurable similarity threshold
- Display similar card pairs using template
- Handle user actions (keep left, keep right, keep both)
- Integrate with session management

## Sub-tasks
- [ ] Implement /similar_cards route in app.py
- [ ] Add threshold configuration parameter
- [ ] Integrate with similarity calculation results
- [ ] Handle user action form submissions
- [ ] Update session state based on user selections
- [ ] Add error handling for edge cases
- [ ] Test route with various scenarios

## Dependencies
- task-6 (Similar cards HTML template)

## Files to Create/Modify
- `src/anki_differ/web/app.py` (main route implementation)
- `templates/similar_cards.html` (integration)
- `tests/integration/test_similar_cards_route.py` (new test file)

## Acceptance Criteria
- /similar_cards route displays similar card pairs
- Threshold configuration works correctly
- User actions update session state appropriately
- Error handling for edge cases
- Integration tests pass
- Route integrates with existing Flask app structure