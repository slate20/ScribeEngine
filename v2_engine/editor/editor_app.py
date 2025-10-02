"""
Main native editor application using Pygame + Dear ImGui.
"""

import os
import sys
import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer

from v2_engine.core.game import Game
from v2_engine.utils.math import Vector2
from v2_engine.editor.editor_state import EditorState
from v2_engine.editor.tools.select_tool import SelectTool
from v2_engine.editor.scene_serializer import SceneSerializer
from v2_engine.editor import gizmos


class EditorApp:
    """
    Main native editor application.

    Provides visual editing for Scribe Engine V2 games using Pygame + ImGui.
    """

    def __init__(self, project_path: str):
        """
        Initialize the editor.

        Args:
            project_path: Path to the game project directory
        """
        self.project_path = os.path.abspath(project_path)

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
        pygame.display.set_caption("Scribe Engine V2 - Editor")

        # Initialize ImGui
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()

        # Set up ImGui IO - CRITICAL: Must happen before any ImGui calls
        io = imgui.get_io()
        io.display_size = self.screen.get_size()
        io.config_flags |= imgui.CONFIG_DOCKING_ENABLE  # Enable docking

        # Set ImGui style
        self._setup_imgui_style()

        # Viewport dimensions (for rendering game scene)
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 800
        self.viewport_height = 600

        # Load project
        self.game = Game(project_path)
        self.game.editor_mode = True  # Flag for game to know it's in editor

        if not self.game.initialize():
            raise RuntimeError("Failed to initialize game")

        # Perform initial scene transition (scene manager queues it but doesn't execute until update)
        if self.game.scene_manager:
            self.game.scene_manager._perform_scene_transition()

        # Editor state
        self.state = EditorState()
        self.select_tool = SelectTool()
        self.scene_serializer = SceneSerializer()
        self.clock = pygame.time.Clock()
        self.running = False

        # Mouse state
        self.mouse_world_pos = Vector2(0, 0)

        print("[Editor] Initialized successfully")

    def _setup_imgui_style(self):
        """Configure ImGui visual style."""
        style = imgui.get_style()
        style.window_rounding = 5.0
        style.frame_rounding = 3.0
        style.scrollbar_rounding = 3.0
        style.grab_rounding = 3.0

    def run(self):
        """Start the editor main loop."""
        self.running = True
        print("[Editor] Starting editor loop...")

        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # Process events
            self._process_events()

            # In edit mode: No game updates (static scene editing)
            # In play mode: Game would run in separate window (not here)

            # Render
            self._render()

            pygame.display.flip()

        print("[Editor] Editor loop ended")

    def quit(self):
        """Clean shutdown."""
        print("[Editor] Shutting down...")
        self.running = False
        self.game.quit()
        pygame.quit()

    def _process_events(self):
        """Process pygame events and editor input."""
        for event in pygame.event.get():
            # Pass to ImGui first
            self.imgui_renderer.process_event(event)

            # Handle quit
            if event.type == pygame.QUIT:
                self.quit()
                return

            # Editor-specific input (in edit mode only)
            if self.state.mode == "edit" and not imgui.get_io().want_capture_mouse:
                self._handle_editor_input(event)

            # Pass to game if in play mode
            if self.state.mode == "play":
                if self.game.scene_manager:
                    self.game.scene_manager.handle_event(event)

    def _handle_editor_input(self, event):
        """Handle editor-specific input events."""
        # Mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_left_click()
            elif event.button == 2:  # Middle click
                self.state.panning = True
                self.state.pan_start = Vector2(event.pos[0], event.pos[1])
            elif event.button == 4:  # Scroll up
                mouse_pos = Vector2(event.pos[0], event.pos[1])
                self.state.camera.zoom_at(mouse_pos, 0.1)
            elif event.button == 5:  # Scroll down
                mouse_pos = Vector2(event.pos[0], event.pos[1])
                self.state.camera.zoom_at(mouse_pos, -0.1)

        # Mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.state.dragging_sprite = False
            elif event.button == 2:  # Middle click release
                self.state.panning = False

        # Mouse motion
        elif event.type == pygame.MOUSEMOTION:
            # Update mouse world position
            screen_pos = Vector2(event.pos[0], event.pos[1])
            self.mouse_world_pos = self.state.camera.screen_to_world(screen_pos)

            # Handle panning
            if self.state.panning:
                current_pos = Vector2(event.pos[0], event.pos[1])
                delta = current_pos - self.state.pan_start
                self.state.camera.pan(delta)
                self.state.pan_start = current_pos

            # Handle sprite dragging
            elif self.state.dragging_sprite and self.state.selected_sprite:
                new_pos = self.mouse_world_pos + self.state.drag_offset
                # Apply grid snapping
                new_pos.x = self.state.camera.snap_to_grid_value(new_pos.x)
                new_pos.y = self.state.camera.snap_to_grid_value(new_pos.y)
                self.state.selected_sprite.position = new_pos

        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_HOME:
                self.state.camera.reset()
            elif event.key == pygame.K_g:
                self.state.camera.snap_to_grid = not self.state.camera.snap_to_grid
                print(f"[Editor] Grid snapping: {self.state.camera.snap_to_grid}")
            elif event.key == pygame.K_DELETE:
                if self.state.selected_sprite:
                    # TODO: Implement sprite deletion
                    print("[Editor] Sprite deletion not yet implemented")

    def _handle_left_click(self):
        """Handle left mouse click in edit mode."""
        # Try to select sprite at mouse position - get actual scene object
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        else:
            scene = None

        clicked_sprite = self.select_tool.handle_click(self.mouse_world_pos, scene)

        if clicked_sprite:
            self.state.selected_sprite = clicked_sprite
            self.state.dragging_sprite = True
            # Calculate drag offset
            self.state.drag_offset = clicked_sprite.position - self.mouse_world_pos
            print(f"[Editor] Selected sprite: {clicked_sprite.__class__.__name__}")
        else:
            self.state.selected_sprite = None
            print("[Editor] Deselected sprite")

    def _render(self):
        """Render game and editor UI."""
        # Clear to dark grey background
        self.screen.fill((45, 45, 48))  # VS Code dark grey

        # Render ImGui UI (this includes the scene viewport)
        self._render_imgui_ui()

    def _render_scene_editor(self):
        """Render static scene editor view (not running game)."""
        # Get current scene
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        else:
            scene = None

        if not scene:
            # No scene loaded - show message
            font = pygame.font.Font(None, 36)
            text = font.render("No scene loaded", True, (150, 150, 150))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
            return

        screen_size = self.screen.get_size()

        # Draw grid background
        gizmos.draw_grid(self.screen, self.state.camera, screen_size)

        # Draw sprites STATICALLY (no game logic, just visual representation)
        if hasattr(scene, 'sprite_groups'):
            # Collect all sprites and sort by layer for proper rendering order
            all_sprites = []
            for group_name, sprite_group in scene.sprite_groups.items():
                all_sprites.extend(sprite_group.sprites)

            # Sort by layer (lower layers render first)
            all_sprites.sort(key=lambda s: getattr(s, 'layer', 0))

            # Render each sprite using editor camera
            for sprite in all_sprites:
                self._render_sprite_in_editor(sprite)

        # Draw editor gizmos on top
        if hasattr(scene, 'sprite_groups'):
            for group_name, sprite_group in scene.sprite_groups.items():
                for sprite in sprite_group.sprites:
                    is_selected = sprite == self.state.selected_sprite
                    gizmos.draw_sprite_gizmo(self.screen, sprite, self.state.camera, is_selected)

    def _render_sprite_in_editor(self, sprite):
        """Render a single sprite using the editor camera (static, no game logic)."""
        if not hasattr(sprite, 'image') or sprite.image is None:
            return

        # Convert sprite world position to screen position using editor camera
        screen_pos = self.state.camera.world_to_screen(sprite.position)

        # Scale sprite image based on editor zoom
        if self.state.camera.zoom != 1.0:
            original_size = sprite.image.get_size()
            scaled_size = (
                int(original_size[0] * self.state.camera.zoom),
                int(original_size[1] * self.state.camera.zoom)
            )
            scaled_image = pygame.transform.scale(sprite.image, scaled_size)
        else:
            scaled_image = sprite.image

        # Calculate render position (accounting for sprite origin)
        origin_offset_x = scaled_image.get_width() * sprite.origin.x
        origin_offset_y = scaled_image.get_height() * sprite.origin.y

        render_x = screen_pos.x - origin_offset_x
        render_y = screen_pos.y - origin_offset_y

        # Render the sprite
        self.screen.blit(scaled_image, (int(render_x), int(render_y)))

    def _render_play_mode(self):
        """Render play mode (game actually running)."""
        # TODO: For now, show a message. Later, this could be a separate game window
        font = pygame.font.Font(None, 48)
        text = font.render("Play Mode - Game Running", True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)

        font2 = pygame.font.Font(None, 24)
        text2 = font2.render("(Game would run in separate window)", True, (150, 150, 150))
        text2_rect = text2.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40))
        self.screen.blit(text2, text2_rect)

    def _render_imgui_ui(self):
        """Render ImGui interface with docked layout."""
        # Update display size for ImGui (handles window resizing)
        io = imgui.get_io()
        io.display_size = self.screen.get_size()

        imgui.new_frame()

        # Setup dockspace (full window)
        viewport = imgui.get_main_viewport()
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(io.display_size.x, io.display_size.y)
        imgui.set_next_window_viewport(viewport.id)

        window_flags = (
            imgui.WINDOW_NO_TITLE_BAR |
            imgui.WINDOW_NO_COLLAPSE |
            imgui.WINDOW_NO_RESIZE |
            imgui.WINDOW_NO_MOVE |
            imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS |
            imgui.WINDOW_NO_NAV_FOCUS |
            imgui.WINDOW_MENU_BAR
        )

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))
        imgui.begin("DockSpace", flags=window_flags)
        imgui.pop_style_var()

        # Create dockspace
        dockspace_id = imgui.get_id("MyDockSpace")
        imgui.dock_space(dockspace_id, (0, 0))

        # Menu bar
        self._render_menu_bar()

        imgui.end()

        # Render panels as docked windows
        self._render_hierarchy_panel()
        self._render_scene_viewport()
        self._render_property_inspector()

        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def _render_menu_bar(self):
        """Render top menu bar with file menu and play/stop button."""
        if imgui.begin_menu_bar():
            # File menu
            if imgui.begin_menu("File"):
                if imgui.menu_item("New Scene")[0]:
                    self._create_new_scene()
                if imgui.menu_item("Save Scene")[0]:
                    self._save_current_scene()
                if imgui.menu_item("Load Scene")[0]:
                    # TODO: Implement scene loading dialog
                    print("[Editor] Scene loading not yet implemented")
                imgui.separator()
                if imgui.menu_item("Exit")[0]:
                    self.quit()
                imgui.end_menu()

            # Edit menu
            if imgui.begin_menu("Edit"):
                if imgui.menu_item("Undo")[0]:
                    # TODO: Implement undo
                    print("[Editor] Undo not yet implemented")
                if imgui.menu_item("Redo")[0]:
                    # TODO: Implement redo
                    print("[Editor] Redo not yet implemented")
                imgui.end_menu()

            # View menu
            if imgui.begin_menu("View"):
                clicked, selected = imgui.menu_item(
                    "Grid Snapping",
                    selected=self.state.camera.snap_to_grid
                )
                if clicked:
                    self.state.camera.snap_to_grid = selected
                if imgui.menu_item("Reset Camera")[0]:
                    self.state.camera.reset()
                imgui.end_menu()

            # Play/Stop button (center-right)
            imgui.same_line(spacing=50)
            if self.state.mode == "edit":
                if imgui.button("▶ Play"):
                    self._enter_play_mode()
            else:
                if imgui.button("⏹ Stop"):
                    self._enter_edit_mode()

            imgui.end_menu_bar()

    def _render_scene_viewport(self):
        """Render the central scene viewport window."""
        imgui.begin("Scene")

        # Get available content region
        avail = imgui.get_content_region_available()
        self.viewport_width = max(100, avail.x)
        self.viewport_height = max(100, avail.y)
        self.viewport_x, self.viewport_y = imgui.get_cursor_screen_position()

        # Create a child region for the scene rendering
        imgui.begin_child("SceneRender", width=self.viewport_width, height=self.viewport_height, border=True)

        # Render the scene here
        if self.state.mode == "edit":
            self._render_scene_to_viewport()

        imgui.end_child()
        imgui.end()

    def _render_scene_to_viewport(self):
        """Render the game scene into the viewport area."""
        # Get current scene
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        else:
            return

        # Create a pygame surface for the viewport
        viewport_surface = pygame.Surface((int(self.viewport_width), int(self.viewport_height)))
        viewport_surface.fill((60, 60, 65))  # Dark background

        # Draw grid
        gizmos.draw_grid(viewport_surface, self.state.camera, (int(self.viewport_width), int(self.viewport_height)))

        # Draw sprites
        if hasattr(scene, 'sprite_groups'):
            all_sprites = []
            for group_name, sprite_group in scene.sprite_groups.items():
                all_sprites.extend(sprite_group.sprites)

            # Sort by layer
            all_sprites.sort(key=lambda s: getattr(s, 'layer', 0))

            # Render each sprite
            for sprite in all_sprites:
                self._render_sprite_to_surface(sprite, viewport_surface)

            # Draw gizmos
            for sprite in all_sprites:
                is_selected = sprite == self.state.selected_sprite
                gizmos.draw_sprite_gizmo(viewport_surface, sprite, self.state.camera, is_selected)

        # Blit viewport surface to main screen at viewport position
        self.screen.blit(viewport_surface, (int(self.viewport_x), int(self.viewport_y)))

    def _render_sprite_to_surface(self, sprite, surface):
        """Render a sprite to a surface using editor camera."""
        if not hasattr(sprite, 'image') or sprite.image is None:
            return

        screen_pos = self.state.camera.world_to_screen(sprite.position)

        if self.state.camera.zoom != 1.0:
            original_size = sprite.image.get_size()
            scaled_size = (
                int(original_size[0] * self.state.camera.zoom),
                int(original_size[1] * self.state.camera.zoom)
            )
            scaled_image = pygame.transform.scale(sprite.image, scaled_size)
        else:
            scaled_image = sprite.image

        origin_offset_x = scaled_image.get_width() * sprite.origin.x
        origin_offset_y = scaled_image.get_height() * sprite.origin.y

        render_x = screen_pos.x - origin_offset_x
        render_y = screen_pos.y - origin_offset_y

        surface.blit(scaled_image, (int(render_x), int(render_y)))

    def _render_property_inspector(self):
        """Render property inspector panel."""
        imgui.begin("Properties")

        if self.state.selected_sprite:
            self._render_sprite_properties(self.state.selected_sprite)
        else:
            imgui.text("No sprite selected")
            imgui.text_wrapped("Click on a sprite in the scene to edit its properties")

        imgui.end()

    def _render_sprite_properties(self, sprite):
        """Render real-time editable properties for a sprite."""
        imgui.text(f"Sprite: {sprite.__class__.__name__}")
        imgui.separator()

        # Position
        imgui.text("Position")
        changed, values = imgui.drag_float2("##pos", sprite.position.x, sprite.position.y, 1.0)
        if changed:
            sprite.position.x = values[0]
            sprite.position.y = values[1]

        # Origin
        imgui.text("Origin")
        changed, values = imgui.slider_float2("##origin", sprite.origin.x, sprite.origin.y, 0.0, 1.0)
        if changed:
            sprite.origin.x = values[0]
            sprite.origin.y = values[1]

        # Origin presets
        if imgui.button("Top-Left"):
            sprite.origin = Vector2(0, 0)
        imgui.same_line()
        if imgui.button("Center"):
            sprite.origin = Vector2(0.5, 0.5)
        imgui.same_line()
        if imgui.button("Bottom"):
            sprite.origin = Vector2(0.5, 1.0)

        # Additional properties if available
        if hasattr(sprite, 'image') and sprite.image:
            imgui.separator()
            imgui.text("Sprite Info")
            imgui.text(f"Width: {sprite.image.get_width()}")
            imgui.text(f"Height: {sprite.image.get_height()}")

    def _render_hierarchy_panel(self):
        """Render scene hierarchy panel."""
        imgui.begin("Hierarchy")

        # Get the actual scene object, not just the name
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        else:
            scene = None

        if scene and hasattr(scene, 'sprite_groups'):
            for group_name, sprite_group in scene.sprite_groups.items():
                if imgui.tree_node(group_name):
                    for i, sprite in enumerate(sprite_group.sprites):
                        sprite_label = f"{sprite.__class__.__name__}_{i}"
                        is_selected = sprite == self.state.selected_sprite

                        if imgui.selectable(sprite_label, is_selected)[0]:
                            self.state.selected_sprite = sprite

                    imgui.tree_pop()
        else:
            imgui.text("No scene loaded")

        imgui.end()

    def _enter_play_mode(self):
        """Switch to play mode."""
        print("[Editor] Entering play mode")
        self.state.enter_play_mode()
        self.game.editor_mode = False

    def _enter_edit_mode(self):
        """Switch to edit mode."""
        print("[Editor] Entering edit mode")
        self.state.enter_edit_mode()
        self.game.editor_mode = True

    def _create_new_scene(self):
        """Create a new empty scene."""
        # TODO: Implement new scene creation
        print("[Editor] New scene creation not yet implemented")

    def _save_current_scene(self):
        """Save the current scene to file."""
        # Get actual scene object
        if self.game.scene_manager and self.game.scene_manager.current_scene:
            scene = self.game.scene_manager.scenes[self.game.scene_manager.current_scene]
        else:
            scene = None

        if not scene:
            print("[Editor] No scene to save")
            return

        # Determine save path
        # For now, save to scenes/ directory in project
        scenes_dir = os.path.join(self.project_path, 'scenes')
        os.makedirs(scenes_dir, exist_ok=True)

        scene_name = scene.__class__.__name__
        scene_file = os.path.join(scenes_dir, f"{scene_name.lower()}.py")

        # Save scene
        self.scene_serializer.save_scene(scene, scene_file)
        print(f"[Editor] Saved scene: {scene_file}")


def main():
    """CLI entry point for running the editor."""
    import argparse

    parser = argparse.ArgumentParser(description='Scribe Engine V2 Native Editor')
    parser.add_argument('project_path', help='Path to the game project directory')

    args = parser.parse_args()

    # Create and run editor
    try:
        editor = EditorApp(args.project_path)
        editor.run()
    except KeyboardInterrupt:
        print("\n[Editor] Interrupted by user")
    except Exception as e:
        print(f"[Editor] Error during editor execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
