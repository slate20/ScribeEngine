#!/usr/bin/env python3
"""
Build script to create a standalone executable of the Scribe Engine Build Tool.
This creates a redistributable build tool that users can run without Python dependencies.
"""

import subprocess
import sys
import os

def build_build_tool():
    """Build the standalone build tool executable."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_tool_script = os.path.join(script_dir, 'build_tool_standalone.py')
    
    if not os.path.exists(build_tool_script):
        print("Error: build_tool_standalone.py not found")
        return False
    
    # Determine platform suffix
    if sys.platform.startswith('linux'):
        platform_suffix = 'linux'
    elif sys.platform.startswith('win'):
        platform_suffix = 'windows'
    elif sys.platform.startswith('darwin'):
        platform_suffix = 'macos'
    else:
        platform_suffix = 'unknown'
    
    executable_name = f'ScribeBuilder-{platform_suffix}'
    if sys.platform.startswith('win'):
        executable_name += '.exe'
    
    # Create output directory
    output_dir = os.path.join(script_dir, 'dist_tools')
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Building Scribe Engine Build Tool")
    print("=" * 60)
    print(f"Platform: {platform_suffix}")
    print(f"Output: {executable_name}")
    print("=" * 60)
    
    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', executable_name.replace('.exe', ''),
        '--distpath', output_dir,
        '--workpath', os.path.join(script_dir, 'build_tools'),
        '--specpath', os.path.join(script_dir, 'spec_tools'),
        '--clean',
        '--noconfirm',
        # Include engine, templates, static as data
        '--add-data', f'{os.path.join(script_dir, "engine")}{os.pathsep}engine',
        '--add-data', f'{os.path.join(script_dir, "templates")}{os.pathsep}templates',
        '--add-data', f'{os.path.join(script_dir, "static")}{os.pathsep}static',
        '--add-data', f'{os.path.join(script_dir, "game_server.py")}{os.pathsep}.',
        '--add-data', f'{os.path.join(script_dir, "game_server_wrapper.py")}{os.pathsep}.',
        build_tool_script
    ]
    
    print("Running PyInstaller...")
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        executable_path = os.path.join(output_dir, executable_name)
        size_mb = os.path.getsize(executable_path) // (1024 * 1024)
        
        print("✓ Build completed successfully!")
        print(f"  Executable: {executable_path}")
        print(f"  Size: {size_mb} MB")
        print("=" * 60)
        print("Usage:")
        print(f"  {executable_name} /path/to/game/project")
        print(f"  {executable_name} --help")
        print("=" * 60)
        return True
    else:
        print("✗ Build failed!")
        print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return False

if __name__ == "__main__":
    success = build_build_tool()
    sys.exit(0 if success else 1)