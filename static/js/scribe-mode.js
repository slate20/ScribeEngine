// PART A: Define the base mode for handling HTML with Jinja inside it.
// This uses the multiplexing addon to switch between htmlmixed and jinja2.
CodeMirror.defineMode("jinja2-htmlmixed", function(config) {
    return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "htmlmixed"), {
            open: "{%",
            close: "%}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true // This is the key fix to highlight code WITHIN the block
        }, {
            open: "{{",
            close: "}}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true // This is the key fix to highlight code WITHIN the block
        }, {
            open: "{#",
            close: "#}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true // This is the key fix to highlight code WITHIN the block
        // }, {
        //     open: "{$",
        //     close: "$}",
        //     mode: CodeMirror.getMode(config, "python"),
        //     parseDelimiters: true
        // }, {
        //     open: "{$-",
        //     close: "-$}",
        //     mode: CodeMirror.getMode(config, "python"),
        //     parseDelimiters: true
        // }
    );
});

// PART B: Define the Scribe overlay that sits on top of our new base mode.
var scribeOverlay = {
    token: function(stream, state) {
        //Highlight Scribe Python delimiters
        if (stream.match("{$") || stream.match("$}") || stream.match("{$-") || stream.match("-$}")) {
            return "scribe-delimiter";
        }

        if (stream.sol() && stream.match("::")) {
            stream.eatWhile(/[\w\- ]/);
            return "keyword";
        }
        const prevChar = stream.string.charAt(stream.pos - 1);
        const atStartOfToken = stream.sol() || /\s/.test(prevChar);
        if (atStartOfToken && stream.match("#")) {
            stream.eatWhile(/[\w-]/);
            return "tag";
        }
        if (stream.match("[[")) {
            let isActionLink = false;
            let ch;
            while ((ch = stream.next()) != null) {
                if (ch == "|" && stream.peek() == "|") { isActionLink = true; }
                if (ch == "]" && stream.peek() == "]") { stream.next(); break; }
            }
            return isActionLink ? "link-action" : "link";
        }
        stream.next();
        return null;
    }
};

// PART C: Define the final "scribe" mode.
// It uses our new "jinja2-htmlmixed" mode as the base and applies the scribe overlay.
CodeMirror.defineMode("scribe", function(config) {
    return CodeMirror.overlayMode(CodeMirror.getMode(config, "jinja2-htmlmixed"), scribeOverlay);
});
