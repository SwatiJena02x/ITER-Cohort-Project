import Editor from '@monaco-editor/react';
import './CodeEditor.css';

const CodeEditor = ({ code, onChange }) => {
  const handleEditorChange = (value) => {
    onChange(value || '');
  };

  return (
    <div className="code-editor" id="code-editor">
      <div className="editor-header">
        <div className="editor-dots">
          <span className="dot dot-red"></span>
          <span className="dot dot-yellow"></span>
          <span className="dot dot-green"></span>
        </div>
        <span className="editor-label">solution.py</span>
      </div>
      <Editor
        height="calc(100vh - 430px)"
        language="python"
        value={code}
        onChange={handleEditorChange}
        theme="vs-dark"
        options={{
          fontSize: 15,
          fontFamily: "'JetBrains Mono', monospace",
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          padding: { top: 16, bottom: 16 },
          lineNumbers: 'on',
          renderLineHighlight: 'line',
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          smoothScrolling: true,
          bracketPairColorization: { enabled: true },
          autoClosingBrackets: 'always',
          autoClosingQuotes: 'always',
          tabSize: 4,
          wordWrap: 'on',
          suggestOnTriggerCharacters: true,
          quickSuggestions: true,
        }}
        beforeMount={(monaco) => {
          // Define custom theme matching our design tokens
          monaco.editor.defineTheme('dsa-coach-dark', {
            base: 'vs-dark',
            inherit: true,
            rules: [
              { token: 'comment', foreground: '7A8394', fontStyle: 'italic' },
              { token: 'keyword', foreground: 'D4793A' },
              { token: 'string', foreground: '44B899' },
              { token: 'number', foreground: 'D4AD42' },
              { token: 'function', foreground: 'C8CCD4' },
              { token: 'variable', foreground: 'C8CCD4' },
              { token: 'type', foreground: '44B899' },
              { token: 'operator', foreground: 'D45454' },
            ],
            colors: {
              'editor.background': '#0C0E14',
              'editor.foreground': '#C8CCD4',
              'editor.lineHighlightBackground': '#13161E',
              'editor.selectionBackground': '#D4793A22',
              'editorCursor.foreground': '#C8CCD4',
              'editorLineNumber.foreground': '#2A2E3A',
              'editorLineNumber.activeForeground': '#7A8394',
              'editor.selectionHighlightBackground': '#D4793A11',
              'editorBracketMatch.background': '#D4793A15',
              'editorBracketMatch.border': '#D4793A30',
              'editorIndentGuide.background': '#1A1D26',
              'editorIndentGuide.activeBackground': '#1E2230',
              'scrollbar.shadow': '#00000000',
              'scrollbarSlider.background': '#1E223044',
              'scrollbarSlider.hoverBackground': '#7A839433',
            },
          });
        }}
        onMount={(editor, monaco) => {
          monaco.editor.setTheme('dsa-coach-dark');
          editor.focus();
        }}
      />
    </div>
  );
};

export default CodeEditor;
