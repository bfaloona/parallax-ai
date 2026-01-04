# Phase 5: Basic UI with shadcn/ui - PLAN v2

**Created:** 2026-01-03
**Status:** Awaiting Approval
**Goal:** Add functional UI with shadcn/ui components - looks good out of the box, emulate Poe Canvas layout

---

## Overview Update

Based on user feedback, **expanding scope to include styling** using **shadcn/ui** - the clear industry choice for Next.js + Tailwind projects in 2026.

### Why shadcn/ui?

**The Clear Choice for 2026:**
- ✅ **Industry standard** - De-facto choice for Next.js + Tailwind projects
- ✅ **Convention over configuration** - Sensible defaults, works out of the box
- ✅ **Looks great immediately** - Beautiful components without customization
- ✅ **Latest tech** - Built for Next.js 15, React 19, Tailwind CSS 4
- ✅ **Copy-paste approach** - You own the code, no runtime dependency
- ✅ **Built on Radix UI** - Rock-solid accessibility primitives
- ✅ **Highly recommended** - Top choice in 5+ component library reviews for 2025/2026

**Research Sources:**
- [14 Best React UI Component Libraries in 2026](https://www.untitledui.com/blog/react-component-libraries)
- [15 Best React UI Libraries for 2026](https://www.builder.io/blog/react-component-libraries-2026)
- [shadcn/ui Official Docs](https://www.shadcn.io/)
- [Next.js Installation Guide](https://ui.shadcn.com/docs/installation/next)

### Updated Scope

**In Scope:**
- Login/Register pages with shadcn/ui forms
- Conversation list sidebar with shadcn/ui components
- Chat interface with shadcn/ui layout
- Message display with shadcn/ui Card/Avatar components
- Message input with shadcn/ui Textarea/Button
- Mode selector with shadcn/ui Select
- Model selector with shadcn/ui Select
- **Emulate Poe Canvas main screen layout** (not sidebar)
- shadcn/ui default styling (no customization)

**Out of Scope (still deferred to Phase 10):**
- Custom colors, brand theming
- Hover states, focus states polish
- Enable/disable state refinement
- Mobile responsive breakpoints
- Dark/light mode toggle
- Loading states, skeletons
- Error boundaries, toast notifications
- Animations, transitions
- Polish, fit and finish

**Philosophy:** Use shadcn/ui defaults to get 80% quality immediately, defer the final 20% polish to Phase 10.

---

## shadcn/ui Setup

### Installation

```bash
cd frontend

# Initialize shadcn/ui (interactive CLI)
npx shadcn@latest init

# CLI will prompt for:
# - TypeScript: yes ✓
# - Style: Default ✓
# - Base color: Slate (or Neutral for Poe-like)
# - CSS variables: yes ✓
# - Tailwind config: yes ✓
# - Components path: @/components ✓
# - Utils path: @/lib/utils ✓
# - React Server Components: yes ✓
# - Icons library: lucide-react ✓
```

**Note for React 19:** May need `--legacy-peer-deps` flag with npm due to Radix UI peer dependencies. The shadcn CLI now prompts for this automatically.

### Components to Install

Install only the components we need:

```bash
# Form components
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add label
npx shadcn@latest add select

# Layout components
npx shadcn@latest add card
npx shadcn@latest add avatar
npx shadcn@latest add separator
npx shadcn@latest add scroll-area

# Navigation
npx shadcn@latest add dropdown-menu
```

**Total:** ~9 components (each is just a single TypeScript file copied into your project)

### Project Structure After Setup

```
frontend/
├── components/
│   └── ui/                    # shadcn/ui components (copied here)
│       ├── button.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── label.tsx
│       ├── select.tsx
│       ├── card.tsx
│       ├── avatar.tsx
│       ├── separator.tsx
│       ├── scroll-area.tsx
│       └── dropdown-menu.tsx
├── lib/
│   └── utils.ts              # shadcn/ui utility functions
└── app/
    └── globals.css           # Tailwind + shadcn/ui styles
```

---

## Poe Canvas Layout Analysis

Based on the screenshot you provided, the Poe Canvas main screen has:

**Layout:**
```
┌───────────────────────────────────────────────┐
│  Header                                        │
│  [Mode: Balanced ▼] [Model: Sonnet 4.5 ▼]    │
├───────────────────────────────────────────────┤
│                                                │
│  Message Thread (centered, max-width)         │
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ User message with avatar                 ││
│  └──────────────────────────────────────────┘│
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ Assistant response with avatar           ││
│  │ - Markdown formatted                     ││
│  │ - Code blocks                            ││
│  └──────────────────────────────────────────┘│
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ User message                             ││
│  └──────────────────────────────────────────┘│
│                                                │
├───────────────────────────────────────────────┤
│  Message Input (fixed bottom)                 │
│  ┌──────────────────────────────────────────┐│
│  │ [Type your message...            ] [Send]││
│  └──────────────────────────────────────────┘│
└───────────────────────────────────────────────┘
```

**Key Design Elements:**
- Clean, centered message thread (max-width ~800px)
- Messages alternate left/right (or both left with avatars)
- User messages: lighter background
- Assistant messages: subtle border/background
- Mode/Model selectors in header (compact dropdowns)
- Fixed message input at bottom
- Lots of whitespace, breathing room
- Simple, minimal design

**What We'll Emulate:**
- Centered message thread with max-width
- Message bubbles with avatars
- Mode/Model selectors in header
- Fixed input at bottom
- Clean, minimal aesthetic

**What We'll Skip (for now):**
- Exact color matching
- Precise spacing/sizing
- Markdown rendering (just plain text for Phase 5)
- Code block syntax highlighting
- Left/right message alignment (we'll do simple top-to-bottom)

---

## Updated Implementation Plan

### 5.1 shadcn/ui Setup (30 min)

**Tasks:**
- [ ] Run `npx shadcn@latest init` in frontend directory
- [ ] Configure with defaults (TypeScript, Slate/Neutral, CSS variables)
- [ ] Install required components (button, input, textarea, select, card, avatar, etc.)
- [ ] Verify Tailwind config updated
- [ ] Verify globals.css has shadcn/ui styles
- [ ] Test: Run `npm run dev`, ensure no errors

### 5.2 Authentication Pages with shadcn/ui (1.5 hours)

**File: `frontend/app/login/page.tsx`**

Using shadcn/ui components:
```tsx
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

// Centered card with form
// Email input (Label + Input)
// Password input (Label + Input)
// Login button (Button variant="default")
// Link to register (text link)
```

**File: `frontend/app/register/page.tsx`**

Similar structure:
```tsx
// Card with register form
// Email, Password, Confirm Password inputs
// Register button
// Link to login
```

**Styling:** shadcn/ui Card centered on page, default styling

### 5.3 Chat Layout with shadcn/ui (1.5 hours)

**File: `frontend/app/chat/layout.tsx`**

Layout structure:
```tsx
import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

// Header: flex with user avatar, email, logout button
// Sidebar: 250px fixed width
// - New Conversation button (Button)
// - ScrollArea with conversation list
// Main: flex-grow content area
```

**File: `frontend/app/chat/components/Sidebar.tsx`**

Using shadcn/ui:
```tsx
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

// "New Conversation" button (full width)
// ScrollArea with conversation list
// Each conversation: clickable div with hover state
// Delete button per conversation (small button)
```

### 5.4 Chat Interface with Poe-like Layout (2 hours)

**File: `frontend/app/chat/[id]/page.tsx`**

Poe Canvas emulation:
```tsx
import { Select } from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

// Layout:
// - Header: Mode selector + Model selector (Select components)
// - Main: ScrollArea with centered message thread (max-w-3xl mx-auto)
// - Footer: Fixed message input area
```

**File: `frontend/app/chat/[id]/components/MessageList.tsx`**

Using shadcn/ui:
```tsx
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"

// Centered container (max-w-3xl)
// Messages map to Cards
// Each message:
// - Avatar (U for user, A for assistant)
// - Card with message content
// - Timestamp (text-sm text-muted-foreground)
// User messages: subtle background
// Assistant messages: border
```

**File: `frontend/app/chat/[id]/components/MessageInput.tsx`**

Using shadcn/ui:
```tsx
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"

// Fixed bottom container
// Centered (max-w-3xl)
// Textarea (auto-resize)
// Send button (Button variant="default")
```

### 5.5 API Integration (Same as v1)

No changes - same API client and auth helpers as original plan.

**Files:**
- `frontend/lib/api.ts` - API client functions
- `frontend/lib/auth.ts` - Auth helpers
- `frontend/types/index.ts` - TypeScript types

### 5.6 Icons with Lucide React

shadcn/ui uses **lucide-react** for icons (automatically installed).

**Common icons we'll use:**
```tsx
import { Send, Plus, Trash2, LogOut, User, Bot } from "lucide-react"

// Send icon for send button
// Plus icon for new conversation
// Trash2 icon for delete
// LogOut icon for logout
// User icon for user avatar
// Bot icon for assistant avatar
```

---

## Updated File Structure

```
frontend/
├── components/
│   └── ui/                              # shadcn/ui components (9 files)
│       ├── button.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── label.tsx
│       ├── select.tsx
│       ├── card.tsx
│       ├── avatar.tsx
│       ├── separator.tsx
│       ├── scroll-area.tsx
│       └── dropdown-menu.tsx
├── lib/
│   ├── utils.ts                        # shadcn/ui utilities
│   ├── auth.ts                         # Auth helpers
│   └── api.ts                          # API client
├── types/
│   └── index.ts                        # TypeScript types
├── app/
│   ├── globals.css                     # Tailwind + shadcn/ui styles
│   ├── page.tsx                        # Home (redirect)
│   ├── login/
│   │   └── page.tsx                    # Login with shadcn/ui Card/Input/Button
│   ├── register/
│   │   └── page.tsx                    # Register with shadcn/ui
│   └── chat/
│       ├── layout.tsx                  # Chat layout with shadcn/ui
│       ├── page.tsx                    # Redirect to latest conversation
│       ├── components/
│       │   └── Sidebar.tsx             # Conversation list with shadcn/ui
│       └── [id]/
│           ├── page.tsx                # Chat interface (Poe-like)
│           └── components/
│               ├── MessageList.tsx     # Messages with Avatar/Card
│               └── MessageInput.tsx    # Input with Textarea/Button
└── package.json                        # Updated with shadcn/ui deps
```

**Total new files:** ~21 (9 shadcn/ui components + 12 app files)

---

## Updated Implementation Steps

### Step 1: shadcn/ui Setup (30 min)
- [ ] Initialize shadcn/ui with CLI
- [ ] Install 9 required components
- [ ] Verify Tailwind config
- [ ] Test dev server

### Step 2: Types & API Client (30 min)
- [ ] Create TypeScript types
- [ ] Create API client skeleton
- [ ] Create auth helpers

### Step 3: Authentication Pages (1.5 hours)
- [ ] Create login page with Card/Input/Button
- [ ] Create register page
- [ ] Implement auth logic
- [ ] Test: Can register, login, logout

### Step 4: Chat Layout (1.5 hours)
- [ ] Create chat layout with header/sidebar
- [ ] Create Sidebar component with ScrollArea
- [ ] Implement conversation list loading
- [ ] Implement new conversation button
- [ ] Test: Can see conversations, create new ones

### Step 5: Chat Interface (2 hours)
- [ ] Create chat page with Poe-like layout
- [ ] Create MessageList with Avatar/Card
- [ ] Create MessageInput with Textarea/Button
- [ ] Implement mode/model selectors (Select)
- [ ] Test: Can view messages, switch mode/model

### Step 6: Message Sending (1.5 hours)
- [ ] Implement API calls
- [ ] Connect MessageInput to backend
- [ ] Display streaming responses
- [ ] Test: Can send messages and see responses

### Step 7: Polish & Icons (30 min)
- [ ] Add lucide-react icons
- [ ] Implement delete conversation
- [ ] Add user avatar/logout to header
- [ ] Test: Full user flow works

**Total estimated time: ~8.5 hours** (slightly longer due to shadcn/ui setup)

---

## Dependencies Added

### Automatic (via shadcn/ui init)

```json
{
  "dependencies": {
    "@radix-ui/react-avatar": "^1.x",
    "@radix-ui/react-dropdown-menu": "^2.x",
    "@radix-ui/react-label": "^2.x",
    "@radix-ui/react-scroll-area": "^1.x",
    "@radix-ui/react-select": "^2.x",
    "@radix-ui/react-separator": "^1.x",
    "@radix-ui/react-slot": "^1.x",
    "class-variance-authority": "^0.7.x",
    "clsx": "^2.x",
    "lucide-react": "^0.index",
    "tailwind-merge": "^2.x",
    "tailwindcss-animate": "^1.x"
  }
}
```

**Total:** ~12 new dependencies (all managed by shadcn/ui CLI)

---

## Poe Canvas Layout Comparison

### What We're Emulating

| Feature | Poe Canvas | Our Implementation |
|---------|------------|-------------------|
| Message thread | Centered, max-width | ✅ Centered, max-w-3xl |
| Message bubbles | Card-like with borders | ✅ shadcn/ui Card |
| Avatars | User/Assistant icons | ✅ Avatar with U/A fallback |
| Mode selector | Dropdown in header | ✅ Select component |
| Model selector | Dropdown in header | ✅ Select component |
| Message input | Fixed bottom | ✅ Fixed bottom |
| Clean aesthetic | Minimal, lots of space | ✅ shadcn/ui defaults |

### What We're Skipping (Phase 10)

| Feature | Poe Canvas | Our Phase 5 | Phase 10 |
|---------|------------|-------------|----------|
| Markdown rendering | ✅ Full markdown | ❌ Plain text | ✅ Add react-markdown |
| Code syntax highlighting | ✅ Highlighted | ❌ Plain text | ✅ Add highlight.js |
| Message alignment | ✅ Left/right | ❌ All top-down | ✅ Flex layout |
| Hover states | ✅ Polished | ⚠️ Default only | ✅ Custom hover |
| Mobile responsive | ✅ Full responsive | ❌ Desktop only | ✅ Breakpoints |
| Dark mode | ✅ Toggle | ❌ Light only | ✅ Theme system |
| Loading states | ✅ Skeletons | ❌ None | ✅ Add skeletons |

---

## Known Limitations (To Fix in Phase 10)

1. **No AI Response Persistence** - Same as v1, deferred to Phase 6
2. **No Markdown Rendering** - Plain text only, add react-markdown in Phase 10
3. **No Code Highlighting** - Plain text code blocks
4. **Desktop Only** - No mobile responsive breakpoints
5. **Light Mode Only** - No dark mode toggle
6. **No Loading States** - No spinners or skeletons
7. **Basic Error Handling** - Errors in console, not UI
8. **No Message Alignment** - All messages top-down, not left/right
9. **Default Hover/Focus** - shadcn/ui defaults only, not custom
10. **Generic Conversation Titles** - All "New Conversation"

**All intentional for Phase 5** - Focus is on functionality + decent aesthetics.

---

## Success Criteria

Phase 5 is complete when:

- [x] shadcn/ui installed and configured
- [x] Login/register pages use shadcn/ui components
- [x] Chat layout uses shadcn/ui components
- [x] Messages display in centered, Poe-like layout
- [x] Message bubbles use Card component with avatars
- [x] Mode/Model selectors use Select component
- [x] Message input uses Textarea/Button components
- [x] Lucide icons used throughout
- [x] Interface looks clean and professional (shadcn/ui defaults)
- [x] All functionality from v1 plan works
- [x] No console errors during normal usage
- [x] **Looks significantly better than bare HTML** ✨

---

## Timeline Estimate

| Task | Time | Cumulative |
|------|------|------------|
| shadcn/ui Setup | 30 min | 0.5 hr |
| Types & API Client | 30 min | 1 hr |
| Auth Pages | 1.5 hr | 2.5 hr |
| Chat Layout | 1.5 hr | 4 hr |
| Chat Interface | 2 hr | 6 hr |
| Message Sending | 1.5 hr | 7.5 hr |
| Polish & Icons | 30 min | 8 hr |
| Testing & Bug Fixes | 1.5 hr | 9.5 hr |

**Total: ~9.5 hours** (with buffer for shadcn/ui learning curve)

---

## Questions for User

Before proceeding, please confirm:

1. **shadcn/ui approved?** - This is the clear industry choice for 2026
2. **Poe Canvas emulation scope?** - Centered layout, Card-based messages, default styling (no exact color matching)
3. **Markdown rendering?** - Plain text for Phase 5, add react-markdown in Phase 10?
4. **Mobile responsive?** - Desktop only for Phase 5, add breakpoints in Phase 10?
5. **Dark mode?** - Light mode only for Phase 5, add toggle in Phase 10?

---

## Research References

**Component Library Comparisons:**
- [14 Best React UI Component Libraries in 2026 - Untitled UI](https://www.untitledui.com/blog/react-component-libraries)
- [15 Best React UI Libraries for 2026 - Builder.io](https://www.builder.io/blog/react-component-libraries-2026)
- [8 Top Customizable UI Libraries for Next.js - DEV Community](https://dev.to/ethanleetech/8-most-customizable-ui-libraries-for-nextjs-24f)

**shadcn/ui Documentation:**
- [shadcn/ui Official Site](https://www.shadcn.io/)
- [Next.js Installation Guide](https://ui.shadcn.com/docs/installation/next)
- [shadcn/ui Components](https://ui.shadcn.com/docs/components)

**React 19 Compatibility:**
- [Installing shadcn/ui on Next.js 15 RC](https://github.com/shadcn-ui/ui/discussions/3988)
- [Installation fails with Next.js 15 and/or React 19](https://github.com/shadcn-ui/ui/issues/5557)

---

**Status: ⏸️ AWAITING APPROVAL**

**Summary:** This updated plan adds shadcn/ui for professional-looking UI out of the box, emulates Poe Canvas centered message layout, and still defers fit-and-finish polish to Phase 10. Estimated at ~9.5 hours with testing.
