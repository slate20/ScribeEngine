 Native Editor POC - Architecture Plan

 Mission Alignment

 Build a native Pygame + Dear ImGui editor that bridges the gap between simple engines and Godot/Unity, providing:
 - Visual tooling that abstracts Pygame complexity
 - Direct code editing for advanced developers
 - Full capability for "AAA" level 2D games

 POC Scope (Core Fundamentals)

 1. Project Creation - New project wizard
 2. Scene Creation - Add/manage scenes
 3. Navigation Controls - Pan, zoom, grid snapping
 4. Object Manipulation - Drag sprites, edit properties in real-time
 5. Playable Preview - Toggle between edit/play modes

 ---
 Branch Strategy

 # Create feature branch from current v2-development
 git checkout v2-development
 git checkout -b v2-native-editor-poc

 Architecture Overview

 Core Components

 6. Editor Application (v2_engine/editor/editor_app.py)
 class EditorApp:
     """Main native editor application"""
     def __init__(self):
         self.game = None           # Game instance (runs in editor)
         self.editor_state = None   # Edit vs Play mode
         self.selected_sprite = None
         self.camera_pan = Vector2(0, 0)
         self.camera_zoom = 1.0

 7. Editor Modes
 - Edit Mode: Manipulate scene, pause game logic, draw gizmos
 - Play Mode: Run game normally, hide editor UI except controls

 3. Integration Point
 Modify Game class to support editor mode:
 class Game:
     def __init__(self, project_path, editor_mode=False):
         self.editor_mode = editor_mode
         # If editor_mode, pause updates but allow rendering

 ---
 File Structure (New Files)

 v2_engine/editor/
 ├── __init__.py
 ├── editor_app.py          # Main editor application
 ├── editor_state.py        # Edit/Play mode, selection, camera
 ├── gizmos.py              # Visual handles, origin markers, bounds
 ├── property_panel.py      # ImGui property inspector
 ├── hierarchy_panel.py     # ImGui scene hierarchy
 ├── toolbar.py             # ImGui toolbar (New, Save, Play, etc)
 ├── scene_serializer.py    # Save/load scene files (uses existing scene_writer)
 └── project_wizard.py      # New project creation UI

 v2_engine/editor/tools/
 ├── __init__.py
 ├── select_tool.py         # Click to select sprites
 ├── move_tool.py           # Drag to move sprites
 └── camera_tool.py         # Pan/zoom viewport

 ---
 Key Dependencies
                                            dear
 Add to requirements.txt:
 imgui[pygame]==2.0.0    # Dear ImGui with Pygame backend

 ---
 Implementation Plan

 Phase 1: Minimal Working Editor (Hours 1-3)

 File: v2_engine/editor/editor_app.py
 import pygame
 import imgui
 from imgui.integrations.pygame import PygameRenderer

 class EditorApp:
     def __init__(self, project_path):
         pygame.init()
         self.screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
         pygame.display.set_caption("Scribe Engine V2 - Editor")

         # Initialize ImGui
         imgui.create_context()
         self.imgui_renderer = PygameRenderer()

         # Load project
         self.game = Game(project_path, editor_mode=True)
         self.game.initialize()

         self.mode = "edit"  # "edit" or "play"
         self.selected_sprite = None

     def run(self):
         clock = pygame.time.Clock()
         running = True

         while running:
             dt = clock.tick(60) / 1000.0

             # Process events
             for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     running = False
                 self.imgui_renderer.process_event(event)

                 # Editor-specific input (in edit mode only)
                 if self.mode == "edit":
                     self.handle_editor_input(event)

             # Update game (only in play mode)
             if self.mode == "play":
                 self.game._update(dt)

             # Render game
             self.game._render()

             # Render editor UI on top
             self.render_editor_ui()

             pygame.display.flip()

     def render_editor_ui(self):
         imgui.new_frame()

         # Toolbar
         if imgui.begin_main_menu_bar():
             if imgui.begin_menu("File"):
                 if imgui.menu_item("New Scene")[0]:
                     self.create_new_scene()
                 if imgui.menu_item("Save Scene")[0]:
                     self.save_current_scene()
                 imgui.end_menu()

             # Play/Stop button
             if self.mode == "edit":
                 if imgui.button("▶ Play"):
                     self.enter_play_mode()
             else:
                 if imgui.button("⏹ Stop"):
                     self.enter_edit_mode()

             imgui.end_main_menu_bar()

         # Property Inspector (right panel)
         imgui.set_next_window_position(1300, 30)
         imgui.set_next_window_size(300, 870)
         imgui.begin("Properties", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)

         if self.selected_sprite:
             self.render_sprite_properties(self.selected_sprite)
         else:
             imgui.text("No sprite selected")

         imgui.end()

         imgui.render()
         self.imgui_renderer.render(imgui.get_draw_data())

     def render_sprite_properties(self, sprite):
         """Real-time property editing - changes apply immediately"""
         imgui.text(f"Sprite: {sprite.__class__.__name__}")
         imgui.separator()

         # Position
         changed, (x, y) = imgui.drag_float2("Position", sprite.position.x, sprite.position.y)
         if changed:
             sprite.position.x = x
             sprite.position.y = y

         # Origin
         changed, (ox, oy) = imgui.slider_float2("Origin", sprite.origin.x, sprite.origin.y, 0.0, 1.0)
         if changed:
             sprite.origin.x = ox
             sprite.origin.y = oy

         # Origin presets
         if imgui.button("Top-Left"):
             sprite.origin = Vector2(0, 0)
         imgui.same_line()
         if imgui.button("Center"):
             sprite.origin = Vector2(0.5, 0.5)
         imgui.same_line()
         if imgui.button("Bottom"):
             sprite.origin = Vector2(0.5, 1.0)

 Phase 2: Scene Manipulation (Hours 3-5)

 File: v2_engine/editor/tools/select_tool.py
 class SelectTool:
     """Click to select sprites"""
     def handle_click(self, world_pos, scene):
         # Find sprite at world_pos
         for sprite_group in scene.sprite_groups.values():
             for sprite in sprite_group:
                 if sprite.get_rect().collidepoint(world_pos):
                     return sprite
         return None

 File: v2_engine/editor/gizmos.py
 def draw_sprite_gizmo(screen, sprite, camera, selected=False):
     """Draw editor handles for sprite"""
     rect = sprite.get_rect()
     screen_rect = camera.world_to_screen_rect(rect)

     # Draw bounding box
     color = (0, 255, 0) if selected else (255, 255, 255)
     pygame.draw.rect(screen, color, screen_rect, 2)

     # Draw origin point
     origin_world = sprite.position
     origin_screen = camera.world_to_screen(origin_world)
     pygame.draw.circle(screen, (255, 0, 255), origin_screen, 5)

     # Draw crosshair at origin
     pygame.draw.line(screen, (255, 0, 255),
                      (origin_screen.x - 8, origin_screen.y),
                      (origin_screen.x + 8, origin_screen.y), 1)
     pygame.draw.line(screen, (255, 0, 255),
                      (origin_screen.x, origin_screen.y - 8),
                      (origin_screen.x, origin_screen.y + 8), 1)

 Phase 3: Save/Load Integration (Hours 5-7)

 File: v2_engine/editor/scene_serializer.py
 from ide.scene_writer import SceneWriter

 class SceneSerializer:
     """Bridge between editor and file-based scene storage"""

     def save_scene(self, scene, file_path):
         """Save scene state to Python file"""
         writer = SceneWriter(file_path)

         # Iterate live sprite objects
         for group_name, sprite_group in scene.sprite_groups.items():
             for sprite in sprite_group.sprites:
                 properties = {
                     'x': sprite.position.x,
                     'y': sprite.position.y,
                     'origin_x': sprite.origin.x,
                     'origin_y': sprite.origin.y
                 }

                 # Add type-specific properties
                 if hasattr(sprite, 'image') and sprite.image:
                     properties['width'] = sprite.image.get_width()
                     properties['height'] = sprite.image.get_height()

                 # Write to file
                 sprite_name = f"self.{sprite.__class__.__name__.lower()}_{id(sprite)}"
                 writer.update_sprite_properties(sprite_name, properties)

 Phase 4: Camera Controls (Hours 7-8)

 Navigation:
 - Middle mouse drag = Pan camera
 - Mouse wheel = Zoom
 - Grid snapping (toggle with G key)
 - Reset view (Home key)

 File: v2_engine/editor/editor_state.py
 class EditorCamera:
     """Editor viewport camera (separate from game camera)"""
     def __init__(self):
         self.position = Vector2(0, 0)
         self.zoom = 1.0
         self.grid_size = 32
         self.snap_to_grid = True

     def screen_to_world(self, screen_pos):
         return Vector2(
             screen_pos.x / self.zoom + self.position.x,
             screen_pos.y / self.zoom + self.position.y
         )

 ---
 Success Criteria for POC

 ✅ Can create new empty project
 ✅ Can add Platform object to scene✅ Can drag platform and see position update in inspector immediately
 ✅ Can edit origin point with sliders and see visual change instantly
 ✅ Can pan/zoom editor viewport
 ✅ Can press Play and see game run with physics
 ✅ Can press Stop and return to edit mode with changes preserved
 ✅ Can save scene and reload editor with sprites in correct positions

 ---
 Comparison Metrics (Web vs Native)

 Measure after POC completion:

 | Metric                  | Web Editor          | Native Editor      |
 |-------------------------|---------------------|--------------------|
 | Lines of code           | ~2000 (JS + Python) | ~800 (Python only) |
 | Property change latency | ~100ms (HTTP)       | <1ms (direct)      |
 | File reloads needed     | Every change        | Only on save       |
 | State synchronization   | 3 systems           | 1 system           |
 | Debugging ease          | Console.log         | Python debugger    |

 ---
 Migration Decision Tree

 If POC shows:
 - Simpler code + Better UX → Migrate to native architecture
 - Comparable complexity → Evaluate based on team preference
 - More complex → Stick with web, document lessons learned

 ---
 Timeline

 Total: 8 hours for complete POC
 - Hour 1-3: Basic editor loop with ImGui + property inspector
 - Hour 3-5: Sprite selection, dragging, gizmos
 - Hour 5-7: Save/load scene files
 - Hour 7-8: Camera controls, grid snapping, play mode

 Next Session: Implement Phase 1 (minimal working editor)