# Parallax AI Branding Guide

## Logo & Icon System

### Original Logo
The Parallax AI logo features a watercolor-style illustration showing interlocking geometric blocks within a speech bubble frame. This represents the core concepts:
- **Multiple perspectives** (parallax effect)
- **Technical precision** (geometric forms)
- **Interconnected thinking** (interlocking pieces)
- **Dimensional analysis** (3D representation)
- **Communication** (speech bubble frame)

### Icon Variations

#### 1. Standard Icon (`parallax-icon.svg` - 64x64px)
Simplified vector version for general UI use:
- Hexagonal outer frame
- Interlocking 3D blocks (teal and tan)
- Directional arrows indicating perspective
- **Use for**: App headers, toolbars, desktop icons

#### 2. Simple Icon (`parallax-icon-simple.svg` - 32x32px)
Ultra-simplified version for small displays:
- Minimal hexagon frame
- Reduced block pattern
- Single directional arrow
- **Use for**: Favicons, mobile icons, small UI elements

## Color Palette

### Primary Colors (from logo)

**Teal/Blue Family:**
- Dark: `#2C5F6F` - Primary brand color
- Medium: `#3A7B8F` - Interactive elements
- Light: `#5A9BAF` - Highlights, hover states

**Tan/Gold Family:**
- Dark: `#C4A886` - Accent color
- Medium: `#D4B896` - Secondary accents
- Light: `#E8D4B4` - Subtle backgrounds

**Neutral:**
- Dark Accent: `#1A3A44` - Text, borders

### UI Color Palette (Migration Guide)

**Dark Theme:**
```css
--background: #0A0E12
--surface: #1A1F26
--border: #2A3441
--text-primary: #E8E9ED
--text-secondary: #A0A8B8
--primary: #2C5F6F (from logo)
--accent: #C4A886 (from logo)
```

**Light Theme:**
```css
--background: #FFFFFF
--surface: #F5F7FA
--border: #DFE3E8
--text-primary: #1A1F26
--text-secondary: #5A6270
--primary: #2C5F6F (from logo)
--accent: #C4A886 (from logo)
```

## Typography

**UI Font:** Inter (sans-serif)
- Headings: 600-700 weight
- Body: 400-500 weight
- Small text: 400 weight

**Code Font:** JetBrains Mono (monospace)
- Code blocks, technical content

## Mode System Icons

Each of the 7 modes has a distinct icon:

| Mode | Icon | Color Usage |
|------|------|-------------|
| Balanced | ◉ | Neutral teal |
| Challenge | 🛡️ | Warning tan/gold |
| Explore | 🗺️ | Light teal |
| Ideate | 💡 | Bright accent |
| Clarify | ❓ | Medium teal |
| Plan | ☑️ | Dark teal |
| Audit | 💲 | Dark tan/gold |

## File Locations

```
frontend/public/images/
├── parallax-logo-original.png    # Original watercolor logo
├── parallax-icon.svg             # Standard icon (64x64)
├── parallax-icon-simple.svg      # Simple icon (32x32)
└── README.md                     # Detailed usage guide
```

## Implementation Notes

### Next.js Metadata
The favicon and app icons are configured in `frontend/src/app/layout.tsx`:

```typescript
export const metadata: Metadata = {
  title: "Parallax AI",
  description: "Technical design assistant with 7 distinct thinking modes",
  icons: {
    icon: [{ url: '/images/parallax-icon-simple.svg', type: 'image/svg+xml' }],
    apple: [{ url: '/images/parallax-icon.svg', type: 'image/svg+xml' }],
  },
};
```

### Future Enhancements
- Generate PNG versions for better browser compatibility
- Create PWA manifest icons (192x192, 512x512)
- Generate Apple Touch icons
- Create social media preview images (OG images)

## Brand Voice

**Tone:** Technical, precise, collaborative
**Style:** Direct but supportive, rigorous but approachable
**Focus:** Engineering excellence, multiple perspectives, thorough analysis

## Usage Guidelines

1. **Always maintain aspect ratio** when resizing logos
2. **Minimum size:** 24px for simple icon, 48px for standard icon
3. **Clear space:** Maintain at least 8px padding around icons
4. **Background:** Logos work on both light and dark backgrounds
5. **Modifications:** Do not alter colors or geometry without approval
