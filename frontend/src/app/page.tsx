'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data && data !== '[DONE]') {
              setResponse(prev => prev + data);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error: Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-900 text-white">
      <h1 className="text-2xl font-bold mb-4">Parallax AI - Round Trip Test</h1>

      <div className="max-w-2xl">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="w-full p-3 bg-gray-800 rounded border border-gray-700 mb-4"
          rows={3}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 bg-teal-600 rounded hover:bg-teal-700 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>

        {response && (
          <div className="mt-6 p-4 bg-gray-800 rounded">
            <h2 className="text-sm text-gray-400 mb-2">Response:</h2>
            <div className="whitespace-pre-wrap">{response}</div>
          </div>
        )}
      </div>
    </main>
  );
}
