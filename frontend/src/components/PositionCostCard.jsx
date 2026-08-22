import React from 'react';

function PositionCostCard({ position }) {
  return (
    <div className="position-cost-card">
      <h3>Position ID: {position.position_id}</h3>
      <p>Asset: {position.asset}</p>
      <p>Transactions: {position.transactions.length}</p>
      {/* True cost calculation will be integrated here later */}
      <p>Estimated Cost: [Calculate True Cost Here]</p>
    </div>
  );
}

export default PositionCostCard;
