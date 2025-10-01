Scribe Engine's real power comes from its two-stage processing system. For every passage, the engine first executes all Python code, then it renders the output using the Jinja2 templating language. Understanding this separation is key to creating dynamic games.

**Execution Order:**

1. **Python First**: All Python blocks (`{$...$}` and `{$-...-$}`) are executed to calculate game logic and set variable states.
    
2. **Jinja2 Second**: The passage text and Jinja2 blocks (`{{...}}` and `{%...%}`) are rendered to display the final content to the player.
    

## Executing Python Code

You can embed Python code directly into your passages to handle game logic, manage variables, and create dynamic events.

### Inline Python: `{$ ... $}`

Use this for single statements and simple assignments. It's clean and easy to read.

```python
:: forest_encounter
You defeat the goblin!
{$ player.experience += 10 $}
{$ player.gold += 5 $}
{$ goblins_defeated += 1 $}
```

### Multi-line Python: `{$- ... -$}`

Use this for more complex logic, such as calculations, function definitions, or importing modules.

```python
:: combat_turn
{$-
import random

damage = player.get_attack_power()
modifier = random.uniform(0.8, 1.2) # Add some randomness
final_damage = int(damage * modifier)
enemy.health -= final_damage
-$}
```

### Global Scope

Variables created or modified in one passage persist and are available in all subsequent passages. You can initialize your main game variables in your `:: start` passage.

```python
:: start
{$-
# Initialize all game variables here
player.health = 100
player.gold = 50
player.inventory = ["Rusty Sword", "Bread"]
player.location = "Village Square"

goblins_defeated = 0

initialized = True
-$}
```

### Variable Management

Scribe Engine provides a special `delete_var()` function for cleaning up temporary variables to prevent your game state from becoming cluttered.

```python
:: process_transaction
{$-
# Create temporary variables for calculation
temp_price = item.base_price * (1 + tax_rate)
temp_discount = calculate_discount(player.loyalty_level)
final_price = temp_price - temp_discount

# Apply the transaction
player.gold -= final_price
player.inventory.append(item.name)

# Clean up temporary variables
delete_var('temp_price')
delete_var('temp_discount')
delete_var('final_price')
-$}
```

**When to use `delete_var()`:**
- After calculations that create temporary variables
- When passing data between action buttons and target passages
- To prevent debug displays from showing internal variables
- To keep your game state clean and organized

**Note:** The `delete_var()` function safely removes variables from both the current execution scope and the persistent game state. If the variable doesn't exist, it silently does nothing (no error is thrown).

## Rendering with Jinja2

After all Python code has been executed, the engine uses Jinja2 to display content.

### Displaying Variables: `{{ ... }}`

This is the most common Jinja2 syntax. It prints the final value of a variable.

```jinja2
<div class="status-bar">
    <span>Health: {{ player.health }}</span>
    <span>Gold: {{ player.gold }}</span>
</div>
```

### Conditional Content: `{% if ... %}`

You can show or hide entire blocks of text, links, or HTML based on the state of your variables.

```jinja2
{% if player.health < 25 %}
    <p class="warning"><b>You are badly wounded!</b></p>
{% endif %}

{% if "Magic Key" in player.inventory %}
    [[Use the Magic Key to unlock the ancient door->ancient_treasure_room]]
{% else %}
    <p>The ancient door is sealed by a powerful magic you cannot break.</p>
{% endif %}
```

You can also use `{% elif ... %}` and `{% else %}` for more complex conditions.

### Loops: `{% for ... %}`

Loops are perfect for displaying lists, like the items in a player's inventory or the goods in a shop.

```jinja2
:: shop_inventory
<h2>Merchant's Wares</h2>
<ul>
{% for item in shop_items %}
    <li>{{ item.name }} - {{ item.price }} gold</li>
{% endfor %}
</ul>
```

## When to Use Python vs. Custom `.py` Files

- **In-Passage Python** is excellent for passage-specific logic, prototyping ideas quickly, and simple state changes.
    
- **Custom `.py` Files** are better for complex, reusable systems that you want to use across many passages, such as a combat calculator, an inventory manager, or a quest system.
    

Scribe Engine **automatically discovers and loads all `.py` files** in your project folder. Any functions or classes you define in them are globally available in any passage without needing to be imported.

**Next:** You can now create dynamic logic. Let's learn how to organize your game's data cleanly. Continue to [**State Management and Classes**](5.-State-Management-and-Classes).