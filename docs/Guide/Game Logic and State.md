The **game state** is the heart of your PyVN game. It's a dynamic Python dictionary that holds all mutable data: player stats, inventory, quest progress, world events, and more. Your Python code manipulates this state, and your `.tgame` files read from it to display a dynamic story.

When a game is saved, the entire game state is stored. When loaded, it's restored, returning the game to its exact previous condition.

## The PyVN Global API

To make development simple and direct, PyVN automatically makes several objects and helper functions available globally in all your game's Python code (both in `.py` files and `{%- python %}` blocks). You **do not** need to import them.

### Directly Accessible Objects

These objects are always available for you to read from and write to.

- **`player`**: An object representing the player. If `use_default_player` is `true` in `project.json`, it comes with default attributes like `player.name`, `player.health`, `player.score`, `player.experience`, and `player.level`. You can add your own custom attributes at any time (e.g., `player.mana = 100`).
    
- **`flags`**: A dictionary for managing boolean (true/false) states. Perfect for tracking events that have occurred.
    
    ```
    flags['door_unlocked'] = True
    if flags['quest_completed']:
        debug("Quest is done!")
    ```
    
- **`variables`**: A dictionary for all other game data. It can hold strings, numbers, lists, dictionaries—any Python data structure.
    
    ```
    variables['day_count'] = 5
    variables['current_location'] = 'forest'
    variables['npcs'] = {'guard': {'health': 50}}
    ```
    
- **`project_path`**: A string containing the absolute path to your game project's root directory. Useful for loading external data files.
    
    ```
    import os
    data_file = os.path.join(project_path, 'data', 'items.json')
    ```
    
- **`passage_tags`**: A list of strings representing the tags assigned to the currently rendered passage. This allows you to implement logic based on the passage's tags.
    
    ```
    if 'dark' in passage_tags:
        debug("It's dark in here!")
    ```

- **`last_passage`**: A string containing the name of the last *non-menu* passage visited. This is automatically updated by the engine and is useful for creating "back" buttons or returning to the main game flow from a UI screen. See the `#menu` tag in the [Writing Your Story](link-to-writing-your-story-guide) guide for more details.

    ```
    [[Back to Game->{{ last_passage }}]]
    ```
    

### Helper Functions

These global functions simplify common game state manipulations.

- **`set_flag(name: str, value: bool = True)`**: Sets a flag's value. `set_flag('puzzle_solved')`
    
- **`get_flag(name: str, default: bool = False)`**: Retrieves a flag's value, returning a default if it doesn't exist. `if get_flag('puzzle_solved'): ...`
    
- **`set_variable(key: str, value: any)`**: Sets a variable in the **global game state**. This variable will persist across passages and be saved/loaded with the game. Supports dot notation for nested data. It creates intermediate dictionaries as needed. `set_variable('quest.main.status', 'started')`
    *   **Important Note on Variable Scope:**
        *   Use `set_variable()` (or `set_flag()`) for data that needs to persist throughout the game (e.g., player health, quest status, inventory). These are part of the `game_state`.
        *   For temporary variables used only within the current passage's rendering, use Jinja2's `{% set variable_name = value %}`. These variables are local to the passage and do not persist in the game state.
    
- **`get_variable(key: str, default: any = None)`**: Retrieves a variable using dot notation, returning a default if the path doesn't exist. `quest_status = get_variable('quest.main.status', 'not_started')`
    
- **`add_to_inventory(item: str, quantity: int = 1)`**: Adds an item to `player.inventory`. Updates quantity if the item exists. (Requires `use_default_inventory`). `add_to_inventory('gold_coin', 5)`
    
- **`remove_from_inventory(item: str, quantity: int = 1)`**: Removes an item from `player.inventory`. (Requires `use_default_inventory`). `remove_from_inventory('healing_potion')`
    
- **`has_item(item: str)`**: Checks if the player has an item. Returns `True` or `False`. (Requires `use_default_inventory`). `if has_item('key'): ...`
    
- **`get_item_count(item: str)`**: Returns the quantity of an item in the inventory. (Requires `use_default_inventory`). `num_potions = get_item_count('healing_potion')`
    
- **`debug(message: any)`**: Prints a message to the engine's console. `debug(f"Player health is now {player.health}")`
    
- **`now()`**: Returns the current `datetime` object.
    

### Custom Logic in Python Files

You can define your own functions in any `.py` file in your project. These functions automatically have access to the global API.

**Example `systems.py`:**

```
# systems.py
def decrease_health(amount):
    # 'player' and 'debug' are globally available
    player.health = max(0, player.health - amount)
    debug(f"Player health decreased to {player.health}")
```

You can then call this function from a `.tgame` file:

```
:: TrapRoom
You stepped on a trap!
{% do decrease_health(10) %}
Your health is now {{ player.health }}.
```

### Managing Game Data

For larger sets of static data (items, NPC stats, etc.), it's best to define them in a dedicated Python or JSON file, not in your story files. This keeps your data organized and easy to update.

#### Simple Example: Displaying NPC Data

Let's say you have a database of NPCs and want to display their details in a passage.

**1. Create the data file (`data/npcs.py`):**

```
# data/npcs.py
NPC_DB = {
    "guard_captain": {
        "name": "Captain Valerius",
        "title": "Captain of the City Guard",
        "stats": {
            "level": 15,
            "hp": 200
        }
    },
    "town_blacksmith": {
        "name": "Gregor",
        "title": "Blacksmith",
        "stats": {
            "level": 8,
            "hp": 120
        }
    }
}

def get_npc_details(npc_id):
    return NPC_DB.get(npc_id)
```

**2. Use the data in a passage (`.tgame` file):**

All functions from your `.py` files (like `get_npc_details`) are globally available in your passages. The ideal way to use this data is to call your function once, store its result in a local variable using `{% set %}`, and then access the variable's properties using dot notation. This approach is efficient and keeps your code clean.

```
:: TownSquare
You see a formidable figure by the gate.
{# 
  1. Call the function with the NPC's ID.
  2. Store the returned dictionary in a local variable called 'npc'.
#}
{% set npc = get_npc_details("guard_captain") %}

"Halt!" says {{ npc.name }}, the {{ npc.title }}.

{# 
  To access nested values, like 'level' inside 'stats',
  just chain the keys with a dot.
#}
You assess his strength and guess he must be around Level {{ npc.stats.level }}.
```

**Alternative for a Single Data Point**

If you only need to display a single piece of data, you can call the function directly inside the `{{ }}` brackets for a more compact syntax. However, this is less efficient if you need multiple values, as it calls the function repeatedly for each property.

```
:: TownSquare
You see a formidable figure by the gate.

"Halt!" says {{ get_npc_details("guard_captain").name }}.
```

#### Advanced Example: A Dynamic Inventory

This same pattern is powerful for more complex displays, like an inventory screen.

**1. Data file (`data/items.py`):**

```
# data/items.py
ITEM_DB = {
    "sword": {"name": "Iron Sword", "damage": 10, "desc": "A trusty, but basic, blade."},
    "potion": {"name": "Healing Potion", "heal": 25, "desc": "Restores a small amount of health."}
}

def get_item_details(item_id):
    return ITEM_DB.get(item_id)
```

**2. Logic file (`systems.py`):**

```
# systems.py
from data.items import get_item_details

def give_player_item(item_id):
    item_data = get_item_details(item_id)
    if item_data:
        # Add the item ID to the inventory. We'll fetch details on demand.
        add_to_inventory(item_id, 1)
```

**3. Passage file (`inventory.tgame`):**

```
:: InventoryScreen
# Your Inventory

{% if not player.inventory %}
  <p>Your inventory is empty.</p>
{% else %}
  <table>
    <tr>
      <th>Item</th>
      <th>Quantity</th>
      <th>Description</th>
    </tr>
    {% for item in player.inventory %}
      {# Here, item.name holds the ID like "sword" or "potion" #}
      {% set details = get_item_details(item.name) %}
      <tr>
        <td>{{ details.name }}</td>
        <td>{{ item.quantity }}</td>
        <td>{{ details.desc }}</td>
      </tr>
    {% endfor %}
  </table>
{% endif %}

[[Back to Game->LastPassage]]
```