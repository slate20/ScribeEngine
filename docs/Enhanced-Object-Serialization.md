# Enhanced Object Serialization Feature Request

## Problem Statement

Currently, Scribe Engine requires custom classes to implement manual `to_dict()` and `from_dict()` methods for JSON serialization in the save/load system. This creates unnecessary friction for users who want to create simple game objects.

**Current Issues:**
- Users must manually implement serialization methods for every custom class
- No-argument constructor requirement is not well documented
- Error messages (`Object of type X is not JSON serializable`) are not user-friendly
- Breaks the "natural Python syntax" philosophy of the engine

## Proposed Solution

Implement automatic object serialization with fallback strategies to eliminate manual serialization requirements while maintaining backward compatibility.

### Implementation Strategy

**1. Automatic Introspection-Based Serialization**
```python
def auto_serialize_object(obj):
    """Automatically serialize objects with simple attributes"""
    if hasattr(obj, '__dict__'):
        data = {'__class__': obj.__class__.__name__, '__module__': obj.__class__.__module__}
        for key, value in obj.__dict__.items():
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                data[key] = value
            elif hasattr(value, '__dict__'):
                data[key] = auto_serialize_object(value)  # Recursive for nested objects
            else:
                # Skip non-serializable attributes (methods, file handles, etc.)
                continue
        return data
    return obj
```

**2. Fallback Hierarchy**
```python
def serialize_object(obj):
    # 1. User-defined methods (backward compatibility)
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()

    # 2. Python's standard pickling protocol
    elif hasattr(obj, '__getstate__'):
        return {'__class__': obj.__class__.__name__, '__state__': obj.__getstate__()}

    # 3. Dataclass support
    elif hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)

    # 4. Automatic introspection
    else:
        return auto_serialize_object(obj)
```

**3. Enhanced Restoration**
```python
def restore_object(class_name, data, project_modules):
    # Find class in project modules
    cls = find_class_in_modules(class_name, project_modules)
    if not cls:
        raise ValueError(f"Class {class_name} not found in project")

    obj = cls()  # No-argument constructor

    # Restore using appropriate method
    if hasattr(obj, 'from_dict'):
        obj.from_dict(data)
    elif hasattr(obj, '__setstate__'):
        obj.__setstate__(data['__state__'])
    else:
        # Auto-restore attributes
        for key, value in data.items():
            if key not in ['__class__', '__module__']:
                setattr(obj, key, value)

    return obj
```

## Benefits

**User Experience:**
- Zero boilerplate for simple custom classes
- "It just works" approach aligns with engine philosophy
- Better error messages with suggestions for fixes

**Backward Compatibility:**
- Existing projects with manual serialization continue working
- Gradual migration path for users

**Flexibility:**
- Supports multiple serialization patterns
- Handles nested objects automatically
- Works with dataclasses and standard Python patterns

## Example Usage

**Before (Current):**
```python
class QuestManager:
    def __init__(self):
        self.active_quests = []
        self.completed = {}

    def to_dict(self):  # Required boilerplate
        return {
            'active_quests': self.active_quests,
            'completed': self.completed
        }

    def from_dict(self, data):  # Required boilerplate
        self.active_quests = data.get('active_quests', [])
        self.completed = data.get('completed', {})
```

**After (Proposed):**
```python
class QuestManager:
    def __init__(self):
        self.active_quests = []
        self.completed = {}

    # That's it! Serialization happens automatically
```

## Implementation Notes

**Phase 1:** Automatic introspection for simple objects
**Phase 2:** Dataclass and attrs library support
**Phase 3:** Advanced features (custom type handlers, circular reference detection)

**Considerations:**
- Performance impact should be minimal (serialization only happens during saves)
- Security: Only restore classes found in project directory
- Documentation: Update user guide with new capabilities and migration path

## Related Issues

- Improve error messages for serialization failures
- Document no-argument constructor requirement more clearly
- Consider allowing constructor parameters with default values