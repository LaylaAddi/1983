# Speaker Attribution Feature - Implementation Guide

## Overview

This feature allows users to highlight and organize transcript text by attributing quotes to specific people (plaintiff, defendants, witnesses). This organized data is then used by AI to generate more accurate and properly cited legal documents.

## Problem Solved

**Before:**
- Raw transcripts with no speaker identification
- Users manually editing transcripts to add "Officer Smith:" prefixes
- AI not knowing who said what
- Difficulty organizing evidence by speaker
- No structured way to cite quotes in legal documents

**After:**
- Visual highlighting system for text selection
- Structured speaker attribution with metadata
- Color-coded quotes by role (plaintiff/defendant/witness)
- Automatic citation generation: "At 3:45, Officer Smith stated: '...'"
- Organized evidence ready for AI document generation

## Database Schema

### 1. Person Model
Tracks all people involved in the case.

**Fields:**
- `document` - ForeignKey to LawsuitDocument
- `name` - Full name (e.g., "John Smith")
- `role` - plaintiff | defendant | witness | other
- `title` - Job title (e.g., "Officer", "Detective")
- `badge_number` - For law enforcement
- `color_code` - Hex color for UI highlighting
- `notes` - Additional information

**Key Features:**
- Auto-syncs from `document.defendants` field
- Auto-creates plaintiff from user profile
- Supports custom witnesses and other parties
- Color-coded by role:
  - Plaintiff: Blue (#0d6efd)
  - Defendants: Red (#dc3545)
  - Witnesses: Green (#198754)
  - Other: Gray (#6c757d)

### 2. TranscriptQuote Model
Stores highlighted text segments with speaker attribution.

**Fields:**
- `video_evidence` - ForeignKey to VideoEvidence segment
- `text` - The quoted text
- `start_position` - Character position in transcript
- `end_position` - Character position in transcript
- `speaker` - ForeignKey to Person
- `approximate_timestamp` - Time within segment (MM:SS)
- `significance` - Why this quote matters
- `violation_tags` - Related constitutional violations
- `notes` - Additional context
- `sort_order` - Manual ordering
- `include_in_document` - Boolean flag

**Key Features:**
- Tracks exact position in transcript for highlighting
- Links to Person for speaker attribution
- Supports categorization and significance tagging
- Can be included/excluded from final document
- Generates formatted citations automatically

## API Endpoints

### Person Management

```
GET    /documents/<pk>/people/
POST   /documents/<pk>/people/add/
PUT    /documents/<pk>/people/<person_id>/update/
DELETE /documents/<pk>/people/<person_id>/delete/
POST   /documents/<pk>/people/sync/  (Auto-sync from defendants field)
```

### Quote Management

```
GET    /documents/<pk>/evidence/<segment_id>/quotes/
POST   /documents/<pk>/evidence/<segment_id>/quotes/add/
PUT    /documents/<pk>/evidence/<segment_id>/quotes/<quote_id>/update/
DELETE /documents/<pk>/evidence/<segment_id>/quotes/<quote_id>/delete/
```

## User Workflow

### Step 1: Setup People
1. User creates/edits a lawsuit document
2. Enters defendants in the defendants field (e.g., "Officer John Smith, Detective Jane Doe")
3. Navigates to Evidence Manager
4. Clicks "Sync People from Document" button
5. System auto-creates:
   - Plaintiff (from user profile)
   - All defendants (parsed from defendants field)

### Step 2: Extract & Edit Transcript
1. User extracts video transcript (existing workflow)
2. Reviews and edits raw transcript for accuracy
3. Now ready to attribute quotes to speakers

### Step 3: Highlight & Attribute Quotes
1. **People Panel** shows all involved parties:
   ```
   ┌─────────────────────────────┐
   │ People Involved             │
   ├─────────────────────────────┤
   │ 🔵 John Doe (Plaintiff)     │
   │ 🔴 Officer Smith (Defendant)│
   │ 🔴 Detective Jones (Defendant)│
   │ [+ Add Person]              │
   └─────────────────────────────┘
   ```

2. **Transcript Section** with highlighting:
   - User selects/highlights text in edited transcript
   - Popup appears: "Tag this quote?"
   - User selects speaker from dropdown
   - Adds optional significance/tags
   - Quote is saved and highlighted with speaker's color

3. **Quotes Panel** shows all tagged quotes:
   ```
   ┌──────────────────────────────────────────┐
   │ Tagged Quotes (3)              [+ Add]   │
   ├──────────────────────────────────────────┤
   │ 🎯 "Show me your ID"                     │
   │    👤 Officer Smith (Defendant)          │
   │    📌 Unlawful demand for ID             │
   │    ⚖️ Fourth Amendment                   │
   │    🕐 3:45-3:47                          │
   │    [Edit] [Delete] [☑ Include]          │
   ├──────────────────────────────────────────┤
   │ 🎯 "Am I being detained?"                │
   │    👤 John Doe (Plaintiff)               │
   │    🕐 3:48                               │
   │    [Edit] [Delete] [☑ Include]          │
   └──────────────────────────────────────────┘
   ```

### Step 4: Organize & Review
- Drag-and-drop to reorder quotes
- Toggle include/exclude for each quote
- Edit speakers, significance, tags
- Add notes and context
- Review all quotes before document generation

### Step 5: Generate Document
- Click "Generate Statement of Facts"
- AI uses organized quotes with proper attribution
- Generates citations like:
  ```
  "At 3:45 in the bodycam footage (Exhibit A), Officer Smith
  stated: 'Show me your ID.' The plaintiff responded: 'Am I
  being detained?' (Exhibit A, timestamp 3:48). This exchange
  demonstrates an unlawful demand for identification without
  reasonable suspicion, violating the Fourth Amendment."
  ```

## Frontend Implementation (TODO)

### JavaScript Components Needed

1. **TextHighlighter** - Captures text selection in transcript
2. **QuoteModal** - Popup for attributing selected text
3. **PeopleManager** - CRUD interface for managing people
4. **QuotesList** - Display and manage all quotes
5. **DragDropHandler** - Reorder quotes
6. **SyncButton** - Auto-sync people from defendants

### UI Libraries to Use
- Bootstrap 5 (already in use)
- Vanilla JavaScript for text selection
- SortableJS for drag-and-drop (optional)

### Key Functions

```javascript
// Text selection handler
function handleTextSelection(event) {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0) {
        const range = selection.getRangeAt(0);
        const start = getSelectionStart(range);
        const end = getSelectionEnd(range);

        showQuoteModal(text, start, end);
    }
}

// Show modal for speaker attribution
function showQuoteModal(text, startPos, endPos) {
    // Display modal with:
    // - Quote preview
    // - Speaker dropdown (populated from people)
    // - Significance input
    // - Violation tags checkboxes
    // - Save button -> calls API to create quote
}

// Save quote via API
async function saveQuote(quoteData) {
    const response = await fetch(`/documents/${docId}/evidence/${segmentId}/quotes/add/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(quoteData)
    });

    if (response.ok) {
        const data = await response.json();
        addQuoteToList(data.quote);
        highlightTextInTranscript(data.quote);
    }
}

// Highlight saved quotes in transcript
function highlightTextInTranscript(quote) {
    // Wrap quote.text in <mark> tag with speaker's color
    // Use data-quote-id attribute for editing/deletion
}

// Load and display quotes
async function loadQuotes(segmentId) {
    const response = await fetch(`/documents/${docId}/evidence/${segmentId}/quotes/`);
    const data = await response.json();

    data.quotes.forEach(quote => {
        addQuoteToList(quote);
        highlightTextInTranscript(quote);
    });
}
```

## AI Integration (TODO)

Update `evidence_to_facts_service.py` to use quotes:

```python
def generate_facts_with_quotes(document):
    """
    Generate Statement of Facts using organized quotes.
    """
    facts = []

    # Group quotes by video segment
    segments = VideoEvidence.objects.filter(
        document=document,
        include_in_complaint=True
    ).prefetch_related('quotes__speaker')

    for segment in segments:
        included_quotes = segment.quotes.filter(include_in_document=True)

        if included_quotes.exists():
            # Generate narrative with attributed quotes
            for quote in included_quotes:
                fact = f"At {quote.full_timestamp}, {quote.speaker.display_name} "
                fact += f'stated: "{quote.text}"'

                if quote.significance:
                    fact += f" This {quote.significance.lower()}."

                facts.append(fact)

    return "\n\n".join(facts)
```

## Migration Steps

### On Your Local Machine:

1. **Create migrations:**
   ```bash
   python manage.py makemigrations
   ```

2. **Review migration file:**
   ```bash
   # Check documents/migrations/XXXX_person_transcriptquote.py
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Test in Django admin:**
   ```bash
   python manage.py runserver
   # Visit http://localhost:8000/admin
   # Check Person and TranscriptQuote models
   ```

### On Production (Render):

1. **Commit and push changes**
2. **Render auto-deploys and runs migrations**
3. **Or manually run:** `python manage.py migrate`

## Testing Checklist

- [ ] Migrations run successfully
- [ ] Person model appears in Django admin
- [ ] TranscriptQuote model appears in Django admin
- [ ] Can create Person records manually
- [ ] Can create TranscriptQuote records manually
- [ ] API endpoints return correct JSON
- [ ] Sync people from defendants works
- [ ] People appear in evidence manager context
- [ ] Frontend can fetch people list
- [ ] Frontend can create quotes
- [ ] Frontend can highlight text
- [ ] Quotes display with proper colors
- [ ] Can edit/delete quotes
- [ ] Can reorder quotes
- [ ] AI generation uses quotes correctly

## Next Steps

**Phase 1: Backend** ✅ COMPLETE
- [x] Create Person model
- [x] Create TranscriptQuote model
- [x] Create API endpoints
- [x] Add URL patterns
- [x] Update evidence_manager view

**Phase 2: Frontend UI** 🚧 IN PROGRESS
- [ ] Create People Management panel
- [ ] Implement text selection/highlighting
- [ ] Build Quote Attribution modal
- [ ] Display tagged quotes list
- [ ] Add drag-and-drop reordering
- [ ] Color-code quotes by speaker

**Phase 3: AI Integration** 📝 TODO
- [ ] Update evidence_to_facts_service.py
- [ ] Use quotes for Statement of Facts
- [ ] Generate proper citations
- [ ] Include speaker attribution

**Phase 4: Polish** ✨ TODO
- [ ] Keyboard shortcuts (Ctrl+H to highlight)
- [ ] Bulk operations (tag multiple quotes)
- [ ] Export quotes to CSV
- [ ] Quote search/filter
- [ ] Analytics (quotes per speaker)

## Benefits

### For Users:
- ✅ Clear visual organization of who said what
- ✅ Easy attribution without manual text editing
- ✅ Better evidence preparation
- ✅ Professional-quality citations

### For AI:
- ✅ Structured data instead of raw text
- ✅ Knows exactly who said each quote
- ✅ Can generate accurate citations
- ✅ Better context for legal analysis

### For Legal Documents:
- ✅ Proper citation format
- ✅ Accurate attribution
- ✅ Professional presentation
- ✅ Easier to verify evidence

## Technical Notes

- Uses Django ORM relationships for data integrity
- Color-coding based on role for visual clarity
- Position tracking allows persistent highlighting
- Sort order enables manual organization
- Include/exclude flags for flexibility
- Prefetching optimizes database queries
- AJAX for smooth UX without page reloads

## Support

For implementation help:
1. Check Django admin for data verification
2. Use browser DevTools to debug API calls
3. Check Django logs for backend errors
4. Review this documentation for workflow

---

**Status:** Backend Complete | Frontend Pending | AI Integration Pending
**Last Updated:** 2025-10-26
