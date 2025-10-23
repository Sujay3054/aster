"""
Aster SDK - Info module for market data and user information
"""

from typing import Any, Dict, List, Optional, Union, Callable
from .api import API
from .utils.types import (
    Meta,
    SpotMeta,
    SpotMetaAndAssetCtxs,
    Subscription,
    Cloid,
)
from .utils.constants import MAINNET_API_URL


class Info(API):
    """Info module for retrieving market data and user information from Aster DEX"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        skip_ws: Optional[bool] = False,
        meta: Optional[Meta] = None,
        spot_meta: Optional[SpotMeta] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize Info client
        
        Args:
            base_url: Base URL for the API
            skip_ws: Skip WebSocket initialization
            meta: Pre-loaded perp metadata
            spot_meta: Pre-loaded spot metadata
            timeout: Request timeout
        """
        super().__init__(base_url, timeout)
        
        # Initialize metadata mappings
        self.coin_to_asset = {}
        self.name_to_coin = {}
        self.asset_to_sz_decimals = {}
        
        # Load spot metadata
        if spot_meta is None:
            spot_meta = self.spot_meta()
        
        # Process spot assets (start at 10000)
        for spot_info in spot_meta["universe"]:
            asset = spot_info["index"] + 10000
            self.coin_to_asset[spot_info["name"]] = asset
            self.name_to_coin[spot_info["name"]] = spot_info["name"]
            
            # Get token information
            base, quote = spot_info["tokens"]
            base_info = spot_meta["tokens"][base]
            self.asset_to_sz_decimals[asset] = base_info["szDecimals"]
            
            # Create trading pair name
            quote_info = spot_meta["tokens"][quote]
            name = f'{base_info["name"]}/{quote_info["name"]}'
            if name not in self.name_to_coin:
                self.name_to_coin[name] = spot_info["name"]
        
        # Load perp metadata
        if meta is None:
            meta = self.meta()
        
        # Process perp assets
        for asset, asset_info in enumerate(meta["universe"]):
            self.coin_to_asset[asset_info["name"]] = asset
            self.name_to_coin[asset_info["name"]] = asset_info["name"]
            self.asset_to_sz_decimals[asset] = asset_info["szDecimals"]

    def user_state(self, address: str) -> Any:
        """
        Retrieve trading details about a user.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            User state information including positions, margin, and balances
        """
        return self.post("/info", {"type": "clearinghouseState", "user": address})

    def spot_user_state(self, address: str) -> Any:
        """
        Retrieve spot trading details about a user.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            Spot user state information
        """
        return self.post("/info", {"type": "spotClearinghouseState", "user": address})

    def open_orders(self, address: str) -> Any:
        """
        Retrieve a user's open orders.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of open orders
        """
        return self.post("/info", {"type": "openOrders", "user": address})

    def frontend_open_orders(self, address: str) -> Any:
        """
        Retrieve a user's open orders with additional frontend info.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of open orders with frontend information
        """
        return self.post("/info", {"type": "frontendOpenOrders", "user": address})

    def all_mids(self) -> Any:
        """
        Retrieve all mids for all actively traded coins.
        
        Returns:
            Dictionary of coin names to mid prices
        """
        return self.post("/info", {"type": "allMids"})

    def user_fills(self, address: str) -> Any:
        """
        Retrieve a given user's fills.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of user fills
        """
        return self.post("/info", {"type": "userFills", "user": address})

    def user_fills_by_time(
        self, 
        address: str, 
        start_time: int, 
        end_time: Optional[int] = None,
        aggregate_by_time: Optional[bool] = False
    ) -> Any:
        """
        Retrieve a given user's fills by time.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            start_time: Unix timestamp in milliseconds
            end_time: Unix timestamp in milliseconds (optional)
            aggregate_by_time: Whether to aggregate fills by time
            
        Returns:
            List of user fills within the time range
        """
        payload = {
            "type": "userFillsByTime",
            "user": address,
            "startTime": start_time,
            "aggregateByTime": aggregate_by_time,
        }
        if end_time is not None:
            payload["endTime"] = end_time
            
        return self.post("/info", payload)

    def meta(self) -> Meta:
        """
        Retrieve exchange perp metadata.
        
        Returns:
            Perp metadata including universe information
        """
        return self.post("/info", {"type": "meta"})

    def meta_and_asset_ctxs(self) -> Any:
        """
        Retrieve exchange MetaAndAssetCtxs.
        
        Returns:
            Metadata and asset contexts
        """
        return self.post("/info", {"type": "metaAndAssetCtxs"})

    def spot_meta(self) -> SpotMeta:
        """
        Retrieve exchange spot metadata.
        
        Returns:
            Spot metadata including universe and token information
        """
        return self.post("/info", {"type": "spotMeta"})

    def spot_meta_and_asset_ctxs(self) -> SpotMetaAndAssetCtxs:
        """
        Retrieve exchange spot asset contexts.
        
        Returns:
            Spot metadata and asset contexts
        """
        return self.post("/info", {"type": "spotMetaAndAssetCtxs"})

    def funding_history(self, name: str, start_time: int, end_time: Optional[int] = None) -> Any:
        """
        Retrieve funding history for a given coin.
        
        Args:
            name: Coin name
            start_time: Unix timestamp in milliseconds
            end_time: Unix timestamp in milliseconds (optional)
            
        Returns:
            List of funding history records
        """
        coin = self.name_to_coin[name]
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_time,
        }
        if end_time is not None:
            payload["endTime"] = end_time
            
        return self.post("/info", payload)

    def user_funding_history(self, user: str, start_time: int, end_time: Optional[int] = None) -> Any:
        """
        Retrieve a user's funding history.
        
        Args:
            user: User address
            start_time: Start time in milliseconds
            end_time: End time in milliseconds (optional)
            
        Returns:
            List of user funding history records
        """
        payload = {
            "type": "userFunding",
            "user": user,
            "startTime": start_time,
        }
        if end_time is not None:
            payload["endTime"] = end_time
            
        return self.post("/info", payload)

    def l2_snapshot(self, name: str) -> Any:
        """
        Retrieve L2 snapshot for a given coin.
        
        Args:
            name: Coin name
            
        Returns:
            L2 order book snapshot
        """
        return self.post("/info", {"type": "l2Book", "coin": self.name_to_coin[name]})

    def candles_snapshot(self, name: str, interval: str, start_time: int, end_time: int) -> Any:
        """
        Retrieve candles snapshot for a given coin.
        
        Args:
            name: Coin name
            interval: Candlestick interval
            start_time: Unix timestamp in milliseconds
            end_time: Unix timestamp in milliseconds
            
        Returns:
            List of candlestick data
        """
        req = {
            "coin": self.name_to_coin[name],
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
        }
        return self.post("/info", {"type": "candleSnapshot", "req": req})

    def user_fees(self, address: str) -> Any:
        """
        Retrieve the volume of trading activity associated with a user.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            User fee information and trading volume
        """
        return self.post("/info", {"type": "userFees", "user": address})

    def user_staking_summary(self, address: str) -> Any:
        """
        Retrieve the staking summary associated with a user.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            User staking summary
        """
        return self.post("/info", {"type": "delegatorSummary", "user": address})

    def user_staking_delegations(self, address: str) -> Any:
        """
        Retrieve the user's staking delegations.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of user staking delegations
        """
        return self.post("/info", {"type": "delegations", "user": address})

    def user_staking_rewards(self, address: str) -> Any:
        """
        Retrieve the historic staking rewards associated with a user.
        
        Args:
            address: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of staking rewards
        """
        return self.post("/info", {"type": "delegatorRewards", "user": address})

    def delegator_history(self, user: str) -> Any:
        """
        Retrieve comprehensive staking history for a user.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            Comprehensive staking history
        """
        return self.post("/info", {"type": "delegatorHistory", "user": user})

    def query_order_by_oid(self, user: str, oid: int) -> Any:
        """
        Query order by order ID.
        
        Args:
            user: User address
            oid: Order ID
            
        Returns:
            Order information
        """
        return self.post("/info", {"type": "orderStatus", "user": user, "oid": oid})

    def query_order_by_cloid(self, user: str, cloid: Cloid) -> Any:
        """
        Query order by client order ID.
        
        Args:
            user: User address
            cloid: Client order ID
            
        Returns:
            Order information
        """
        return self.post("/info", {"type": "orderStatus", "user": user, "oid": cloid.to_raw()})

    def query_referral_state(self, user: str) -> Any:
        """
        Query referral state for a user.
        
        Args:
            user: User address
            
        Returns:
            Referral state information
        """
        return self.post("/info", {"type": "referral", "user": user})

    def query_sub_accounts(self, user: str) -> Any:
        """
        Query sub accounts for a user.
        
        Args:
            user: User address
            
        Returns:
            List of sub accounts
        """
        return self.post("/info", {"type": "subAccounts", "user": user})

    def historical_orders(self, user: str) -> Any:
        """
        Retrieve a user's historical orders.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of historical orders
        """
        return self.post("/info", {"type": "historicalOrders", "user": user})

    def user_non_funding_ledger_updates(self, user: str, start_time: int, end_time: Optional[int] = None) -> Any:
        """
        Retrieve non-funding ledger updates for a user.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            start_time: Start time in milliseconds
            end_time: End time in milliseconds (optional)
            
        Returns:
            List of non-funding ledger updates
        """
        payload = {
            "type": "userNonFundingLedgerUpdates",
            "user": user,
            "startTime": start_time,
        }
        if end_time is not None:
            payload["endTime"] = end_time
            
        return self.post("/info", payload)

    def portfolio(self, user: str) -> Any:
        """
        Retrieve comprehensive portfolio performance data.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            Portfolio performance data
        """
        return self.post("/info", {"type": "portfolio", "user": user})

    def user_twap_slice_fills(self, user: str) -> Any:
        """
        Retrieve a user's TWAP slice fills.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of TWAP slice fills
        """
        return self.post("/info", {"type": "userTwapSliceFills", "user": user})

    def user_vault_equities(self, user: str) -> Any:
        """
        Retrieve user's equity positions across all vaults.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            Vault equity information
        """
        return self.post("/info", {"type": "userVaultEquities", "user": user})

    def user_role(self, user: str) -> Any:
        """
        Retrieve the role and account type information for a user.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            User role and account type information
        """
        return self.post("/info", {"type": "userRole", "user": user})

    def user_rate_limit(self, user: str) -> Any:
        """
        Retrieve user's API rate limit configuration and usage.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            Rate limit configuration and usage
        """
        return self.post("/info", {"type": "userRateLimit", "user": user})

    def extra_agents(self, user: str) -> Any:
        """
        Retrieve extra agents associated with a user.
        
        Args:
            user: Onchain address in 42-character hexadecimal format
            
        Returns:
            List of extra agents
        """
        return self.post("/info", {"type": "extraAgents", "user": user})

    def name_to_asset(self, name: str) -> int:
        """
        Convert coin name to asset ID.
        
        Args:
            name: Coin name
            
        Returns:
            Asset ID
        """
        return self.coin_to_asset[self.name_to_coin[name]]
