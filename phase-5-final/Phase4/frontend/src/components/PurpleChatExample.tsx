// ChatGPT-style Light Purple AI Chat UI
// Drop this into a Vite + React + Tailwind project

import { useState } from "react";
import { Send } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "ai", text: "Hello! I am your AI Todo Assistant 🤖" },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((m) => [...m, { role: "user", text: input }]);
    setInput("");

    setTimeout(() => {
      setMessages((m) => [...m, { role: "ai", text: "Got it! ✨" }]);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-100 to-purple-200 flex justify-center items-center">
      <div className="w-full max-w-3xl h-[90vh] bg-white/70 backdrop-blur-xl rounded-2xl shadow-xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="p-4 border-b flex items-center gap-3 bg-purple-50">
          <div className="w-10 h-10 rounded-full bg-purple-400 flex items-center justify-center text-white font-bold">🤖</div>
          <div>
            <h2 className="font-semibold text-purple-900">Todo AI Assistant</h2>
            <p className="text-xs text-purple-600">Online • Smart Mode</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
                m.role === "user"
                  ? "ml-auto bg-purple-500 text-white"
                  : "mr-auto bg-purple-100 text-purple-900 border border-purple-200"
              }`}
            >
              {m.text}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-purple-50 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask me to manage your tasks..."
            className="flex-1 px-4 py-3 rounded-xl border border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 bg-white/80"
          />
          <button
            onClick={sendMessage}
            className="w-12 h-12 rounded-xl bg-purple-500 hover:bg-purple-600 text-white flex items-center justify-center transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}