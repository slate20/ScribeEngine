# Scribe Engine Version Management

## 🎯 Simple Version Updates

Version management for Scribe Engine is now **trivial** with a single command:

```bash
# Update to new version
python set_version.py 1.4.0

# Check current version
python set_version.py
```

## 📋 Release Workflow

1. **Set new version**: `python set_version.py 1.4.0`
2. **Commit changes**: `git add . && git commit -m "Bump version to 1.4.0"`
3. **Build executable**: `python build_engine.py gui`
4. **Create GitHub release**: Upload the built executable

## 🔧 How It Works

### Single Source of Truth
- **`version_info.py`** is the definitive version source
- **`build_engine.py`** reads from `version_info.py`
- **`update_checker.py`** reads from embedded `version_info.py`

### Automatic Build Metadata
When you run `python build_engine.py gui`, it automatically:
- Captures current git commit hash
- Records build timestamp
- Embeds version info in the executable

### Rename-Proof Version Detection
Users can rename executables to anything (e.g., `my-awesome-engine.exe`) and version detection still works because the version info is embedded inside the executable.

## 📁 File Structure

```
ScribeEngine/
├── version_info.py          # ← SINGLE SOURCE OF TRUTH
├── set_version.py           # ← Version management tool
├── build_engine.py          # ← Reads from version_info.py
└── update_checker.py        # ← Reads embedded version_info.py
```

## ✅ Benefits

- **One command** to update versions
- **No manual editing** of multiple files
- **Automatic metadata** capture during builds
- **Rename-proof** version detection
- **Clear workflow** with helpful next-step prompts

## 🔍 Version Detection Priority

1. **Embedded `version_info.py`** (works even when executable is renamed)
2. **Executable filename pattern** (fallback for edge cases)
3. **Local `build_engine.py`** (development fallback)
4. **Default "1.0.0"** (final safety net)

This system ensures robust version detection under all circumstances while keeping version management simple for developers.