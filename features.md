This file can contain mistakes and was created in cooperation between Human and AI.

# Mati Features

## Overview

Mati (Mathematics and Tactic Intelligence) is a puzzle game and utility application with the following core capabilities:

- Grid-based number selection puzzles (4x4 to 7x7)
- Normal and Ultra gameplay modes
- In-game terminal with command interface
- Game history with export functionality
- Statistics tracking and achievements
- Language localization (English, German, Spanish, French, Klingon)
- Settings customization
- Tutorial system

**Version:** V0.7.1.2 (Beta V1.0.30)

---

## Core Features

### Puzzle Game

#### Grid Sizes
- **4x4** (Easy)
- **5x5** (Advanced)
- **6x6** (Hard)
- **7x7** (Expert)

#### Game Modes
- **Normal Mode:** Standard puzzle solving
- **Ultra Mode:** Bonus mode (requires terminal discovery to access)

#### Gameplay Mechanics
- Left-click to select cells
- Right-click to mark/dim cells (exclude from solution)
- Each row and column has a target sum
- Select cells so their values sum to the target for each row and column
- Cells auto-dim when their row or column is correctly fulfilled

#### Controls During Gameplay
- **Hint Button:** Provides a free hint (can be used multiple times per game)
- **Undo Button:** Reverts the last action
- **Pause (P key):** Pauses the game timer
- **Menu (Ctrl+M):** Returns to main menu
- **New Round (Ctrl+N):** Starts a new game
- **Fullscreen (F11):** Toggles fullscreen mode

#### Timer System
- Optional timer display (toggle in settings)
- Millisecond precision option (when timer is enabled)
- Timer pauses during game pause state
- Play time tracked per game

---

## Commands

### Terminal Commands

Access the terminal by pressing **Ctrl+T** in the menu. Type help to see all commands.

#### Navigation Commands
| Command | Description |
|---------|-------------|
| history | Opens game history screen |
| settings | Opens settings screen |
| about | Opens about screen |
| achievements | Opens achievements screen |
| advancedsettings | Opens advanced settings screen |

#### Game Start Commands
| Command | Description |
|---------|-------------|
| play4x4, p4x4 | Start 4x4 game |
| play5x5, p5x5 | Start 5x5 game |
| play6x6, p6x6 | Start 6x6 game |
| play7x7, p7x7 | Start 7x7 game |

#### Ultra Mode Commands
| Command | Description |
|---------|-------------|
| playultra4x4, pu4x4 | Start 4x4 Ultra game |
| playultra5x5, pu5x5 | Start 5x5 Ultra game |
| playultra6x6, pu6x6 | Start 6x6 Ultra game |
| playultra7x7, pu7x7 | Start 7x7 Ultra game |

#### Terminal Help Commands
| Command | Description |
|---------|-------------|
| help | Shows available commands |
| clear | Clears terminal output |

#### Terminal Gameplay Commands (in Ultra mode)
| Command | Description |
|---------|-------------|
| hint | Use a hint |
| new | Start new round |
| continue, c | Resume paused game |
| pause, break, b, p | Pause/unpause game |
| playtime, pt | Show current play time |
| playtimelong, ptl | Show detailed play time |
| return | Exit to previous screen |
| <cell> | Make cell selection (e.g., 1l2 = column 1, row 2, left-click) |

Cell input format depends on input_order setting:
- Default: column_row_action (e.g., 1l2 = col 1, row 2, left)
- Action can be l (left-click) or r (right-click/dim)

---

## UI Features

### Main Menu
- **Start buttons:** Grid size selection (4x4 through 7x7)
- **Settings button:** Opens settings screen
- **History button:** Opens game history
- **Quit button:** Exits application

### Settings Screen
Toggle options:
- **Save Played:** Enable/disable saving game history
- **Sound:** Enable/disable game sounds
- **Keyboard-Navigation:** Enable/disable alt control mode
- **Show Timer:** Enable/disable timer display
- **Milliseconds:** Show timer with millisecond precision (when timer enabled)
- **Fullscreen:** Toggle fullscreen mode
- **Live Clock:** Show current time in top-right corner

### Advanced Settings Screen
Available after accessing terminal:
- **Ultra Timer:** Enable/disable ultra mode timer display
- **Ultra Milliseconds:** Show ultra timer with millisecond precision
- **Terminal Clock:** Show clock in terminal
- **Game Volume:** Slider (0-100%)
- **Terminal Volume:** Slider (0-100%)
- **Language:** Dropdown selection
- **Ultra Terminal Input Order:** Selection of input format
- **Keybindings:** Customize keyboard shortcuts

### Keybindings (Default)
| Binding | Function |
|---------|----------|
| Ctrl+M | Back to Menu |
| Ctrl+N | New Round |
| F11 | Toggle Fullscreen |
| Ctrl+Z | Undo |
| P | Pause |
| H | Use Hint |
| R | Right-Click Cell |

### History Screen
- Lists all saved games
- Shows game size, mode (Normal/Ultra), duration
- **Filter buttons:**
  - Size filters (All, 4x4, 5x5, 6x6, 7x7)
  - Top 10 filter
  - Ultra filter (when terminal discovered)
- **Delete button (x):** Remove individual history entries
- **Click entry:** Opens detailed replay view
- **Scrollable list** with scrollbar
- **Keyboard navigation** support

### History Detail Screen
- **Replay functionality:** Step through game actions
- **Grid visualization:** Shows board state at each action
- **Action list:** Scrollable list of all actions
- **Export button:** Export this game as MP4
- **Export quality selector:** Standard/High/Ultra
- **Export FPS selector:** 30/60 FPS
- **Show End button:** Jump to final state
- **Back button:** Return to history

### Stats Screen
- Graphical statistics table
- **Sortable columns:** Size, Mode, Games, Best Time, Average Time
- Shows per-size/per-mode statistics
- **Back button:** Return to menu

### Achievements Screen
- Achievement pages with navigation
- **Pages:**
  - General (total games, total playtime milestones)
  - Per-size achievements (4x4, 5x5, 6x6, 7x7 - Normal and Ultra)
  - Easter Egg achievements
- **Progress indicators:** Circular progress for milestones
- **Navigation arrows:** Move between pages

### About Screen
- Application information
- Creator credit
- **Back button:** Return to menu

### Export Functionality
- Export finished games as MP4 video
- **Export qualities:** Standard (1x), High (2x), Ultra (4x)
- **FPS options:** 30 or 60 FPS
- **Background export:** Continue playing while exporting
- **Export notification:** Completion alert
- **Export exists check:** Warning if already exported

---

## Keyboard Navigation

### Focus System
- Arrow keys move focus between UI elements
- Enter/Space confirms selection
- Focus tracking with visual indicator

### Mouse Navigation
- Hover effects on interactive elements
- Click to activate buttons/selections
- Scroll wheel for scrolling lists

### Scrollbars
- Auto-hide after inactivity (700ms)
- Visible on hover or recent scroll
- Draggable handles
- Track click to jump

---

## Settings & Configuration

### Display Settings
- **Scale Modes:** Auto, 1x, 2x, 4x
- **Render Quality:** Normal, High, Ultra (text supersampling)
- **Fullscreen:** Toggle via F11 or setting
- **Live Clock:** Show/hide current time

### Audio Settings
- **Game Sound:** On/Off toggle
- **Game Volume:** 0-100% slider
- **Terminal Sound:** Independent toggle
- **Terminal Volume:** 0-100% slider

### Gameplay Settings
- **Save History:** Enable/disable game saving
- **Show Timer:** Enable/disable timer
- **Milliseconds:** Timer precision option
- **Keyboard Navigation:** Alt control mode
- **Input Order:** Column/Row/Action format selection

### Language Support
- **Built-in:** English (fallback)
- **Supported languages:**
  - Deutsch (German)
  - Espanol (Spanish)
  - Francais (French)

Language files stored as .smati files

---

## Data Management

### Game Saving
- Automatic save on game completion or pause
- Saved games stored as .mati files
- Obfuscated storage (XOR + compression + base64)

### History Management
- Optional history saving (toggle in settings)
- Saved in history/ directory
- Export history tracked separately

### Statistics Tracking
- Games played per size/mode
- Best times per size/mode
- Total playtime
- Automatically updated on game completion

---

## Easter Eggs

### Terminal
Hidden feature accessible via **Ctrl+T** in menu.

Features:
- Command-line interface
- Game control commands
- Navigation commands
- Settings commands
- Ultra mode access

---

## Technical Features

### Rendering
- Virtual screen at 800x600 (4:3 aspect ratio)
- Dynamic scaling to window size
- Text rendering with supersampling options
- Adaptive redraw system for performance

### Sound System
- Procedurally generated sounds (no external assets)
- Sine-wave tones for clicks, hints, wins
- Background music loops per game state
- Volume control for game and terminal sounds
- Crossfade between music tracks

### Input Handling
- Mouse click detection
- Keyboard event processing
- Focus management system
- Scroll wheel handling
- Key repeat functionality (hold-to-repeat)

### Persistence
- Settings saved to settings.mati
- Game data saved as .mati files
- Export history in separate .smati file
- Obfuscated data storage

### Export System
- MP4 video creation via ffmpeg/av library
- Frame-by-frame rendering
- Chapter-based video structure
- Configurable quality and FPS

---

## User Interactions

### Mouse Interactions
- Left-click: Select, activate
- Right-click: Dim/mark cells, context actions
- Hover: Visual feedback, scrollbar appearance
- Scroll wheel: Scroll lists

### Keyboard Shortcuts
- Arrow keys: Navigate focus
- Enter/Space: Confirm action
- Escape: Close popups/back navigation
- Ctrl+T: Open terminal (menu only)
- F11: Toggle fullscreen
- Ctrl+Z: Undo
- P: Pause

---

## Game States

### Menu States
- **MENU:** Main menu
- **SETTINGS:** Basic settings
- **ADVANCED_SETTINGS:** Advanced settings
- **ABOUT:** Application info
- **STATS:** Statistics
- **ACHIEVEMENTS:** Achievements
- **HISTORY:** Game history list
- **HISTORY_DETAIL:** Replay view
- **DELETE_HISTORY:** Delete confirmation
- **EXPORT_EXISTS:** Export info dialog
- **RESUME_CHOICE:** Continue/new game choice
- **TUTORIAL:** Tutorial overlay

### Game States
- **PLAY:** Active gameplay
- **TERMINAL:** Terminal interface

---

## Achievements System

### Achievement Categories

#### General Milestones
- Total games played (1, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)
- Total playtime (30min, 1h, 5h, 10h, 24h)

#### Per-Size Milestones
- Games completed (1, 25, 50, 75, 100, 150, 200) for each size/mode
- Speed achievements (time-based) for each size/mode

#### Speed Achievements Examples
- 4x4: 7.5s, 10s, 15s
- 4x4 Ultra: 20s, 25s, 30s
- 5x5: 30s, 35s, 45s
- 5x5 Ultra: 60s, 70s, 90s
- 6x6: 60s, 70s, 80s
- 6x6 Ultra: 180s, 200s, 240s
- 7x7: 75s, 90s, 120s
- 7x7 Ultra: 270s, 300s, 330s

---

## Accessibility & Usability

### Visual Indicators
- Focus highlighting with colored outline
- Hover states on interactive elements
- Selected cell highlighting (mint green)
- Dimmed cell indication (grayed)
- Fulfilled row/column indicators
- Tutorial speech bubbles

### Feedback Systems
- Sound effects for actions
- Visual feedback for clicks
- Timer display updates
- Achievement unlock notifications

### Help Systems
- In-game tutorial for first-time players
- Terminal help command
- Settings tooltips (via labels)

---

## File Operations

### Supported File Types
- **.mati:** Game save files (obfuscated)
- **.smati:** Language files (obfuscated JSON)

### Save Location
- Game saves: history/ directory
- Settings: settings.mati
- Export history: export_history.smati

---

## Performance Features

### Adaptive Rendering
- Redraw optimization based on changes
- Clock/timer updates at 100Hz cadence
- Cursor hide after 5s mouse idle
- Scrollbar fade after 700ms

### Resource Management
- Text rendering cache
- Sound buffer reuse
- Efficient history storage

---

## Mini Tutorial System

### First-Run Tutorial
- Guides new players through first match
- Introduces gameplay mechanics
- Hints at hidden terminal feature
- Leads to advanced settings discovery
- Non-blocking overlay (speech bubble style)

### Tutorial Steps
1. Welcome message on menu
2. How to play instructions during first game
3. Reminder to continue during gameplay
4. Victory message after first win
5. Hint about hidden terminal
6. Terminal discovery acknowledgment
7. Completion message after accessing advanced settings

---

*This documentation reflects the actual capabilities present in Mati V0.7.1.2 as of 2026-09-13.*
