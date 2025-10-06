# Split View UX Design - Code Editing Clarity

**Created**: 2025-10-06
**Status**: Design Document - Implementation Guide
**Purpose**: Ensure users understand instance vs shared code editing

---

## The Challenge

Users need to edit code in split view, but there are two types of edits:

1. **Instance Code** ([Obj] This Object Only)
   - Affects only the selected sprite instance
   - Lives in scene file
   - Safe to edit without side effects

2. **Shared Behavior Classes** ([Class] Shared)
   - Affects ALL objects using this behavior
   - Lives in behavior file
   - Edits have wide-reaching impact

**Goal**: Make this distinction crystal clear to prevent accidental changes.

---

## Visual Design System

### Tab Design

```
┌─ Code Tabs ────────────────────────────────────────────────────┐
│ [Obj] This Object *  │ [Class] EnemyPatrol (Shared) │ [Class] Health (Shared)│
│ [Accent Color]     │ [Neutral Color]         │ [Neutral Color]   │
└────────────────────────────────────────────────────────────────┘
```

**Visual Elements:**

| Element | Instance Tab | Behavior Tab |
|---------|-------------|--------------|
| Icon | [Obj] (document) | [Class] (wrench) |
| Label | "This Object" | "[Name] (Shared)" |
| Color | Accent (blue) | Neutral (gray) |
| Star Badge | * if has overrides | Never |
| Tooltip | "Object-specific code" | "Affects ALL objects using [Name]" |

### Warning Banner (Shared Tabs Only)

```
┌─ EnemyPatrol.py (Shared Behavior Class) ───────────────────────┐
│ WARNING:  WARNING: Editing this file affects ALL objects using       │
│    EnemyPatrol behavior across all scenes.                     │
│                            [ Edit This Object Only] [Continue]│
├─────────────────────────────────────────────────────────────────┤
│ class EnemyPatrol(Component):                                   │
│     def __init__(self, sprite, speed=50, distance=200):         │
```

**Banner Features:**
- Orange/yellow background (warning color)
- Bold warning icon and text
- Action button: "Edit This Object Only"
- Clicking button switches to instance tab and highlights code

### Scope Indicator (Top of Code Area)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Obj] Editing: This Object Only                                   │ ← Blue
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ [Class] Editing: EnemyPatrol (Shared Class)    Affects 12 object(s) │ ← Yellow
└─────────────────────────────────────────────────────────────────┘
```

**Always visible** at top of code editor, updates when tab changes.

---

## User Flows

### Flow 1: User Wants to Tweak One Enemy

1. Click enemy sprite in scene viewport
2. Split view opens with tabs:
   - `[Obj] This Object` (selected by default)
   - `[Class] EnemyPatrol (Shared)`
   - `[Class] Health (Shared)`
3. Scope indicator shows: "[Obj] Editing: This Object Only" (blue)
4. User edits speed property in instance code:
   ```python
   patrol = EnemyPatrol(enemy1, speed=30, distance=100)  # Changed to 30
   ```
5. Save → Only this enemy affected ✓

### Flow 2: User Accidentally Clicks Shared Tab

1. User clicks `[Class] EnemyPatrol (Shared)` tab
2. **Warning banner appears** (orange background)
3. Scope indicator changes: "[Class] Editing: EnemyPatrol (Shared Class) - Affects 12 object(s)" (yellow)
4. User reads warning: "Editing this file affects ALL objects..."
5. User clicks **[ Edit This Object Only]**
6. Switches back to instance tab ✓
7. Helper comment shows where to add instance code

### Flow 3: Advanced User Wants to Fix Behavior for All Enemies

1. Click any enemy with EnemyPatrol behavior
2. Click `[Class] EnemyPatrol (Shared)` tab
3. See warning, click **[Continue]** or dismiss (they know what they're doing)
4. Edit the behavior class:
   ```python
   def update(self, dt):
       # Fixed bug that affected all enemies
       if self.velocity.x > 0:
           self.sprite.flip_x = False
   ```
5. Save → All 12 enemies fixed ✓
6. Hot-reload updates all instances immediately

### Flow 4: Instance Has Custom Overrides

1. Click enemy that has custom code
2. Tab shows: `[Obj] This Object *` (star badge)
3. Tooltip: "Object-specific code\n* Has custom overrides"
4. Instance code shows:
   ```python
   patrol = EnemyPatrol(enemy1, speed=30, distance=100)

   # Custom override for boss enemy
   def boss_attack_pattern(dt):
       if self.sprite.health < 50:
           patrol.speed *= 2  # Enrage mode!
       patrol.original_update(dt)

   patrol.update = boss_attack_pattern  # ← Override
   ```
5. User understands this instance has special behavior ✓

---

## Implementation Components

### 1. CodeTabBar Widget (`code_tab_bar.py`)
- Custom QTabWidget with visual indicators
- Automatic warning banners for shared tabs
- "Edit This Object Only" button handler
- Star badge detection for overrides

### 2. EditScopeIndicator Widget (`edit_scope_indicator.py`)
- Persistent indicator at top of code area
- Shows current edit scope (instance vs shared)
- Shows instance count for shared edits
- Color-coded (blue = safe, yellow = caution)

### 3. Split View Integration
- Default to instance tab when sprite selected
- Behavior tabs as reference/advanced editing
- Sync scope indicator with tab selection
- Count instances of each behavior in scene

### 4. Instance Override Detection
```python
def has_instance_overrides(sprite, scene_code: str) -> bool:
    """
    Check if sprite has custom code in scene file.

    Looks for:
    - Custom properties set after component creation
    - Method overrides (patrol.update = ...)
    - Lambda/function definitions
    """
    sprite_section = extract_sprite_section(scene_code, sprite.name)

    # Check for patterns indicating overrides
    has_custom_properties = "." + "=" in sprite_section after add_component
    has_method_override = ".update = " in sprite_section
    has_lambda = "lambda " in sprite_section

    return has_custom_properties or has_method_override or has_lambda
```

---

## Color Coding System

| Scope | Primary Color | Meaning |
|-------|--------------|---------|
| Instance | Blue (`accent_primary`) | Safe, localized changes |
| Shared | Yellow/Orange (`warning`) | Caution, wide-reaching impact |
| Override Badge | Gold star (*) | This instance has custom code |

**Contrast Principle:**
- Blue = "You're in the safe zone"
- Yellow = "Be careful, this affects many things"
- Star = "This one is special"

---

## Error Prevention

### Before Save (Shared Code)
```
┌─────────────────────────────────────────────────────────────────┐
│ WARNING:  You are about to modify a SHARED behavior class            │
│                                                                 │
│ This will affect 12 object(s) across 3 scene(s):               │
│   • 8 enemies in Level1                                        │
│   • 3 enemies in Level2                                        │
│   • 1 enemy in BossRoom                                        │
│                                                                 │
│ [ Show Affected Objects ] [ Cancel ] [ Save & Hot-Reload ]     │
└─────────────────────────────────────────────────────────────────┘
```

**Only show this dialog if:**
- User is editing shared behavior
- Changes are significant (not just formatting/comments)
- Multiple instances exist

---

## Future Enhancements

### Phase 2: Visual Impact Preview
- Highlight affected sprites in viewport when hovering shared tab
- Show count badge on sprites using selected behavior
- "Show affected objects" button in warning dialog

### Phase 3: Diff View
- Show changes between shared class and instance overrides
- "This instance differs from default" indicator
- "Reset to default" button to remove overrides

### Phase 4: Behavior Inheritance
- Allow creating "FastEnemy" subclass of EnemyPatrol
- Show inheritance chain in tabs
- Override only specific methods

---

## Testing Checklist

- [ ] Instance tab always shows blue indicator
- [ ] Shared tabs always show yellow indicator + warning
- [ ] Star badge appears only when overrides detected
- [ ] "Edit This Object Only" button switches to instance tab
- [ ] Scope indicator updates on tab change
- [ ] Instance count accurate for shared behaviors
- [ ] Warning dialog shows affected objects correctly
- [ ] Hot-reload works after editing shared behavior
- [ ] Instance overrides preserved after hot-reload
- [ ] Tooltips explain scope clearly

---

*This design ensures users understand the impact of their code edits and prevents accidental changes to shared behavior classes.*
