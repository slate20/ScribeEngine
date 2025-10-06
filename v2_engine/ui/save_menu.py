"""
Pygame-based Save/Load Menu for Scribe Engine V2.

In-game save/load interface using Pygame UI components.
"""

import pygame
from datetime import datetime
from v2_engine.ui.panel import Panel
from v2_engine.ui.button import Button
from v2_engine.ui.text import TextLabel
from v2_engine.ui.widget import Widget


class SaveSlotButton(Widget):
    """Button representing a save slot with metadata display."""

    def __init__(self, x: float, y: float, width: float, height: float, slot_number: int, metadata: dict = None):
        super().__init__(x, y, width, height)

        self.slot_number = slot_number
        self.metadata = metadata or {}
        self.is_hovered = False
        self.is_pressed = False
        self.is_selected = False

        # Colors
        self.empty_color = (50, 50, 50)
        self.filled_color = (60, 70, 80)
        self.hover_color = (80, 90, 100)
        self.selected_color = (70, 120, 150)
        self.border_color = (100, 150, 200) if metadata else (80, 80, 80)
        self.selected_border_color = (150, 200, 255)
        self.text_color = (220, 220, 220)
        self.meta_color = (150, 150, 150)

        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.desc_font = pygame.font.Font(None, 20)
        self.meta_font = pygame.font.Font(None, 16)

    def handle_event(self, event):
        """Handle mouse events."""
        if not self.enabled or not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.contains_point(event.pos[0], event.pos[1])

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos[0], event.pos[1]):
                # Debug output removed for cleaner experience
                self.is_pressed = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            if self.is_pressed and self.contains_point(event.pos[0], event.pos[1]):
                if self.on_click:
                    self.on_click()
                self.is_pressed = False
                return True
            elif was_pressed:
                # Mouse was pressed but released outside - still reset state
                self.is_pressed = False

        return False

    def render(self, screen):
        """Render save slot button."""
        if not self.visible:
            return

        rect = self.get_rect()

        # Background
        if self.is_selected:
            bg_color = self.selected_color
        elif self.is_pressed:
            bg_color = (40, 50, 60)
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.filled_color if self.metadata else self.empty_color

        # Border color based on selection
        border_color = self.selected_border_color if self.is_selected else self.border_color
        border_width = 3 if self.is_selected else 2

        pygame.draw.rect(screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)

        # Slot number
        title_text = f"Slot {self.slot_number + 1}"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        screen.blit(title_surface, (rect.x + 10, rect.y + 10))

        if self.metadata:
            # Description
            desc = self.metadata.get('description', 'No description')
            if len(desc) > 40:
                desc = desc[:37] + "..."
            desc_surface = self.desc_font.render(desc, True, self.text_color)
            screen.blit(desc_surface, (rect.x + 10, rect.y + 45))

            # Scene name
            scene = self.metadata.get('scene_name', 'Unknown')
            scene_text = f"Scene: {scene}"
            scene_surface = self.meta_font.render(scene_text, True, self.meta_color)
            screen.blit(scene_surface, (rect.x + 10, rect.y + 70))

            # Timestamp
            timestamp = self.metadata.get('timestamp', '')
            if timestamp:
                time_str = self._format_timestamp(timestamp)
                time_surface = self.meta_font.render(time_str, True, self.meta_color)
                screen.blit(time_surface, (rect.x + 10, rect.y + 90))
        else:
            # Empty slot
            empty_text = "Empty Slot"
            empty_surface = self.desc_font.render(empty_text, True, (100, 100, 100))
            text_rect = empty_surface.get_rect(center=(rect.centerx, rect.centery + 10))
            screen.blit(empty_surface, text_rect)

    def _format_timestamp(self, timestamp_str):
        """Format timestamp as relative time."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            delta = now - timestamp

            if delta.days > 0:
                return f"{delta.days}d ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            else:
                return "Just now"
        except:
            return timestamp_str


class SaveMenu:
    """In-game save menu overlay."""

    def __init__(self, game, mode='save'):
        """
        Initialize save menu.

        Args:
            game: Game instance
            mode: 'save' or 'load'
        """
        self.game = game
        self.mode = mode
        self.active = False

        # Get screen dimensions
        screen = pygame.display.get_surface()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Menu dimensions
        self.menu_width = min(900, self.screen_width - 100)
        self.menu_height = min(700, self.screen_height - 100)
        self.menu_x = (self.screen_width - self.menu_width) // 2
        self.menu_y = (self.screen_height - self.menu_height) // 2

        # UI elements
        self.panel = None
        self.slot_buttons = []
        self.description_input = None
        self.action_buttons = []
        self.selected_slot = None

        self.build_ui()

    def build_ui(self):
        """Build menu UI elements."""
        from v2_engine.core.game_state import get_game_state

        # Main panel
        self.panel = Panel(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        self.panel.bg_color = (30, 30, 30, 240)
        self.panel.border_color = (100, 150, 200)

        # Title
        title_text = "Save Game" if self.mode == 'save' else "Load Game"
        title = TextLabel(
            self.menu_x + self.menu_width // 2,
            self.menu_y + 30,
            title_text,
            font_size=36
        )
        title.align = 'center'
        title.text_color = (100, 150, 200)
        self.panel.add_widget(title)

        # Save slots (3x2 grid)
        game_state = get_game_state()
        slot_width = (self.menu_width - 60) // 2
        slot_height = 120

        for i in range(6):
            row = i // 2
            col = i % 2

            x = self.menu_x + 20 + col * (slot_width + 20)
            y = self.menu_y + 80 + row * (slot_height + 15)

            metadata = game_state.get_save_metadata(i, self.game.project_path)

            slot_btn = SaveSlotButton(x, y, slot_width, slot_height, i, metadata)
            slot_btn.on_click = lambda slot=i: self.select_slot(slot)
            self.slot_buttons.append(slot_btn)
            self.panel.add_widget(slot_btn)

        # Action buttons at bottom
        button_y = self.menu_y + self.menu_height - 60

        if self.mode == 'save':
            # Save button (initially disabled)
            save_btn = Button(
                self.menu_x + self.menu_width - 120,
                button_y,
                100, 40,
                "Save",
                font_size=20
            )
            save_btn.enabled = False
            save_btn.on_click = self.perform_save
            self.action_buttons.append(save_btn)
            self.panel.add_widget(save_btn)
        else:
            # Load button (initially disabled)
            load_btn = Button(
                self.menu_x + self.menu_width - 240,
                button_y,
                100, 40,
                "Load",
                font_size=20
            )
            load_btn.enabled = False
            load_btn.on_click = self.perform_load
            self.action_buttons.append(load_btn)
            self.panel.add_widget(load_btn)

            # Delete button (initially disabled)
            delete_btn = Button(
                self.menu_x + self.menu_width - 130,
                button_y,
                100, 40,
                "Delete",
                font_size=20
            )
            delete_btn.enabled = False
            delete_btn.on_click = self.delete_slot
            self.action_buttons.append(delete_btn)
            self.panel.add_widget(delete_btn)

        # Cancel button
        cancel_btn = Button(
            self.menu_x + 20,
            button_y,
            100, 40,
            "Cancel",
            font_size=20
        )
        cancel_btn.on_click = self.close
        self.panel.add_widget(cancel_btn)

    def refresh_slots(self):
        """Refresh save slot metadata (call when menu opens)."""
        from v2_engine.core.game_state import get_game_state
        game_state = get_game_state()

        for i, slot_btn in enumerate(self.slot_buttons):
            metadata = game_state.get_save_metadata(i, self.game.project_path)
            slot_btn.metadata = metadata or {}
            # Update border color based on whether slot has data
            slot_btn.border_color = (100, 150, 200) if metadata else (80, 80, 80)

    def select_slot(self, slot_number):
        """Handle slot selection."""
        from v2_engine.core.game_state import get_game_state

        msg = f"[SaveMenu] Slot {slot_number + 1} selected"
        print(msg)
        if hasattr(self.game, 'debug_overlay') and self.game.debug_overlay:
            self.game.debug_overlay.add_console_line(msg)

        # Deselect all slots first
        for slot_btn in self.slot_buttons:
            slot_btn.is_selected = False

        # Select the clicked slot
        self.selected_slot = slot_number
        self.slot_buttons[slot_number].is_selected = True

        game_state = get_game_state()
        metadata = game_state.get_save_metadata(slot_number, self.game.project_path)

        if self.mode == 'save':
            # Enable save button
            for btn in self.action_buttons:
                btn.enabled = True
                msg = "[SaveMenu] Enabled save button"
                print(msg)
                if hasattr(self.game, 'debug_overlay') and self.game.debug_overlay:
                    self.game.debug_overlay.add_console_line(msg)
        else:
            # Enable load/delete only if slot has data
            for btn in self.action_buttons:
                btn.enabled = bool(metadata)
                msg = f"[SaveMenu] {'Enabled' if metadata else 'Disabled'} load/delete buttons"
                print(msg)
                if hasattr(self.game, 'debug_overlay') and self.game.debug_overlay:
                    self.game.debug_overlay.add_console_line(msg)

    def perform_save(self):
        """Save game to selected slot."""
        print(f"[SaveMenu] perform_save called, selected_slot={self.selected_slot}")

        if self.selected_slot is None:
            print(f"[SaveMenu] No slot selected, aborting save")
            return

        try:
            from v2_engine.core.game_state import get_game_state

            # Get description (for now, use scene name - can add input later)
            game_state = get_game_state()
            scene_name = self.game.scene_manager.current_scene if self.game.scene_manager else "unknown"
            description = f"Save at {scene_name}"

            print(f"[SaveMenu] Saving to slot {self.selected_slot + 1}: {description}")

            # Save
            result = game_state.save_to_file(
                self.selected_slot,
                scene_name,
                description,
                self.game.project_path
            )

            if result:
                print(f"[SaveMenu] Game saved to slot {self.selected_slot + 1}")
                self.close()
            else:
                print(f"[SaveMenu] Save failed!")
        except Exception as e:
            print(f"[SaveMenu] ERROR during save: {e}")
            import traceback
            traceback.print_exc()

    def perform_load(self):
        """Load game from selected slot."""
        if self.selected_slot is None:
            return

        try:
            from v2_engine.core.game_state import get_game_state

            game_state = get_game_state()
            success = game_state.load_from_file(self.selected_slot, self.game.project_path)

            if success:
                print(f"[SaveMenu] Game loaded from slot {self.selected_slot + 1}")
                # Reload scene to apply loaded state
                if self.game.scene_manager:
                    print(f"[SaveMenu] Reloading scene...")
                    self.game.scene_manager.reload_current_scene()
                    print(f"[SaveMenu] Scene reloaded successfully")
                self.close()
            else:
                print(f"[SaveMenu] Load failed!")
        except Exception as e:
            print(f"[SaveMenu] ERROR during load: {e}")
            import traceback
            traceback.print_exc()

    def delete_slot(self):
        """Delete selected save slot."""
        if self.selected_slot is None:
            return

        from v2_engine.core.game_state import get_game_state

        game_state = get_game_state()
        success = game_state.delete_save(self.selected_slot, self.game.project_path)

        if success:
            print(f"[SaveMenu] Deleted slot {self.selected_slot + 1}")
            # Rebuild UI to reflect deletion
            self.panel.clear()
            self.slot_buttons = []
            self.action_buttons = []
            self.selected_slot = None
            self.build_ui()

    def open(self):
        """Open the save menu."""
        self.active = True

        # Refresh slot metadata to show latest saves
        self.refresh_slots()

        # Pause game (if game has pause functionality)
        if hasattr(self.game, 'pause'):
            self.game.pause()

    def close(self):
        """Close the save menu."""
        self.active = False
        # Unpause game
        if hasattr(self.game, 'unpause'):
            self.game.unpause()

    def toggle(self):
        """Toggle menu open/closed."""
        if self.active:
            self.close()
        else:
            self.open()

    def handle_event(self, event):
        """Handle input events."""
        if not self.active:
            return False

        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True

        # Pass to UI elements (pass all events, not just when panel exists)
        if self.panel:
            # Don't consume the event - let it propagate through all widgets
            self.panel.handle_event(event)

        # Return True to consume event and prevent it from reaching the game
        return True

    def update(self, dt):
        """Update menu."""
        if not self.active:
            return

        if self.panel:
            self.panel.update(dt)

    def render(self, screen):
        """Render menu overlay."""
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Render menu panel
        if self.panel:
            self.panel.render(screen)
