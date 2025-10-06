"""
Debug overlay system for visualizing game state during development.

Provides real-time visualization of physics data, collision states,
and other debugging information.
"""

import pygame
from v2_engine.components.rigidbody import RigidBody
from v2_engine.components.box_collider import BoxCollider


class DebugOverlay:
    """
    Debug overlay for visualizing game state and physics data.

    Features:
    - Velocity vectors
    - Grounded state indicators
    - Collision box visualization
    - Frame-by-frame state display
    - FPS counter
    """

    def __init__(self):
        """Initialize debug overlay."""
        self.enabled = True
        self.show_velocity = True
        self.show_grounded = True
        self.show_colliders = True
        self.show_fps = True
        self.show_position = True
        self.show_history = True
        self.show_frame_log = False  # Toggle with F4

        # Font for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        self.tiny_font = pygame.font.Font(None, 14)

        # Colors
        self.velocity_color = (255, 255, 0)  # Yellow
        self.grounded_color = (0, 255, 0)    # Green
        self.airborne_color = (255, 100, 100) # Red
        self.collider_color = (0, 255, 255)  # Cyan
        self.text_bg_color = (0, 0, 0, 180)  # Semi-transparent black

        # Frame history tracking (last 120 frames = 2 seconds at 60fps)
        self.frame_history = {}  # sprite_id -> list of frame data
        self.max_history = 120
        self.frame_count = 0

        # On-screen log buffer (last N log messages)
        self.log_buffer = []
        self.max_log_lines = 15

        # Console output capture
        self.show_console = False  # Toggle with F5
        self.console_buffer = []
        self.max_console_lines = 30
        self._original_stdout = None

    def toggle(self):
        """Toggle debug overlay visibility."""
        self.enabled = not self.enabled

    def toggle_frame_log(self):
        """Toggle frame-by-frame console logging."""
        self.show_frame_log = not self.show_frame_log

    def toggle_console(self):
        """Toggle console output display."""
        self.show_console = not self.show_console

    def add_console_line(self, text: str):
        """Add line to console buffer."""
        self.console_buffer.append(text)
        if len(self.console_buffer) > self.max_console_lines:
            self.console_buffer.pop(0)

    def render(self, screen: pygame.Surface, scene, fps: float = 0):
        """
        Render debug overlay on screen.

        Args:
            screen: pygame Surface to render to
            scene: Current scene to debug
            fps: Current frames per second
        """
        if not self.enabled:
            return

        self.frame_count += 1

        # Render FPS in top-left corner
        if self.show_fps:
            self._render_fps(screen, fps)

        # Render debug info for all sprites in scene
        if hasattr(scene, 'sprite_groups'):
            for group_name, sprite_group in scene.sprite_groups.items():
                for sprite in sprite_group.sprites:
                    self._render_sprite_debug(screen, sprite, scene)
                    self._track_sprite_history(sprite)

        # Render frame history graph
        if self.show_history:
            self._render_history_graph(screen)

        # Render on-screen log panel
        if self.show_frame_log and self.log_buffer:
            self._render_log_panel(screen)

        # Render console output
        if self.show_console:
            self._render_console(screen)

    def _render_fps(self, screen: pygame.Surface, fps: float):
        """Render FPS counter in top-left corner."""
        text = f"FPS: {int(fps)}"
        text_surface = self.font.render(text, True, (255, 255, 255))

        # Draw background
        bg_rect = text_surface.get_rect(topleft=(10, 10))
        bg_rect.inflate_ip(10, 5)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill(self.text_bg_color)
        screen.blit(bg_surface, bg_rect)

        # Draw text
        screen.blit(text_surface, (10, 10))

    def _render_sprite_debug(self, screen: pygame.Surface, sprite, scene):
        """
        Render debug information for a single sprite.

        Args:
            screen: pygame Surface to render to
            sprite: Sprite to debug
            scene: Current scene (for camera offset if needed)
        """
        # Get sprite screen position (account for camera if present)
        sprite_pos = sprite.position

        # Render collision box
        if self.show_colliders and sprite.has_component(BoxCollider):
            self._render_collider(screen, sprite)

        # Render rigidbody debug info
        if sprite.has_component(RigidBody):
            rb = sprite.get_component(RigidBody)

            # Render velocity vector
            if self.show_velocity:
                self._render_velocity_vector(screen, sprite_pos, rb.velocity)

            # Render grounded state indicator
            if self.show_grounded:
                self._render_grounded_indicator(screen, sprite_pos, rb.grounded)

            # Render position and physics data
            if self.show_position:
                self._render_physics_data(screen, sprite, rb)

    def _render_collider(self, screen: pygame.Surface, sprite):
        """Render collision box outline."""
        collider = sprite.get_component(BoxCollider)
        rect = collider.get_rect()

        # Draw rectangle outline
        pygame.draw.rect(screen, self.collider_color, rect, 1)

    def _render_velocity_vector(self, screen: pygame.Surface, pos, velocity):
        """
        Render velocity as an arrow from sprite center.

        Args:
            screen: pygame Surface to render to
            pos: Sprite position (Vector2)
            velocity: Velocity vector (Vector2)
        """
        # Scale velocity for visibility (1 pixel = 10 units/sec)
        scale = 0.1
        arrow_end = (
            pos.x + velocity.x * scale,
            pos.y + velocity.y * scale
        )

        # Only draw if velocity is significant
        if abs(velocity.x) > 0.1 or abs(velocity.y) > 0.1:
            # Draw line
            pygame.draw.line(
                screen,
                self.velocity_color,
                (int(pos.x), int(pos.y)),
                (int(arrow_end[0]), int(arrow_end[1])),
                2
            )

            # Draw arrowhead (simple circle)
            pygame.draw.circle(
                screen,
                self.velocity_color,
                (int(arrow_end[0]), int(arrow_end[1])),
                3
            )

    def _render_grounded_indicator(self, screen: pygame.Surface, pos, grounded: bool):
        """
        Render grounded state as a circle at sprite center.

        Args:
            screen: pygame Surface to render to
            pos: Sprite position (Vector2)
            grounded: Whether sprite is grounded
        """
        color = self.grounded_color if grounded else self.airborne_color
        pygame.draw.circle(
            screen,
            color,
            (int(pos.x), int(pos.y)),
            5,
            2  # Outline only
        )

    def _render_physics_data(self, screen: pygame.Surface, sprite, rb: RigidBody):
        """
        Render detailed physics data as text overlay.

        Args:
            screen: pygame Surface to render to
            sprite: Sprite being debugged
            rb: RigidBody component
        """
        # Position text above sprite
        text_x = int(sprite.position.x + 10)
        text_y = int(sprite.position.y - 60)

        # Build debug text lines
        lines = [
            f"Pos: ({sprite.position.x:.1f}, {sprite.position.y:.1f})",
            f"Vel: ({rb.velocity.x:.1f}, {rb.velocity.y:.1f})",
            f"Grounded: {rb.grounded}",
        ]

        # Render each line
        y_offset = 0
        for line in lines:
            text_surface = self.small_font.render(line, True, (255, 255, 255))

            # Draw background
            bg_rect = text_surface.get_rect(topleft=(text_x, text_y + y_offset))
            bg_rect.inflate_ip(4, 2)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill(self.text_bg_color)
            screen.blit(bg_surface, bg_rect)

            # Draw text
            screen.blit(text_surface, (text_x, text_y + y_offset))
            y_offset += 16

    def _track_sprite_history(self, sprite):
        """
        Track sprite state over time for historical analysis.

        Args:
            sprite: Sprite to track
        """
        if not sprite.has_component(RigidBody):
            return

        # Only track Player sprite to avoid clutter
        if not (hasattr(sprite, 'name') and sprite.name == 'Player'):
            return

        rb = sprite.get_component(RigidBody)
        sprite_id = id(sprite)

        # Initialize history for this sprite
        if sprite_id not in self.frame_history:
            self.frame_history[sprite_id] = []

        # Record current frame data (capture EXACT float values)
        frame_data = {
            'frame': self.frame_count,
            'pos_y': float(sprite.position.y),
            'vel_y': float(rb.velocity.y),
            'grounded': rb.grounded,
            'was_grounded': rb.was_grounded if hasattr(rb, 'was_grounded') else False,
        }

        self.frame_history[sprite_id].append(frame_data)

        # Trim history to max length
        if len(self.frame_history[sprite_id]) > self.max_history:
            self.frame_history[sprite_id].pop(0)

        # On-screen logging if enabled
        if self.show_frame_log:
            # Always log to see the full sequence
            if len(self.frame_history[sprite_id]) > 1:
                prev = self.frame_history[sprite_id][-2]
                curr = frame_data

                # Detect state changes
                grounded_changed = prev['grounded'] != curr['grounded']
                pos_delta = curr['pos_y'] - prev['pos_y']
                vel_delta = curr['vel_y'] - prev['vel_y']

                # Color code by state
                state_char = 'G' if curr['grounded'] else 'A'  # Grounded or Airborne
                was_state = 'G' if curr['was_grounded'] else 'A'

                log_msg = (f"F{self.frame_count:05d} [{state_char}|was:{was_state}] "
                          f"Pos:{curr['pos_y']:.4f} Δ{pos_delta:+.4f} | "
                          f"Vel:{curr['vel_y']:.2f} Δ{vel_delta:+.2f}")

                if grounded_changed:
                    log_msg += " <STATE CHG>"

                self._add_log(log_msg)

    def _render_history_graph(self, screen: pygame.Surface):
        """
        Render timeline graph showing state changes over recent frames.

        Args:
            screen: pygame Surface to render to
        """
        if not self.frame_history:
            return

        # Graph position (bottom-right corner)
        graph_width = 400
        graph_height = 200
        graph_x = screen.get_width() - graph_width - 10
        graph_y = screen.get_height() - graph_height - 10

        # Background
        bg_surface = pygame.Surface((graph_width, graph_height), pygame.SRCALPHA)
        bg_surface.fill(self.text_bg_color)
        screen.blit(bg_surface, (graph_x, graph_y))

        # Draw border
        pygame.draw.rect(screen, (100, 100, 100),
                        (graph_x, graph_y, graph_width, graph_height), 1)

        # Title
        title = self.small_font.render("Last 2 seconds (Y-axis)", True, (255, 255, 255))
        screen.blit(title, (graph_x + 5, graph_y + 5))

        # Plot data for first sprite with RigidBody
        for sprite_id, history in self.frame_history.items():
            if len(history) < 2:
                continue

            # Find Y-position range for scaling
            y_positions = [h['pos_y'] for h in history]
            y_min = min(y_positions)
            y_max = max(y_positions)
            y_range = max(y_max - y_min, 10)  # Minimum range of 10 pixels

            # Plot area
            plot_x = graph_x + 10
            plot_y = graph_y + 30
            plot_width = graph_width - 20
            plot_height = graph_height - 60

            # Draw grid lines
            for i in range(5):
                grid_y = plot_y + (plot_height * i // 4)
                pygame.draw.line(screen, (50, 50, 50),
                               (plot_x, grid_y), (plot_x + plot_width, grid_y), 1)

            # Plot Y position as line graph
            points = []
            for i, frame_data in enumerate(history):
                x = plot_x + (i * plot_width // max(len(history) - 1, 1))
                # Normalize Y position to graph
                normalized_y = (frame_data['pos_y'] - y_min) / y_range
                y = plot_y + plot_height - (normalized_y * plot_height)
                points.append((x, int(y)))

                # Draw grounded state as colored dots
                color = self.grounded_color if frame_data['grounded'] else self.airborne_color
                pygame.draw.circle(screen, color, (x, int(y)), 2)

            # Draw line connecting points
            if len(points) > 1:
                pygame.draw.lines(screen, (100, 150, 255), False, points, 1)

            # Draw velocity graph (smaller, on right side)
            vel_points = []
            for i, frame_data in enumerate(history):
                x = plot_x + (i * plot_width // max(len(history) - 1, 1))
                # Scale velocity to fit (-500 to +500 range)
                vel_normalized = (frame_data['vel_y'] + 500) / 1000
                vel_normalized = max(0, min(1, vel_normalized))  # Clamp
                y = plot_y + plot_height - (vel_normalized * plot_height * 0.3)
                vel_points.append((x, int(y)))

            if len(vel_points) > 1:
                pygame.draw.lines(screen, self.velocity_color, False, vel_points, 1)

            # Legend
            legend_y = graph_y + graph_height - 20
            pygame.draw.circle(screen, self.grounded_color, (graph_x + 15, legend_y), 4)
            legend_text = self.tiny_font.render("Grounded", True, (255, 255, 255))
            screen.blit(legend_text, (graph_x + 25, legend_y - 6))

            pygame.draw.circle(screen, self.airborne_color, (graph_x + 100, legend_y), 4)
            legend_text = self.tiny_font.render("Airborne", True, (255, 255, 255))
            screen.blit(legend_text, (graph_x + 110, legend_y - 6))

            pygame.draw.line(screen, (100, 150, 255),
                           (graph_x + 190, legend_y), (graph_x + 210, legend_y), 2)
            legend_text = self.tiny_font.render("Position", True, (255, 255, 255))
            screen.blit(legend_text, (graph_x + 215, legend_y - 6))

            pygame.draw.line(screen, self.velocity_color,
                           (graph_x + 280, legend_y), (graph_x + 300, legend_y), 2)
            legend_text = self.tiny_font.render("Velocity", True, (255, 255, 255))
            screen.blit(legend_text, (graph_x + 305, legend_y - 6))

            # Only show first sprite to avoid clutter
            break

    def _add_log(self, message: str):
        """
        Add a message to the on-screen log buffer.

        Args:
            message: Log message to display
        """
        self.log_buffer.append(message)

        # Trim to max lines
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer.pop(0)

    def _render_log_panel(self, screen: pygame.Surface):
        """
        Render on-screen log panel showing recent frame events.

        Args:
            screen: pygame Surface to render to
        """
        # Panel position (left side, below FPS)
        panel_width = 500
        panel_x = 10
        panel_y = 50
        line_height = 18

        # Calculate panel height based on content
        panel_height = (len(self.log_buffer) * line_height) + 30

        # Background
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_surface.fill(self.text_bg_color)
        screen.blit(bg_surface, (panel_x, panel_y))

        # Border
        pygame.draw.rect(screen, (100, 100, 100),
                        (panel_x, panel_y, panel_width, panel_height), 1)

        # Title
        title = self.small_font.render("Frame Log (F4 to toggle)", True, (255, 255, 0))
        screen.blit(title, (panel_x + 5, panel_y + 5))

        # Render log lines (most recent at bottom)
        y_offset = panel_y + 25
        for log_msg in self.log_buffer:
            # Color code based on content
            if "[G]" in log_msg:
                color = (100, 255, 100)  # Green for grounded
            elif "[A]" in log_msg:
                color = (255, 200, 100)  # Orange for airborne
            else:
                color = (255, 255, 255)  # White default

            if "STATE CHG" in log_msg:
                color = (255, 100, 100)  # Red for state changes

            text_surface = self.tiny_font.render(log_msg, True, color)
            screen.blit(text_surface, (panel_x + 5, y_offset))
            y_offset += line_height

    def _render_console(self, screen: pygame.Surface):
        """
        Render console output panel.

        Args:
            screen: pygame Surface to render to
        """
        # Panel position (right side, full height)
        panel_width = 600
        panel_height = screen.get_height() - 20
        panel_x = screen.get_width() - panel_width - 10
        panel_y = 10
        line_height = 16

        # Background
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_surface.fill(self.text_bg_color)
        screen.blit(bg_surface, (panel_x, panel_y))

        # Border
        pygame.draw.rect(screen, (100, 100, 100),
                        (panel_x, panel_y, panel_width, panel_height), 1)

        # Title
        title = self.small_font.render("Debug Console (F5 to toggle)", True, (100, 255, 255))
        screen.blit(title, (panel_x + 5, panel_y + 5))

        # Render console lines
        y_offset = panel_y + 25
        for line in self.console_buffer:
            if y_offset + line_height > panel_y + panel_height:
                break  # Don't overflow panel
            text_surface = self.tiny_font.render(str(line)[:100], True, (200, 200, 200))
            screen.blit(text_surface, (panel_x + 5, y_offset))
            y_offset += line_height
