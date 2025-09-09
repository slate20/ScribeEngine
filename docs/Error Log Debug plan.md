This feature is designed to provided game developers with error responses from the server directly in the preview panels debug terminal. This removes the need to use the browser dev tools to try to find error responses so they can efficiently debug their .tgame and .py files.

Phase 1: Backend Modifications (`app.py`) 

- Update the existing flask routes related to parsing, executing, link actions, passage rendering, and other "game dev" functions to return JSON instead of HTML, and include the exception value. Remove the if debug_mode checks

Phase 2: Frontend HTML Modifications (`templates/_fragments/_preview_panel.html`)

1. Tab Navigation: Add a set of tab buttons within the debug-terminal-header (e.g., "Game State" and "Errors").
2. Error Content Area: Create a new div (e.g., error-log-content) to display the server errors, similar to the existing game-state-content. This new div will initially be hidden.

Phase 3: Frontend JavaScript Modifications (`static/js/gui.js`)

1. Global State:
    - currentDebugTab: To track the active tab ('game-state' or 'errors').
    - clientErrorLog: A client-side array to store error messages extracted from server responses.
2. Tab Switching Function: Implement switchDebugTab(tabName) to handle showing/hiding the correct content area and styling the active tab button.
3. Error Logging Enhancement:
    - Modify the fetch calls within gui.js (e.g., saveFile, openFile, etc.) that interact with the backend.
    - After receiving a response, check if response.ok is false (HTTP error status) or if the parsed JSON data.status is 'error'.
    - If an error is detected, extract data.message (or a generic error if response.ok is false but no JSON message is available) and push it to clientErrorLog.
    - Consider adding a timestamp to each error entry.
    - Implement a mechanism to limit the size of clientErrorLog to prevent excessive memory usage.
4. Error Display Function: Create updateErrorLogDisplay() which will:
    - Render the contents of the clientErrorLog array into the error-log-content div.
    - Only update if the 'Errors' tab is currently active.
5. Conditional Updates: Modify updateGameStateDisplay() to only update if the 'Game State' tab is active.
6. Event Listeners:
    - Attach click event listeners to the new tab buttons to call switchDebugTab().
    - Set up a periodic call (e.g., using setInterval) for updateErrorLogDisplay() to keep the error log fresh.

Phase 4: Apply styling (`static/css/gui.css`)

- Implement styling for the new debug terminal tabs to blend in with the establish GUI styles.