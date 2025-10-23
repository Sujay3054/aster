"""
Aster SDK - WebSocket manager for real-time data
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import websocket


class WebsocketManager:
    """WebSocket manager for Aster DEX real-time data"""
    
    def __init__(self, base_url: str):
        """
        Initialize WebSocket manager
        
        Args:
            base_url: Base URL for the WebSocket connection
        """
        self.base_url = base_url
        self.ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws"
        self.ws: Optional[websocket.WebSocketApp] = None
        self.subscriptions: Dict[int, Dict[str, Any]] = {}
        self.callbacks: Dict[int, Callable[[Any], None]] = {}
        self.subscription_id_counter = 0
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        self.ping_interval = 50
        self.pong_timeout = 10
        self._logger = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the WebSocket connection"""
        if self.is_running:
            return
            
        self.is_running = True
        self._connect()

    def stop(self) -> None:
        """Stop the WebSocket connection"""
        self.is_running = False
        if self.ws:
            self.ws.close()

    def _connect(self) -> None:
        """Establish WebSocket connection"""
        try:
            self._logger.info(f"Connecting to WebSocket: {self.ws_url}")
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
        except Exception as e:
            self._logger.error(f"Failed to connect to WebSocket: {e}")
            self._handle_reconnect()

    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        """Handle WebSocket connection open"""
        self._logger.info("WebSocket connection opened")
        self.reconnect_attempts = 0
        
        # Resubscribe to all active subscriptions
        with self._lock:
            for subscription_id, subscription in self.subscriptions.items():
                self._send_subscription(subscription)

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle WebSocket message"""
        try:
            data = json.loads(message)
            self._logger.debug(f"Received message: {data}")
            
            # Handle different message types
            if isinstance(data, dict):
                if "stream" in data and "data" in data:
                    # Stream data
                    stream = data["stream"]
                    stream_data = data["data"]
                    
                    # Find subscription by stream
                    with self._lock:
                        for subscription_id, subscription in self.subscriptions.items():
                            if self._matches_subscription(subscription, stream):
                                callback = self.callbacks.get(subscription_id)
                                if callback:
                                    try:
                                        callback(stream_data)
                                    except Exception as e:
                                        self._logger.error(f"Error in callback: {e}")
                                break
                                
                elif "result" in data:
                    # Subscription result
                    self._logger.info(f"Subscription result: {data['result']}")
                    
                elif "error" in data:
                    # Error message
                    self._logger.error(f"WebSocket error: {data['error']}")
                    
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            self._logger.error(f"Error handling WebSocket message: {e}")

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        """Handle WebSocket error"""
        self._logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """Handle WebSocket connection close"""
        self._logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        
        if self.is_running:
            self._handle_reconnect()

    def _handle_reconnect(self) -> None:
        """Handle WebSocket reconnection"""
        if not self.is_running or self.reconnect_attempts >= self.max_reconnect_attempts:
            self._logger.error("Max reconnection attempts reached or connection stopped")
            return
            
        self.reconnect_attempts += 1
        self._logger.info(f"Attempting to reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        time.sleep(self.reconnect_delay)
        self._connect()

    def _send_subscription(self, subscription: Dict[str, Any]) -> None:
        """Send subscription message"""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            message = json.dumps(subscription)
            self.ws.send(message)
            self._logger.debug(f"Sent subscription: {message}")

    def _matches_subscription(self, subscription: Dict[str, Any], stream: str) -> bool:
        """Check if a stream matches a subscription"""
        sub_type = subscription.get("type")
        sub_coin = subscription.get("coin")
        
        if sub_type == "l2Book" and stream.endswith("@depth"):
            return stream.startswith(sub_coin.lower())
        elif sub_type == "trades" and stream.endswith("@trade"):
            return stream.startswith(sub_coin.lower())
        elif sub_type == "ticker" and stream.endswith("@ticker"):
            return stream.startswith(sub_coin.lower())
        elif sub_type == "candle" and "@kline_" in stream:
            return stream.startswith(sub_coin.lower())
        elif sub_type == "bbo" and stream.endswith("@bbo"):
            return stream.startswith(sub_coin.lower())
        elif sub_type == "activeAssetCtx" and stream.endswith("@activeAssetCtx"):
            return stream.startswith(sub_coin.lower())
            
        return False

    def subscribe(self, subscription: Dict[str, Any], callback: Callable[[Any], None]) -> int:
        """
        Subscribe to a data stream
        
        Args:
            subscription: Subscription parameters
            callback: Callback function for received data
            
        Returns:
            Subscription ID
        """
        with self._lock:
            subscription_id = self.subscription_id_counter
            self.subscription_id_counter += 1
            
            self.subscriptions[subscription_id] = subscription
            self.callbacks[subscription_id] = callback
            
            # Send subscription if connected
            if self.ws and self.ws.sock and self.ws.sock.connected:
                self._send_subscription(subscription)
                
        return subscription_id

    def unsubscribe(self, subscription: Dict[str, Any], subscription_id: int) -> bool:
        """
        Unsubscribe from a data stream
        
        Args:
            subscription: Subscription parameters
            subscription_id: Subscription ID
            
        Returns:
            True if unsubscribed successfully
        """
        with self._lock:
            if subscription_id in self.subscriptions:
                del self.subscriptions[subscription_id]
                del self.callbacks[subscription_id]
                
                # Send unsubscribe message if connected
                if self.ws and self.ws.sock and self.ws.sock.connected:
                    unsubscribe_msg = {
                        "method": "UNSUBSCRIBE",
                        "params": [subscription.get("stream", "")],
                        "id": subscription_id
                    }
                    self.ws.send(json.dumps(unsubscribe_msg))
                    
                return True
                
        return False

    def subscribe_l2_book(self, symbol: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to L2 order book updates
        
        Args:
            symbol: Trading symbol
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@depth"],
            "id": self.subscription_id_counter,
            "type": "l2Book",
            "coin": symbol
        }
        return self.subscribe(subscription, callback)

    def subscribe_trades(self, symbol: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to trade updates
        
        Args:
            symbol: Trading symbol
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@trade"],
            "id": self.subscription_id_counter,
            "type": "trades",
            "coin": symbol
        }
        return self.subscribe(subscription, callback)

    def subscribe_ticker(self, symbol: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to ticker updates
        
        Args:
            symbol: Trading symbol
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@ticker"],
            "id": self.subscription_id_counter,
            "type": "ticker",
            "coin": symbol
        }
        return self.subscribe(subscription, callback)

    def subscribe_candles(self, symbol: str, interval: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to candlestick updates
        
        Args:
            symbol: Trading symbol
            interval: Time interval (1m, 5m, 1h, etc.)
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@kline_{interval}"],
            "id": self.subscription_id_counter,
            "type": "candle",
            "coin": symbol,
            "interval": interval
        }
        return self.subscribe(subscription, callback)

    def subscribe_bbo(self, symbol: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to best bid/offer updates
        
        Args:
            symbol: Trading symbol
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@bbo"],
            "id": self.subscription_id_counter,
            "type": "bbo",
            "coin": symbol
        }
        return self.subscribe(subscription, callback)

    def subscribe_active_asset_ctx(self, symbol: str, callback: Callable[[Any], None]) -> int:
        """
        Subscribe to active asset context updates
        
        Args:
            symbol: Trading symbol
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@activeAssetCtx"],
            "id": self.subscription_id_counter,
            "type": "activeAssetCtx",
            "coin": symbol
        }
        return self.subscribe(subscription, callback)
