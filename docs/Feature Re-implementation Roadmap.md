  This document details features that were partially implemented in the codebase, comparing them against the existing documentation. It serves as a guide for re-implementing these features after a rollback.

  1. Enhanced Link Functionality

  Code Changes (Summary):
   * `app.py`: Added a new /link_action route to handle links with embedded Python/Jinja actions
   * `engine/core.py`:
       * Modified generate_passage_html to support new link types: basic, redirect, and links with actions
       * Introduced execute_script method for safe execution of Python code from link actions.
       * Updated render_main_passage to handle silent passages and last_passage tracking.
   * `engine/parser.py`:
       * Updated link_pattern regular expression to parse action attributes from links.
       * Modified parse_passage to extract these new link attributes.
   * `docs/Guide/Writing Your Story.md`: This file was updated in the diff to include detailed explanations and syntax for "Redirect Links", "Links with Actions", and the introduced `#silent` and `#menu` passage tags.

  Documentation (Existing):
  The original docs/Guide/Writing Your Story.md only covered basic links ([[Link Text->PassageName]]).

  Discrepancies/New Features:
  This is a significant expansion of the linking system, introducing new types of links with dynamic behavior (redirection, script execution, delays). The updated documentation in the diff accurately describes
  these new features.

  Roadmap for Re-implementation:
   1. Parser (`engine/parser.py`): Re-implement the updated link_pattern regex to correctly capture  action components. Ensure parse_passage extracts these into the passage's link data structure.
   2. Core Engine (`engine/core.py`):
       * Re-implement the execute_script method to safely execute arbitrary Python/Jinja code.
       * Modify generate_passage_html to dynamically create HTMX requests based on the link type (basic hx-get, redirect hx-trigger="load", action hx-post to /link_action).
       * Ensure render_main_passage correctly processes silent passages by executing their content and immediately redirecting, and accurately tracks last_passage (excluding #menu passages).
   3. Flask App (`app.py`): Re-implement the /link_action route to receive target_passage and action_script, execute it via game_engine.execute_script, and then render the target
      passage.
   4. Documentation (`docs/Guide/Writing Your Story.md`): Ensure the documentation is fully restored with the detailed explanations for all new link types and their syntax.

  5. Passage Tags and Styling

  Code Changes (Summary):
   * `engine/core.py`: render_main_passage now sets game_state['passage_tags'] and generates an out-of-band HTMX swap div (#passage-tags-container) with classes derived from the current passage's tags.
   * `engine/parser.py`: parse_passage was updated to extract tags from passage headers (e.g., :: PassageName #tag1 #tag2).
   * `static/css/engine.css`: New CSS rules were added to style the #passage-tags-container based on the applied tags.
   * `templates/base.html`: A new <div id="passage-tags-container"></div> was added within #main-content-area.
   * `docs/Guide/Writing Your Story.md`: This file was updated to include sections on "Passage Tags" and "Special Tags" (#menu, #silent).
   * `docs/Guide/Game Logic and State.md`: This file was updated to include passage_tags as a "Directly Accessible Object".

  Documentation (Existing):
  No existing documentation for passage tags.

  Discrepancies/New Features:
  This is a completely new feature enabling semantic tagging of passages for both styling and game logic. The updated documentation in the diff provides a clear guide on its usage and the special behaviors of
  #menu and #silent tags.

  Roadmap for Re-implementation:
   1. Parser (`engine/parser.py`): Re-implement the logic to parse tags from passage headers and store them in the passage data.
   2. Core Engine (`engine/core.py`):
       * Ensure render_main_passage populates game_state['passage_tags'] with the current passage's tags.
       * Re-implement the generation of the <div id="passage-tags-container"> with dynamic classes based on passage_tags for HTMX OOB swap.
   3. Frontend (`static/css/engine.css`, `templates/base.html`): Restore the CSS rules for tag-based styling and ensure the #passage-tags-container div is present in the base template.
   4. Documentation (`docs/Guide/Writing Your Story.md`, `docs/Guide/Game Logic and State.md`): Restore the documentation for passage tags, including the special #menu and #silent tags, and the passage_tags
      accessible object.

  5. Custom Player Class Support

  Code Changes (Summary):
   * `engine/core.py`:
       * Modified the GameEngine __init__ to allow instantiation of a custom Player class (if use_default_player is False and a Player class is defined in project Python files).
       * get_template_context was updated to create either a SimpleNamespace or an instance of the custom Player class for the player object in the Jinja template context.
   * `engine/executor.py`:
       * create_safe_globals was modified to conditionally include a custom Player class instance in the sandbox environment.
       * update_game_state was updated to correctly convert the player object (whether SimpleNamespace or custom class instance) back to a dictionary for storage in game_state.

  Documentation (Existing):
  docs/Guide/Game Logic and State.md mentions the player object and the use_default_player feature in project.json, implying a fixed default structure. It also discusses "Custom Logic in Python Files."

  Discrepancies/New Features:
  This is a new advanced feature that allows developers to define their own Python Player class with custom attributes and methods, providing greater flexibility over the default player object. This was not
  explicitly documented before the attempted implementation.

  Roadmap for Re-implementation:
   1. Executor (`engine/executor.py`): Re-implement the logic in create_safe_globals to detect and instantiate a custom Player class from loaded systems if use_default_player is disabled. Ensure update_game_state
      correctly serializes the custom Player object back into a dictionary for the game state.
   2. Core Engine (`engine/core.py`): Re-implement the logic in __init__ and get_template_context to properly handle the custom Player class, ensuring it's available and correctly structured for Jinja templates.
   3. Documentation: Add a new section to docs/Guide/Game Logic and State.md (or a new advanced topic) explaining how to define and use a custom Player class, including how it interacts with use_default_player in
      project.json.

  4. Debugging Enhancements

  Code Changes (Summary):
   * `static/js/engine.js`: The JavaScript for the debug panel was simplified. Debug information is now fetched and updated dynamically after HTMX requests (htmx:afterRequest). The save/load button logic was also
     simplified and moved.

  Documentation (Existing):
  docs/Guide/Advanced Topics.md has a "Debugging Your Game" section that mentions viewing game state via /debug/state.

  Discrepancies/New Features:
  This is an improvement to the existing debugging functionality, making the debug panel more responsive and integrated with HTMX.

  Roadmap for Re-implementation:
   1. Frontend (`static/js/engine.js`): Re-implement the simplified debug panel JavaScript, ensuring it fetches and updates the debug state (/debug/state) after HTMX requests. Restore the simplified save/load button
      logic.
   2. Verification: Confirm that the /debug/state endpoint in app.py (which was not part of the diff, but is an existing feature) is still functional and provides the necessary game state information.
   3. Documentation (`docs/Guide/Advanced Topics.md`): Update the "Debugging Your Game" section to reflect the improved dynamic debug panel if the user interaction has changed.

  4. Project Configuration (starting_passage)

  Code Changes (Summary):
   * `main_engine.py`: When creating a new project, the default_project_json now uses "starting_passage": "start" instead of "main_story_file": "story.tgame".
   * `engine/state.py`: The StateManager constructor now accepts a starting_passage argument, which is used to initialize current_passage.

  Documentation (Existing):
  docs/Guide/Project Structure.md mentions main_story_file in project.json.

  Discrepancies/New Features:
  This is a change in how the initial passage is specified, moving from a file-centric approach (main_story_file) to a passage-name-centric approach (starting_passage). This is a more direct and flexible way to
  define the game's entry point.

  Roadmap for Re-implementation:
   1. Project Creation (`main_engine.py`): Re-implement the change to use starting_passage in the default_project_json for new projects.
   2. State Management (`engine/state.py`): Re-implement the StateManager to accept and use starting_passage for initializing the game state.
   3. Documentation (`docs/Guide/Project Structure.md`): Update the project.json reference to reflect the change from main_story_file to starting_passage.

  4. Flask Server Duplication (Bug Fix)

  Code Changes (Summary):
   * `app.py`: Duplicated app.run calls were present at the end of the file.

  Documentation (Existing):
  N/A (this is a bug).

  Discrepancies/New Features:
  This is a bug introduced during the attempted implementations.

  Roadmap for Re-implementation:
   1. Flask App (`app.py`): Remove the duplicated app.run calls, ensuring only one app.run call is present and correctly configured.