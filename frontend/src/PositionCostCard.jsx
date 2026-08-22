import React, { useState } from 'react';

const PositionCostCard = () => {
  const [formData, setFormData] = useState({
    market: 'BTC-PERP',
    size_usd: 10000,
    leverage: 10,
    entry_price: 30000,
    current_price: 30500,
    funding_rate_8h: 0.0001,
    mark_fill_spread_pct: 0.0005,
    insurance_fund_health: 0.9,
    entry_timestamp: Math.floor(Date.now() / 1000) - 86400, // 24 hours ago
    current_timestamp: Math.floor(Date.now() / 1000),
  });

  const [costResponse, setCostResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseFloat(value) : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setCostResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/position-cost', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong');
      }

      const data = await response.json();
      setCostResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'DO_NOT_ACT': return 'bg-red-600';
      case 'CAUTION': return 'bg-yellow-500';
      case 'ACT': return 'bg-green-600';
      default: return 'bg-gray-500';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const renderADLGauge = (adlScore) => {
    const circumference = 2 * Math.PI * 45; // r=45 for a 100x100 svg
    const offset = circumference - (adlScore / 10) * circumference;

    let colorClass = 'text-green-500'; // Default for low ADL
    if (adlScore >= 7) {
      colorClass = 'text-red-500';
    } else if (adlScore >= 4) {
      colorClass = 'text-yellow-500';
    }

    return (
      <div className="relative w-24 h-24">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            className="text-gray-700"
            strokeWidth="10"
            stroke="currentColor"
            fill="transparent"
            r="45"
            cx="50"
            cy="50"
          />
          {/* Progress circle */}
          <circle
            className={colorClass}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="45"
            cx="50"
            cy="50"
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div className={`absolute top-0 left-0 w-full h-full flex items-center justify-center text-xl font-bold font-mono ${colorClass}`}>
          {adlScore !== undefined ? adlScore.toFixed(1) : 'N/A'}
        </div>
      </div>
    );
  };


  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-xl mb-8">
      <h2 className="text-3xl font-semibold text-purple-300 mb-6">Position Cost Analysis</h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {Object.keys(formData).map((key) => (
          <div key={key}>
            <label htmlFor={key} className="block text-gray-300 text-sm font-bold mb-2 capitalize">
              {key.replace(/_/g, ' ')}:
            </label>
            <input
              type={typeof formData[key] === 'number' ? 'number' : 'text'}
              id={key}
              name={key}
              value={formData[key]}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline bg-gray-700 border-gray-600"
              step={key.includes('rate') || key.includes('pct') ? "0.00001" : "any"}
            />
          </div>
        ))}
        <div className="lg:col-span-3 text-center">
          <button
            type="submit"
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors duration-300"
            disabled={loading}
          >
            {loading ? 'Calculating...' : 'Submit to /position-cost API'}
          </button>
        </div>
      </form>

      {error && <div className="bg-red-800 text-white p-4 rounded-md mb-4">Error: {error}</div>}

      {costResponse && (
        <div className="mt-8 border-t border-gray-700 pt-8">
          <h3 className="text-2xl font-semibold text-purple-200 mb-4">Analysis Results</h3>

          {/* Daily Cost Calm vs Stressed */}
          <div className="flex flex-col md:flex-row justify-around items-center mb-6 bg-gray-700 p-4 rounded-md">
            <div className="text-center m-4">
              <p className="text-gray-300 text-lg mb-2">Daily Cost (Calm)</p>
              <p className="text-green-400 text-4xl font-bold font-mono">{formatCurrency(costResponse.daily_cost_calm_usd)}</p>
            </div>
            <div className="text-center m-4">
              <p className="text-gray-300 text-lg mb-2">Daily Cost (Stressed)</p>
              <p className="text-red-400 text-4xl font-bold font-mono">{formatCurrency(costResponse.daily_cost_stress_usd)}</p>
            </div>
          </div>

          {/* Effective Liquidation Price */}
          <div className="mb-6 flex items-center justify-between bg-gray-700 p-4 rounded-md">
            <div>
              <p className="text-gray-300 text-lg">Effective Liquidation Price:</p>
              <p className="text-blue-400 text-3xl font-bold font-mono">{formatCurrency(costResponse.liquidation_price_effective)}</p>
            </div>
            {costResponse.price_drift_to_liquidation && (
                <div className="flex items-center">
                    <span className="text-gray-400 text-sm mr-2">Drift:</span>
                    <span className={`text-xl font-bold font-mono ${costResponse.price_drift_to_liquidation > 0 ? 'text-red-500' : 'text-green-500'}`}>
                        {costResponse.price_drift_to_liquidation > 0 ? '▲' : '▼'} {Math.abs(costResponse.price_drift_to_liquidation).toFixed(2)}%
                    </span>
                </div>
            )}
          </div>


          {/* ADL Score & Edge/Cost Ratio */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-700 p-4 rounded-md flex flex-col items-center justify-center">
              <p className="text-gray-300 text-lg mb-2">ADL Score</p>
              {renderADLGauge(costResponse.adl_score)}
            </div>
            <div className="bg-gray-700 p-4 rounded-md flex flex-col items-center justify-center">
              <p className="text-gray-300 text-lg mb-2">Edge/Cost Ratio</p>
              <p className="text-teal-400 text-3xl font-bold font-mono mb-4">{(costResponse.edge_cost_ratio * 100).toFixed(2)}%</p>
              <span className={`px-4 py-2 rounded-full text-sm font-bold ${getRecommendationColor(costResponse.recommendation)}`}>
                {costResponse.recommendation}
              </span>
            </div>
          </div>

          {/* Detailed Metrics (Optional - as needed) */}
          <div className="bg-gray-700 p-4 rounded-md">
            <h4 className="text-xl font-semibold text-purple-200 mb-3">Detailed Metrics</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-gray-300 text-sm">
                <p>Entry Margin (USD): <span className="font-mono text-white">{formatCurrency(costResponse.entry_margin_usd)}</span></p>
                <p>Required Initial Margin (%): <span className="font-mono text-white">{(costResponse.required_initial_margin_pct * 100).toFixed(2)}%</span></p>
                <p>Maintenance Margin (USD): <span className="font-mono text-white">{formatCurrency(costResponse.maintenance_margin_usd)}</span></p>
                <p>Required Maintenance Margin (%): <span className="font-mono text-white">{(costResponse.required_maintenance_margin_pct * 100).toFixed(2)}%</span></p>
                <p>Borrow Interest Rate (%): <span className="font-mono text-white">{(costResponse.borrow_interest_rate_pct * 100).toFixed(4)}%</span></p>
                <p>Funding Cost (Daily USD): <span className="font-mono text-white">{formatCurrency(costResponse.funding_cost_daily_usd)}</span></p>
                <p>Liquidation Fee (USD): <span className="font-mono text-white">{formatCurrency(costResponse.liquidation_fee_usd)}</span></p>
                <p>ADL Priority: <span className="font-mono text-white">{costResponse.adl_priority}</span></p>
                <p>Settlement Escalation Multiplier: <span className="font-mono text-white">{costResponse.settlement_escalation_multiplier.toFixed(2)}x</span></p>
                <p>Margin Drained (USD): <span className="font-mono text-white">{formatCurrency(costResponse.margin_drained_usd)}</span></p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PositionCostCard;

