This guide covers how to customize the visual appearance of your games using CSS.

## How Styling Works

Scribe Engine renders your game as a web page. This means you can use standard CSS to control every visual aspect, from colors and fonts to layout and animations.

There are two main ways to style your game:

1. **Override CSS Variables (Easy)**: The default theme is built with CSS variables for key properties like colors and fonts. Overriding these is the fastest way to create a new look.
    
2. **Write Custom CSS (Advanced)**: For full control, you can write your own CSS rules to target specific elements of the game's interface.
    

## Getting Started with `game_theme.css`

When you create a new project, Scribe Engine generates a `game_theme.css` file with a complete starter theme. This file includes all the CSS variables you can customize and comes pre-loaded with an attractive earthy/fantasy theme.

1. In the IDE sidebar, go to the **Files** tab.

2. Under the **Styling (.css)** section, click on `game_theme.css` to open it.

## Default Theme

Your `game_theme.css` file comes with a complete earthy/fantasy theme that includes:

- **Earthy color palette**: Forest greens, warm golds, and cream backgrounds
- **Professional typography**: Lora serif for body text and Montserrat sans-serif for headings
- **Styled interface elements**: Enhanced nav links, choice buttons, and action buttons
- **All CSS variables**: Complete set of customizable properties with descriptive comments

You can use this theme as-is or customize it by modifying the CSS variables and styles.

## Method 1: Overriding CSS Variables (Recommended)

This is the easiest way to create a new theme. Your `game_theme.css` file already contains a `:root` block with all available CSS variables. Simply modify the values you want to change.

### Example: A Dark "Cyberpunk" Theme

```css
/* Modify the :root section in your game_theme.css file */
:root {
    /* Main Colors */
    --primary-color: #00ffff;        /* Bright Cyan */
    --background-color: #0a0a0a;     /* Near Black */
    --content-bg: #1a1a1a;          /* Dark Gray */
    --text-color: #e0e0e0;          /* Light Gray Text */
    --link-color: #ff00ff;          /* Magenta */

    /* Typography */
    --font-family-body: 'Courier New', monospace;
    --font-family-heading: 'Verdana', sans-serif;
}
```

### Key CSS Variables to Override

|   |   |
|---|---|
|**Variable**|**Default Usage**|
|`--primary-color`|Main accent color, button hovers.|
|`--secondary-color`|Secondary accent color for interactive elements.|
|`--background-color`|The background of the entire game page.|
|`--content-bg`|The background of the main story content area.|
|`--text-color`|The main color for paragraphs and body text.|
|`--link-color`|The color of passage links.|
|`--nav-bg`|Background color of the navigation sidebar.|
|`--button-bg`|Background color for buttons and interactive elements.|
|`--border-color`|Color for borders and horizontal lines (`<hr>`).|
|`--error-bg` / `--error-text`|Colors for error messages and backgrounds.|
|`--success-text`|Color for success messages.|
|`--info-text`|Color for informational messages.|
|`--font-family-body`|The font for the main story text.|
|`--font-family-heading`|The font for headings (`<h1>`, `<h2>`, etc.).|

## Method 2: Advanced Custom CSS

You can target specific elements of the game's UI for more detailed styling. The Live Preview in the IDE is a great way to inspect elements and test styles.

### Example: Styling Links as Buttons

By default, links are simple text. You can make them look like clickable buttons with a few CSS rules.

```css
/* Add this to the bottom of your game_theme.css file */

/* Target all passage links, which have the class .passage-link */
.passage-link {
    display: block;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid var(--border-color);
    background-color: var(--content-bg);
    color: var(--link-color);
    text-align: center;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.2s, color 0.2s;
}

/* Add a hover effect */
.passage-link:hover {
    background-color: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}
```

### Using Custom Fonts

You can import web fonts (like Google Fonts) at the top of your `game_theme.css` file and then use them in your theme.

```css
/* Add this at the top of your game_theme.css file */
@import url('[https://fonts.googleapis.com/css2?family=MedievalSharp&display=swap](https://fonts.googleapis.com/css2?family=MedievalSharp&display=swap)');

:root {
    --font-family-heading: 'MedievalSharp', cursive;
}

h1, h2, h3 {
    font-family: var(--font-family-heading);
}
```

## Save/Load Modal Styling

The save and load screens are also fully stylable. They use the same CSS variables as the main game, but also have their own specific variables you can override for more granular control.

### Key Modal CSS Variables

|   |   |
|---|---|
|**Variable**|**Usage**|
|`--save-slot-bg`|Background of an individual save slot.|
|`--save-slot-border`|Border of a save slot.|
|`--save-slot-hover`|Background of a slot when hovered.|
|`--save-slot-selected`|Accent color for the currently selected slot.|

## Upgrading from custom.css

If you have an existing project that uses `custom.css`, you should rename it to `game_theme.css` to ensure proper loading. The legacy `custom.css` may not load correctly in all situations.

**To upgrade:**
1. **Rename** your existing `custom.css` file to `game_theme.css`
2. Your existing styles will continue to work
3. You can now add the new CSS variables and enhanced default styles to your theme
4. Consider merging your styles with the new default theme for the best experience

**Next:** You've learned how to build and style your game. Let's look at more advanced features. Continue to [**Advanced Concepts**](7.-Advanced-Concepts).