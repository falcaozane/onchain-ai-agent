import { useEffect, useState } from 'react';

import { useWallet } from '../hooks/useWallet';
import { createAgent } from '../services/ai-agent';

function MainPage() {
    const { createVault, deposit, withdraw, grant, revoke, topup, vaultAddress } = useWallet();

    const [vault, setVault] = useState<string>('');
    const [amount, setAmount] = useState<number>(0);
    const [, setAgent] = useState(null);
    const [agentAddress, setAgentAddress] = useState<string>('');

    const handleCreateAgent = async () => {
        const name = "DeFi AI Agent";
        const instructions = "Automate DeFi tasks";
        const response = await createAgent(name, instructions);
        console.log(response);
        setAgent(response);
        setAgentAddress(response.agent.wallet);
    }

    useEffect(() => {
        setVault(vaultAddress);
    }, [vaultAddress]);

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
        <div className="container mx-auto mt-10 px-4 py-3">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-gray-800"> Leverage AI to automate DeFi tasks and create unique meme tokens effortlessly.</h1>
            {/* <p className="text-lg text-gray-600 mt-2">
              Leverage AI to automate DeFi tasks and create unique meme tokens effortlessly.
            </p> */}
          </div>
  
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* DeFi Section */}
            <div className="bg-white p-6 shadow-lg rounded-lg">
              <h2 className="text-2xl font-semibold text-gray-800 border-b pb-2 mb-4">DeFi Automation</h2>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-700">1. Create your first vault</h3>
                  {vault.length === 0 || vaultAddress.length === 0 ? (
                    <button
                        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        onClick={() => createVault()}
                    >
                        Create Vault
                    </button>
                    ) : (
                    <button
                        className="mt-2 px-4 py-2 bg-gray-400 text-white rounded"
                        disabled
                    >
                        Vault Created
                    </button>
                )}
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-700">2. Deposit in vault</h3>
                  <div className="flex mt-2 gap-2">
                    <input
                      type="text"
                      placeholder="Enter amount"
                      className="flex-1 p-2 border border-gray-300 rounded"
                      onChange={(e) => setAmount(Number(e.target.value))}
                    />
                    <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700" onClick={() => deposit(amount)}>
                      Deposit USDC
                    </button>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-700">
                    3. Create your AI Agent Assistance
                  </h3>
                  <div className="flex mt-2 gap-2">
                    <input
                      type="text"
                      placeholder="Enter Agent Name"
                      className="flex-1 p-2 border border-gray-300 rounded"
                    />
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700" onClick={(() => handleCreateAgent())}>
                      Create Agent
                    </button>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-700">
                    4. Grant Permission to AI Agent
                  </h3>
                  <div className="flex gap-4 mt-2">
                    <button className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700" onClick={() => grant(agentAddress)}>
                      Grant Permission
                    </button>
                    <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" disabled>
                      Revoke Permission
                    </button>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-700">
                    5. Topup native token to AI Agent
                  </h3>
                  <button className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700" onClick={() => topup(agentAddress)}>
                    Topup 0.001 ETH
                  </button>
                </div>
              </div>
            </div>
  
            {/* AI x Meme Section */}
            <div className="bg-white p-6 shadow-lg rounded-lg">
              <h2 className="text-2xl font-semibold text-gray-800 border-b pb-2 mb-4">AI x Meme Creation</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-700">1. Create your AI x Meme token</h3>
                  <div className="grid grid-cols-1 gap-3">
                    <input
                      type="text"
                      placeholder="Enter token name"
                      className="p-2 border border-gray-300 rounded"
                    />
                    <input
                      type="text"
                      placeholder="Enter token symbol"
                      className="p-2 border border-gray-300 rounded"
                    />
                    <input
                      type="text"
                      placeholder="Enter token supply"
                      className="p-2 border border-gray-300 rounded"
                    />
                    <input
                      type="text"
                      placeholder="Enter AI agent name"
                      className="p-2 border border-gray-300 rounded"
                    />
                    <textarea
                      placeholder="Enter AI agent instruction"
                      className="p-2 border border-gray-300 rounded"
                    />
                  </div>
                  <button className="mt-4 px-4 py-2 bg-pink-600 text-white rounded hover:bg-pink-700">
                    Create AI Agent & Token
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
}
  
export default MainPage;
  