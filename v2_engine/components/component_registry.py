"""
Component Registry - Auto-discovery and metadata system for behaviors.

Provides centralized component registration, search, filtering, and metadata management.
"""

import os
import importlib
import inspect
from dataclasses import dataclass, field
from typing import Dict, List, Type, Optional
from enum import Enum


class ComponentCategory(Enum):
    """Component categories for organization and filtering."""
    PHYSICS = "Physics"
    RENDERING = "Rendering"
    GAMEPLAY = "Gameplay"
    AI = "AI"
    AUDIO = "Audio"
    INTERACTION = "Interaction"
    CUSTOM = "Custom"


@dataclass
class ComponentMetadata:
    """Metadata for a component class."""
    name: str
    class_ref: Type
    category: ComponentCategory
    description: str
    icon: str
    properties_info: Dict[str, str] = field(default_factory=dict)

    def matches_search(self, query: str) -> bool:
        """Check if component matches search query."""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.description.lower() or
            query_lower in self.category.value.lower()
        )


class ComponentRegistry:
    """
    Central registry for all component types.

    Auto-discovers components from engine and project directories,
    manages metadata, and provides search/filter functionality.
    """

    def __init__(self):
        self.components: Dict[str, ComponentMetadata] = {}
        self._initialized = False

    def initialize(self, project_path: Optional[str] = None):
        """
        Discover and register all available components.

        Args:
            project_path: Optional path to project for custom components
        """
        if self._initialized:
            return

        # Discover built-in engine components
        self._discover_engine_components()

        # Discover custom project components
        if project_path:
            self._discover_project_components(project_path)

        self._initialized = True

    def _discover_engine_components(self):
        """Discover components from v2_engine/components/ directory."""
        from v2_engine.components.component import Component

        # Import all component modules
        component_modules = [
            'rigidbody',
            'box_collider',
            'platformer_controller',
            'camera_follow',
            'scene_trigger',
            'spawn_point'
        ]

        for module_name in component_modules:
            try:
                module = importlib.import_module(f'v2_engine.components.{module_name}')

                # Find Component subclasses in module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Component) and obj != Component:
                        # Check if component has metadata
                        if hasattr(obj, 'METADATA'):
                            metadata_dict = obj.METADATA
                            self._register_component(
                                name,
                                obj,
                                metadata_dict.get('category', 'Custom'),
                                metadata_dict.get('description', ''),
                                metadata_dict.get('icon', '🔧'),
                                metadata_dict.get('properties_info', {})
                            )
                        else:
                            # Fallback for components without metadata
                            self._register_component(
                                name,
                                obj,
                                'Custom',
                                f'{name} component',
                                '🔧',
                                {}
                            )
            except Exception as e:
                print(f"[ComponentRegistry] Warning: Could not load component module '{module_name}': {e}")

    def _discover_project_components(self, project_path: str):
        """
        Discover custom components from project directory.

        Scans project/behaviors/ directory for Python files containing
        Component subclasses and registers them.

        Args:
            project_path: Path to game project
        """
        from v2_engine.components.component import Component
        import sys

        behaviors_dir = os.path.join(project_path, 'behaviors')

        if not os.path.exists(behaviors_dir):
            print(f"[ComponentRegistry] No behaviors directory found: {behaviors_dir}")
            return

        # Add behaviors directory to Python path if not already there
        if behaviors_dir not in sys.path:
            sys.path.insert(0, behaviors_dir)

        # Add project path to sys.path for imports
        if project_path not in sys.path:
            sys.path.insert(0, project_path)

        print(f"[ComponentRegistry] Scanning for custom behaviors in: {behaviors_dir}")

        # Scan for .py files in behaviors directory
        discovered_count = 0
        for filename in os.listdir(behaviors_dir):
            if not filename.endswith('.py') or filename.startswith('_'):
                continue

            module_name = filename[:-3]  # Remove .py extension

            try:
                # Import the module
                if f'behaviors.{module_name}' in sys.modules:
                    # Module already imported, reload it
                    module = importlib.reload(sys.modules[f'behaviors.{module_name}'])
                else:
                    module = importlib.import_module(f'behaviors.{module_name}')

                # Find all Component subclasses in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip if not a Component subclass or is Component itself
                    if not issubclass(obj, Component) or obj is Component:
                        continue

                    # Skip if defined in a different module (imported)
                    if obj.__module__ != f'behaviors.{module_name}':
                        continue

                    # Extract metadata
                    metadata = getattr(obj, '__metadata__', {})

                    category = metadata.get('category', 'Custom')
                    icon = metadata.get('icon', '⭐')
                    description = metadata.get('description', f'Custom behavior: {name}')
                    properties_info = metadata.get('properties_info', {})

                    # Register the component
                    self._register_component(
                        name=name,
                        class_ref=obj,
                        category=category,
                        description=description,
                        icon=icon,
                        properties_info=properties_info
                    )

                    discovered_count += 1
                    print(f"[ComponentRegistry] Discovered custom behavior: {name}")

            except Exception as e:
                print(f"[ComponentRegistry] Error loading behavior from {filename}: {e}")
                import traceback
                traceback.print_exc()

        print(f"[ComponentRegistry] Discovered {discovered_count} custom behavior(s)")

    def _register_component(
        self,
        name: str,
        class_ref: Type,
        category: str,
        description: str,
        icon: str,
        properties_info: Dict[str, str]
    ):
        """
        Register a component with metadata.

        Args:
            name: Component class name
            class_ref: Component class reference
            category: Category name (will be converted to enum)
            description: Short description
            icon: Unicode icon/emoji
            properties_info: Property hints for tooltips
        """
        # Convert category string to enum
        try:
            if isinstance(category, str):
                category_enum = ComponentCategory[category.upper()]
            else:
                category_enum = category
        except KeyError:
            category_enum = ComponentCategory.CUSTOM

        metadata = ComponentMetadata(
            name=name,
            class_ref=class_ref,
            category=category_enum,
            description=description,
            icon=icon,
            properties_info=properties_info
        )

        self.components[name] = metadata
        print(f"[ComponentRegistry] Registered: {name} ({category_enum.value})")

    def get_component(self, name: str) -> Optional[ComponentMetadata]:
        """Get component metadata by name."""
        return self.components.get(name)

    def get_all_components(self) -> List[ComponentMetadata]:
        """Get list of all registered components."""
        return list(self.components.values())

    def search_components(self, query: str) -> List[ComponentMetadata]:
        """
        Search components by name, description, or category.

        Args:
            query: Search string

        Returns:
            List of matching components
        """
        if not query:
            return self.get_all_components()

        return [
            comp for comp in self.components.values()
            if comp.matches_search(query)
        ]

    def filter_by_category(self, categories: List[ComponentCategory]) -> List[ComponentMetadata]:
        """
        Filter components by category.

        Args:
            categories: List of categories to include

        Returns:
            List of components in specified categories
        """
        if not categories:
            return self.get_all_components()

        return [
            comp for comp in self.components.values()
            if comp.category in categories
        ]

    def get_categories(self) -> List[ComponentCategory]:
        """Get list of all categories that have components."""
        categories = set()
        for comp in self.components.values():
            categories.add(comp.category)
        return sorted(list(categories), key=lambda c: c.value)

    def refresh_custom_behaviors(self, project_path: str):
        """
        Re-scan and reload custom behaviors from project.

        Removes existing custom behaviors and re-discovers them.
        Useful for hot-reload when behavior files change.

        Args:
            project_path: Path to game project
        """
        # Remove existing custom behaviors
        custom_components = [
            name for name, metadata in self.components.items()
            if metadata.category == ComponentCategory.CUSTOM
        ]

        for name in custom_components:
            del self.components[name]
            print(f"[ComponentRegistry] Removed custom behavior: {name}")

        # Re-discover custom behaviors
        self._discover_project_components(project_path)

        print(f"[ComponentRegistry] Custom behaviors refreshed")


# Global registry instance
_global_registry = ComponentRegistry()


def get_component_registry() -> ComponentRegistry:
    """Get the global component registry instance."""
    return _global_registry
