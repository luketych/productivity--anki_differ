# Similar Cards Matching Feature

## Overview
Add a new tab to the web interface that displays cards from "Only in MacOS Export" and "Only in Android Export" side-by-side, with similar cards aligned to help users identify potential duplicates or near-duplicates.

## User Problem
Users may have similar cards in different exports that aren't exact matches due to:
- Minor text variations (typos, formatting differences)
- Different deck assignments
- Slight content modifications over time
- Export timing differences

## Feature Requirements

### Core Functionality
1. **New Tab**: Add "Similar Cards" tab to the existing web interface
2. **Side-by-Side Display**: Show cards from both exports in parallel columns
3. **Similarity Matching**: Calculate text similarity percentage between cards
4. **Smart Alignment**: Pair cards with highest similarity scores
5. **User Actions**: Allow users to:
   - Keep one card and discard the other
   - Keep both cards
   - Mark as reviewed/handled

### Similarity Algorithm
- **Primary Match**: Calculate text similarity percentage between question fields
- **Secondary Match**: Calculate similarity between answer fields
- **Threshold**: Configurable similarity threshold (default: 70%)
- **Weighting**: Question similarity weighted higher than answer similarity

### UI Design
```
[Existing Tabs] | [Similar Cards]

Similar Cards Tab:
┌─────────────────────────────────────────────────────────────────┐
│ Similarity Threshold: [70%] [Update]                           │
├─────────────────────────────────────────────────────────────────┤
│ MacOS Export                    │ Android Export                │
├─────────────────────────────────┼─────────────────────────────────┤
│ Card A (85% match)              │ Card B (85% match)            │
│ Q: What is Python?              │ Q: What is Python programming? │
│ A: A programming language       │ A: A programming language     │
│ [Keep] [Discard] [Keep Both]    │ [Keep] [Discard] [Keep Both]  │
├─────────────────────────────────┼─────────────────────────────────┤
│ Card C (72% match)              │ Card D (72% match)            │
│ ...                             │ ...                           │
└─────────────────────────────────┴─────────────────────────────────┘
```

## Technical Implementation

### Data Structure
```python
@dataclass
class SimilarCardPair:
    card1: Card  # from file1 (MacOS)
    card2: Card  # from file2 (Android)
    similarity_score: float
    question_similarity: float
    answer_similarity: float
    metadata_match: dict  # deck, tags, etc.
```

### Algorithm Steps
1. Extract cards unique to each export
2. Calculate pairwise similarity matrix
3. Use Hungarian algorithm or greedy matching for optimal pairing
4. Filter pairs above similarity threshold
5. Sort by similarity score (descending)

### Available Metadata (Investigation Results)

**Currently Supported by Anki Export Format:**
- **Deck Information**: Available via `#deck:DeckName` header or deck column
- **Tags**: Available as space-separated values in tags field/column  
- **Card Types**: Available via `#notetype:BasicType` header or notetype column
- **GUID**: Unique identifiers available if exported
- **Media Files**: Audio `[sound:file.mp3]` and image references in content
- **Extra Fields**: Support for note types with >2 fields

**Current Implementation Limitation:**
The existing codebase only parses Question and Answer fields. Additional metadata (tags, deck, audio files) is present in export files but not extracted by the current parsing logic.

**Enhancement Needed:**
Modify `/src/anki_differ/core/diff.py` parsing to extract all available fields for richer similarity matching using deck names, tags, and media content.

## File Changes Required

### New Files
- `/src/anki_differ/core/similarity.py` - Similarity calculation logic
- `/src/templates/similar_cards.html` - New tab template

### Modified Files
- `/src/anki_differ/web/app.py` - Add similarity route and logic
- `/src/templates/base.html` - Add new tab navigation
- `/src/anki_differ/core/diff.py` - Extend to support similarity matching
- `/src/data/comparison_data.json` - Store similarity results

### Dependencies
- **Text Similarity**: `difflib.SequenceMatcher` (built-in) or `fuzzywuzzy` library
- **Optimal Matching**: `scipy.optimize.linear_sum_assignment` for Hungarian algorithm

## Success Criteria
1. Users can identify similar cards across exports
2. Similarity calculation is accurate and useful
3. UI is intuitive and responsive
4. Performance is acceptable for typical dataset sizes
5. Integration with existing export generation works seamlessly

## Future Enhancements
- Machine learning-based similarity (semantic similarity)
- Batch actions for multiple similar pairs
- Export similarity statistics/reports
- Custom similarity algorithms per field type
- Integration with Anki's built-in duplicate detection