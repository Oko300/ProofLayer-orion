import React, { useState, useEffect } from 'react';
import SignalCard from './SignalCard';
import PositionCostCard from './PositionCostCard';

function Dashboard() {
  const [signals, setSignals] = useState([]);
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    // Fetch mock data (or real data from backend later)
    const fetchMockData = async () => {
      // In a real app, you'd fetch from your FastAPI backend
      const mockSignals = [
        { id: "signal_001", whale_address: "0xWhaleAddress1", transaction_value_usd: 1000000, indicator_value: 0.85 },
        { id: "signal_002", whale_address: "0xWhaleAddress2", transaction_value_usd: 500000, indicator_value: 0.92 }
      ];
      const mockPositions = [
        { position_id: "POS_001", asset: "ETH", transactions: [{type: "buy", price: 2000, quantity: 10}] },
        { position_id: "POS_002", asset: "BTC", transactions: [{type: "buy", price: 40000, quantity: 0.5}] }
      ];
      setSignals(mockSignals);
      setPositions(mockPositions);
    };
    fetchMockData();
  }, []);

  return (
    <div className="dashboard">
      <h2>Signals</h2>
      <div className="signals-grid">
        {signals.map(signal => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </div>

      <h2>Positions</h2>
      <div className="positions-grid">
        {positions.map(position => (
          <PositionCostCard key={position.position_id} position={position} />
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
