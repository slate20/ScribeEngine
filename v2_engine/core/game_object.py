"""
Base GameObject class for Scribe Engine V2.

All game entities inherit from this base class.
"""


class GameObject:
    """
    Base class for all game entities (SpriteObject and LogicObject).

    GameObjects have:
    - Component attachment system
    - Update lifecycle
    - Active state
    - Persistence across scenes
    - Unique entity ID
    """

    def __init__(self):
        """Initialize base game object."""
        # Components
        self.components = {}  # component_type -> component instance

        # Lifecycle
        self.active = True

        # Persistence (for GameState system)
        self.is_persistent = False  # Survives scene transitions
        self.entity_id = None  # Unique ID for persistent entities

        # Name (for editor and debugging)
        self.name = ""

    def add_component(self, component: 'Component'):
        """
        Add a behavior component to this object.

        Args:
            component: Component instance
        """
        component_type = type(component)
        self.components[component_type] = component

    def get_component(self, component_type: type) -> 'Component':
        """
        Get component by type.

        Args:
            component_type: Type of component to retrieve

        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_type)

    def has_component(self, component_type: type) -> bool:
        """
        Check if object has a component of given type.

        Args:
            component_type: Type of component to check

        Returns:
            True if component exists
        """
        return component_type in self.components

    def remove_component(self, component_type: type):
        """
        Remove component by type.

        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            component = self.components[component_type]
            component.on_destroy()
            del self.components[component_type]

    def update(self, dt: float):
        """
        Update object and all components.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        # Update all components
        for component in self.components.values():
            if component.enabled:
                component.update(dt)

    def destroy(self):
        """Destroy object and cleanup components."""
        for component in list(self.components.values()):
            component.on_destroy()
        self.components.clear()
        self.active = False
