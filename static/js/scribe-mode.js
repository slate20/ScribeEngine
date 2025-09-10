// PART A: Define the new base multiplexer for the Scribe language.
// This mode understands the file as plain text with islands of Jinja2 and Python.
CodeMirror.defineMode("scribe-base", function(config) {
    return CodeMirror.multiplexingMode(
        CodeMirror.getMode(config, "htmlmixed"), // The base mode is plain text.
        // Rule for Jinja2 statements {% ... %}
        {
            open: "{%",
            close: "%}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true
        },
        // Rule for Jinja2 expressions {{ ... }}
        {
            open: "{{",
            close: "}}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true
        },
        // Rule for Jinja2 comments {# ... #}
        {
            open: "{#",
            close: "#}",
            mode: CodeMirror.getMode(config, "jinja2"),
            parseDelimiters: true
        },
        // Rule for Scribe Engine inline Python {$ ... $}
        {
            open: "{$",
            close: "$}",
            mode: CodeMirror.getMode(config, "python"),
            parseDelimiters: false
        },
        // Rule for Scribe Engine Python blocks {$ - ... -$ }
        {
            open: "{$-",
            close: "-$}",
            mode: CodeMirror.getMode(config, "python"),
            parseDelimiters: false
        }
    );
});


// PART B: Define the Scribe overlay that sits on top of our new base mode.
// This handles syntax unique to Scribe, like passage definitions and links.
var scribeOverlay = {
    token: function(stream, state) {
		//Highlight Scribe Python delimiters
        if (stream.match("{$") || stream.match("$}") || stream.match("{$-") || stream.match("-$}")) {
            return "scribe-delimiter";
        }

        // Highlight ::passage definitions at the start of a line
        if (stream.sol() && stream.match("::")) {
            stream.eatWhile(/[\w\- ]/);
            return "keyword"; // This is a special style for passage names
        }

        // Highlight #tags
        const prevChar = stream.string.charAt(stream.pos - 1);
        const atStartOfToken = stream.sol() || /\s/.test(prevChar);
        if (atStartOfToken && stream.match("#")) {
            stream.eatWhile(/[\w-]/);
            return "tag";
        }

        // Highlight [[links]] and checks for the -> arrow
        if (stream.match("[[")) {
            let isActionLink = false;
            let ch;
            while ((ch = stream.next()) != null) {
                // Check for the action delimiter ||
                if (ch == "|" && stream.peek() == "|") {
                    isActionLink = true;
                }
                // Check for the closing brackets
                if (ch == "]" && stream.peek() == "]") {
                    stream.next();
                    break;
                }
            }
            // Use different styles for links based on whether they have a target
            return isActionLink ? "link-action" : "link";
        }

        // Advance the stream if no custom Scribe token is found
        stream.next();
        return null;
    }
};


// PART C: Define the final "scribe" mode.
// It uses our new "scribe-base" mode and applies the overlay.
CodeMirror.defineMode("scribe", function(config) {
    return CodeMirror.overlayMode(CodeMirror.getMode(config, "scribe-base"), scribeOverlay);
});
