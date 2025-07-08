# Frontend Card Loading Fix - Milestones

## Overview
This document breaks down the frontend card loading issue fix into detailed milestones with specific tasks, acceptance criteria, and deliverables.

## Milestone 1: Immediate Diagnosis and Logging Setup
**Duration**: 30 minutes  
**Priority**: Critical  
**Dependencies**: None  

### Tasks
1. **Backend Logging Enhancement**
   - [ ] Add detailed logging to `/select` route showing data structure passed to template
   - [ ] Log card counts for each category (different, identical, unique1, unique2)
   - [ ] Add logging to show template data serialization process
   - [ ] Log file paths and data file timestamps

2. **Frontend Console Logging**
   - [ ] Add console.log in DOMContentLoaded to show initial data structure
   - [ ] Log each card type count and DOM element count
   - [ ] Add logging to tab switching events
   - [ ] Log pagination calculations and current page states

3. **Create Debug Test Route**
   - [ ] Create `/debug/card-loading` route that returns simplified data structure
   - [ ] Add minimal template that displays raw card counts
   - [ ] Test data accessibility without complex UI logic

### Acceptance Criteria
- [ ] Console shows exact data structure on page load
- [ ] Backend logs show card counts and data passing process
- [ ] Debug route confirms data is accessible
- [ ] Can identify if issue is data access or UI rendering

### Deliverables
- Enhanced logging in `src/anki_differ/web/app.py`
- Debug console output in browser
- `/debug/card-loading` route for testing

---

## Milestone 2: Root Cause Identification
**Duration**: 30 minutes  
**Priority**: Critical  
**Dependencies**: Milestone 1 complete  

### Tasks
1. **Data Flow Analysis**
   - [ ] Verify `{{ data|tojson|safe }}` produces valid JavaScript object
   - [ ] Check if `data.different_cards` exists and has expected structure
   - [ ] Confirm template loops (`{% for card in data.different_cards %}`) find cards
   - [ ] Verify DOM elements are created for each card

2. **UI State Analysis**
   - [ ] Check if cards are hidden by CSS (display: none)
   - [ ] Verify pagination logic isn't hiding all cards
   - [ ] Test if Bootstrap tab initialization is working
   - [ ] Confirm tab content areas are being populated

3. **JavaScript Execution Analysis**
   - [ ] Verify all event listeners are properly attached
   - [ ] Check if `updateVisibility()` function is being called
   - [ ] Test if pagination setup is working correctly
   - [ ] Confirm no JavaScript errors are preventing execution

### Acceptance Criteria
- [ ] Exact cause of card loading failure identified
- [ ] Clear understanding of whether issue is data, rendering, or visibility
- [ ] Specific line/function where failure occurs is known

### Deliverables
- Root cause analysis report
- Specific code locations where fix is needed
- Understanding of whether fix is backend or frontend

---

## Milestone 3: Data Structure Fix
**Duration**: 45 minutes  
**Priority**: High  
**Dependencies**: Milestone 2 complete  

### Tasks
1. **Backend Data Consistency**
   - [ ] Ensure `/select` route passes complete data structure to template
   - [ ] Verify all card arrays are populated with correct data
   - [ ] Fix any serialization issues in template data passing
   - [ ] Test with various data sizes to ensure consistency

2. **Template Data Binding**
   - [ ] Fix template variable access if needed
   - [ ] Ensure `data.different_cards` etc. are accessible in template
   - [ ] Verify JavaScript can access serialized data object
   - [ ] Fix any template syntax issues

3. **JavaScript Data Access**
   - [ ] Fix JavaScript data object access if needed
   - [ ] Ensure `data.different_cards` is properly populated in JS
   - [ ] Add defensive checks for undefined/null data
   - [ ] Fix any data structure mismatches

### Acceptance Criteria
- [ ] JavaScript `data` object contains all expected card arrays
- [ ] Template loops find and render cards correctly
- [ ] No undefined/null data errors in console
- [ ] Card counts match between backend and frontend

### Deliverables
- Fixed data passing between backend and frontend
- Working template data binding
- JavaScript data object with all card data

---

## Milestone 4: UI Visibility and Pagination Fix
**Duration**: 45 minutes  
**Priority**: High  
**Dependencies**: Milestone 3 complete  

### Tasks
1. **Fix Visibility Logic**
   - [ ] Audit `updateVisibility()` function for logic errors
   - [ ] Fix pagination calculations that might hide all cards
   - [ ] Ensure cards are shown by default on page load
   - [ ] Fix any CSS display issues preventing card visibility

2. **Fix Pagination System**
   - [ ] Verify `ITEMS_PER_PAGE` and page calculations are correct
   - [ ] Fix `currentPage` initialization for all tabs
   - [ ] Ensure pagination doesn't hide cards unnecessarily
   - [ ] Test pagination with different card counts

3. **Fix Tab Initialization**
   - [ ] Ensure Bootstrap tabs are properly initialized
   - [ ] Fix tab content loading on first page load
   - [ ] Verify tab switching properly updates visibility
   - [ ] Test that "Different" tab shows cards immediately

### Acceptance Criteria
- [ ] Cards are visible in all tabs when page loads
- [ ] Pagination shows correct number of cards per page
- [ ] Tab switching works and shows appropriate content
- [ ] No cards are hidden due to pagination errors

### Deliverables
- Working card visibility system
- Functional pagination for all tabs
- Proper tab initialization and switching

---

## Milestone 5: Search and Filter Functionality
**Duration**: 30 minutes  
**Priority**: Medium  
**Dependencies**: Milestone 4 complete  

### Tasks
1. **Fix Search Functionality**
   - [ ] Verify search filters work correctly
   - [ ] Fix any issues with `filterCards()` function
   - [ ] Ensure search doesn't conflict with pagination
   - [ ] Test search with various card types

2. **Fix Filter Integration**
   - [ ] Ensure search filters work with pagination
   - [ ] Fix filter reset when changing tabs
   - [ ] Test filter clearing functionality
   - [ ] Verify filtered cards are properly counted

### Acceptance Criteria
- [ ] Search filters cards correctly in all tabs
- [ ] Search works with pagination system
- [ ] Filter clearing works properly
- [ ] No conflicts between search and other UI elements

### Deliverables
- Working search functionality
- Proper filter integration with pagination
- Tested search across all card types

---

## Milestone 6: Enhanced Debugging Tools
**Duration**: 30 minutes  
**Priority**: Low  
**Dependencies**: Milestone 4 complete  

### Tasks
1. **Permanent Debug Features**
   - [ ] Add toggleable debug mode with detailed logging
   - [ ] Create debug panel showing data structure and counts
   - [ ] Add visual indicators for card states
   - [ ] Implement debug routes for testing

2. **Error Handling Enhancement**
   - [ ] Add user-friendly error messages
   - [ ] Implement graceful degradation for missing data
   - [ ] Add error recovery mechanisms
   - [ ] Test error scenarios

### Acceptance Criteria
- [ ] Debug mode can be toggled on/off
- [ ] Clear error messages for users
- [ ] Debugging tools help identify future issues
- [ ] System gracefully handles error conditions

### Deliverables
- Debug mode toggle and panel
- Enhanced error handling
- Debugging tools for future maintenance

---

## Milestone 7: Comprehensive Testing
**Duration**: 45 minutes  
**Priority**: High  
**Dependencies**: Milestones 3-5 complete  

### Tasks
1. **Functional Testing**
   - [ ] Test with various data sizes (small, medium, large datasets)
   - [ ] Test all card types (different, identical, unique1, unique2)
   - [ ] Test pagination with different card counts
   - [ ] Test search functionality across all tabs

2. **Integration Testing**
   - [ ] Test complete user workflow (upload → select → export)
   - [ ] Test card selection and state persistence
   - [ ] Test export functionality with selections
   - [ ] Test reset functionality

3. **Browser Compatibility**
   - [ ] Test in Chrome, Firefox, Safari
   - [ ] Test responsive design on mobile
   - [ ] Test Bootstrap components work correctly
   - [ ] Test JavaScript compatibility

### Acceptance Criteria
- [ ] All functionality works with various data sizes
- [ ] Complete user workflow works end-to-end
- [ ] Works in all major browsers
- [ ] Mobile responsive design works

### Deliverables
- Fully tested and working application
- Documentation of test cases and results
- Confirmed compatibility across browsers

---

## Success Metrics
- **Primary**: Cards are visible in all tabs when page loads
- **Secondary**: Pagination works correctly and shows appropriate number of cards
- **Tertiary**: Search functionality filters cards properly
- **Quaternary**: Export functionality works with user selections
- **Bonus**: Debug tools are available for future maintenance

## Risk Mitigation
- **Issue**: Multiple interacting problems (data + UI + pagination)
  - **Mitigation**: Fix in order of dependency, comprehensive logging
- **Issue**: Breaking existing functionality while fixing
  - **Mitigation**: Incremental changes, testing at each milestone
- **Issue**: Time overrun due to complex debugging
  - **Mitigation**: Focus on core functionality first, debug tools last

## Total Estimated Duration: 4 hours
- Critical Path: Milestones 1-4 (2.5 hours)
- Enhanced Features: Milestones 5-6 (1 hour)
- Testing: Milestone 7 (45 minutes)

## Dependencies
```
Milestone 1 → Milestone 2 → Milestone 3 → Milestone 4 → Milestone 7
                                    ↓
                              Milestone 5 → Milestone 6
```

## Next Actions
1. Begin Milestone 1 immediately
2. Complete critical path (Milestones 1-4) before optional features
3. Focus on getting basic card display working first
4. Add enhanced features only after core functionality is confirmed