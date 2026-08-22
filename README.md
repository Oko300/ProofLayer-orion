# ProofLayer Monorepo

ProofLayer is an advanced analytics application designed for institutional traders and quantitative analysts in the DeFi space. It provides real-time insights into market health, identifies potential wash trading and whale manipulations, assesses the risk and cost of perpetual futures positions, and monitors for cascading liquidations. By leveraging sophisticated on-chain and off-chain data analysis, ProofLayer empowers users to make more informed and strategic trading decisions, mitigating risks and optimizing returns in volatile crypto markets.

**Judging Track:** DeFi/AI Agents

## Quick Start

To get the ProofLayer application up and running:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/prooflayer.git
    cd prooflayer
    ```
2.  **Run the setup script:**
    ```bash
    bash run.sh
    ```
    This script will create a Python virtual environment, install backend dependencies, and start the FastAPI backend on `http://localhost:8000` in the background.
3.  **Open the frontend:**
    Open `prooflayer/frontend/index.html` in your web browser.

## API Documentation
### 1. `/api/verify-signal` (POST) - Signal Verifier

Analyzes on-chain and off-chain data to verify the legitimacy and strength of a trading signal.

*   **Request Body Example:**
    ```json
    {
      "wallet_address": "0xWhaleAccumulator",
      "market": "ETH-PERP",
      "asset_price_history": [2000, 2010, 2005, 2020, 2030],
      "volume_history": [1000000, 1100000, 900000, 1200000, 1300000],
      "trade_sizes": [1000, 1100, 900, 1200, 1300],
      "funding_rates": [0.0001, 0.00015, 0.00012, 0.00018, 0.0001],
      "social_sentiment_scores": [0.6, 0.7, 0.65, 0.72, 0.68],
      "onchain_flows": [10000, -5000, 20000, -10000, 15000],
      "source_data": [
        {"id": "data_aggregator", "confidence": 0.8},
        {"id": "social_feed_A", "confidence": 0.7},
        {"id": "trading_bot_B", "confidence": 0.6}
      ]
    }
    ```
*   **Response Body Example:**
    ```json
    {
      "id": "whale_accumulation_debunk",
      "wallet_address": "0xWhaleAccumulator",
      "market": "ETH-PERP",
      "confidence_score": 0.35,
      "recommendation": "DO_NOT_ACT",
      "evidence_summary": "The signal for wallet 0xWhaleAccumulator in market ETH-PERP shows a confidence score of 0.35. Wallet attributed as exchange with high confidence. Potential wash trading detected. Overall recommendation: DO_NOT_ACT.",
      "attribution_analysis": {
        "label": "exchange",
        "confidence": 0.87,
        "probabilities": {
          "exchange": 0.87,
          "accumulator": 0.05,
          "arbitrageur": 0.04,
          "liquidation_bot": 0.02,
          "market_maker": 0.02
        }
      },
      "ks_test_results": {
        "wash_trade_detected": true,
        "adjusted_organic_volume": 400000,
        "adjusted_volume_pct": 0.40
      },
      "zscore_analysis": {
        "anomaly": false,
        "severity": "low",
        "z_score": 0.5,
        "total_volume": 1000000
      },
      "correlation_analysis": {
        "r_value": 0.15,
        "are_independent": true,
        "independent_observations": 3
      },
      "decay_analysis": {
        "remaining_strength": 0.66
      },
      "conflict_detection": {
        "conflict": false
      }
    }
    ```

### 2. `/api/position-cost` (POST) - Position Cost Calculator

Calculates the effective cost and liquidation risks for a perpetual futures position.

*   **Request Body Example:**
    ```json
    {
      "market": "BTC-PERP",
      "size_usd": 10000,
      "leverage": 5,
      "entry_price": 30000,
      "current_price": 29500,
      "funding_rate_8h": 0.003,
      "mark_fill_spread_pct": 0.001,
      "insurance_fund_health": 0.7,
      "entry_timestamp": 1678886400,
      "current_timestamp": 1679145600
    }
    ```
*   **Response Body Example:**
    ```json
    {
      "liquidation_price_theoretical": 28000.0,
      "liquidation_price_effective": 28150.0,
      "price_drift_to_liquidation": 4.5,
      "adl_score": 7,
      "adl_priority": "high",
      "edge_cost_ratio": 0.8,
      "recommendation": "DO_NOT_ACT",
      "entry_margin_usd": 2000.0,
      "required_initial_margin_pct": 0.05,
      "maintenance_margin_usd": 1000.0,
      "required_maintenance_margin_pct": 0.025,
      "borrow_interest_rate_pct": 0.0001,
      "funding_cost_daily_usd": 3.75,
      "liquidation_fee_usd": 100.0,
      "settlement_escalation_multiplier": 1.2,
      "margin_drained_usd": 100.0
    }
    ```



### 3. `/api/market-health` (GET) - Market Health Dashboard

Provides an overview of the health and stability of a given market.

*   **Request Example:**
    ```bash
    curl "http://localhost:8000/api/market-health?market_id=BTC-PERP"
    ```
*   **Response Body Example:**
    ```json
    {
      "market_id": "BTC-PERP",
      "funding_anomaly_zscore": 2.5,
      "wash_trade_adjusted_volume": 0.85,
      "top_signals": [
        {
          "signal_type": "large_trades",
          "decay_score": 0.9
        },
        {
          "signal_type": "social_sentiment_spike",
          "decay_score": 0.75
        }
      ]
    }
    ```

### 4. `/api/liquidation-watch` (GET) - Liquidation Watch

Monitors and predicts potential cascading liquidation events across markets.

*   **Request Example:**
    ```bash
    curl "http://localhost:8000/api/liquidation-watch"
    ```
*   **Response Body Example:**
    ```json
    [
      {
        "id": "btc_stressed",
        "market": "BTC-PERP",
        "wallet_address": "0xExampleAddress1",
        "liquidation_price": 28150.0,
        "current_price": 29500,
        "time_to_liquidation_hours": 24,
        "impact_score": 0.8
      },
      {
        "id": "eth_calm",
        "market": "ETH-PERP",
        "wallet_address": "0xExampleAddress2",
        "liquidation_price": 1900.0,
        "current_price": 2010,
        "time_to_liquidation_hours": 72,
        "impact_score": 0.2
      }
    ]
    ```

## Architecture Diagram

```
+-------------------+      +-------------------------+
|     Frontend      |      |                         |
| (React, HTML/CSS) |      |        Backend          |
|                   |      |    (FastAPI, Python)    |
+---------+---------+      +-----------+-------------+
          |                            |
          | HTTP/REST API calls        |
          |                            |
          |                +-----------v-----------+
          |                |      API Routes       |
          |                | (/verify-signal, etc.)|
          |                +-----------+-----------+
          |                            |
          |                            | Calls various
          |                            |  analytics engines
          |                            |
          |                +-----------v-----------+
          |                |     Core Analytics    |
          |                | (Z-score, Bayesian,   |
          |                |  K-S Test, Decay,     |
          |                |  Correlation, Conflict)|
          |                +-----------+-----------+
          |                            |
          |                            | Reads mock data
          |                            |  (for MOCK_MODE)
          |                            |
          |                +-----------v-----------+
          |                |     Data Layer        |
          |                | (mock_signals.json,   |
          |                |  mock_positions.json) |
          +----------------+-----------------------+
```