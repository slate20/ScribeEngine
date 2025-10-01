## Scribe Engine v1.3.2 Release Notes

This update adds powerful new interaction systems for building dynamic user interfaces. Action buttons provide context-aware interactions, while improved variable management keeps your game state clean. Plus quality-of-life improvements to the editor interface.

### New Features

*   **Action Buttons:** New `<<...>>` syntax creates interactive elements that can stay on the current passage or navigate elsewhere.
    *   Access loop variables like `item` from Jinja2 templates in button actions
    *   Two modes: reload current passage or navigate to target passage
    *   Perfect for shopping systems, inventory management, and dynamic interfaces

*   **Enhanced Variable Management:** New `delete_var()` function removes temporary variables from game state.
    *   Clean up calculation variables and temporary data
    *   Prevent debug displays from showing internal variables
    *   Keep save files organized and clutter-free

*   **Expanded Built-in Functions:** Added 25+ new safe built-in functions to Python execution environment.
    *   Standard functions like `enumerate`, `zip`, `sorted`, and `type`
    *   Exception types for proper error handling
    *   Enhanced iterator and collection operations

### Editor Improvements

*   **File Renaming:** Added rename buttons to all file types - hover over any file to see rename and delete options
*   **Improved Auto-closing:** Angle brackets (`<>`) now auto-close in the editor for easier HTML and link syntax
*   **Enhanced Action Button Styling:** Action buttons now have distinct button appearance instead of plain text links
*   **Better Tab Close Buttons:** Fixed sizing issues with tab close button icons

### What This Means for Users

*   **Better Interactions:** Build responsive interfaces that update without page navigation
*   **Cleaner Code:** Access template variables in actions and clean up temporary data easily
*   **More Flexibility:** Choose whether actions reload current passage or navigate elsewhere
*   **No Breaking Changes:** All existing link syntax continues working as before

### Example

**Navigation Links (existing):**
```
[[Go to shop->village_shop]]
[[Buy item->purchase||{$ player.gold -= 10 $}]]
```

**Action Buttons (new):**
```
{% for item in shop_items %}
    <div>
        {{ item.name }} - {{ item.price }} gold
        <!-- Stay on current passage -->
        <<Quick Buy||{$
            if player.gold >= item.price:
                player.gold -= item.price
                player.inventory.append(item.name)
        $}>>

        <!-- Navigate to details -->
        <<Examine->item_details||{$ selected_item = item $}>>
    </div>
{% endfor %}
```

**Variable Cleanup:**
```python
# Process transaction
{$-
total_price = base_price * (1 + tax_rate)
player.gold -= total_price

# Clean up temporary variable
delete_var('total_price')
-$}
```

### Breaking Changes (Minor)

*   **Theme File Renamed:** Projects now use `game_theme.css` instead of `custom.css`
    *   **Existing projects:** Rename your `custom.css` file to `game_theme.css` to restore your custom styling
    *   New projects automatically get the updated filename with enhanced action button styles

*Otherwise, your existing projects work unchanged *