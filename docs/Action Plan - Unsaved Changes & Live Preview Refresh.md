

  Overall Goal: Implement visual indicators for unsaved changes in the editor and file list,
   and ensure the game engine resets and the live preview refreshes upon saving a file.

  ---

  Step 1: Implement CodeMirror Change Detection and Basic Save Button UI Update


   * Objective: The "Save File" button should visually indicate when the currently open file
     has unsaved changes.
   * Changes:
       1. `static/js/gui.js`:
           * Declare a global unsavedFiles = new Set(); to track files with pending changes.
           * In initEditor(), add an editor.on('change', ...) event listener. This listener
             will:
               * Add the currentFile to the unsavedFiles set.
               * Call a new function, updateEditorUI().
           * Implement a basic updateEditorUI() function that:
               * Gets a reference to the "Save File" button (#save-file-btn).
               * If currentFile is in unsavedFiles, add the class unsaved-changes to the
                 button.
               * Otherwise, remove the unsaved-changes class.
           * In openFile(), after setting the editor content and making it writable, call
             updateEditorUI().
           * In saveFile(), after a successful save, remove currentFile from unsavedFiles and
             call updateEditorUI().
       2. `static/css/gui.css`:
           * Add CSS rules for #save-file-btn.unsaved-changes to style it with a blue
             background and white text.
   * Test Procedure:
       1. Start the Scribe Engine.
       2. Open any file in the editor.
       3. Observe that the "Save File" button is grey (its default state).
       4. Make a small change in the editor (e.g., add a space).
       5. Verify: The "Save File" button immediately turns blue.
       6. Click the "Save File" button.
       7. Verify: The "Save File" button turns back to grey.
       8. Close the browser tab and reopen it, or refresh the page.
       9. Open the same file.
       10. Verify: The "Save File" button is grey (no unsaved changes from previous session).

  ---

  Step 2: Implement Unsaved Changes Indication in File List and Editor Title

   * Objective: Files with unsaved changes should be visually distinct in the sidebar file
     list (e.g., with an asterisk and/or different background color), and the editor's title
      should also show an asterisk.
   * Changes:
       1. `templates/_fragments/_file_list.html`:
           * Ensure that each <li> element representing a file (with class file-item) has a
             data-filepath="{{ file }}" attribute. This is crucial for JavaScript to
             identify which file corresponds to which list item.
       2. `static/js/gui.js`:
           * Enhance the updateEditorUI() function to also handle:
               * Editor Title: Get the #editor-file-title element. If currentFile is in
                 unsavedFiles, append an asterisk ( *) to its text content; otherwise,
                 ensure no asterisk is present.
               * File List Items: Iterate through all elements with class file-item. For
                 each item:
                   * Retrieve its data-filepath attribute.
                   * If the data-filepath is in unsavedFiles, add the class
                     unsaved-file-item and append an asterisk ( *) to the item's text
                     content (if not already present).
                   * Otherwise, remove the unsaved-file-item class and remove any asterisk
                     from its text content.
           * In the htmx:afterSwap event listener (which runs when the editor page is
             loaded), call updateEditorUI() to ensure the initial state of all UI elements
             is correct.
       3. `static/css/gui.css`:
           * Add CSS rules for .file-item.unsaved-file-item to give it a distinct background
              color (e.g., a light yellow or a subtle highlight) and potentially bold text.
   * Test Procedure:
       1. Start the Scribe Engine.
       2. Open a file.
       3. Make a change.
       4. Verify: The "Save File" button turns blue, the editor title shows an asterisk
          (e.g., "my_file.tgame *"), AND the file in the sidebar list shows an asterisk
          and/or changes its background color.
       5. Open a different file without saving the first one.
       6. Verify: The first file in the sidebar still shows its unsaved status
          (asterisk/color), while the newly opened file's save button is grey and its title
          has no asterisk.
       7. Go back to the first file.
       8. Save the first file.
       9. Verify: The save button turns grey, the editor title loses its asterisk, AND the
          file in the sidebar reverts to its original state (no asterisk, no special color).

  ---

  Step 3: Implement Server-Side Engine Reset on Save

   * Objective: Confirm that the Flask backend's reset_game_engine() function is called
     whenever a file is saved.
   * Changes:
       1. `app.py`:
           * Locate the save_file_content() route.
           * After the line f.write(data['content']), add a call to reset_game_engine().
           * (Optional for testing, remove later): Add a print("Game engine reset!")
             statement inside the reset_game_engine() function itself to easily observe its
             execution in the server console.
   * Test Procedure:
       1. Start the Scribe Engine from your terminal so you can see its console output.
       2. Open any file in the editor.
       3. Make a change.
       4. Save the file.
       5. Verify: Check the terminal where the Flask server is running. You should see the
          "Game engine reset!" message printed.
       6. Repeat with another file to ensure it consistently triggers the reset.

  ---

  Step 4: Implement Live Preview Refresh via HTMX

   * Objective: After a file is saved, the live preview iframe should automatically refresh
     to display the updated game state.
   * Changes:
       1. `static/js/gui.js`:
           * In the saveFile() function, after the fetch request to /api/save-file/...
             successfully completes (i.e., inside the .then(data => { ... }) block where
             data.status === 'success'):
               * Remove the existing refreshPreview() call.
               * Add code to trigger an HTMX request to refresh the preview panel:

   1                 const previewPanelContainer = document.getElementById(
     'preview-panel-container');
   2                 if (previewPanelContainer) {
   3                     htmx.ajax('GET', '/api/preview-panel', { target:
     previewPanelContainer, swap: 'outerHTML' });
   4                 }
   * Test Procedure:
       1. Start the Scribe Engine.
       2. Open a .tgame file that contains text visible in the game (e.g., the start
          passage).
       3. Make a noticeable change to the text in the editor (e.g., change "Hello World" to
          "Hello Scribe Engine!").
       4. Save the file.
       5. Verify: The live preview iframe on the right automatically reloads, and the updated
           text is immediately visible in the game.
       6. Make another change and save to confirm consistent behavior.