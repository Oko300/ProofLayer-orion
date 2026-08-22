import React, { useState } from 'react';

const SignalCard = () => {
  const [formData, setFormData] = useState({
    wallet_address: '0xAbc123DeF456',
    market: 'BTC-PERP',
    asset_price_history: '[100, 102, 101, 103, 105]',
    volume_history: '[1000, 1200, 1100, 1300, 1400]',
    trade_sizes: '[10, 12, 11, 13, 14]',
    funding_rates: '[0.0001, 0.00015, 0.00012, 0.00018, 0.0001]',
    social_sentiment_scores: '[0.6, 0.7, 0.65, 0.72, 0.68]',
    onchain_flows: '[10000, -5000, 20000, -10000, 15000]',
    source_data: '[{"id": "src1", "confidence": 0.8}, {"id": "src2", "confidence": 0.7}]'
  });

  const [signalResponse, setSignalResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSignalResponse(null);

    try {
      const parsedData = {
        ...formData,
        asset_price_history: JSON.parse(formData.asset_price_history),
        volume_history: JSON.parse(formData.volume_history),
        trade_sizes: JSON.parse(formData.trade_sizes),
        funding_rates: JSON.parse(formData.funding_rates),
        social_sentiment_scores: JSON.parse(formData.social_sentiment_scores),
        onchain_flows: JSON.parse(formData.onchain_flows),
        source_data: JSON.parse(formData.source_data),
      };

      const response = await fetch('http://localhost:8000/api/verify-signal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong');
      }

      const data = await response.json();
      setSignalResponse(data);
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

  const getConfidenceColor = (score) => {
    if (score > 0.7) return 'text-green-400';
    if (score > 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-xl mb-8">
      <h2 className="text-3xl font-semibold text-purple-300 mb-6">Signal Verifier</h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {Object.keys(formData).map((key) => (
          <div key={key}>
            <label htmlFor={key} className="block text-gray-300 text-sm font-bold mb-2 capitalize">
              {key.replace(/_/g, ' ')}:
            </label>
            <textarea
              id={key}
              name={key}
              value={formData[key]}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline bg-gray-700 border-gray-600"
              rows={key.includes('history') || key.includes('source_data') ? 3 : 1}
            />
          </div>
        ))}
        <div className="md:col-span-2 text-center">
          <button
            type="submit"
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors duration-300"
            disabled={loading}
          >
            {loading ? 'Verifying...' : 'Verify Signal'}
          </button>
        </div>
      </form>

      {error && <div className="bg-red-800 text-white p-4 rounded-md mb-4">Error: {error}</div>}


      {signalResponse && (
        <div className="mt-8 border-t border-gray-700 pt-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-700">
            <span className={`px-4 py-2 rounded-full text-sm font-bold ${getRecommendationColor(signalResponse.recommendation)}`}>
              {signalResponse.recommendation}
            </span>
            <span className={`text-3xl font-bold font-mono ${getConfidenceColor(signalResponse.confidence_score)}`}>
              Confidence: {(signalResponse.confidence_score * 100).toFixed(2)}%
            </span>
          </div>

          {/* Entity Section */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-purple-200 mb-3">Entity Analysis</h3>
            <p className="text-lg text-gray-300 mb-2">Wallet Address: <span className="font-mono text-blue-400">{signalResponse.wallet_address}</span></p>
            {signalResponse.attribution_analysis && signalResponse.attribution_analysis.label && (
              <p className="text-md text-gray-400 mb-4">
                Attributed as: <span className="font-bold text-teal-400">{signalResponse.attribution_analysis.label}</span> with <span className="font-mono">{(signalResponse.attribution_analysis.confidence * 100).toFixed(1)}%</span> confidence.
              </p>
            )}
            {signalResponse.attribution_analysis && signalResponse.attribution_analysis.probabilities && Object.keys(signalResponse.attribution_analysis.probabilities).length > 0 && (
              <div>
                <h4 className="text-md text-gray-300 mb-2">Attribution Probabilities:</h4>
                <div className="space-y-2">
                  {Object.entries(signalResponse.attribution_analysis.probabilities).map(([label, prob]) => (
                    <div key={label} className="flex items-center">
                      <span className="w-32 text-gray-400 text-sm capitalize mr-2">{label.replace(/_/g, ' ')}:</span>
                      <div className="flex-1 bg-gray-700 rounded-full h-4 relative overflow-hidden">
                        <div
                          className="h-full rounded-full bg-blue-500 transition-all duration-500 ease-out"
                          style={{ width: `${(prob * 100).toFixed(2)}%` }}
                        ></div>
                        <span className="absolute inset-0 flex items-center justify-center text-xs font-mono text-white">
                          {(prob * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>


          {/* Volume Integrity */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-purple-200 mb-3">Volume Integrity (KS Test & Z-score)</h3>
            {signalResponse.ks_test_results && (
              <div className="mb-4">
                <p className="text-gray-300 mb-2">
                  Wash Trade Detected: <span className={`font-bold ${signalResponse.ks_test_results.wash_trade_detected ? 'text-red-500' : 'text-green-500'}`}>
                    {signalResponse.ks_test_results.wash_trade_detected ? 'Yes' : 'No'}
                  </span>
                </p>
                <p className="text-gray-300 mb-2">Reported Volume: <span className="font-mono text-yellow-400">{(signalResponse.zscore_analysis.total_volume || 0).toLocaleString()}</span></p>
                <p className="text-gray-300 mb-4">KS-Adjusted Organic Volume: <span className="font-mono text-teal-400">{(signalResponse.ks_test_results.adjusted_organic_volume || 0).toLocaleString()}</span></p>

                <div className="flex items-center mb-2">
                  <span className="w-40 text-gray-400 text-sm mr-2">Reported Volume:</span>
                  <div className="flex-1 bg-gray-700 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="h-full rounded-full bg-yellow-500"
                      style={{ width: `100%` }}
                    ></div>
                    <span className="absolute inset-0 flex items-center justify-center text-sm font-mono text-white">
                      100%
                    </span>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className="w-40 text-gray-400 text-sm mr-2">Organic Volume:</span>
                  <div className="flex-1 bg-gray-700 rounded-full h-6 relative overflow-hidden">
                    <div
                      className="h-full rounded-full bg-teal-500 transition-all duration-500 ease-out"
                      style={{ width: `${(signalResponse.ks_test_results.adjusted_volume_pct * 100).toFixed(2)}%` || '0%'}}
                    ></div>
                     <span className="absolute inset-0 flex items-center justify-center text-sm font-mono text-white">
                      {(signalResponse.ks_test_results.adjusted_volume_pct * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
            {signalResponse.zscore_analysis && (
              <div className="mt-4">
                 <p className="text-gray-300 mb-2">Z-score Anomaly: <span className={`font-bold ${signalResponse.zscore_analysis.anomaly ? 'text-red-500' : 'text-green-500'}`}>
                    {signalResponse.zscore_analysis.anomaly ? 'Detected' : 'No Anomaly'}
                  </span></p>
                {signalResponse.zscore_analysis.anomaly && (
                  <p className="text-gray-300">Severity: <span className={`font-bold ${signalResponse.zscore_analysis.severity === 'high' ? 'text-red-500' : signalResponse.zscore_analysis.severity === 'medium' ? 'text-yellow-500' : 'text-green-500'}`}>{signalResponse.zscore_analysis.severity}</span></p>
                )}
              </div>
            )}
          </div>


          {/* Source Independence */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-purple-200 mb-3">Source Independence (Correlation)</h3>
            {signalResponse.correlation_analysis && (
              <div>
                <p className="text-gray-300 mb-2">Correlation R Value: <span className="font-mono text-blue-400">{signalResponse.correlation_analysis.r_value.toFixed(4)}</span></p>
                <p className="text-gray-300">Are Independent: <span className={`font-bold ${signalResponse.correlation_analysis.are_independent ? 'text-green-500' : 'text-red-500'}`}>
                  {signalResponse.correlation_analysis.are_independent ? 'Yes' : 'No'}
                </span></p>
                <p className="text-gray-300 mt-2">Treated as <span className="font-mono text-blue-400">{signalResponse.correlation_analysis.independent_observations}</span> independent observations</p>
              </div>
            )}
          </div>

          {/* Signal Decay */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-purple-200 mb-3">Signal Decay</h3>
            {signalResponse.decay_analysis && (
              <div>
                <p className="text-gray-300 mb-2">Remaining Strength: <span className="font-mono text-green-400">{(signalResponse.decay_analysis.remaining_strength * 100).toFixed(2)}%</span></p>
                <div className="w-full bg-gray-700 rounded-full h-4 relative overflow-hidden">
                  <div
                    className="h-full rounded-full bg-green-500 transition-all duration-500 ease-out"
                    style={{ width: `${(signalResponse.decay_analysis.remaining_strength * 100).toFixed(2)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Conflict Section */}
          {signalResponse.conflict_detection && signalResponse.conflict_detection.conflict && (
            <div className="mb-6 bg-red-900 bg-opacity-30 p-4 rounded-md border border-red-700">
              <h3 className="text-xl font-semibold text-red-400 mb-3">Conflict Detected!</h3>
              <p className="text-red-300 mb-2">Possible Cause: <span className="font-bold">{signalResponse.conflict_detection.possible_cause}</span></p>
              <p className="text-red-300">Conflicting Sources: {signalResponse.conflict_detection.conflicting_sources.join(', ')}</p>
            </div>
          )}

          {/* Evidence Summary */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold text-purple-200 mb-3">Evidence Summary</h3>
            <p className="text-gray-300 leading-relaxed text-lg">{signalResponse.evidence_summary}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SignalCard;

