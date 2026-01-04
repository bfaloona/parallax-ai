# Phase 5: Basic UI Implementation - PLAN

**Created:** 2026-01-03
**Status:** Awaiting Approval
**Goal:** Add minimal UI to see existing backend functionality working

---

## Overview

Create a very basic UI with **no extra styling** - just forms and data on webpages to see the working backend. This phase focuses on functionality, not aesthetics.

### Scope

**In Scope:**
- Login/Register pages with forms
- Conversation list sidebar
- Chat interface with message display
- Message input and sending
- Mode selector (7 modes)
- Model selector (Haiku/Sonnet/Opus)
- New conversation button
- Basic navigation

**Out of Scope (deferred to Phase 10 - UI Polish):**
- Custom styling, theming, brand colors
- Dark/light mode toggle
- Responsive mobile layout
- Animations, transitions
- Loading states, skeletons
- Error boundaries
- Polish, refinements

---

## Current State

### Backend API (Already Complete)

All required endpoints exist and are tested:

**Auth Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - JWT token generation
- `GET /api/auth/me` - Current user info

**Conversation Endpoints:**
- `POST /api/conversations` - Create conversation
- `GET /api/conversations` - List user's conversations
- `GET /api/conversations/{id}` - Get conversation with messages
- `DELETE /api/conversations/{id}` - Delete conversation
- `PATCH /api/conversations/{id}/mode` - Update mode

**Message Endpoints:**
- `POST /api/conversations/{id}/messages` - Add user message
- `POST /api/chat` - Legacy streaming endpoint (SSE)

**Mode System:**
- 7 modes available: Balanced, Creative, Precise, Technical, Research, Audit, Domain Expert
- Mode stored on conversation, affects system prompt

**Model Selection:**
- 3 models: Haiku, Sonnet, Opus
- Cost indicators available

### Frontend Scaffold (Already Exists)

- Next.js 16.1.1 with App Router
- React 19.2.3
- TypeScript 5
- Tailwind CSS 4
- No existing pages (empty scaffold)

---

## Implementation Plan

### 5.1 Authentication Pages

**File: `frontend/app/login/page.tsx`**

Features:
- Email input field
- Password input field
- Login button
- Link to register page
- Error message display
- On success: Store JWT in localStorage, redirect to `/chat`

**File: `frontend/app/register/page.tsx`**

Features:
- Email input field
- Password input field
- Confirm password field
- Register button
- Link to login page
- Error message display
- On success: Auto-login, redirect to `/chat`

**File: `frontend/lib/auth.ts`**

Helper functions:
- `login(email, password)` - Call API, store token
- `register(email, password)` - Call API, auto-login
- `logout()` - Clear token, redirect to login
- `getToken()` - Get JWT from localStorage
- `isAuthenticated()` - Check if token exists
- `getAuthHeaders()` - Return Authorization header

**No styling** - just basic HTML form elements.

### 5.2 Chat Layout

**File: `frontend/app/chat/layout.tsx`**

Layout structure:
```
┌─────────────────────────────────────┐
│ Header (user email, logout button)  │
├──────────┬──────────────────────────┤
│          │                          │
│ Sidebar  │   Main Chat Area         │
│          │                          │
│ - New    │   (nested page.tsx)      │
│ - List   │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

Components:
- Fixed header with user info
- Sidebar (250px fixed width)
- Main content area (flex-grow)
- Protected route (redirect to login if not authenticated)

**File: `frontend/app/chat/components/Sidebar.tsx`**

Features:
- "New Conversation" button (creates conversation, navigates to it)
- List of conversations (title, timestamp)
- Click conversation to navigate to `/chat/{id}`
- Active conversation highlighted
- Delete button per conversation

**No styling** - just list of links.

### 5.3 Chat Interface

**File: `frontend/app/chat/[id]/page.tsx`**

Layout:
```
┌──────────────────────────────────────┐
│ Conversation Controls                │
│ [Mode: Balanced ▼] [Model: Haiku ▼] │
├──────────────────────────────────────┤
│                                      │
│ Message Display Area                 │
│                                      │
│ [User message]                       │
│ [Assistant response]                 │
│ [User message]                       │
│ [Assistant response...]              │
│                                      │
├──────────────────────────────────────┤
│ Message Input Area                   │
│ [Text input field                  ] │
│                           [Send]     │
└──────────────────────────────────────┘
```

Features:
- Load conversation and messages on mount
- Display messages (user vs assistant)
- Mode selector dropdown (7 options)
- Model selector dropdown (3 options)
- Text input for new message
- Send button
- Scroll to bottom on new message

**File: `frontend/app/chat/[id]/components/MessageList.tsx`**

Features:
- Map over messages array
- Display role (user/assistant)
- Display content
- Display timestamp
- Auto-scroll to bottom

**File: `frontend/app/chat/[id]/components/MessageInput.tsx`**

Features:
- Textarea for message input
- Send button
- On send:
  1. Add user message to conversation (POST /api/conversations/{id}/messages)
  2. Call chat endpoint (POST /api/chat) - Note: This endpoint doesn't persist yet
  3. Stream response and display
  4. Clear input

**No styling** - just basic form elements and divs.

### 5.4 API Integration

**File: `frontend/lib/api.ts`**

API client functions:
```typescript
// Auth
export async function loginUser(email: string, password: string): Promise<{token: string}>
export async function registerUser(email: string, password: string): Promise<{token: string}>
export async function getCurrentUser(): Promise<User>

// Conversations
export async function getConversations(): Promise<Conversation[]>
export async function createConversation(title: string): Promise<Conversation>
export async function getConversation(id: string): Promise<ConversationWithMessages>
export async function deleteConversation(id: string): Promise<void>
export async function updateConversationMode(id: string, mode: string): Promise<void>

// Messages
export async function addMessage(conversationId: string, content: string): Promise<Message>
export async function streamChat(
  conversationId: string,
  message: string,
  mode: string,
  model: string,
  onChunk: (text: string) => void
): Promise<void>
```

All functions:
- Use fetch API
- Include Authorization header from getToken()
- Handle errors (throw with error message)
- Base URL from env var: `NEXT_PUBLIC_API_URL` (default: http://localhost:8000)

### 5.5 Type Definitions

**File: `frontend/types/index.ts`**

```typescript
export interface User {
  id: string
  email: string
  tier: string
  is_active: boolean
  created_at: string
}

export interface Conversation {
  id: string
  title: string
  current_mode: string
  current_model: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[]
}

export type Mode = 'balanced' | 'creative' | 'precise' | 'technical' | 'research' | 'audit' | 'domain_expert'
export type Model = 'haiku' | 'sonnet' | 'opus'
```

### 5.6 Environment Configuration

**File: `frontend/.env.local`**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production (later):
```bash
NEXT_PUBLIC_API_URL=https://api.parallax-ai.com
```

---

## File Structure

New files to create:

```
frontend/
├── app/
│   ├── login/
│   │   └── page.tsx                    # Login form
│   ├── register/
│   │   └── page.tsx                    # Register form
│   ├── chat/
│   │   ├── layout.tsx                  # Chat layout with sidebar
│   │   ├── page.tsx                    # Redirect to /chat/new or latest
│   │   ├── components/
│   │   │   └── Sidebar.tsx             # Conversation list sidebar
│   │   └── [id]/
│   │       ├── page.tsx                # Chat interface
│   │       └── components/
│   │           ├── MessageList.tsx     # Message display
│   │           └── MessageInput.tsx    # Message input form
│   └── page.tsx                        # Home (redirect to /login or /chat)
├── lib/
│   ├── auth.ts                         # Auth helpers
│   └── api.ts                          # API client
└── types/
    └── index.ts                        # TypeScript types
```

Total: ~12 new files

---

## Implementation Steps

### Step 1: Setup & Types (30 min)
- [ ] Create environment file with API URL
- [ ] Create TypeScript type definitions
- [ ] Create API client functions (no implementation yet)
- [ ] Create auth helper functions (no implementation yet)

### Step 2: Authentication Pages (1 hour)
- [ ] Create login page with form
- [ ] Create register page with form
- [ ] Implement auth helpers (login, register, logout, getToken)
- [ ] Implement API client auth functions
- [ ] Test: Can register, login, logout

### Step 3: Chat Layout (1 hour)
- [ ] Create chat layout with header and sidebar
- [ ] Implement protected route logic
- [ ] Create Sidebar component
- [ ] Implement conversation list loading
- [ ] Implement new conversation creation
- [ ] Test: Can see conversations, create new ones

### Step 4: Chat Interface (2 hours)
- [ ] Create chat page for conversation
- [ ] Implement message loading
- [ ] Create MessageList component
- [ ] Create MessageInput component
- [ ] Implement mode selector
- [ ] Implement model selector
- [ ] Test: Can view messages, switch mode/model

### Step 5: Message Sending (1.5 hours)
- [ ] Implement addMessage API call
- [ ] Implement streaming chat endpoint
- [ ] Connect MessageInput to API
- [ ] Display streaming responses
- [ ] Handle errors
- [ ] Test: Can send messages and see responses

### Step 6: Delete & Navigation (30 min)
- [ ] Implement delete conversation
- [ ] Add delete buttons
- [ ] Implement navigation (home page redirect)
- [ ] Test: Full user flow works

**Total estimated time: ~6.5 hours**

---

## Known Limitations (To Fix Later)

### Phase 5 Known Issues

These are **intentional limitations** that will be addressed in future phases:

1. **No AI Response Persistence**: Messages sent via `/api/chat` streaming endpoint are displayed but not saved to database
   - **Impact**: Refresh page = lose assistant responses
   - **Fix**: Phase 6 - Integrate chat streaming with message persistence

2. **No Loading States**: No spinners, skeletons, or loading indicators
   - **Impact**: Unclear when requests are in progress
   - **Fix**: Phase 10 - UI Polish

3. **No Error Handling UI**: Errors just thrown, not displayed nicely
   - **Impact**: Poor user experience on errors
   - **Fix**: Phase 10 - UI Polish

4. **No Mobile Responsiveness**: Fixed sidebar, desktop-only layout
   - **Impact**: Broken on mobile
   - **Fix**: Phase 10 - UI Polish

5. **No Styling**: Bare HTML, no colors, no spacing
   - **Impact**: Ugly but functional
   - **Fix**: Phase 10 - UI Polish

6. **No Auto-Title Generation**: Conversations created with generic "New Conversation" title
   - **Impact**: All conversations have same title
   - **Fix**: Phase 6 - Add auto-title from first message

7. **No Streaming UI Feedback**: Streaming works but no typing indicator or character-by-character display
   - **Impact**: Response appears all at once
   - **Fix**: Phase 10 - UI Polish

---

## Testing Plan

### Manual Testing Checklist

**Authentication Flow:**
- [ ] Navigate to http://localhost:3000
- [ ] Redirects to /login if not authenticated
- [ ] Can register new user
- [ ] Auto-login after registration
- [ ] Redirects to /chat after login
- [ ] Can logout
- [ ] Redirects to /login after logout
- [ ] Can login with existing credentials

**Conversation Management:**
- [ ] Click "New Conversation" creates conversation
- [ ] Conversation appears in sidebar
- [ ] Click conversation navigates to it
- [ ] Can see conversation messages
- [ ] Delete conversation removes it from sidebar
- [ ] Deleted conversation redirects to another conversation

**Chat Functionality:**
- [ ] Can type message in input
- [ ] Send button adds message to display
- [ ] Message appears in conversation
- [ ] Can change mode (dropdown works)
- [ ] Can change model (dropdown works)
- [ ] Refresh page preserves conversation and messages
- [ ] User messages persist (from /api/conversations/{id}/messages)

**Known Limitation - AI Responses:**
- [ ] AI response appears during session (streaming works)
- [ ] ⚠️ Refresh page loses AI responses (expected - not persisted yet)

### Browser Compatibility

Test in:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)

### API Integration Testing

- [ ] All API calls include Authorization header
- [ ] 401 errors redirect to login
- [ ] Network errors display in console
- [ ] CORS works (frontend → backend)

---

## Dependencies

### No New Dependencies Required

All necessary dependencies already installed:
- Next.js 16.1.1 (with App Router)
- React 19.2.3
- TypeScript 5
- Tailwind CSS 4 (installed but minimal usage for Phase 5)

### Environment Variables

**Backend (.env):**
```bash
# Already configured
DATABASE_URL=postgresql+asyncpg://parallax:parallax_dev@postgres:5432/parallax_ai
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=your-secret-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Frontend (.env.local):**
```bash
# New for Phase 5
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Changes Required

### NONE

All required backend functionality already exists and is tested:
- Auth endpoints ✓
- Conversation CRUD ✓
- Message persistence ✓
- Mode system ✓
- Model selection ✓
- SSE streaming ✓

**The backend is 100% ready for Phase 5.**

---

## Migration Guide Integration

After approval, this plan will be inserted into `docs/MIGRATION_GUIDE.md` as:

**Phase 4: Basic UI** (renumbering existing phases)

Updated Phase Summary:
| Phase | Name | Status |
|-------|------|--------|
| 0 | Infrastructure Setup | ✓ Complete |
| 1 | Minimal Round Trip | ✓ Complete |
| 2 | Database & Auth | ✓ Complete |
| 3 | Conversation CRUD | ✓ Complete |
| 4 | Testing Infrastructure | ✓ Complete |
| **5** | **Basic UI** | **← NEW** |
| 6 | Mode System | Pending |
| 7 | Domain System | Pending (Optional) |
| 8 | Model Selection | Pending |
| 9 | File Upload | Pending |
| ... | ... | ... |

---

## Success Criteria

Phase 5 is complete when:

- [x] User can register and login via web UI
- [x] User can see list of their conversations
- [x] User can create new conversations
- [x] User can view conversation messages
- [x] User can send messages and see them persisted
- [x] User can see AI responses (during session)
- [x] User can change mode via dropdown
- [x] User can change model via dropdown
- [x] User can delete conversations
- [x] User can logout
- [x] All manual testing checklist items pass
- [x] No errors in browser console during normal usage
- [x] Full user flow works: register → create conversation → chat → logout → login → continue

**Note:** AI response persistence is intentionally deferred to Phase 6.

---

## Next Steps After Phase 5

### Phase 6: AI Response Persistence

**Goal:** Make assistant responses persist to database

**Changes needed:**
1. Create new endpoint: `POST /api/conversations/{id}/chat`
   - Accepts user message
   - Saves user message to database
   - Calls Claude API
   - Streams response to frontend
   - **Saves assistant response to database**
   - Returns complete message objects

2. Update frontend to use new endpoint

3. Test: Refresh preserves full conversation history

**Estimated time:** 2-3 hours

### Phase 7: Mode System Polish

**Goal:** Implement mode-specific system prompts

**Changes needed:**
1. Create system prompts config file
2. Update chat endpoint to use mode-specific prompts
3. Test: Different modes produce different responses

**Estimated time:** 3-4 hours

---

## Questions for User

Before proceeding, please confirm:

1. **Styling approach confirmed?** - Absolutely no custom styling in Phase 5, all deferred to Phase 10?
   - ✓ Confirmed: "no extra styling, just forms and data on webpages"

2. **AI response persistence?** - Okay to defer to Phase 6?
   - Phase 5: Responses display but don't persist (lost on refresh)
   - Phase 6: Add persistence
   - Alternative: Include persistence in Phase 5 (+2 hours)

3. **Conversation titles?** - All conversations called "New Conversation" or generate from first message?
   - Phase 5: Generic titles
   - Phase 6: Auto-generate from first message
   - Alternative: Add title input field (+30 min)

4. **Landing page?** - Just redirect to /login or create marketing page?
   - Current plan: Simple redirect
   - Alternative: Add basic landing page (+1 hour)

5. **Screenshot reference?** - The screenshot you provided shows the old app. Should we match that layout exactly or just use it as inspiration?
   - Current plan: Similar layout (sidebar + chat), but simplified
   - Alternative: Exact pixel-perfect match (+3 hours)

---

## Risk Assessment

### Low Risk
- ✅ Backend API fully functional and tested
- ✅ Frontend scaffold already exists
- ✅ No complex state management needed
- ✅ No new dependencies required

### Medium Risk
- ⚠️ SSE streaming integration - might need debugging
- ⚠️ JWT token management - localStorage vs. cookies decision
- ⚠️ CORS configuration - must be correct for API calls

### Mitigation Strategies
- Test streaming with simple example first
- Use localStorage for Phase 5 simplicity (can migrate to httpOnly cookies later)
- Verify CORS_ORIGINS includes localhost:3000

---

## Estimated Timeline

| Task | Time | Cumulative |
|------|------|------------|
| Setup & Types | 30 min | 0.5 hr |
| Auth Pages | 1 hr | 1.5 hr |
| Chat Layout | 1 hr | 2.5 hr |
| Chat Interface | 2 hr | 4.5 hr |
| Message Sending | 1.5 hr | 6 hr |
| Delete & Navigation | 30 min | 6.5 hr |
| Testing & Bug Fixes | 1.5 hr | 8 hr |

**Total: ~8 hours** (with buffer for debugging)

---

## Approval Required

**Please review this plan and confirm:**

1. Scope is appropriate (minimal UI, no styling)
2. Known limitations are acceptable
3. Timeline estimate is reasonable
4. Ready to proceed with implementation

**Once approved, I will:**
1. Insert this plan into Migration Guide as Phase 5
2. Begin implementation immediately
3. Complete all 6 steps sequentially
4. Test against manual checklist
5. Report completion with demo instructions

---

**Status: ⏸️ AWAITING APPROVAL**
