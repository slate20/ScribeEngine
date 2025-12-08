# ScribeEngine - Complete Architecture Documentation

**Version:** 2.0 (Ground-up Rewrite)
**Purpose:** Web application framework with inline Python templating
**Target Audience:** Developers implementing ScribeEngine from scratch

---

## Documentation Structure

This documentation set provides a complete specification for building ScribeEngine from the ground up. Read the documents in order for best understanding.

### **Getting Started**

1. **[01_OVERVIEW.md](01_OVERVIEW.md)** - Vision, philosophy, and what makes ScribeEngine unique
2. **[02_QUICK_START.md](02_QUICK_START.md)** - 5-minute introduction with working examples

### **Core Architecture**

3. **[03_ARCHITECTURE.md](03_ARCHITECTURE.md)** - System design, components, and data flow
4. **[04_PROJECT_STRUCTURE.md](04_PROJECT_STRUCTURE.md)** - File organization and conventions

### **Template System**

5. **[05_TEMPLATE_SPECIFICATION.md](05_TEMPLATE_SPECIFICATION.md)** - Complete .stpl syntax reference
6. **[06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)** - Parser implementation guide
7. **[07_EXECUTION_CONTEXT.md](07_EXECUTION_CONTEXT.md)** - Python execution environment

### **Database Layer**

8. **[08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md)** - Multi-database support design
9. **[09_MIGRATION_SYSTEM.md](09_MIGRATION_SYSTEM.md)** - Database migration specification

### **Web Framework Integration**

10. **[10_FLASK_INTEGRATION.md](10_FLASK_INTEGRATION.md)** - Flask route generation and request handling
11. **[11_HELPERS_API.md](11_HELPERS_API.md)** - Built-in functions and decorators
12. **[12_AUTHENTICATION.md](12_AUTHENTICATION.md)** - Auth system specification

### **Configuration & CLI**

13. **[13_CONFIGURATION.md](13_CONFIGURATION.md)** - scribe.json schema and settings
14. **[14_CLI_SPECIFICATION.md](14_CLI_SPECIFICATION.md)** - Command-line interface design

### **IDE & Tooling**

15. **[15_IDE_SPECIFICATION.md](15_IDE_SPECIFICATION.md)** - Integrated development environment
16. **[16_BUILD_SYSTEM.md](16_BUILD_SYSTEM.md)** - Executable packaging

### **Security & Best Practices**

17. **[17_SECURITY.md](17_SECURITY.md)** - Security model and considerations
18. **[18_BEST_PRACTICES.md](18_BEST_PRACTICES.md)** - Recommended patterns

### **Reference & Examples**

19. **[19_COMPLETE_EXAMPLES.md](19_COMPLETE_EXAMPLES.md)** - Full application examples
20. **[20_API_REFERENCE.md](20_API_REFERENCE.md)** - Complete API documentation

---

## Implementation Roadmap

### **Phase 1: Proof of Concept (Week 1-2)**
- Basic template parser (`@route()` and `{$ $}` extraction)
- Flask route generation
- Python execution context
- SQLite database only
- CLI dev server
- **Goal:** Run the login example from testing

### **Phase 2: Core Features (Week 3-6)**
- Complete template syntax support
- Multi-database support (PostgreSQL, MySQL, MSSQL)
- Migration system
- Helper functions (auth, forms, redirects)
- Configuration system
- Auto-loading Python modules

### **Phase 3: Developer Experience (Week 7-10)**
- CLI improvements
- Project templates
- Error handling and debugging
- Hot reload
- Documentation generation

### **Phase 4: IDE & Tooling (Week 11-14)**
- Web-based IDE
- Database browser
- Migration manager
- Build system
- Deployment tools

### **Phase 5: Polish & Release (Week 15+)**
- Testing
- Performance optimization
- Documentation
- Example applications
- Community features

---

## Key Principles

1. **Simplicity First** - Zero boilerplate, sensible defaults
2. **No Magic (That Confuses)** - Clear what's happening, even if automatic
3. **Escape Hatches** - Can always drop to raw Flask/SQL when needed
4. **Web Standards** - Use HTTP methods, status codes, headers correctly
5. **Developer Joy** - Fast feedback loops, helpful error messages

---

## Quick Navigation

**Just want to see code?** → [02_QUICK_START.md](02_QUICK_START.md)
**Implementing the parser?** → [06_TEMPLATE_PARSER.md](06_TEMPLATE_PARSER.md)
**Database support?** → [08_DATABASE_ABSTRACTION.md](08_DATABASE_ABSTRACTION.md)
**Building the IDE?** → [15_IDE_SPECIFICATION.md](15_IDE_SPECIFICATION.md)
**Security concerns?** → [17_SECURITY.md](17_SECURITY.md)

---

## Contributing to This Documentation

This documentation should be:
- **Complete** - No assumptions about prior knowledge
- **Precise** - Exact specifications, not vague descriptions
- **Tested** - All examples must work
- **Maintained** - Updated as implementation evolves

When adding new features, update relevant documentation first, then implement.

---

## Version History

- **v2.0** - Ground-up rewrite specification (this document)
- **v1.x** - Original game engine (deprecated)

---

**Next Steps:** Read [01_OVERVIEW.md](01_OVERVIEW.md) to understand the vision and philosophy.
