"""
Aster SDK - Type definitions
"""

from typing import Any, Dict, List, Optional, Union, Literal, TypedDict
from decimal import Decimal


# =============================================================================
# BASIC TYPES
# =============================================================================

# Common type aliases
Any = Any
Dict = Dict
List = List
Optional = Optional
Union = Union
Literal = Literal
TypedDict = TypedDict

# =============================================================================
# ORDER TYPES
# =============================================================================

# Time in force options
Tif = Union[Literal["Alo"], Literal["Ioc"], Literal["Gtc"]]

# Order type definitions
LimitOrderType = TypedDict("LimitOrderType", {"tif": Tif})
OrderType = TypedDict("OrderType", {"limit": LimitOrderType}, total=False)

# Order request structure
OrderRequest = TypedDict(
    "OrderRequest",
    {
        "coin": str,
        "is_buy": bool,
        "sz": float,
        "limit_px": float,
        "order_type": OrderType,
        "reduce_only": bool,
    },
    total=False,
)

# Order wire format
OrderWire = TypedDict(
    "OrderWire",
    {
        "a": int,  # asset
        "b": bool,  # is_buy
        "p": str,  # limit_px
        "s": str,  # sz
        "r": bool,  # reduce_only
        "t": OrderType,  # order_type
    },
)

# =============================================================================
# CANCEL TYPES
# =============================================================================

CancelRequest = TypedDict("CancelRequest", {"coin": str, "oid": int})
CancelByCloidRequest = TypedDict("CancelByCloidRequest", {"coin": str, "cloid": str})

# =============================================================================
# MODIFY TYPES
# =============================================================================

ModifyRequest = TypedDict(
    "ModifyRequest",
    {
        "oid": Union[int, str],  # order ID or client order ID
        "order": OrderRequest,
    },
)

# =============================================================================
# CLIENT ORDER ID
# =============================================================================

class Cloid:
    """Client Order ID wrapper"""
    
    def __init__(self, cloid: str):
        self.cloid = cloid
    
    def to_raw(self) -> str:
        return self.cloid
    
    def __str__(self) -> str:
        return self.cloid
    
    def __repr__(self) -> str:
        return f"Cloid('{self.cloid}')"

# =============================================================================
# META TYPES
# =============================================================================

# Asset information
AssetInfo = TypedDict(
    "AssetInfo",
    {
        "name": str,
        "szDecimals": int,
        "maxLeverage": Optional[int],
        "onlyIsolated": Optional[bool],
    },
)

# Universe metadata
Universe = List[AssetInfo]

# Meta structure
Meta = TypedDict(
    "Meta",
    {
        "universe": Universe,
    },
)

# =============================================================================
# SPOT TYPES
# =============================================================================

# Token information
TokenInfo = TypedDict(
    "TokenInfo",
    {
        "name": str,
        "szDecimals": int,
        "weiDecimals": int,
        "index": int,
        "tokenId": str,
        "isCanonical": bool,
    },
)

# Spot universe item
SpotUniverseItem = TypedDict(
    "SpotUniverseItem",
    {
        "tokens": List[int],
        "name": str,
        "index": int,
        "isCanonical": bool,
    },
)

# Spot metadata
SpotMeta = TypedDict(
    "SpotMeta",
    {
        "universe": List[SpotUniverseItem],
        "tokens": List[TokenInfo],
    },
)

# Spot asset context
SpotAssetCtx = TypedDict(
    "SpotAssetCtx",
    {
        "dayNtlVlm": str,
        "markPx": str,
        "midPx": Optional[str],
        "prevDayPx": str,
        "circulatingSupply": str,
        "coin": str,
    },
)

# Spot meta and asset contexts
SpotMetaAndAssetCtxs = TypedDict(
    "SpotMetaAndAssetCtxs",
    {
        "meta": SpotMeta,
        "assetCtxs": List[SpotAssetCtx],
    },
)

# =============================================================================
# WEBSOCKET TYPES
# =============================================================================

# Subscription types
Subscription = TypedDict(
    "Subscription",
    {
        "type": str,
        "coin": str,
        "interval": Optional[str],
    },
)

# =============================================================================
# BUILDER TYPES
# =============================================================================

BuilderInfo = TypedDict(
    "BuilderInfo",
    {
        "b": str,  # builder address
        "maxFee": str,  # maximum fee
    },
)

# =============================================================================
# PERP DEX TYPES
# =============================================================================

PerpDexSchemaInput = TypedDict(
    "PerpDexSchemaInput",
    {
        "fullName": str,
        "collateralToken": str,
        "oracleUpdater": Optional[str],
    },
)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def cast(typ, obj):
    """Type casting utility"""
    return obj
