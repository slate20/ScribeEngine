PyVN stories are written in `.tgame` files, which are plain text files using a simple markup language combined with the powerful Jinja2 templating engine.

### Passages

A story is divided into **passages**. Each passage is a distinct screen or section of your narrative, starting with `::` followed by the passage name.

```
:: Start
Welcome to my first PyVN game! This is the starting passage.

:: ForestPath
You are on a path in a dark forest. It's spooky here.
```

### Links

Create links between passages using double square brackets `[[Link Text->PassageName]]`.

```
:: Start
Welcome! Where would you like to go?
[[To the forest->ForestPath]]

:: ForestPath
You are on the forest path.
[[Go back->Start]]
```

### Special Passages

PyVN reserves three passage names for special functions:

- `:: NavMenu`: Content here is rendered as a persistent navigation menu. Ideal for global links like Inventory, Stats, or Save/Load.
    
- `:: PrePassage`: Content here is rendered _before_ every other passage. Useful for a persistent HUD or status display.
    
- `:: PostPassage`: Content here is rendered _after_ every other passage. Useful for footers.
    

### Text Formatting & HTML

You can use basic formatting syntax or embed raw HTML directly in your passages for full control over presentation.

- **Bold:** `**bold text**` or `<b>bold text</b>`
    
- **Italics:** `*italic text*` or `<i>italic text</i>`
    
- **Underline:** `<u>underline text</u>`
    
- **Line Breaks:** Use a blank line for a paragraph break, or `<br>` for a single line break.
    

**HTML Example:**

```
:: MyCustomPassage
<h1>Chapter 1</h1>
<p style="color: blue;">This is custom-styled text.</p>
<img src="/game/assets/my_image.png" alt="A beautiful scene">
```

### Dynamic Content with Jinja2

PyVN uses Jinja2 to render passages, allowing you to display variables and use logic based on the game's state.

- **Displaying Variables:** Use `{{ }}` to show data from the game state.
    
    ```
    :: Welcome
    Hello, {{ player.name }}! You have {{ player.health }} HP.
    ```
    
- **Conditional Logic:** Use `{% if %}` blocks to show content conditionally.
    
    ```
    :: CheckItem
    {% if has_item('key') %}
    You use the key to unlock the door.
    {% else %}
    The door is locked. You need a key.
    {% endif %}
    ```
    
- **Loops:** Use `{% for %}` to iterate over lists, like an inventory.
    
    ```
    :: Inventory
    Your items:
    <ul>
    {% for item in player.inventory %}
      <li>{{ item.name }} ({{ item.quantity }})</li>
    {% endfor %}
    </ul>
    ```
    

> **Note:** Variables like `player` and functions like `has_item()` are part of the game state and logic system. See the [**Game Logic and State**](https://www.google.com/search?q=./04_Game_Logic_and_State.md "null") guide for a full reference.

### Python Code Blocks

For more complex logic directly within a passage, you can embed Python code using `{%- python %}` blocks. This code is executed when the passage is rendered and has access to the full game state.

```
:: DarkCave
You enter a dark cave. A chill runs down your spine.

{%- python %}
# This code runs when the player enters the DarkCave passage
import random
if random.randint(1, 10) > 7:
    set_flag('found_torch', True)
    add_to_inventory('torch', 1)
    debug("Player found a torch!")
{%- endpython %}

{% if get_flag('found_torch') %}
  <p class="success-text">You spot something glimmering and find a torch!</p>
{% endif %}
```