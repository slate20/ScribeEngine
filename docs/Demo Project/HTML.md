<body id="main-body" class="engine-themed">
    <div id="game-container" class="layout-horizontal">
        
        
        <nav id="main-nav" hx-trigger="load">
            <div class="nav-section title">
                <h1>Gui Test</h1>
            </div>
            <div class="nav-section user-links">
                <div class="passage" data-passage="NavMenu"><div class="content"><a hx-get="/passage/start" hx-target="#game-content" class="nav-link">Home</a></div></div>
            </div>
            <div class="nav-section game-controls">
                <button id="save-btn">Save</button>
                <button id="load-btn">Load</button>
                
            </div>
        </nav>
        

        <div id="main-content-area">
            <div id="passage-tags-container"></div>
            <div class="content-container">
                <main id="game-content" hx-get="/passage/start" hx-trigger="load" class=""><div class="passage" data-passage="PrePassage"><div class="content"><div class="hud">
    <span>Health: 100</span>
    <span>Score: 0</span>
</div>
<hr></div></div><div class="passage" data-passage="start"><div class="content">Welcome to your new adventure, Tester!

This is your first passage. You can edit this file (story.tgame) to begin writing your story.</div><div class="choices">
                        <button hx-get="/passage/first_step" hx-target="#game-content" class="choice-btn" data-target="first_step">
                            Start the adventure!
                        </button>
                    </div></div><div class="passage" data-passage="PostPassage"><div class="content"><hr>
<div class="footer">
    <p>Copyright 2025, </p>
</div></div></div></main>
            </div>
            
            
        </div>
    </div>
    
    <script src="/static/js/engine.js"></script>

</body>