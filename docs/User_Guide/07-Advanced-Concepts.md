This guide covers advanced Scribe Engine concepts for building large, robust, and optimized games, including architectural patterns and complex Python modules.

## Modular Architecture

For complex games, organizing your code into a clear structure is essential. Instead of putting all your Python classes in one file, consider a modular approach using directories. Scribe Engine will automatically discover and load all `.py` files within your project folder, including those in subdirectories.

### Recommended Directory Structure

```
MyGame/
├── systems/                 # Folder for core game systems
│   ├── combat.py           # Combat mechanics
│   ├── quests.py           # Quest management system
│   └── items.py            # Item, weapon, and armor classes
├── data/                    # Folder for game data (e.g., JSON files)
│   ├── items.json          # Item definitions
│   └── npcs.json           # NPC data
├── utils/                   # Folder for utility functions
│   └── text_formatter.py   # Text processing helpers
└── start.tgame
```

This pattern keeps your code organized, reusable, and easier to manage, especially in a team environment.

## Event Management System

An event system (also known as a publish-subscribe pattern) is a powerful architecture for decoupling your game's systems. Instead of systems calling each other directly, they can emit an event (e.g., "player_leveled_up") and other systems can subscribe to that event to react accordingly.

### Example: A Simple Event Manager

Create a file `utils/events.py`:

```
# utils/events.py

class EventManager:
    def __init__(self):
        # A dictionary where keys are event names
        # and values are lists of functions (callbacks)
        self.listeners = {}

    def subscribe(self, event_type, callback):
        """Register a function to listen for an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):
        """Trigger an event and notify all listeners."""
        if event_type in self.listeners:
            # Call each subscribed function with the event data
            for callback in self.listeners[event_type]:
                callback(data)

# Create a single, global instance to be used everywhere
events = EventManager()
```

### Using the Event Manager

Now, different parts of your game can communicate without being directly linked.

**In `systems/player.py`:**

```
# systems/player.py
from utils.events import events # Import the global instance

class Player:
    # ... (other player methods) ...
    def level_up(self):
        self.level += 1
        # Instead of directly calling other systems, just emit an event.
        events.emit("player_leveled_up", {"new_level": self.level})
```

**In `systems/ui.py`:**

```
# systems/ui.py
from utils.events import events

class UIManager:
    def __init__(self):
        # Subscribe the show_level_up_animation method to the event.
        events.subscribe("player_leveled_up", self.show_level_up_animation)

    def show_level_up_animation(self, data):
        # This method now runs automatically whenever the player levels up.
        print(f"DISPLAYING ANIMATION: Player reached level {data['new_level']}!")

# Create an instance so it starts listening
ui_manager = UIManager()
```

This makes your code much cleaner. Your `Player` class doesn't need to know anything about the `UIManager`; it just announces that it leveled up.

## Custom Serialization for Complex Data

While Scribe Engine's save system handles most standard Python objects, you might occasionally need to save data types that it doesn't understand (like `datetime` objects). You can handle this by providing custom `to_dict()` and `from_dict()` methods.

```
# In your custom class file
from datetime import datetime

class Character:
    def __init__(self):
        self.name = "Hero"
        self.created_at = datetime.now() # This object is not natively savable

    def to_dict(self):
        """Return a savable dictionary representation of the object."""
        return {
            "name": self.name,
            # Convert the datetime object to a standard ISO format string
            "created_at": self.created_at.isoformat(),
            # Special key to help the engine know what class this is
            "__class_name__": "Character"
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Character instance from a loaded dictionary."""
        instance = cls()
        instance.name = data.get("name")
        # Convert the string back into a datetime object
        instance.created_at = datetime.fromisoformat(data.get("created_at"))
        return instance
```

The engine will automatically detect and use these methods during the save/load process.

**Next:** This concludes the main learning path. The final document, [**CLI Development Workflow**](8.-CLI-Development-Workflow), is for advanced users who wish to work outside the IDE.