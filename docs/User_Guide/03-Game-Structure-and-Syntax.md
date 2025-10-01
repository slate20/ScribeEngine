This guide covers the `.tgame` file format, passage structure, and all the syntax elements you'll use to build your game in Scribe Engine.

## The `.tgame` File Format

Scribe Engine uses plain text `.tgame` files to create your game. These files are a blend of five key components:

- **Passages**: Discrete sections of your game.
    
- **HTML**: For rich text formatting, layout, and media.
    
- **Links**: For navigation between passages.
    
- **Python code**: For game logic and state changes.
    
- **Jinja2 templates**: For displaying dynamic content.
    

## Passages: The Building Blocks of Your Story

### Defining Passages

A passage is a single screen or moment in your game. You define one using two colons `::` followed by a unique name.

```
:: start
This is the content of the starting passage.

:: forest_path
This is the content of another passage.

```

**Rules for passage names:**

- Must be unique across your entire project.
    
- Can contain letters, numbers, and underscores.
    
- **Should NOT contain spaces.** (technically can still work, but could potentially cause issues later)
    
- Are case-sensitive (`forest_path` is different from `Forest_Path`).
    

## Using Assets (Images & Audio)

You can bring your game to life by including images and audio.

### The `assets` Directory

All of your media files should be placed in the `assets` folder within your project directory. You can create subdirectories inside `assets` to keep things organized (e.g., `assets/images`, `assets/sounds`).

### Referencing Assets in a Passage

To use an asset, you reference it using a special path that starts with `game/assets/`. You use standard HTML tags to display them.

#### Images

Use the `<img>` tag to display an image.

```html
:: village_square
You arrive at the bustling village square.
<img src="game/assets/images/village_market.png" alt="A busy marketplace" width="400">
```

#### Audio

Use the `<audio>` tag to embed sound. The `controls` attribute will show the browser's default play/pause buttons, and `autoplay` will make it play automatically.

```html
:: spooky_cave
A chilling wind howls through the cave entrance.
<audio src="game/assets/sounds/cave_wind.mp3" controls autoplay></audio>
```



## Link Syntax: Navigation and Actions

Links are the primary way players interact with your game.

### Basic Links

The standard format is `[[Link Text->target_passage]]`.

```
The path splits in two. A sign points in each direction.
[[Go to the village->village_gate]]
[[Head into the forest->forest_path]]

```

If the link text is the same as the target passage name, you can use a shortcut: `[[cave_entrance]]`.

### Link Actions

You can execute a short piece of Python code when a link is clicked by adding `||` followed by an inline Python block. This is perfect for simple state changes that don't require a lot of logic.

```html
:: treasure_chest
You see a wooden chest. A shiny gold coin rests on top.
<img src="assets/images/chest.png" alt="A treasure chest" width="200">

[[Pick up the coin->continue_exploring||{$ player.gold += 1 $}]]
[[Leave it be->continue_exploring]]

```

In this example, the player's gold will increase by 1 _only_ if they click the "Pick up the coin" link.

### Action Buttons

Action buttons use the `<<...>>` syntax and can work in two ways:

1. **Stay on current passage** (no target specified): Execute code and reload the current passage
2. **Navigate to target passage**: Execute code, then go to the specified passage

#### Example 1: Stay on Current Passage

Perfect for interactive elements where you want to update the display without changing location:

```
:: village_shop
<h2>Village Shop</h2>
<p>Your Gold: {{ player.gold }}</p>

{% for item in shop_items %}
    <div>
        <strong>{{ item.name }}</strong> - {{ item.price }} gold
        <p>{{ item.description }}</p>
        <<Buy||{$
            if player.gold >= item.price:
                player.gold -= item.price
                player.inventory.append(item.name)
                shop_items.remove(item)
                purchase_message = f"You bought {item.name}!"
            else:
                purchase_message = "Not enough gold!"
        $}>>
    </div>
{% endfor %}

{% if purchase_message %}
    <p><em>{{ purchase_message }}</em></p>
{% endif %}
```

In this example, clicking "Buy" executes the purchase logic and reloads the same passage, showing the updated gold, inventory, and shop items.

#### Example 2: Navigate to Target Passage

Useful when you need to process data from loops and then move to a different passage:

```
:: item_selection
<h2>Choose Your Reward</h2>
{% for item in available_rewards %}
    <div>
        <strong>{{ item.name }}</strong>
        <p>{{ item.description }}</p>
        <<Choose This->process_reward||{$ chosen_item = item $}>>
    </div>
{% endfor %}

:: process_reward
{$-
# The chosen_item variable contains the selected item
player.inventory.append(chosen_item.name)
reward_message = f"You received {chosen_item.name}!"

# Clean up the temporary variable
delete_var('chosen_item')
-$}

<p>{{ reward_message }}</p>
[[Continue your adventure->next_area||{$ delete_var('reward_message') $}]]
```

**Key differences between all interaction types:**

- **Navigation Links** `[[Text->passage]]`: Navigate to a different passage
- **Action Links** `[[Text->passage||{$ code $}]]`: Execute code, then navigate
- **Action Buttons (reload)** `<<Text||{$ code $}>>`: Execute code, then reload current passage
- **Action Buttons (navigate)** `<<Text->passage||{$ code $}>>`: Execute code, then navigate to passage

**When to use action buttons:**
- **Reload current passage**: Shopping systems, inventory management, stat adjustments
- **Navigate to target**: Processing loop data, complex workflows, confirmation screens

## Getting Player Input

To make your game more interactive, you can ask the player for input, such as their name or a password.

### The `input_field()` Function

You can render a text box and a submit button using the `input_field()` function directly within your passage content.

```jinja2
What is your name, adventurer?

{{ input_field('player_name') }}
```

When the player types into this box and clicks "Submit", the value they entered will be stored in the `player_name` variable.

### Customizing the Input Field

The function has several optional parameters to customize its behavior:

`{{ input_field(variable_name, input_type='text', placeholder='', button_text='Submit', next_passage=None) }}`

- **`variable_name`** (Required): The name of the variable where the player's input will be stored (e.g., `'player.name'`).
    
- **`input_type`**: The type of input field. Defaults to `'text'`, but you can use other HTML input types like `'password'` or `'number'`.
    
- **`placeholder`**: Faint text that appears in the input box before the user types anything.
    
- **`button_text`**: The text displayed on the submit button. Defaults to "Submit".
    
- **`next_passage`**: If provided, the game will automatically navigate to this passage after the player clicks the submit button.
    

### Example: Character Creation

Here's how you could use a customized input field to start your game.

```jinja2
:: character_creation
<h2>Character Creation</h2>
<p>Please enter your name to begin your journey.</p>

{{ input_field('player.name', placeholder='e.g., Elara', button_text='Begin Adventure', next_passage='start_adventure') }}

:: start_adventure
{$
# The player.name variable now holds the value the user entered
$}
<h1>Welcome, {{ player.name }}!</h1>
<p>Your story is about to begin...</p>

[[Continue->town_square]]
```


## Special Passage Tags

You can add tags to a passage on the same line as its definition using a `#`. Tags can be used for your own organization or for special engine functionality.

```
:: inventory_screen #ui #menu

```

Scribe Engine recognizes two special tags with built-in functionality:

### The `#silent` Tag

A passage tagged `#silent` will execute its Python code without rendering any output to the screen. This is perfect for "logic-only" passages that perform calculations or determine the next event behind the scenes.

**Important**: A `#silent` passage **must** contain a link that directs the engine to the next visible passage. This can be conditional as well:

```
:: check_for_ambush #silent
{$-
# This code runs silently to determine the next event
import random
ambushed = random.random() < 0.5 # 50% chance of ambush
-$}

{# The engine will automatically follow one of these links #}
{% if ambushed %}
    [[->forest_ambush]]
{% else %}
    [[->forest_path_clear]]
{% endif %}

```

### The `#menu` Tag

The `#menu` tag marks a passage as a UI screen (like an inventory or map) and tells the engine **not** to update its internal `last_passage` variable. This is essential for making "Back" buttons work correctly. It ensures the player returns to the last _story_ passage, not the menu they just viewed.

```
:: inventory_screen #menu
<h1>Inventory</h1>
<ul>
{% for item in player.inventory %}
    <li>{{ item.name }}</li>
{% endfor %}
</ul>

{# This link correctly returns the player to where they were #}
[[Back->{{ last_passage }}]]

```

## Special UI Passages

Scribe Engine reserves three specific passage names for built-in UI functionality.

- `::NavMenu`: Any links placed in this passage are automatically added to your game's main navigation bar. This is perfect for links to inventory, maps, or quest logs.
    
- `::PrePassage`: The content of this passage is rendered _above_ every single passage in your game. It's the ideal place to create a persistent Heads-Up Display (HUD).
    
- `::PostPassage`: The content of this passage is rendered _below_ every passage, useful for footers or persistent action bars.
    

```
::NavMenu
[[Inventory->inventory_screen]]
[[Map->map_screen]]

::PrePassage
<div class="hud">
    <span>HP: <b>{{ player.health }}</b></span> | <span>Location: <i>{{ player.location }}</i></span>
</div>
<hr>

::PostPassage
<hr>
<div class="footer">
    <span>Gold: {{ player.gold }}</span>
</div>

```

**Next:** Now you know how to structure your game. Let's explore how to bring it to life with logic. Continue to [**Python and Templates**](4.-Python-and-Templates).