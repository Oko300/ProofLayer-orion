import React, { useState } from 'react';
import SignalCard from './SignalCard';
import PositionCostCard from './PositionCostCard';
import MarketHealthDashboard from './MarketHealthDashboard';

const API_BASE = "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState('Signal Verifier');

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-gray-100 p-8 font-mono">
      <h1 className="text-5xl font-bold text-center mb-10 text-purple-400">ProofLayer Analytics</h1>
      
      <div className="flex justify-center mb-8">
        <button
          className={`px-6 py-3 mx-2 rounded-lg text-lg font-medium transition-colors duration-300
            ${activeTab === 'Signal Verifier' ? 'bg-purple-600 text-white shadow-lg' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
          onClick={() => setActiveTab('Signal Verifier')}
        >
          Signal Verifier
        </button>
        <button
          className={`px-6 py-3 mx-2 rounded-lg text-lg font-medium transition-colors duration-300
            ${activeTab === 'Position Cost' ? 'bg-purple-600 text-white shadow-lg' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
          onClick={() => setActiveTab('Position Cost')}
        >
          Position Cost
        </button>
        <button
          className={`px-6 py-3 mx-2 rounded-lg text-lg font-medium transition-colors duration-300
            ${activeTab === 'Market Health' ? 'bg-purple-600 text-white shadow-lg' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
          onClick={() => setActiveTab('Market Health')}
        >
          Market Health
        </button>
      </div>

      <div className="max-w-7xl mx-auto">
        {activeTab === 'Signal Verifier' && <SignalCard />}
        {activeTab === 'Position Cost' && <PositionCostCard />}
        {activeTab === 'Market Health' && <MarketHealthDashboard />}
      </div>
    </div>
  );
}

export default App;


