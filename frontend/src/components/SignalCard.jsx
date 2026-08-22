import React from 'react';

function SignalCard({ signal }) {
  return (
    <div className="signal-card">
      <h3>Signal ID: {signal.id}</h3>
      <p>Whale Address: {signal.whale_address}</p>
      <p>Value: ${signal.transaction_value_usd}</p>
      <p>Indicator: {signal.indicator_value}</p>
    </div>
  );
}

export default SignalCard;
