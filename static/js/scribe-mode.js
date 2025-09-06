CodeMirror.defineMode("scribe", function(config, parserConfig) {
  var scribeOverlay = {
    token: function(stream, state) {
      if (stream.match("::")) {
        stream.eatWhile(/[\w-]/);
        return "keyword"; // Passage definition
      }
      if (stream.match("#")) {
        stream.eatWhile(/[\w-]/);
        return "tag";
      }
      if (stream.match("[[")) {
        let isActionLink = false;
        let ch;
        while ((ch = stream.next()) != null) {
          if (ch == "|" && stream.peek() == "|") {
            isActionLink = true;
          }
          if (ch == "]" && stream.peek() == "]") {
            stream.next(); // consume the second ']'
            break;
          }
        }
        return isActionLink ? "link-action" : "link";
      }
      if (stream.match("{#")) {
        while ((ch = stream.next()) != null)
          if (ch == "#" && stream.next() == "}") break;
        return "comment";
      }
      
      while (stream.next() != null && !stream.match("::", false) && !stream.match("#", false) && !stream.match("[[", false) && !stream.match("{#", false)) {}
      return null;
    }
  };

  return CodeMirror.overlayMode(CodeMirror.getMode(config, "jinja2"), scribeOverlay);
});
