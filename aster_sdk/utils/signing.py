"""
Aster SDK - Signing utilities adapted for Aster blockchain
"""

import time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, Literal, TypedDict

# Blockchain dependencies
try:
    import msgpack
except ImportError:
    msgpack = None
    print("Warning: msgpack not available. Some signing functions may not work.")

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak, to_hex

from .constants import ASTER_CHAIN_ID, ASTER_DOMAIN_NAME, ASTER_VERSION
from .types import OrderRequest, OrderWire, OrderType, Cloid


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

Tif = Union[Literal["Alo"], Literal["Ioc"], Literal["Gtc"]]
LimitOrderType = TypedDict("LimitOrderType", {"tif": Tif})
OrderType = TypedDict("OrderType", {"limit": LimitOrderType}, total=False)

# =============================================================================
# ASTER-SPECIFIC SIGNING TYPES
# =============================================================================

# Define EIP-712 signing types for Aster transactions
ASTER_ORDER_SIGN_TYPES = [
    {"name": "asterChain", "type": "string"},      # "Mainnet" or "Testnet"
    {"name": "coin", "type": "string"},
    {"name": "is_buy", "type": "bool"},
    {"name": "sz", "type": "string"},
    {"name": "limit_px", "type": "string"},
    {"name": "order_type", "type": "string"},
    {"name": "reduce_only", "type": "bool"},
    {"name": "nonce", "type": "uint64"},
]

ASTER_TRANSFER_SIGN_TYPES = [
    {"name": "asterChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "token", "type": "string"},
    {"name": "time", "type": "uint64"},
]

ASTER_WITHDRAW_SIGN_TYPES = [
    {"name": "asterChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "time", "type": "uint64"},
]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)

def float_to_wire(x: float) -> str:
    """Convert float to string for wire format."""
    rounded = f"{x:.8f}"
    if abs(float(rounded) - x) >= 1e-12:
        raise ValueError("float_to_wire causes rounding", x)
    if rounded == "-0":
        rounded = "0"
    normalized = Decimal(rounded).normalize()
    return f"{normalized:f}"

def float_to_int(x: float, power: int) -> int:
    """Convert float to integer with specified decimal places."""
    with_decimals = x * 10**power
    if abs(round(with_decimals) - with_decimals) >= 1e-3:
        raise ValueError("float_to_int causes rounding", x)
    return round(with_decimals)

def address_to_bytes(address: str) -> bytes:
    """Convert Ethereum address to bytes."""
    return bytes.fromhex(address[2:] if address.startswith("0x") else address)

# =============================================================================
# TRANSACTION HASHING
# =============================================================================

def action_hash(action: Dict[str, Any], vault_address: Optional[str], nonce: int, expires_after: Optional[int]) -> bytes:
    """
    Create hash for action - adapted for Aster's hashing requirements.
    """
    if msgpack is None:
        # Fallback to JSON serialization if msgpack is not available
        import json
        data = json.dumps(action, sort_keys=True).encode()
    else:
        # Pack the action data
        data = msgpack.packb(action)
    
    data += nonce.to_bytes(8, "big")
    
    # Add vault address if present
    if vault_address is None:
        data += b"\x00"
    else:
        data += b"\x01"
        data += address_to_bytes(vault_address)
    
    # Add expiration if present
    if expires_after is not None:
        data += b"\x00"
        data += expires_after.to_bytes(8, "big")
    
    return keccak(data)

def construct_phantom_agent(hash: bytes, is_mainnet: bool) -> Dict[str, Any]:
    """Construct phantom agent for signing - adapted for Aster's agent system."""
    return {
        "source": "a" if is_mainnet else "b", 
        "connectionId": hash.hex()
    }

# =============================================================================
# EIP-712 PAYLOAD CONSTRUCTION
# =============================================================================

def l1_payload(phantom_agent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create EIP-712 payload for L1 actions.
    Adapted for Aster's domain and types.
    """
    return {
        "domain": {
            "chainId": ASTER_CHAIN_ID,
            "name": ASTER_DOMAIN_NAME,
            "verifyingContract": "0x0000000000000000000000000000000000000000",
            "version": ASTER_VERSION,
        },
        "types": {
            "Agent": [
                {"name": "source", "type": "string"},
                {"name": "connectionId", "type": "bytes32"},
            ],
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        },
        "primaryType": "Agent",
        "message": phantom_agent,
    }

def user_signed_payload(primary_type: str, payload_types: List[Dict], action: Dict[str, Any]) -> Dict[str, Any]:
    """Create EIP-712 payload for user-signed actions."""
    chain_id = int(action.get("signatureChainId", f"0x{ASTER_CHAIN_ID:x}"), 16)
    return {
        "domain": {
            "name": "AsterSignTransaction",
            "version": ASTER_VERSION,
            "chainId": chain_id,
            "verifyingContract": "0x0000000000000000000000000000000000000000",
        },
        "types": {
            primary_type: payload_types,
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        },
        "primaryType": primary_type,
        "message": action,
    }

# =============================================================================
# SIGNING FUNCTIONS
# =============================================================================

def sign_inner(wallet: Account, data: Dict[str, Any]) -> Dict[str, Any]:
    """Core signing function using EIP-712."""
    structured_data = encode_typed_data(full_message=data)
    signed = wallet.sign_message(structured_data)
    return {
        "r": to_hex(signed["r"]), 
        "s": to_hex(signed["s"]), 
        "v": signed["v"]
    }

def sign_l1_action(wallet: Account, action: Dict[str, Any], vault_address: Optional[str], 
                  nonce: int, expires_after: Optional[int], is_mainnet: bool) -> Dict[str, Any]:
    """Sign L1 actions (orders, cancels, etc.)."""
    hash_bytes = action_hash(action, vault_address, nonce, expires_after)
    phantom_agent = construct_phantom_agent(hash_bytes, is_mainnet)
    data = l1_payload(phantom_agent)
    return sign_inner(wallet, data)

def sign_user_signed_action(wallet: Account, action: Dict[str, Any], payload_types: List[Dict], 
                           primary_type: str, is_mainnet: bool) -> Dict[str, Any]:
    """Sign user-signed actions (transfers, withdrawals, etc.)."""
    # Set chain identifiers
    action["signatureChainId"] = f"0x{ASTER_CHAIN_ID:x}"
    action["asterChain"] = "Mainnet" if is_mainnet else "Testnet"
    
    data = user_signed_payload(primary_type, payload_types, action)
    return sign_inner(wallet, data)

# =============================================================================
# ASTER-SPECIFIC SIGNING FUNCTIONS
# =============================================================================

def sign_aster_order_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign Aster order actions."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,
        "AsterTransaction:Order",
        is_mainnet,
    )

def sign_aster_transfer_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign Aster transfer actions."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_TRANSFER_SIGN_TYPES,
        "AsterTransaction:Transfer",
        is_mainnet,
    )

def sign_aster_withdraw_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign Aster withdrawal actions."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_WITHDRAW_SIGN_TYPES,
        "AsterTransaction:Withdraw",
        is_mainnet,
    )

# =============================================================================
# ORDER CONVERSION FUNCTIONS
# =============================================================================

def order_request_to_order_wire(order: OrderRequest, asset_id: int) -> OrderWire:
    """Convert order request to wire format for Aster."""
    return {
        "a": asset_id,
        "b": order["is_buy"],
        "p": float_to_wire(order["limit_px"]),
        "s": float_to_wire(order["sz"]),
        "r": order["reduce_only"],
        "t": order["order_type"],
    }

def order_wires_to_order_action(order_wires: List[OrderWire], builder: Optional[Dict] = None) -> Dict[str, Any]:
    """Convert order wires to order action for Aster."""
    action = {
        "type": "order",
        "orders": order_wires,
    }
    if builder:
        action["builder"] = builder
    return action

# =============================================================================
# USD CONVERSION
# =============================================================================

def float_to_usd_int(x: float) -> int:
    """Convert float USD to integer representation."""
    return float_to_int(x, 6)  # 6 decimal places for USD

# =============================================================================
# CANCEL AND MODIFY FUNCTIONS
# =============================================================================

def cancel_request_to_cancel_wire(cancel: Dict[str, Any], asset_id: int) -> Dict[str, Any]:
    """Convert cancel request to wire format."""
    return {
        "a": asset_id,
        "o": cancel["oid"],
    }

def cancel_by_cloid_request_to_cancel_wire(cancel: Dict[str, Any], asset_id: int) -> Dict[str, Any]:
    """Convert cancel by cloid request to wire format."""
    return {
        "asset": asset_id,
        "cloid": cancel["cloid"],
    }

# =============================================================================
# TRANSFER FUNCTIONS
# =============================================================================

def sign_usd_transfer_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign USD transfer action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_TRANSFER_SIGN_TYPES,
        "AsterTransaction:Transfer",
        is_mainnet,
    )

def sign_spot_transfer_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign spot transfer action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_TRANSFER_SIGN_TYPES,
        "AsterTransaction:Transfer",
        is_mainnet,
    )

def sign_withdraw_from_bridge_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign withdraw from bridge action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_WITHDRAW_SIGN_TYPES,
        "AsterTransaction:Withdraw",
        is_mainnet,
    )

# =============================================================================
# AGENT FUNCTIONS
# =============================================================================

def sign_agent(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign agent action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,  # Use order types for agent actions
        "AsterTransaction:Agent",
        is_mainnet,
    )

# =============================================================================
# MULTI-SIG FUNCTIONS
# =============================================================================

def sign_multi_sig_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool, 
                         vault_address: Optional[str], nonce: int, expires_after: Optional[int]) -> Dict[str, Any]:
    """Sign multi-sig action."""
    return sign_l1_action(wallet, action, vault_address, nonce, expires_after, is_mainnet)

# =============================================================================
# TOKEN DELEGATION
# =============================================================================

def sign_token_delegate_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign token delegation action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,  # Use order types for delegation
        "AsterTransaction:Delegate",
        is_mainnet,
    )

# =============================================================================
# BUILDER FEE APPROVAL
# =============================================================================

def sign_approve_builder_fee(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign builder fee approval."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,  # Use order types for builder fee
        "AsterTransaction:ApproveBuilderFee",
        is_mainnet,
    )

# =============================================================================
# CONVERT TO MULTI-SIG USER
# =============================================================================

def sign_convert_to_multi_sig_user_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign convert to multi-sig user action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,  # Use order types for multi-sig conversion
        "AsterTransaction:ConvertToMultiSig",
        is_mainnet,
    )

# =============================================================================
# SEND ASSET
# =============================================================================

def sign_send_asset_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign send asset action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_TRANSFER_SIGN_TYPES,
        "AsterTransaction:SendAsset",
        is_mainnet,
    )

# =============================================================================
# USD CLASS TRANSFER
# =============================================================================

def sign_usd_class_transfer_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign USD class transfer action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_TRANSFER_SIGN_TYPES,
        "AsterTransaction:UsdClassTransfer",
        is_mainnet,
    )

# =============================================================================
# USER DEX ABSTRACTION
# =============================================================================

def sign_user_dex_abstraction_action(wallet: Account, action: Dict[str, Any], is_mainnet: bool) -> Dict[str, Any]:
    """Sign user dex abstraction action."""
    return sign_user_signed_action(
        wallet,
        action,
        ASTER_ORDER_SIGN_TYPES,  # Use order types for dex abstraction
        "AsterTransaction:UserDexAbstraction",
        is_mainnet,
    )
