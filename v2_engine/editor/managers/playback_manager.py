"""
Playback Manager - Manages game playback in a separate process.

Handles:
- Play/stop game subprocess control
- Process monitoring and cleanup
- Toolbar button state coordination
- Game launcher script creation
"""

import subprocess
import sys
import os
import time
from PyQt6.QtCore import QObject, pyqtSignal


class PlaybackManager(QObject):
    """
    Manages game playback in a separate process.

    Signals:
        playback_started: Emitted when game starts playing
        playback_stopped: Emitted when game stops (exit code)
    """

    # Signals
    playback_started = pyqtSignal(int)  # PID
    playback_stopped = pyqtSignal(int)  # exit_code

    def __init__(self, editor):
        """
        Initialize the playback manager.

        Args:
            editor: Reference to EditorWindow
        """
        super().__init__()
        self.editor = editor

        # Playback state
        self.play_process = None  # subprocess.Popen instance
        self.is_playing = False   # Current playback state

    def play(self, project_path, scene_name=None):
        """
        Start playing the scene in a separate window.

        Args:
            project_path: Path to the game project
            scene_name: Name of scene to play (optional, uses entry scene if None)

        Returns:
            bool: True if launched successfully, False otherwise
        """
        # Check if game is already running
        if self.play_process and self.play_process.poll() is None:
            print("[PlaybackManager] Game is already running")
            return False

        # Launch game in separate process
        try:
            # Use the v2_engine main entry point to run the game
            python_executable = sys.executable
            game_script = os.path.join(os.path.dirname(__file__), '..', '..', 'main.py')

            # Check if main.py exists
            if not os.path.exists(game_script):
                print(f"[PlaybackManager] Error: Game launcher not found at {game_script}")
                # Create a simple launcher script
                self._create_game_launcher(game_script)

            # Launch subprocess with current scene
            args = [python_executable, game_script, project_path]
            if scene_name:
                args.append(scene_name)
                print(f"[PlaybackManager] Playing scene: {scene_name}")

            self.play_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"[PlaybackManager] Game launched (PID: {self.play_process.pid})")

            # Check if process is still running after a brief moment
            time.sleep(0.5)
            if self.play_process.poll() is not None:
                # Process exited - read output
                stdout, stderr = self.play_process.communicate(timeout=1)
                print(f"[PlaybackManager] Game process exited with code {self.play_process.returncode}")
                if stdout:
                    print(f"[PlaybackManager] Game stdout:\n{stdout}")
                if stderr:
                    print(f"[PlaybackManager] Game stderr:\n{stderr}")
                self.play_process = None
                return False

            # Update play mode state
            self.is_playing = True

            # Emit signal
            self.playback_started.emit(self.play_process.pid)

            return True

        except Exception as e:
            print(f"[PlaybackManager] Error launching game: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop(self):
        """
        Stop the running game.

        Returns:
            bool: True if stopped successfully, False if no game was running
        """
        if self.play_process and self.play_process.poll() is None:
            self.play_process.terminate()
            try:
                self.play_process.wait(timeout=2)
                print("[PlaybackManager] Game stopped")
            except subprocess.TimeoutExpired:
                print("[PlaybackManager] Game didn't stop gracefully, forcing kill...")
                self.play_process.kill()
                self.play_process.wait()
                print("[PlaybackManager] Game forcefully killed")

            return_code = self.play_process.returncode
            self.play_process = None
            self.is_playing = False

            # Emit signal
            self.playback_stopped.emit(return_code)

            return True
        else:
            print("[PlaybackManager] No game running")
            return False

    def check_process(self):
        """
        Check if the play process is still running.

        Returns:
            bool: True if process ended naturally, False if still running or wasn't running
        """
        if self.play_process is not None:
            # Check if process has terminated
            return_code = self.play_process.poll()
            if return_code is not None:
                # Process has ended naturally
                print(f"[PlaybackManager] Game process ended (exit code: {return_code})")
                self.play_process = None
                self.is_playing = False

                # Emit signal
                self.playback_stopped.emit(return_code)

                return True
        return False

    def is_running(self):
        """
        Check if game is currently running.

        Returns:
            bool: True if game is running, False otherwise
        """
        if self.play_process is not None:
            if self.play_process.poll() is None:
                return True
            else:
                # Process ended, clean up
                self.play_process = None
                self.is_playing = False
        return False

    def _create_game_launcher(self, script_path):
        """
        Create a simple game launcher script if it doesn't exist.

        Args:
            script_path: Path where the launcher script should be created
        """
        launcher_code = '''#!/usr/bin/env python3
"""
V2 Engine Game Launcher
"""
import sys
import os

# Add engine to path
engine_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(engine_root))

from v2_engine.core.game import Game

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    game = Game(project_path, editor_mode=False)

    # Initialize engine systems
    if not game.initialize():
        print("[Game] Failed to initialize game engine")
        sys.exit(1)

    # Load entry scene
    entry_scene = game.project_config.get('scenes', {}).get('entry_scene')
    if entry_scene:
        game.scene_manager.load_scene(entry_scene)

    # Run game loop
    game.run()
'''
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(launcher_code)
        print(f"[PlaybackManager] Created game launcher: {script_path}")
