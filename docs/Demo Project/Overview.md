### Game Concept: "NetRunner's Gambit"

**Theme:** A short, self-contained cyberpunk heist. The player is a freelance "NetRunner" (hacker) hired to infiltrate the secure servers of the monolithic OmniCorp to steal a valuable data package.

**Why this concept is ideal for a showcase:**

- **Visually Striking:** The cyberpunk/terminal aesthetic can be made incredibly immersive and stylish using only text and CSS. We can create a "glowing text," "scan lines," and "glitch" effects that make the interface itself part of the experience.
    
- **Mechanically Rich:** The theme naturally calls for features like skill checks, mini-games, dynamic stats (like a "Trace Level"), and inventory management (for hacking programs), all of which are perfect for showing off the Python backend.
    
- **Dynamic UI:** A hacker's interface is expected to have a Heads-Up Display (HUD) with constantly updating information, which is a perfect use case for the `:: PrePassage` and `:: PostPassage` features.
    

### Key Features to Showcase

This demo will be a "vertical slice," demonstrating a wide range of engine features in a short, polished experience.

1. **Advanced CSS & Theming (`custom.css` & `project.json`):**
    
    - We'll create a retro-futuristic terminal interface. Dark background, glowing neon text, monospaced fonts, and subtle animations. The main content will appear inside a styled "terminal" window.
        
2. **Dynamic HUD (`:: PrePassage`):**
    
    - A persistent header will display the player's handle, their current "Trace Level" (how close they are to being caught), and their active objective. This will update in real-time without page reloads.
        
3. **Complex State Management (`player`, `variables`, `flags`):**
    
    - The player will have core skills (e.g., `Hacking`, `Stealth`).
        
    - We'll use `variables` to manage the `trace_level` and track the state of various security systems.
        
    - `flags` will be used to track one-time events, like whether a specific backdoor has been discovered.
        
4. **Custom Python Logic (`.py` files):**
    
    - We will separate our logic into different files (`systems.py`, `minigames.py`) to show off the engine's organizational capabilities.
        
    - We'll implement a `skill_check()` function that determines success or failure based on the player's skills and a random element.
        
    - A simple, text-based hacking mini-game (e.g., a timed password breaker or a node-capture sequence) will be programmed entirely in Python.
        
5. **Rich Narrative Interactivity (`.tgame` file):**
    
    - **Links with Actions:** Choices will directly call Python functions. Ex: `[[Run 'ICEPick.exe' on the firewall->Infiltration||{% do run_hack('firewall') %}]]`
        
    - **`#silent` Passages:** These will be used extensively for processing the outcomes of skill checks. The player makes a choice, a silent passage runs the Python logic, updates the game state (e.g., increases the Trace Level), and then seamlessly redirects them to the appropriate result passage.
        
    - **Jinja2 Templating:** We'll use conditional logic (`{% if %}`) to show different text based on success or failure, and loops (`{% for %}`) to display the player's inventory of hacking programs.
        
    - **User Input:** The game will start by asking the player for their hacker handle using the `input_field` macro.
        
6. **Assets (`assets/` folder):**
    
    - We'll incorporate character portraits for the client, a logo for OmniCorp, and maybe a simple server schematic to make the world feel more tangible.
        
    - Background ambient music and short UI sound effects for success/failure will demonstrate the audio capabilities.