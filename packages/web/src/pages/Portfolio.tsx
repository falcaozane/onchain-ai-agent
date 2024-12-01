import React, { useRef, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

function PortfolioPage() {
  const chartRef = useRef(null); // Reference to the chart instance

  // Mock data for vaults
  const vaultData = [
    { name: "Vault 1", balance: 2.5 },
    { name: "Vault 2", balance: 1.8 },
    { name: "Vault 3", balance: 0.7 },
  ];

  // Preparing data for the pie chart
  const chartData = {
    labels: vaultData.map((vault) => vault.name),
    datasets: [
      {
        label: "Vault Balances",
        data: vaultData.map((vault) => vault.balance),
        backgroundColor: ["#4CAF50", "#FF9800", "#2196F3"], // Colors for each slice
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    plugins: {
      legend: {
        position: "bottom",
      },
    },
    responsive: true,
    maintainAspectRatio: false, // Fix potential canvas reuse issue
  };

  // Cleanup Effect for Chart
  useEffect(() => {
    return () => {
      // Destroy the chart instance if it exists
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
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
      <div className="container mx-auto px-4 py-6">
        <h2 className="text-3xl font-bold text-gray-800 text-center mb-6">
          Your Vault Overview
        </h2>

        {/* Chart and Details */}
        <div className="flex flex-col lg:flex-row gap-8 justify-center items-center">
          {/* Pie Chart */}
          <div className="w-full lg:w-1/2" style={{ height: "300px" }}>
            <Pie ref={chartRef} data={chartData} options={chartOptions} />
          </div>

          {/* Vault Details */}
          <div className="w-full lg:w-1/2 bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              Vault Details
            </h3>
            <ul>
              {vaultData.map((vault, index) => (
                <li
                  key={index}
                  className="flex justify-between py-2 border-b last:border-b-0"
                >
                  <span className="text-gray-700 font-medium">{vault.name}</span>
                  <span className="text-gray-600">{vault.balance} ETH</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PortfolioPage;
