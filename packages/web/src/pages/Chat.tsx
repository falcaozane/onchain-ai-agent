import React, { useState } from "react";
import { useParams } from "react-router-dom";

function ChatPage() {
  // Retrieve agentId from the URL
  const { agentId } = useParams();
  // Mock data for the AI agent
  const agentInfo = {
    name: "Agent Alpha",
    walletAddress: "0x1234...abcd",
    agentBalance: "0.005 ETH",
    vaultBalance: "1.23 ETH",
    vaultAddress: "0xabcd...1234",
  };

  // State for chat messages
  const [messages, setMessages] = useState([
    { sender: "AI Agent", text: "Hello! How can I assist you today?" },
  ]);
  const [input, setInput] = useState("");

  // Function to handle sending a message
  const handleSendMessage = () => {
    if (!input.trim()) return;

    // Add the user's message to the chat
    setMessages((prev) => [...prev, { sender: "User", text: input }]);

    // Simulate an AI agent response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "AI Agent", text: "Let me process that for you." },
      ]);
    }, 1000);

    // Clear the input field
    setInput("");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Navigation */}
      <nav className="w-full bg-slate-700 p-4">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-white text-lg font-semibold">On-chain AI Agent Platform</h1>
            <ul className="flex gap-4">
                <li>
                    <a href="/" className="text-white hover:underline">
                    Home
                    </a>
                </li>
                <li>
                    <a href="/ai" className="text-white hover:underline">
                    AIs
                    </a>
                </li>
                <li>
                    <a href="/portfolio" className="text-white hover:underline">
                    Portfolio
                    </a>
                </li>
            </ul>
            <div>
              <w3m-button />
            </div>
          </div>
        </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6 flex flex-col flex-grow">
        {/* Agent Information */}
        <div className="bg-white shadow-lg rounded-lg p-4 mb-6">
          <h2 className="text-xl font-bold text-gray-800">Agent Details</h2>
          <div className="mt-2">
            <p>
              <span className="font-medium text-gray-700">Name:</span> {agentInfo.name}
            </p>
            <p>
              <span className="font-medium text-gray-700">Wallet Address:</span>{" "}
              <span className="text-blue-600">{agentInfo.walletAddress}</span>
            </p>
            <p>
              <span className="font-medium text-gray-700">Agent Balance:</span> {agentInfo.agentBalance}
            </p>
            <p>
              <span className="font-medium text-gray-700">Vault Balance:</span> {agentInfo.vaultBalance}
            </p>
            <p>
              <span className="font-medium text-gray-700">Vault Address:</span>{" "}
              <span className="text-blue-600">{agentInfo.vaultAddress}</span>
            </p>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-grow bg-white shadow-lg rounded-lg overflow-y-auto p-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === "User" ? "justify-end" : "justify-start"
              } mb-4`}
            >
              <div
                className={`${
                  message.sender === "User"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-800"
                } max-w-xs p-3 rounded-lg`}
              >
                <p>{message.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div className="mt-4 flex">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSendMessage();
                }
            }}
            className="flex-grow p-3 border border-gray-300 rounded-l-lg focus:outline-none"
          />
          <button
            onClick={handleSendMessage}
            className="bg-blue-600 text-white px-6 rounded-r-lg hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
