As your game grows, managing state with individual variables can become messy. Scribe Engine is built to handle object-oriented Python, allowing you to organize your game's data into clean, reusable classes.

## The Default Player Object

When you start a project Scribe Engine provides a ready-to-use `player` object. You can add any properties you want to it on the fly.

```
:: start
{$
# Add custom attributes to the default player object
player.name = "Elara"
player.level = 1
player.location = "Tavern"
player.skills = {"magic": 5, "stealth": 3}
$}

Welcome, {{ player.name }}! You are level {{ player.level }}.
```

This is great for smaller projects, but for larger games, creating your own custom classes is more powerful. You can disable the default player object by disabling 'Use Default Player Object' in your project settings.

## Creating Custom Classes

For better organization, you can define your own classes in separate `.py` files in your project directory. Scribe Engine automatically loads these files, making your classes available everywhere.

### Simple Example: A Custom Player Class

1. In the IDE sidebar, click the **+** button next to **Game Logic (.py)** and create a file named `player_class.py`.
    
2. Add the following code to `player_class.py`:
    

```python
# player_class.py

class Player:
    def __init__(self, name="Adventurer"):
        self.name = name
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.inventory = []

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
```

### Using Your Custom Class

Scribe Engine looks for a class named `Player` and, if it finds one, automatically creates an instance of it for you, also named `player`.

```
:: start
{# The 'player' variable is now an instance of our custom Player class #}
{$ player.name = "Sir Gideon" $}
<h2>Welcome, {{ player.name }}</h2>

:: goblin_attack
You are attacked by a goblin!
{$ player.take_damage(15) $}
<p>You took 15 damage! Your health is now {{ player.health }}.</p>
```

### The Save System Requirement (Very Important!)

For Scribe Engine's save/load system to work correctly with your custom classes, it must be able to create an object from scratch. This means your class's `__init__()` constructor **must be callable with no required arguments**.

✅ Correct (Works with Save/Load):

All parameters have default values.

```python
class GoodPlayer:
    def __init__(self, name="Adventurer", level=1):
        self.name = name
        self.level = level
```

❌ Incorrect (Will Break Save/Load):

The name parameter is required and has no default value.

```python
class BadPlayer:
    def __init__(self, name):
        self.name = name
        self.level = 1
```

## Building More Complex Systems

You can create classes for anything in your game, such as items, enemies, quests, or locations.

### Example: An Item System

Create a new file `items.py`:

```Python
# items.py 

class Item: 
	# This class follows the rule: all params have defaults.
	def __init__(self, name="Unknown Item", description=""):
		self.name = name
		self.description = description
		
class Weapon(Item):
	# This class also follows the rule.
	def __init__(self, name="Default Weapon", description="", damage=5):
		super().__init__(name, description)
		self.damage = damage 
		
class Potion(Item): 
	# This class also follows the rule.
	def __init__(self, name="Default Potion", description="", heal_amount=20):
		super().__init__(name, description)
		self.heal_amount = heal_amount
```

### Using the Item System in a Passage

```
:: found_treasure
{$- 
# Create instances of our item classes 
broadsword = Weapon(name="Broadsword", description="A sturdy steel sword.", damage=15)
health_potion = Potion(name="Health Potion", description="Restores a small amount of health.")

# Add the new objects to the player's inventory
player.inventory.append(broadsword) player.inventory.append(health_potion)
-$} 

You open the chest and find a **{{ broadsword.name }}** and a **{{ health_potion.name }}**! 

<h2>Inventory</h2> 
<ul> 
{% for item in player.inventory %}
	<li><b>{{ item.name }}</b>: <i>{{ item.description }}</i>
	{% if item.damage is defined %}
		(Damage: {{ item.damage }})
	{% endif %}
	</li>
{% endfor %}
</ul>
```

This object-oriented approach keeps your story files clean and your game logic organized and reusable.

**Next:** With your game logic and state organized, it's time to make it look good. Continue to [**Theming and Styling**](6.-Theming-and-Styling).