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


@gui_bp.route('/api/database/connections')
def get_database_connections():
    """
    Get list of available database connections
    """
    from flask import current_app

    try:
        db_manager = current_app.config.get('DB')
        if not db_manager:
            return jsonify({'connections': [], 'error': 'No database configured'}), 500

        # Get all connection names
        connections = list(db_manager.keys())

        return jsonify({'connections': connections})

    except Exception as e:
        return jsonify({'connections': [], 'error': str(e)}), 500


@gui_bp.route('/api/database/<connection_name>/tables')
def get_database_tables(connection_name):
    """
    Get list of all database tables for a specific connection
    """
    from flask import current_app

    try:
        db_manager = current_app.config.get('DB')
        if not db_manager:
            return jsonify({'tables': [], 'error': 'No database configured'}), 500

        # Get specific connection
        if connection_name not in db_manager:
            return jsonify({'tables': [], 'error': f'Connection "{connection_name}" not found'}), 404

        db = db_manager[connection_name]

        if not hasattr(db, 'connection'):
            return jsonify({'tables': [], 'error': 'Database type not supported yet'}), 500

        cursor = db.connection.cursor()

        # Detect database type and use appropriate query
        db_type = db.config.get('type', 'sqlite').lower()

        if db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'mssql':
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = [row[0] if isinstance(row, tuple) else row['TABLE_NAME'] for row in cursor.fetchall()]
        else:
            return jsonify({'tables': [], 'error': f'Database type {db_type} not supported yet'}), 500

        cursor.close()
        return jsonify({'tables': tables})

    except Exception as e:
        return jsonify({'tables': [], 'error': str(e)}), 500


@gui_bp.route('/api/database/<connection_name>/table/<table_name>')
def get_table_data(connection_name, table_name):
    """
    Get data from a specific table with pagination
    """
    from flask import current_app

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    try:
        db_manager = current_app.config.get('DB')
        if not db_manager:
            return jsonify({'error': 'No database configured'}), 500

        # Get specific connection
        if connection_name not in db_manager:
            return jsonify({'error': f'Connection "{connection_name}" not found'}), 404

        db = db_manager[connection_name]

        # Security: validate table name (prevent SQL injection)
        if not table_name.replace('_', '').isalnum():
            return jsonify({'error': 'Invalid table name'}), 400

        # Get column names
        if not hasattr(db, 'connection'):
            return jsonify({'error': 'Database type not supported yet'}), 500

        cursor = db.connection.cursor()
        db_type = db.config.get('type', 'sqlite').lower()

        # Get column info based on database type
        if db_type == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
        elif db_type == 'mssql':
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            columns = [row[0] if isinstance(row, tuple) else row['COLUMN_NAME'] for row in cursor.fetchall()]
        else:
            cursor.close()
            return jsonify({'error': f'Database type {db_type} not supported yet'}), 500

        if not columns:
            cursor.close()
            return jsonify({'error': 'Table not found'}), 404

        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]

        # Get paginated data (handle different placeholder styles)
        offset = (page - 1) * per_page
        if db_type == 'sqlite':
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (per_page, offset))
        elif db_type == 'postgresql':
            cursor.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (per_page, offset))
        elif db_type == 'mssql':
            # MSSQL uses OFFSET/FETCH syntax (requires ORDER BY)
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY (SELECT NULL) OFFSET %s ROWS FETCH NEXT %s ROWS ONLY", (offset, per_page))

        # Convert rows to dictionaries
        rows = cursor.fetchall()
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)

        cursor.close()

        return jsonify({
            'table': table_name,
            'columns': columns,
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page
        })

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
