'use client';

import React from 'react';
import Editor from '@monaco-editor/react';

interface CodeViewerProps {
  code: string;
  language: string;
  theme?: string;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, language, theme = 'vs-dark' }) => {
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
      />
    </div>
  );
};

export default CodeViewer;
