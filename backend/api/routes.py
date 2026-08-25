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
    sources: List[str] = Field(default_factory=list)
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
    exit_liquidity_slippage_usd: float = 0.0

class PositionCostRequest(BaseModel):
    chain: str = "ethereum"
    market: str = "BTC-USDT"
    size_usd: float = 10000.0
    leverage: float = 5.0
    entry_price: float = 65000.0
    current_price: float = 64200.0
    funding_rate_8h: float = 0.0003
    mark_fill_spread_pct: float = 0.001
    insurance_fund_health: float = 0.8
    entry_timestamp: int = 0
    current_timestamp: int = 0



@router.post("/verify-signal", response_model=VerifySignalResponse, status_code=status.HTTP_200_OK)
async def verify_signal(request: VerifySignalRequest):
    try:
        # Placeholder for actual signal verification logic
        # For now, return mock data or basic computation
        confidence_score = 0.5  # Placeholder
        recommendation = "CAUTION" # Placeholder
        evidence_summary = "Preliminary analysis suggests moderate confidence with some contributing factors." # Placeholder

        # Example of how engine functions would be called
        zscore_output = compute_zscore(request.reported_volume_usd, request.volume_history)
        attribution_output = compute_attribution(request.wallet_address, request.signal_type, request.transfer_size_usd)
        correlation_output = test_independence(request.asset_price_history, request.social_sentiment_scores)
        ks_test_output = detect_wash_trading(request.trade_sizes)
        decay_output = compute_decay(time.time(), request.timestamp, initial_confidence=confidence_score) # Assuming initial confidence
        conflict_output = detect_conflict(request.source_data) # Assuming source_data provides intervals


        combined_output = {
            "confidence_score": float(confidence_score),
            "recommendation": recommendation,
            "evidence_summary": evidence_summary,
            "zscore_analysis": zscore_output,
            "attribution_analysis": attribution_output,
            "correlation_analysis": correlation_output,
            "ks_test_results": ks_test_output,
            "decay_analysis": decay_output,
            "conflict_detection": conflict_output
        }

        # Dynamic weighting based on signal_type and market conditions
        # (This is a simplified example; a real system would have a more robust weighting mechanism)
        weight_zscore = 0.2
        weight_bayesian = 0.3
        weight_correlation = 0.15
        weight_ks_test = 0.2
        weight_decay = 0.1
        weight_conflict = 0.05

        confidence_score = 0.0 # Reset for re-calculation based on engine outputs

        # Z-score: High anomaly -> lower confidence
        if zscore_output["anomaly"]:
            if zscore_output["severity"] == "critical":
                confidence_score += weight_zscore * 0.1
            elif zscore_output["severity"] == "high":
                confidence_score += weight_zscore * 0.3
            else: # medium/low
                confidence_score += weight_zscore * 0.5
        else:
            confidence_score += weight_zscore * 0.9

        # Bayesian Attribution: known non-market-maker -> higher confidence
        if attribution_output["label"] in ["exchange", "accumulator"] and attribution_output["confidence"] == "high":
            confidence_score += weight_bayesian * 0.9
        elif attribution_output["label"] == "market_maker":
            confidence_score += weight_bayesian * 0.3 # Market makers can be neutral or manipulative
        else: # Unknown or low confidence
            confidence_score += weight_bayesian * 0.5

        # Correlation: independent -> higher confidence
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


@router.post("/position-cost", response_model=PositionCostResponse)
async def get_position_cost(position: PositionCostRequest):
    try:
        result = compute_position_cost(position.dict())
        import json
        print("DEBUG position dict:", json.dumps(position.dict()))
        print("DEBUG result:", json.dumps(result, default=str))
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
        raise HTTPException(status_code=500, detail=str(e))



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




@router.get("/live-market")
async def get_live_market():
    try:
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
            return {"markets": [
                {"name":"Bitcoin","symbol":"BTC","price_usd":data.get("bitcoin",{}).get("usd",64000),"change_24h":data.get("bitcoin",{}).get("usd_24h_change",0),"volume_24h":data.get("bitcoin",{}).get("usd_24h_vol",0),"market":"BTC-USDT"},
                {"name":"Ethereum","symbol":"ETH","price_usd":data.get("ethereum",{}).get("usd",3100),"change_24h":data.get("ethereum",{}).get("usd_24h_change",0),"volume_24h":data.get("ethereum",{}).get("usd_24h_vol",0),"market":"ETH-USDT"},
                {"name":"Solana","symbol":"SOL","price_usd":data.get("solana",{}).get("usd",140),"change_24h":data.get("solana",{}).get("usd_24h_change",0),"volume_24h":data.get("solana",{}).get("usd_24h_vol",0),"market":"SOL-USDT"},
                {"name":"BNB","symbol":"BNB","price_usd":data.get("binancecoin",{}).get("usd",580),"change_24h":data.get("binancecoin",{}).get("usd_24h_change",0),"volume_24h":data.get("binancecoin",{}).get("usd_24h_vol",0),"market":"BNB-USDT"}
            ]}
    except Exception:
        return {"markets": [
            {"name":"Bitcoin","symbol":"BTC","price_usd":64200,"change_24h":-1.2,"volume_24h":28000000000,"market":"BTC-USDT"},
            {"name":"Ethereum","symbol":"ETH","price_usd":3120,"change_24h":0.8,"volume_24h":14000000000,"market":"ETH-USDT"},
            {"name":"Solana","symbol":"SOL","price_usd":142,"change_24h":2.1,"volume_24h":3200000000,"market":"SOL-USDT"},
            {"name":"BNB","symbol":"BNB","price_usd":582,"change_24h":-0.5,"volume_24h":1800000000,"market":"BNB-USDT"}
        ]}

@router.get("/health")
async def health_check():
    return {"status": "ok"}