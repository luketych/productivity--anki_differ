---
id: task-11
title: Update comparison_data.json Structure
status: To Do
assignee: []
created_date: '2025-07-08'
updated_date: '2025-07-08'
labels: [low-priority, data-structure]
dependencies: [task-10]
---

## Description
Update the comparison_data.json structure to include similarity results, ensuring proper data persistence and integration with the export generation process.

## Requirements
- Extend comparison_data.json to include similarity results
- Maintain backward compatibility with existing data structure
- Store similarity scores, pair information, and user selections
- Ensure proper serialization/deserialization

## Sub-tasks
- [ ] Analyze current comparison_data.json structure
- [ ] Design extension for similarity data
- [ ] Update data serialization logic
- [ ] Update data loading/parsing logic
- [ ] Test backward compatibility
- [ ] Validate JSON structure with various datasets
- [ ] Update documentation for new structure

## Dependencies
- task-10 (Similar Cards tab in navigation)

## Files to Create/Modify
- `src/anki_differ/core/diff.py` (data structure updates)
- `src/anki_differ/web/app.py` (JSON handling)
- `tests/unit/test_comparison_data_structure.py` (new test file)

## Acceptance Criteria
- comparison_data.json includes similarity results
- Backward compatibility maintained
- Data serialization works correctly
- JSON structure is valid and well-documented
- Integration with existing code seamless
- Unit tests pass for data structure changes