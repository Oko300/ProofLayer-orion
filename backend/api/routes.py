from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import time
import random
import json
import httpx
import os

from engine.zscore import compute_zscore
from engine.bayesian import compute_attribution
from engine.correlation import test_independence
from engine.ks_test import detect_wash_trading
from engine.decay import compute_decay
from engine.conflict import detect_conflict
from cost.position_cost import compute_position_cost

router = APIRouter()


class SourceData(BaseModel):
    id: str
    confidence: float

class VerifySignalRequest(BaseModel):
    wallet_address: str = "0xDefaultWalletAddress"
    market: str = "BTC-USDT"
    signal_type: str = "onchain_transfer"
    reported_volume_usd: float = 0.0
    transfer_size_usd: float = 0.0
    timestamp: int = 0
    sources: List[str] = Field(default_factory=list) # Changed to List[str] assuming source IDs are strings
    asset_price_history: List[float] = Field(default_factory=list)
    volume_history: List[float] = Field(default_factory=list)
    trade_sizes: List[float] = Field(default_factory=list)
    funding_rates: List[float] = Field(default_factory=list)
    social_sentiment_scores: List[float] = Field(default_factory=list)
    onchain_flows: List[float] = Field(default_factory=list)
    source_data: List[SourceData] = Field(default_factory=list)

class SignalAttributionAnalysis(BaseModel):
    p_exchange: float
    p_accumulator: float
    p_market_maker: float
    p_unknown: float
    label: str
    confidence: str

class SignalKSTestResults(BaseModel):
    ks_statistic: float
    p_value: float
    wash_trade_detected: bool
    adjusted_volume_pct: float
    confidence_str: str

class SignalZscoreAnalysis(BaseModel):
    zscore: float
    mean: float
    std: float
    anomaly: bool
    severity: str

class SignalCorrelationAnalysis(BaseModel):
    pearson_r: float
    spearman_r: float
    are_independent: bool
    effective_evidence_count: int
    note: str

class SignalDecayAnalysis(BaseModel):
    original_confidence: str
    decay_pct: float
    remaining_strength: float
    effective_confidence: str

class SignalConflictDetection(BaseModel):
    conflict: bool
    source_a_ci: List[float]
    source_b_ci: List[float]
    possible_cause: str

class VerifySignalResponse(BaseModel):
    confidence_score: float = 0.0
    recommendation: str = ""
    evidence_summary: str = ""
    zscore_analysis: SignalZscoreAnalysis = None
    attribution_analysis: SignalAttributionAnalysis = None
    correlation_analysis: SignalCorrelationAnalysis = None
    ks_test_results: SignalKSTestResults = None
    decay_analysis: SignalDecayAnalysis = None
    conflict_detection: SignalConflictDetection = None



class PositionCostResponse(BaseModel):
    daily_cost_calm_usd: float = 0.0
    daily_cost_stress_usd: float = 0.0
    current_daily_cost_usd: float = 0.0
    cost_breakdown: dict = {}
    liquidation_price_nominal: float = 0.0
    liquidation_price_effective: float = 0.0
    liquidation_price: float = 0.0
    margin_drained_usd: float = 0.0
    adl_score: int = 0
    edge_cost_ratio: float = 0.0
    recommendation: str = "REVIEW"
    total_cost_usd: float = 0.0
    total_unrealized_pnl_usd: float = 0.0
    collateral_ratio: float = 0.0
    projected_funding_cost_usd: float = 0.0
    maker_taker_fees_usd: float = 0.0
    potential_liquidation_impact: float = 0.0
    exit_liquidity_slippage_usd: float = 0.0dation_impact: float = 0.0
    exit_liquidity_slippage_usd: float = 0.0



@router.get("/live-market")
async def get_live_market():
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "bitcoin,ethereum,solana,binancecoin",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true"
                }
            )
            data = response.json()
            markets = [
                {
                    "name": "Bitcoin", "symbol": "BTC",
                    "price_usd": data.get("bitcoin", {}).get("usd", 64000),
                    "change_24h": data.get("bitcoin", {}).get("usd_24h_change", 0),
                    "volume_24h": data.get("bitcoin", {}).get("usd_24h_vol", 0),
                    "market": "BTC-USDT"
                },
                {
                    "name": "Ethereum", "symbol": "ETH",
                    "price_usd": data.get("ethereum", {}).get("usd", 3100),
                    "change_24h": data.get("ethereum", {}).get("usd_24h_change", 0),
                    "volume_24h": data.get("ethereum", {}).get("usd_24h_vol", 0),
                    "market": "ETH-USDT"
                },
                {
                    "name": "Solana", "symbol": "SOL",
                    "price_usd": data.get("solana", {}).get("usd", 140),
                    "change_24h": data.get("solana", {}).get("usd_24h_change", 0),
                    "volume_24h": data.get("solana", {}).get("usd_24h_vol", 0),
                    "market": "SOL-USDT"
                },
                {
                    "name": "BNB", "symbol": "BNB",
                    "price_usd": data.get("binancecoin", {}).get("usd", 580),
                    "change_24h": data.get("binancecoin", {}).get("usd_24h_change", 0),
                    "volume_24h": data.get("binancecoin", {}).get("usd_24h_vol", 0),
                    "market": "BNB-USDT"
                }
            ]
            return {"markets": markets}
    except Exception as e:
        return {"markets": [
            {"name":"Bitcoin","symbol":"BTC","price_usd":64200,"change_24h":-1.2,"volume_24h":28000000000,"market":"BTC-USDT"},
            {"name":"Ethereum","symbol":"ETH","price_usd":3120,"change_24h":0.8,"volume_24h":14000000000,"market":"ETH-USDT"},
            {"name":"Solana","symbol":"SOL","price_usd":142,"change_24h":2.1,"volume_24h":3200000000,"market":"SOL-USDT"},
            {"name":"BNB","symbol":"BNB","price_usd":582,"change_24h":-0.5,"volume_24h":1800000000,"market":"BNB-USDT"}
        ]}

class PositionCostRequest(BaseModel):
    market: str = Field(..., example="BTC-PERP")
    size_usd: float = Field(..., gt=0, description="Size of the position in USD", example=10000.0)
    leverage: float = Field(..., gt=0, description="Leverage used for the position", example=10.0)
    entry_price: float = Field(..., gt=0, description="Price at which the position was opened", example=30000.0)
    current_price: float = Field(30500.0, gt=0, description="Current mark price of the asset", example=30500.0)
    funding_rate_8h: float = Field(0.0001, description="8-hour funding rate (as a decimal)", example=0.0001)
    mark_fill_spread_pct: float = Field(0.001, ge=0, description="Percentage of spread for filling orders", example=0.001)
    insurance_fund_health: float = Field(0.8, ge=0, le=1, description="Health of the insurance fund (0-1)", example=0.8)
    entry_timestamp: int = Field(0, description="Unix timestamp of when the position was opened", example=1678886400)
    current_timestamp: int = Field(0, description="Current Unix timestamp", example=1679145600)
    chain: str = Field("ethereum", example="ethereum")
    slippage_tolerance: float = Field(0.005, ge=0, le=1, description="Tolerance for price slippage (0-1)", example=0.005)
    liquidation_buffer_factor: float = Field(0.1, ge=0, description="Buffer factor for liquidation price calculation", example=0.1)
    collateral_asset: str = Field("USDT", example="USDT")

class PositionCostRequest(BaseModel):
    market: str = Field(..., example="BTC-PERP")
    size_usd: float = Field(..., gt=0, description="Size of the position in USD", example=10000.0)
    leverage: float = Field(..., gt=0, description="Leverage used for the position", example=10.0)
    entry_price: float = Field(..., gt=0, description="Price at which the position was opened", example=30000.0)
    current_price: float = Field(..., gt=0, description="Current mark price of the asset", example=30500.0)
    funding_rate_8h: float = Field(..., description="8-hour funding rate (as a decimal)", example=0.0001)
    mark_fill_spread_pct: float = Field(..., ge=0, description="Estimated mark-to-fill spread as a percentage", example=0.0005)
    insurance_fund_health: float = Field(..., ge=0, le=1, description="Health of the exchange's insurance fund (0-1)", example=0.9)
    entry_timestamp: int = Field(..., description="Unix timestamp of position entry", example=1678886400)
    current_timestamp: int = Field(..., description="Current Unix timestamp", example=1679145600)

class PositionCostResponse(BaseModel):
    total_cost_usd: float = Field(..., description="Total cost of the position in USD")
    total_unrealized_pnl_usd: float = Field(..., description="Total unrealized PnL of the position in USD")
    liquidation_price: float = Field(..., description="Estimated liquidation price of the position")
    collateral_ratio: float = Field(..., description="Current collateral ratio of the position")
    projected_funding_cost_usd: float = Field(..., description="Projected funding cost in USD")
    maker_taker_fees_usd: float = Field(..., description="Maker and taker fees in USD")
    potential_liquidation_impact: float = Field(..., description="Potential impact of liquidation on the insurance fund")
    exit_liquidity_slippage_usd: float = Field(..., description="Estimated slippage cost upon exit in USD")

@router.post("/verify-signal", response_model=VerifySignalResponse, status_code=status.HTTP_200_OK)
async def verify_signal(request: VerifySignalRequest):
    try:
        # Unpack request parameters
        wallet_address = request.wallet_address
        market = request.market
        asset_price_history = request.asset_price_history
        volume_history = request.volume_history
        trade_sizes = request.trade_sizes
        funding_rates = request.funding_rates
        social_sentiment_scores = request.social_sentiment_scores
        onchain_flows = request.onchain_flows
        source_data = request.source_data

        # Generate mock data if input lists are empty
        if not request.asset_price_history:
            request.asset_price_history = [random.uniform(64000, 66000) for _ in range(30)]
        if not request.volume_history:
            avg_volume = request.reported_volume_usd / 30 if request.reported_volume_usd > 0 else 1000000
            request.volume_history = [random.uniform(avg_volume * 0.8, avg_volume * 1.2) for _ in range(30)]
        if not request.trade_sizes:
            request.trade_sizes = [random.uniform(1000, 500000) for _ in range(50)]

        if request.timestamp == 0:
            request.timestamp = int(time.time())

        if not request.sources and not request.source_data:
            # Default sources if none provided
            request.sources = ["source_a", "source_b"]
            request.source_data = [SourceData(id="source_a", confidence=0.7), SourceData(id="source_b", confidence=0.8)]

        # Initialize combined output dictionary
        combined_output: Dict[str, Any] = {}

        if not request.funding_rates:
            request.funding_rates = [random.uniform(-0.0001, 0.0001) for _ in range(100)]
        if not request.social_sentiment_scores:
            request.social_sentiment_scores = [random.uniform(-1.0, 1.0) for _ in range(100)]
        if not request.onchain_flows:
            request.onchain_flows = [random.uniform(1_000_000, 100_000_000) for _ in range(100)]

        # 1. Z-Score Analysis for volume anomaly detection
        zscore_output = compute_zscore(volume_history)
        combined_output["zscore_analysis"] = zscore_output

        # 2. Bayesian Inference for Signal Attribution
        attribution_output = compute_attribution(wallet_address, source_data)
        combined_output["attribution_analysis"] = attribution_output

        # 3. Correlation Analysis (e.g., between asset price and social sentiment)
        correlation_output = test_independence(asset_price_history, social_sentiment_scores, "pearson")
        combined_output["correlation_analysis"] = correlation_output

        # 4. Kolmogorov-Smirnov Test for Wash Trading Detection
        ks_test_output = detect_wash_trading(trade_sizes, volume_history)
        combined_output["ks_test_results"] = ks_test_output

        # 5. Signal Decay Analysis
        # Assuming an initial confidence score for demonstration, and a time elapsed
        initial_confidence = 0.8  # This would ideally come from external source or initial assessment
        time_elapsed_hours = 24  # Example: 24 hours since signal generation
        decay_output = compute_decay(initial_confidence, time_elapsed_hours)
        combined_output["decay_analysis"] = decay_output

        # 6. Conflict Detection
        # Assuming two hypothetical sources with their confidence intervals
        source_a_ci = [0.7, 0.9]
        source_b_ci = [0.4, 0.6]
        conflict_output = detect_conflict(source_a_ci, source_b_ci)
        combined_output["conflict_detection"] = conflict_output

        # Aggregate and determine overall confidence score and recommendation
        confidence_score = 0.0
        weight_zscore = 0.15
        weight_bayesian = 0.20
        weight_correlation = 0.15
        weight_ks_test = 0.20
        weight_decay = 0.10
        weight_conflict = 0.20

        # Z-score: lower anomaly severity -> higher confidence
        if zscore_output["severity"] == "none":
            confidence_score += weight_zscore * 1.0
        elif zscore_output["severity"] == "low":
            confidence_score += weight_zscore * 0.7
        elif zscore_output["severity"] == "medium":
            confidence_score += weight_zscore * 0.4
        else:
            confidence_score += weight_zscore * 0.1

        # Bayesian: higher confidence in attribution (not unknown) -> higher confidence
        if attribution_output["label"] != "unknown" and attribution_output["confidence"] == "high":
            confidence_score += weight_bayesian * 1.0
        elif attribution_output["label"] != "unknown" and attribution_output["confidence"] == "medium":
            confidence_score += weight_bayesian * 0.7
        elif attribution_output["label"] != "unknown" and attribution_output["confidence"] == "low":
            confidence_score += weight_bayesian * 0.4
        else:
            confidence_score += weight_bayesian * 0.1

        # Correlation: independence (low correlation) -> higher confidence
        if correlation_output["are_independent"]:
            confidence_score += weight_correlation * 0.8
        else:
            confidence_score += weight_correlation * 0.2

        # KS Test: no wash trade detected -> higher confidence
        if not ks_test_output["wash_trade_detected"]:
            confidence_score += weight_ks_test * 0.9
        else:
            confidence_score += weight_ks_test * (1 - ks_test_output["adjusted_volume_pct"])

        # Decay: higher remaining strength -> higher confidence
        confidence_score += weight_decay * decay_output["remaining_strength"]

        # Conflict: no conflict -> higher confidence
        if not conflict_output["conflict"]:
            confidence_score += weight_conflict * 0.9
        else:
            confidence_score += weight_conflict * 0.1

        # Normalize confidence score to 0-1
        total_weights = weight_zscore + weight_bayesian + weight_correlation + weight_ks_test + weight_decay + weight_conflict
        confidence_score /= total_weights

        # Determine Recommendation
        recommendation = "DO_NOT_ACT"
        if confidence_score > 0.7:
            recommendation = "ACT"
        elif confidence_score > 0.4:
            recommendation = "CAUTION"
        
        # Generate Evidence Summary
        evidence_summary = f"The signal for wallet {request.wallet_address} in market {request.market} shows a confidence score of {confidence_score:.2f}. "
        if zscore_output["anomaly"]:
            evidence_summary += f"Anomalous volume detected with {zscore_output['severity']} severity. "
        if attribution_output["label"] != "unknown":
            evidence_summary += f"Wallet attributed as {attribution_output['label']} with {attribution_output['confidence']} confidence. "
        if ks_test_output["wash_trade_detected"]:
            evidence_summary += "Potential wash trading detected. "
        if conflict_output["conflict"]:
            evidence_summary += f"Conflict among sources: {conflict_output['possible_cause']}. "
        evidence_summary += f"Overall recommendation: {recommendation}."


        combined_output["confidence_score"] = float(confidence_score)
        combined_output["recommendation"] = recommendation
        combined_output["evidence_summary"] = evidence_summary

        return VerifySignalResponse(**combined_output)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/position-cost", response_model=PositionCostResponse, status_code=status.HTTP_200_OK)
async def get_position_cost(request: PositionCostRequest):
    try:
        result = compute_position_cost(request.dict())
        result["liquidation_price"] = result.get("liquidation_price_effective", 0.0)
        result["total_cost_usd"] = result.get("daily_cost_stress_usd", 0.0) * 30
        result["total_unrealized_pnl_usd"] = 0.0
        result["collateral_ratio"] = 0.0
        result["projected_funding_cost_usd"] = result.get("daily_cost_calm_usd", 0.0) * 7
        result["maker_taker_fees_usd"] = result.get("cost_breakdown", {}).get("taker_fee_usd", 0.0)
        result["potential_liquidation_impact"] = 0.0
        result["exit_liquidity_slippage_usd"] = 0.0
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/market-health", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_market_health(market_id: str = Query(..., description="The ID of the market")):
    # Mock data for now
    mock_data = {
        "market_id": market_id,
        "funding_anomaly_zscore": 2.5 if market_id == "stressed-market" else 0.5,
        "wash_trade_adjusted_volume": 0.15 if market_id == "stressed-market" else 0.02,
        "top_signals": [
            {"signal_type": "funding_anomaly", "decay_score": 0.8},
            {"signal_type": "social_sentiment", "decay_score": 0.6},
            {"signal_type": "onchain_transfer", "decay_score": 0.9}
        ]
    }
    return mock_data