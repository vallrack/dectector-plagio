'use client';

import React from 'react';
import Editor from '@monaco-editor/react';

interface CodeViewerProps {
  code: string;
  language: string;
  theme?: string;
  highlights?: string[];
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, language, theme = 'vs-dark', highlights = [] }) => {
  // Mapeo de extensiones a lenguajes compatibles con Monaco
  const getMonacoLanguage = (ext: string) => {
    const map: { [key: string]: string } = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'html': 'html',
      'css': 'css',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c'
    };
    return map[ext.toLowerCase()] || 'plaintext';
  };

  return (
    <div className="w-full h-full border border-white/10 rounded-2xl overflow-hidden">
      <Editor
        height="100%"
        language={getMonacoLanguage(language)}
        value={code}
        theme={theme}
        options={{
          readOnly: true,
          minimap: { enabled: true },
          fontSize: 14,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          padding: { top: 16, bottom: 16 },
          lineNumbers: 'on',
          renderWhitespace: 'none',
          smoothScrolling: true,
          cursorStyle: 'line',
          wordWrap: 'on'
        }}
        onMount={(editor, monaco) => {
          if (highlights && highlights.length > 0) {
            const decorations: any[] = [];
            
            highlights.forEach(phrase => {
              if (!phrase || typeof phrase !== 'string') return;
              const model = editor.getModel();
              if (model) {
                const matches = model.findMatches(phrase, true, false, false, null, true);
                matches.forEach(match => {
                  decorations.push({
                    range: match.range,
                    options: {
                      isWholeLine: true,
                      className: 'ai-highlight-line',
                      glyphMarginClassName: 'ai-highlight-glyph',
                      inlineClassName: 'ai-highlight-text',
                      hoverMessage: { value: 'Patrón típico de generación IA' }
                    }
                  });
                });
              }
            });

            editor.deltaDecorations([], decorations);
          }
        }}
      />
      <style jsx global>{`
        .ai-highlight-line {
          background-color: rgba(239, 68, 68, 0.15) !important;
          border-left: 3px solid #ef4444 !important;
        }
        .ai-highlight-text {
          text-decoration: underline wavy #ef4444;
          font-weight: bold;
        }
        .ai-highlight-glyph {
          background-color: #ef4444;
          width: 5px !important;
          margin-left: 5px;
        }
      `}</style>
    </div>
  );
};

export default CodeViewer;
