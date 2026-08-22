import React, { useState } from 'react';

const MarketHealthDashboard = () => {
  const [marketId, setMarketId] = useState('BTC-PERP');
  const [marketHealth, setMarketHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMarketHealth = async () => {
    setLoading(true);
    setError(null);
    setMarketHealth(null);

    try {
      const response = await fetch(`http://localhost:8000/api/market-health?market_id=${marketId}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch market health');
      }

      const data = await response.json();
      setMarketHealth(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-xl mb-8">
      <h2 className="text-3xl font-semibold text-purple-300 mb-6">Market Health Dashboard</h2>

      <div className="flex items-center space-x-4 mb-8">
        <input
          type="text"
          value={marketId}
          onChange={(e) => setMarketId(e.target.value)}
          placeholder="Enter Market ID (e.g., BTC-PERP)"
          className="flex-1 shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline bg-gray-700 border-gray-600"
        />
        <button
          onClick={fetchMarketHealth}
          className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors duration-300"
          disabled={loading}
        >
          {loading ? 'Fetching...' : 'Fetch Market Health'}
        </button>
      </div>

      {error && <div className="bg-red-800 text-white p-4 rounded-md mb-4">Error: {error}</div>}

      {marketHealth && (
        <div className="mt-8 border-t border-gray-700 pt-8">
          <h3 className="text-2xl font-semibold text-purple-200 mb-4">Market Details for {marketHealth.market_id}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-700 p-4 rounded-md">
              <p className="text-gray-300 text-lg mb-2">Funding Anomaly Z-score:</p>
              <p className="text-blue-400 text-3xl font-bold font-mono">{marketHealth.funding_anomaly_zscore.toFixed(2)}</p>
            </div>
            <div className="bg-gray-700 p-4 rounded-md">
              <p className="text-gray-300 text-lg mb-2">Wash Trade Adjusted Volume (%):</p>
              <p className="text-teal-400 text-3xl font-bold font-mono">{(marketHealth.wash_trade_adjusted_volume * 100).toFixed(2)}%</p>
            </div>
          </div>

          {marketHealth.top_signals && marketHealth.top_signals.length > 0 && (
            <div className="bg-gray-700 p-4 rounded-md mt-6">
              <h4 className="text-xl font-semibold text-purple-200 mb-3">Top Signals</h4>
              <div className="space-y-2">
                {marketHealth.top_signals.map((signal, index) => (
                  <div key={index} className="flex items-center justify-between text-gray-300">
                    <span className="font-bold capitalize">{signal.signal_type.replace(/_/g, ' ')}:</span>
                    <span className="font-mono text-yellow-400">Decay Score {signal.decay_score.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MarketHealthDashboard;


