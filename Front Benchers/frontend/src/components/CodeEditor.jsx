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
        height="450px"
        language="python"
        value={code}
        onChange={handleEditorChange}
        theme="vs-dark"
        options={{
          fontSize: 14,
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
              { token: 'comment', foreground: '9AA3B2', fontStyle: 'italic' },
              { token: 'keyword', foreground: 'FF8A3D' },
              { token: 'string', foreground: '4FD8B5' },
              { token: 'number', foreground: 'FF8A3D' },
              { token: 'function', foreground: 'E7E9EE' },
              { token: 'variable', foreground: 'E7E9EE' },
              { token: 'type', foreground: '4FD8B5' },
              { token: 'operator', foreground: 'FF5C5C' },
            ],
            colors: {
              'editor.background': '#0E1117',
              'editor.foreground': '#E7E9EE',
              'editor.lineHighlightBackground': '#14171F',
              'editor.selectionBackground': '#FF8A3D33',
              'editorCursor.foreground': '#FF8A3D',
              'editorLineNumber.foreground': '#3A3F52',
              'editorLineNumber.activeForeground': '#9AA3B2',
              'editor.selectionHighlightBackground': '#FF8A3D1A',
              'editorBracketMatch.background': '#FF8A3D22',
              'editorBracketMatch.border': '#FF8A3D44',
              'editorIndentGuide.background': '#1A1E2A',
              'editorIndentGuide.activeBackground': '#242836',
              'scrollbar.shadow': '#00000000',
              'scrollbarSlider.background': '#24283666',
              'scrollbarSlider.hoverBackground': '#9AA3B244',
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
