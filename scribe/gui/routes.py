"""
GUI IDE Routes

Handles all routes for the ScribeEngine IDE interface.
"""

import os
import json
from flask import render_template, request, jsonify, send_from_directory, abort, g
from pathlib import Path

from scribe.gui import gui_bp


@gui_bp.route('/')
def index():
    """Main IDE interface"""
    return render_template('ide.html')


@gui_bp.route('/test')
def test():
    """Test page for API endpoints"""
    return render_template('test.html')


@gui_bp.route('/debug')
def debug():
    """Debug page to test API endpoints"""
    import os
    from flask import current_app

    project_root = Path(os.getcwd())

    debug_info = {
        'project_root': str(project_root),
        'gui_blueprint_registered': True,
        'static_folder': gui_bp.static_folder,
        'template_folder': gui_bp.template_folder,
        'db_available': current_app.config.get('DB') is not None,
    }

    return f"<pre>{json.dumps(debug_info, indent=2)}</pre>"


@gui_bp.route('/api/files')
def list_files():
    """
    List all files in the project directory
    Returns a tree structure of files and folders
    """
    project_root = Path(os.getcwd())

    def build_tree(path):
        """Recursively build file tree"""
        items = []

        try:
            for item in sorted(path.iterdir()):
                # Skip hidden files, __pycache__, .git, etc.
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue

                if item.is_dir():
                    items.append({
                        'name': item.name,
                        'type': 'directory',
                        'path': str(item.relative_to(project_root)),
                        'children': build_tree(item)
                    })
                else:
                    items.append({
                        'name': item.name,
                        'type': 'file',
                        'path': str(item.relative_to(project_root)),
                        'extension': item.suffix
                    })
        except PermissionError:
            pass

        return items

    tree = build_tree(project_root)
    return jsonify({'files': tree, 'root': str(project_root)})


@gui_bp.route('/api/file/<path:filepath>')
def get_file(filepath):
    """
    Get contents of a specific file
    """
    project_root = Path(os.getcwd())
    file_path = project_root / filepath

    # Security: ensure file is within project directory
    try:
        file_path = file_path.resolve()
        project_root = project_root.resolve()
        if not str(file_path).startswith(str(project_root)):
            abort(403)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'path': filepath,
            'content': content,
            'language': get_language_from_extension(file_path.suffix)
        })
    except UnicodeDecodeError:
        # Binary file
        return jsonify({
            'path': filepath,
            'content': None,
            'error': 'Binary file cannot be displayed',
            'language': 'text'
        }), 400


@gui_bp.route('/api/file/<path:filepath>', methods=['POST'])
def save_file(filepath):
    """
    Save contents to a file
    """
    project_root = Path(os.getcwd())
    file_path = project_root / filepath

    # Security: ensure file is within project directory
    try:
        file_path = file_path.resolve()
        project_root = project_root.resolve()
        if not str(file_path).startswith(str(project_root)):
            abort(403)
    except Exception:
        abort(404)

    data = request.get_json()
    content = data.get('content', '')

    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return jsonify({'success': True, 'path': filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gui_bp.route('/api/file/<path:filepath>', methods=['DELETE'])
def delete_file(filepath):
    """
    Delete a file
    """
    project_root = Path(os.getcwd())
    file_path = project_root / filepath

    # Security: ensure file is within project directory
    try:
        file_path = file_path.resolve()
        project_root = project_root.resolve()
        if not str(file_path).startswith(str(project_root)):
            abort(403)
    except Exception:
        abort(404)

    if not file_path.exists():
        abort(404)

    try:
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            # Only delete if empty
            file_path.rmdir()

        return jsonify({'success': True, 'path': filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gui_bp.route('/api/file/new', methods=['POST'])
def create_file():
    """
    Create a new file or directory
    """
    project_root = Path(os.getcwd())
    data = request.get_json()

    path = data.get('path', '')
    file_type = data.get('type', 'file')  # 'file' or 'directory'

    file_path = project_root / path

    # Security: ensure file is within project directory
    try:
        file_path = file_path.resolve()
        project_root = project_root.resolve()
        if not str(file_path).startswith(str(project_root)):
            abort(403)
    except Exception:
        abort(404)

    try:
        if file_type == 'directory':
            file_path.mkdir(parents=True, exist_ok=True)
        else:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Create empty file
            file_path.touch()

        return jsonify({'success': True, 'path': path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gui_bp.route('/api/routes')
def get_routes():
    """
    Get all routes defined in .stpl files
    This will be used for the route explorer
    """
    from scribe.parser import TemplateParser
    import glob

    project_root = Path(os.getcwd())
    parser = TemplateParser()
    all_routes = []

    # Find all .stpl files
    stpl_files = list(project_root.glob('**/*.stpl'))

    for stpl_file in stpl_files:
        try:
            routes = parser.parse_file(str(stpl_file))

            for route in routes:
                all_routes.append({
                    'path': route.path,
                    'methods': route.methods,
                    'decorators': route.decorators,
                    'file': str(stpl_file.relative_to(project_root))
                })
        except Exception as e:
            # Skip files that fail to parse
            continue

    return jsonify({'routes': all_routes})


@gui_bp.route('/api/database/tables')
def get_database_tables():
    """
    Get list of all database tables
    """
    from flask import current_app

    try:
        db = current_app.config.get('DB')
        if not db:
            return jsonify({'tables': [], 'error': 'No database configured'}), 500

        # Get table list (SQLite-specific for now)
        if hasattr(db, 'connection'):
            cursor = db.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            return jsonify({'tables': tables})
        else:
            return jsonify({'tables': [], 'error': 'Database type not supported yet'}), 500

    except Exception as e:
        return jsonify({'tables': [], 'error': str(e)}), 500


@gui_bp.route('/api/database/table/<table_name>')
def get_table_data(table_name):
    """
    Get data from a specific table with pagination
    """
    from flask import current_app

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    try:
        db = current_app.config.get('DB')
        if not db:
            return jsonify({'error': 'No database configured'}), 500

        # Security: validate table name (prevent SQL injection)
        if not table_name.replace('_', '').isalnum():
            return jsonify({'error': 'Invalid table name'}), 400

        # Get column names
        if hasattr(db, 'connection'):
            cursor = db.connection.cursor()

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            if not columns:
                return jsonify({'error': 'Table not found'}), 404

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total = cursor.fetchone()[0]

            # Get paginated data
            offset = (page - 1) * per_page
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (per_page, offset))

            # Convert rows to dictionaries
            rows = cursor.fetchall()
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                data.append(row_dict)

            return jsonify({
                'table': table_name,
                'columns': columns,
                'data': data,
                'total': total,
                'page': page,
                'per_page': per_page
            })
        else:
            return jsonify({'error': 'Database type not supported yet'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_language_from_extension(ext):
    """Map file extension to Monaco Editor language identifier"""
    language_map = {
        '.stpl': 'scribe-template',  # Custom language we'll define
        '.py': 'python',
        '.js': 'javascript',
        '.json': 'json',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.md': 'markdown',
        '.txt': 'plaintext',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.xml': 'xml',
        '.sh': 'shell',
    }

    return language_map.get(ext.lower(), 'plaintext')
