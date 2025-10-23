"""
Aster SDK - Exchange module for trading operations
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from eth_account.signers.local import LocalAccount

from .api import API
from .info import Info
from .utils.constants import MAINNET_API_URL
from .utils.signing import (
    get_timestamp_ms,
    sign_l1_action,
    sign_user_signed_action,
    order_request_to_order_wire,
    order_wires_to_order_action,
    float_to_wire,
    float_to_usd_int,
    sign_usd_transfer_action,
    sign_spot_transfer_action,
    sign_withdraw_from_bridge_action,
    sign_agent,
    sign_approve_builder_fee,
    sign_convert_to_multi_sig_user_action,
    sign_send_asset_action,
    sign_token_delegate_action,
    sign_usd_class_transfer_action,
    sign_user_dex_abstraction_action,
    sign_multi_sig_action,
)
from .utils.types import (
    OrderRequest,
    OrderType,
    Cloid,
    BuilderInfo,
    Meta,
    SpotMeta,
)


class Exchange(API):
    """Exchange module for trading operations on Aster DEX"""
    
    # Default Max Slippage for Market Orders 5%
    DEFAULT_SLIPPAGE = 0.05

    def __init__(
        self,
        wallet: LocalAccount,
        base_url: Optional[str] = None,
        meta: Optional[Meta] = None,
        vault_address: Optional[str] = None,
        account_address: Optional[str] = None,
        spot_meta: Optional[SpotMeta] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize Exchange client
        
        Args:
            wallet: Ethereum wallet for signing transactions
            base_url: Base URL for the API
            meta: Pre-loaded perp metadata
            vault_address: Vault address for vault trading
            account_address: Account address override
            spot_meta: Pre-loaded spot metadata
            timeout: Request timeout
        """
        super().__init__(base_url, timeout)
        self.wallet = wallet
        self.vault_address = vault_address
        self.account_address = account_address
        self.info = Info(base_url, True, meta, spot_meta, timeout)
        self.expires_after: Optional[int] = None

    def _post_action(self, action: Dict[str, Any], signature: Dict[str, Any], nonce: int) -> Any:
        """
        Post an action to the exchange
        
        Args:
            action: Action to execute
            signature: Signature for the action
            nonce: Nonce for the action
            
        Returns:
            Exchange response
        """
        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature,
            "vaultAddress": self.vault_address if action["type"] not in ["usdClassTransfer", "sendAsset"] else None,
            "expiresAfter": self.expires_after,
        }
        logging.debug(payload)
        return self.post("/exchange", payload)

    def _slippage_price(
        self,
        name: str,
        is_buy: bool,
        slippage: float,
        px: Optional[float] = None,
    ) -> float:
        """
        Calculate slippage-adjusted price
        
        Args:
            name: Coin name
            is_buy: Whether this is a buy order
            slippage: Slippage percentage
            px: Base price (if None, uses mid price)
            
        Returns:
            Slippage-adjusted price
        """
        coin = self.info.name_to_coin[name]
        if not px:
            # Get midprice
            px = float(self.info.all_mids()[coin])

        asset = self.info.coin_to_asset[coin]
        # spot assets start at 10000
        is_spot = asset >= 10_000

        # Calculate Slippage
        px *= (1 + slippage) if is_buy else (1 - slippage)
        # We round px to 5 significant figures and 6 decimals for perps, 8 decimals for spot
        return round(float(f"{px:.5g}"), (6 if not is_spot else 8) - self.info.asset_to_sz_decimals[asset])

    def set_expires_after(self, expires_after: Optional[int]) -> None:
        """
        Set expiration time for actions
        
        Args:
            expires_after: Expiration timestamp in milliseconds
        """
        self.expires_after = expires_after

    def order(
        self,
        name: str,
        is_buy: bool,
        sz: float,
        limit_px: float,
        order_type: OrderType,
        reduce_only: bool = False,
        cloid: Optional[Cloid] = None,
        builder: Optional[BuilderInfo] = None,
    ) -> Any:
        """
        Place a single order
        
        Args:
            name: Coin name
            is_buy: Whether this is a buy order
            sz: Order size
            limit_px: Limit price
            order_type: Order type
            reduce_only: Whether this is a reduce-only order
            cloid: Client order ID
            builder: Builder information
            
        Returns:
            Order response
        """
        order: OrderRequest = {
            "coin": name,
            "is_buy": is_buy,
            "sz": sz,
            "limit_px": limit_px,
            "order_type": order_type,
            "reduce_only": reduce_only,
        }
        if cloid:
            order["cloid"] = cloid
        return self.bulk_orders([order], builder)

    def bulk_orders(self, order_requests: List[OrderRequest], builder: Optional[BuilderInfo] = None) -> Any:
        """
        Place multiple orders
        
        Args:
            order_requests: List of order requests
            builder: Builder information
            
        Returns:
            Bulk order response
        """
        order_wires = [
            order_request_to_order_wire(order, self.info.name_to_asset(order["coin"])) 
            for order in order_requests
        ]
        timestamp = get_timestamp_ms()

        if builder:
            builder["b"] = builder["b"].lower()
        order_action = order_wires_to_order_action(order_wires, builder)

        signature = sign_l1_action(
            self.wallet,
            order_action,
            self.vault_address,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )

        return self._post_action(order_action, signature, timestamp)

    def market_open(
        self,
        name: str,
        is_buy: bool,
        sz: float,
        px: Optional[float] = None,
        slippage: float = DEFAULT_SLIPPAGE,
        cloid: Optional[Cloid] = None,
        builder: Optional[BuilderInfo] = None,
    ) -> Any:
        """
        Place a market order to open a position
        
        Args:
            name: Coin name
            is_buy: Whether this is a buy order
            sz: Order size
            px: Base price (if None, uses mid price)
            slippage: Slippage percentage
            cloid: Client order ID
            builder: Builder information
            
        Returns:
            Market order response
        """
        # Get aggressive Market Price
        px = self._slippage_price(name, is_buy, slippage, px)
        # Market Order is an aggressive Limit Order IoC
        return self.order(
            name, is_buy, sz, px, order_type={"limit": {"tif": "Ioc"}}, reduce_only=False, cloid=cloid, builder=builder
        )

    def market_close(
        self,
        coin: str,
        sz: Optional[float] = None,
        px: Optional[float] = None,
        slippage: float = DEFAULT_SLIPPAGE,
        cloid: Optional[Cloid] = None,
        builder: Optional[BuilderInfo] = None,
    ) -> Any:
        """
        Place a market order to close a position
        
        Args:
            coin: Coin name
            sz: Order size (if None, closes entire position)
            px: Base price (if None, uses mid price)
            slippage: Slippage percentage
            cloid: Client order ID
            builder: Builder information
            
        Returns:
            Market close response
        """
        address: str = self.wallet.address
        if self.account_address:
            address = self.account_address
        if self.vault_address:
            address = self.vault_address
            
        positions = self.info.user_state(address)["assetPositions"]
        for position in positions:
            item = position["position"]
            if coin != item["coin"]:
                continue
            szi = float(item["szi"])
            if not sz:
                sz = abs(szi)
            is_buy = True if szi < 0 else False
            # Get aggressive Market Price
            px = self._slippage_price(coin, is_buy, slippage, px)
            # Market Order is an aggressive Limit Order IoC
            return self.order(
                coin,
                is_buy,
                sz,
                px,
                order_type={"limit": {"tif": "Ioc"}},
                reduce_only=True,
                cloid=cloid,
                builder=builder,
            )

    def cancel(self, name: str, oid: int) -> Any:
        """
        Cancel an order by order ID
        
        Args:
            name: Coin name
            oid: Order ID
            
        Returns:
            Cancel response
        """
        return self.bulk_cancel([{"coin": name, "oid": oid}])

    def cancel_by_cloid(self, name: str, cloid: Cloid) -> Any:
        """
        Cancel an order by client order ID
        
        Args:
            name: Coin name
            cloid: Client order ID
            
        Returns:
            Cancel response
        """
        return self.bulk_cancel_by_cloid([{"coin": name, "cloid": cloid}])

    def bulk_cancel(self, cancel_requests: List[Dict[str, Any]]) -> Any:
        """
        Cancel multiple orders by order ID
        
        Args:
            cancel_requests: List of cancel requests
            
        Returns:
            Bulk cancel response
        """
        timestamp = get_timestamp_ms()
        cancel_action = {
            "type": "cancel",
            "cancels": [
                {
                    "a": self.info.name_to_asset(cancel["coin"]),
                    "o": cancel["oid"],
                }
                for cancel in cancel_requests
            ],
        }
        signature = sign_l1_action(
            self.wallet,
            cancel_action,
            self.vault_address,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )

        return self._post_action(cancel_action, signature, timestamp)

    def bulk_cancel_by_cloid(self, cancel_requests: List[Dict[str, Any]]) -> Any:
        """
        Cancel multiple orders by client order ID
        
        Args:
            cancel_requests: List of cancel by cloid requests
            
        Returns:
            Bulk cancel response
        """
        timestamp = get_timestamp_ms()

        cancel_action = {
            "type": "cancelByCloid",
            "cancels": [
                {
                    "asset": self.info.name_to_asset(cancel["coin"]),
                    "cloid": cancel["cloid"].to_raw(),
                }
                for cancel in cancel_requests
            ],
        }
        signature = sign_l1_action(
            self.wallet,
            cancel_action,
            self.vault_address,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )

        return self._post_action(cancel_action, signature, timestamp)

    def update_leverage(self, leverage: int, name: str, is_cross: bool = True) -> Any:
        """
        Update leverage for a position
        
        Args:
            leverage: New leverage value
            name: Coin name
            is_cross: Whether to use cross margin
            
        Returns:
            Update leverage response
        """
        timestamp = get_timestamp_ms()
        update_leverage_action = {
            "type": "updateLeverage",
            "asset": self.info.name_to_asset(name),
            "isCross": is_cross,
            "leverage": leverage,
        }
        signature = sign_l1_action(
            self.wallet,
            update_leverage_action,
            self.vault_address,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )
        return self._post_action(update_leverage_action, signature, timestamp)

    def update_isolated_margin(self, amount: float, name: str) -> Any:
        """
        Update isolated margin for a position
        
        Args:
            amount: Margin amount
            name: Coin name
            
        Returns:
            Update margin response
        """
        timestamp = get_timestamp_ms()
        amount = float_to_usd_int(amount)
        update_isolated_margin_action = {
            "type": "updateIsolatedMargin",
            "asset": self.info.name_to_asset(name),
            "isBuy": True,
            "ntli": amount,
        }
        signature = sign_l1_action(
            self.wallet,
            update_isolated_margin_action,
            self.vault_address,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )
        return self._post_action(update_isolated_margin_action, signature, timestamp)

    def set_referrer(self, code: str) -> Any:
        """
        Set referrer code
        
        Args:
            code: Referrer code
            
        Returns:
            Set referrer response
        """
        timestamp = get_timestamp_ms()
        set_referrer_action = {
            "type": "setReferrer",
            "code": code,
        }
        signature = sign_l1_action(
            self.wallet,
            set_referrer_action,
            None,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )
        return self._post_action(set_referrer_action, signature, timestamp)

    def create_sub_account(self, name: str) -> Any:
        """
        Create a sub account
        
        Args:
            name: Sub account name
            
        Returns:
            Create sub account response
        """
        timestamp = get_timestamp_ms()
        create_sub_account_action = {
            "type": "createSubAccount",
            "name": name,
        }
        signature = sign_l1_action(
            self.wallet,
            create_sub_account_action,
            None,
            timestamp,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )
        return self._post_action(create_sub_account_action, signature, timestamp)

    def usd_transfer(self, amount: float, destination: str) -> Any:
        """
        Transfer USD to another address
        
        Args:
            amount: Transfer amount
            destination: Destination address
            
        Returns:
            Transfer response
        """
        timestamp = get_timestamp_ms()
        action = {"destination": destination, "amount": str(amount), "time": timestamp, "type": "usdSend"}
        is_mainnet = self.base_url == MAINNET_API_URL
        signature = sign_usd_transfer_action(self.wallet, action, is_mainnet)
        return self._post_action(action, signature, timestamp)

    def spot_transfer(self, amount: float, destination: str, token: str) -> Any:
        """
        Transfer spot tokens to another address
        
        Args:
            amount: Transfer amount
            destination: Destination address
            token: Token name
            
        Returns:
            Transfer response
        """
        timestamp = get_timestamp_ms()
        action = {
            "destination": destination,
            "amount": str(amount),
            "token": token,
            "time": timestamp,
            "type": "spotSend",
        }
        is_mainnet = self.base_url == MAINNET_API_URL
        signature = sign_spot_transfer_action(self.wallet, action, is_mainnet)
        return self._post_action(action, signature, timestamp)

    def withdraw_from_bridge(self, amount: float, destination: str) -> Any:
        """
        Withdraw from bridge
        
        Args:
            amount: Withdrawal amount
            destination: Destination address
            
        Returns:
            Withdrawal response
        """
        timestamp = get_timestamp_ms()
        action = {"destination": destination, "amount": str(amount), "time": timestamp, "type": "withdraw3"}
        is_mainnet = self.base_url == MAINNET_API_URL
        signature = sign_withdraw_from_bridge_action(self.wallet, action, is_mainnet)
        return self._post_action(action, signature, timestamp)

    def approve_agent(self, name: Optional[str] = None) -> Tuple[Any, str]:
        """
        Approve an agent
        
        Args:
            name: Agent name (optional)
            
        Returns:
            Tuple of (approval response, agent private key)
        """
        import secrets
        agent_key = "0x" + secrets.token_hex(32)
        account = LocalAccount.from_key(agent_key)
        timestamp = get_timestamp_ms()
        is_mainnet = self.base_url == MAINNET_API_URL
        action = {
            "type": "approveAgent",
            "agentAddress": account.address,
            "agentName": name or "",
            "nonce": timestamp,
        }
        signature = sign_agent(self.wallet, action, is_mainnet)
        if name is None:
            del action["agentName"]

        return (
            self._post_action(action, signature, timestamp),
            agent_key,
        )

    def approve_builder_fee(self, builder: str, max_fee_rate: str) -> Any:
        """
        Approve builder fee
        
        Args:
            builder: Builder address
            max_fee_rate: Maximum fee rate
            
        Returns:
            Approval response
        """
        timestamp = get_timestamp_ms()

        action = {"maxFeeRate": max_fee_rate, "builder": builder, "nonce": timestamp, "type": "approveBuilderFee"}
        signature = sign_approve_builder_fee(self.wallet, action, self.base_url == MAINNET_API_URL)
        return self._post_action(action, signature, timestamp)

    def convert_to_multi_sig_user(self, authorized_users: List[str], threshold: int) -> Any:
        """
        Convert account to multi-sig user
        
        Args:
            authorized_users: List of authorized user addresses
            threshold: Signature threshold
            
        Returns:
            Conversion response
        """
        timestamp = get_timestamp_ms()
        authorized_users = sorted(authorized_users)
        signers = {
            "authorizedUsers": authorized_users,
            "threshold": threshold,
        }
        action = {
            "type": "convertToMultiSigUser",
            "signers": json.dumps(signers),
            "nonce": timestamp,
        }
        signature = sign_convert_to_multi_sig_user_action(self.wallet, action, self.base_url == MAINNET_API_URL)
        return self._post_action(action, signature, timestamp)

    def token_delegate(self, validator: str, wei: int, is_undelegate: bool) -> Any:
        """
        Delegate or undelegate tokens
        
        Args:
            validator: Validator address
            wei: Amount in wei
            is_undelegate: Whether this is an undelegation
            
        Returns:
            Delegation response
        """
        timestamp = get_timestamp_ms()
        action = {
            "validator": validator,
            "wei": wei,
            "isUndelegate": is_undelegate,
            "nonce": timestamp,
            "type": "tokenDelegate",
        }
        is_mainnet = self.base_url == MAINNET_API_URL
        signature = sign_token_delegate_action(self.wallet, action, is_mainnet)
        return self._post_action(action, signature, timestamp)

    def send_asset(self, destination: str, source_dex: str, destination_dex: str, token: str, amount: float) -> Any:
        """
        Send asset between DEXes
        
        Args:
            destination: Destination address
            source_dex: Source DEX
            destination_dex: Destination DEX
            token: Token name
            amount: Amount to send
            
        Returns:
            Send asset response
        """
        timestamp = get_timestamp_ms()
        str_amount = str(amount)

        action = {
            "type": "sendAsset",
            "destination": destination,
            "sourceDex": source_dex,
            "destinationDex": destination_dex,
            "token": token,
            "amount": str_amount,
            "fromSubAccount": self.vault_address if self.vault_address else "",
            "nonce": timestamp,
        }
        signature = sign_send_asset_action(self.wallet, action, self.base_url == MAINNET_API_URL)
        return self._post_action(action, signature, timestamp)

    def usd_class_transfer(self, amount: float, to_perp: bool) -> Any:
        """
        Transfer between USD classes
        
        Args:
            amount: Transfer amount
            to_perp: Whether to transfer to perp
            
        Returns:
            Transfer response
        """
        timestamp = get_timestamp_ms()
        str_amount = str(amount)
        if self.vault_address:
            str_amount += f" subaccount:{self.vault_address}"

        action = {
            "type": "usdClassTransfer",
            "amount": str_amount,
            "toPerp": to_perp,
            "nonce": timestamp,
        }
        signature = sign_usd_class_transfer_action(self.wallet, action, self.base_url == MAINNET_API_URL)
        return self._post_action(action, signature, timestamp)

    def user_dex_abstraction(self, user: str, enabled: bool) -> Any:
        """
        Enable/disable user dex abstraction
        
        Args:
            user: User address
            enabled: Whether to enable
            
        Returns:
            Abstraction response
        """
        timestamp = get_timestamp_ms()
        action = {
            "type": "userDexAbstraction",
            "user": user.lower(),
            "enabled": enabled,
            "nonce": timestamp,
        }
        signature = sign_user_dex_abstraction_action(self.wallet, action, self.base_url == MAINNET_API_URL)
        return self._post_action(action, signature, timestamp)

    def multi_sig(self, multi_sig_user: str, inner_action: Dict[str, Any], signatures: List[Dict[str, Any]], nonce: int, vault_address: Optional[str] = None) -> Any:
        """
        Execute multi-sig action
        
        Args:
            multi_sig_user: Multi-sig user address
            inner_action: Inner action to execute
            signatures: List of signatures
            nonce: Nonce for the action
            vault_address: Vault address (optional)
            
        Returns:
            Multi-sig response
        """
        multi_sig_user = multi_sig_user.lower()
        multi_sig_action = {
            "type": "multiSig",
            "signatureChainId": "0x66eee",
            "signatures": signatures,
            "payload": {
                "multiSigUser": multi_sig_user,
                "outerSigner": self.wallet.address.lower(),
                "action": inner_action,
            },
        }
        is_mainnet = self.base_url == MAINNET_API_URL
        signature = sign_multi_sig_action(
            self.wallet,
            multi_sig_action,
            is_mainnet,
            vault_address,
            nonce,
            self.expires_after,
        )
        return self._post_action(multi_sig_action, signature, nonce)
