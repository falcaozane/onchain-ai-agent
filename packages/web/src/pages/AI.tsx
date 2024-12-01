import React, { useState, useEffect } from "react";

function AIsPage() {
  // Mock data for the AI agents
  const [agents, setAgents] = useState([
    {
      name: "Agent Alpha",
      instruction: "Manage DeFi vault transactions",
      walletBalance: "0.005 ETH",
      vaultBalance: "1.50 ETH",
    },
    {
      name: "Agent Beta",
      instruction: "Optimize yield farming strategies",
      walletBalance: "0.005 ETH",
      vaultBalance: "1.50 ETH",
    },
    {
      name: "Agent Gamma",
      instruction: "Execute on-chain token swaps",
      walletBalance: "0.005 ETH",
      vaultBalance: "1.50 ETH",
    },
  ]);

  useEffect(() => {
    // Fetch the list of agents from the backend (mocked here)
    // Example:
    // fetch('/api/agents')
    //   .then((res) => res.json())
    //   .then((data) => setAgents(data));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
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
      <div className="container mx-auto mt-10 px-4">
        <h2 className="text-3xl font-bold text-gray-800 text-center mb-6">
          AI Agent List
        </h2>
        {agents.length === 0 ? (
          <p className="text-lg text-gray-600 text-center">
            You haven’t created any AI agents yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <div
                key={index}
                className="bg-white p-6 shadow-lg rounded-lg hover:shadow-xl transition"
              >
                <h3 className="text-xl font-semibold text-gray-700">
                  {agent.name}
                </h3>
                <p className="text-gray-600 mt-2">
                  <span className="font-medium">Instruction:</span>{" "}
                  {agent.instruction}
                </p>
                <p className="text-gray-600 mt-2">
                  <span className="font-medium">Wallet Balance:</span>{" "}
                  {agent.walletBalance}
                </p>
                <p className="text-gray-600 mt-2">
                  <span className="font-medium">Vault Balance:</span>{" "}
                  {agent.vaultBalance}
                </p>
                <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Chat
                </button>
                <button className="ml-5 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                    Revoke Permission
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AIsPage;
