"""
Aster SDK - Unit Tests
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from eth_account import Account

from aster_sdk import Info, Exchange, API
from aster_sdk.utils.constants import MAINNET_API_URL
from aster_sdk.utils.error import ClientError, ServerError
from aster_sdk.utils.types import Cloid


class TestAPI:
    """Test API base class"""
    
    def test_api_initialization(self):
        """Test API initialization"""
        api = API()
        assert api.base_url == MAINNET_API_URL
        assert api.timeout is None
        
        custom_url = "https://custom.api.com"
        api = API(custom_url, timeout=30)
        assert api.base_url == custom_url
        assert api.timeout == 30
    
    @patch('aster_sdk.api.requests.Session.post')
    def test_post_success(self, mock_post):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        api = API()
        response = api.post("/test", {"data": "test"})
        
        assert response == {"success": True}
        mock_post.assert_called_once()
    
    @patch('aster_sdk.api.requests.Session.post')
    def test_post_client_error(self, mock_post):
        """Test POST request with client error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = '{"code": "INVALID_REQUEST", "msg": "Bad request"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response
        
        api = API()
        
        with pytest.raises(ClientError) as exc_info:
            api.post("/test", {"data": "test"})
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "INVALID_REQUEST"
    
    @patch('aster_sdk.api.requests.Session.post')
    def test_post_server_error(self, mock_post):
        """Test POST request with server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        api = API()
        
        with pytest.raises(ServerError) as exc_info:
            api.post("/test", {"data": "test"})
        
        assert exc_info.value.status_code == 500


class TestInfo:
    """Test Info module"""
    
    def test_info_initialization(self):
        """Test Info initialization"""
        info = Info(MAINNET_API_URL, skip_ws=True)
        assert info.base_url == MAINNET_API_URL
        assert info.coin_to_asset == {}
        assert info.name_to_coin == {}
    
    @patch('aster_sdk.info.Info.post')
    def test_all_mids(self, mock_post):
        """Test getting all mid prices"""
        mock_post.return_value = {"BTC": "50000.0", "ETH": "3000.0"}
        
        info = Info(MAINNET_API_URL, skip_ws=True)
        mids = info.all_mids()
        
        assert mids == {"BTC": "50000.0", "ETH": "3000.0"}
        mock_post.assert_called_once_with("/info", {"type": "allMids"})
    
    @patch('aster_sdk.info.Info.post')
    def test_user_state(self, mock_post):
        """Test getting user state"""
        mock_user_state = {
            "assetPositions": [],
            "marginSummary": {"accountValue": "1000.0"},
            "withdrawable": "1000.0"
        }
        mock_post.return_value = mock_user_state
        
        info = Info(MAINNET_API_URL, skip_ws=True)
        user_state = info.user_state("0x123")
        
        assert user_state == mock_user_state
        mock_post.assert_called_once_with("/info", {"type": "clearinghouseState", "user": "0x123"})
    
    @patch('aster_sdk.info.Info.post')
    def test_l2_snapshot(self, mock_post):
        """Test getting L2 order book snapshot"""
        mock_l2_book = {
            "coin": "BTC",
            "levels": [[{"px": "50000", "sz": "1.0"}]],
            "time": 1234567890
        }
        mock_post.return_value = mock_l2_book
        
        info = Info(MAINNET_API_URL, skip_ws=True)
        info.name_to_coin = {"BTC": "BTC"}  # Mock the mapping
        
        l2_book = info.l2_snapshot("BTC")
        
        assert l2_book == mock_l2_book
        mock_post.assert_called_once_with("/info", {"type": "l2Book", "coin": "BTC"})


class TestExchange:
    """Test Exchange module"""
    
    def setup_method(self):
        """Setup test method"""
        self.private_key = "0x" + "0" * 64
        self.wallet = Account.from_key(self.private_key)
        self.exchange = Exchange(self.wallet, MAINNET_API_URL)
    
    def test_exchange_initialization(self):
        """Test Exchange initialization"""
        assert self.exchange.wallet == self.wallet
        assert self.exchange.base_url == MAINNET_API_URL
        assert self.exchange.vault_address is None
        assert self.exchange.account_address is None
    
    @patch('aster_sdk.exchange.Exchange._post_action')
    @patch('aster_sdk.exchange.get_timestamp_ms')
    def test_order(self, mock_timestamp, mock_post_action):
        """Test placing an order"""
        mock_timestamp.return_value = 1234567890
        mock_post_action.return_value = {"status": "success"}
        
        # Mock the info module
        self.exchange.info.name_to_asset = {"BTC": 0}
        
        response = self.exchange.order(
            name="BTC",
            is_buy=True,
            sz=0.001,
            limit_px=50000.0,
            order_type={"limit": {"tif": "Gtc"}},
            reduce_only=False
        )
        
        assert response == {"status": "success"}
        mock_post_action.assert_called_once()
    
    @patch('aster_sdk.exchange.Exchange._post_action')
    @patch('aster_sdk.exchange.get_timestamp_ms')
    def test_cancel(self, mock_timestamp, mock_post_action):
        """Test canceling an order"""
        mock_timestamp.return_value = 1234567890
        mock_post_action.return_value = {"status": "cancelled"}
        
        # Mock the info module
        self.exchange.info.name_to_asset = {"BTC": 0}
        
        response = self.exchange.cancel("BTC", 123)
        
        assert response == {"status": "cancelled"}
        mock_post_action.assert_called_once()
    
    @patch('aster_sdk.exchange.Exchange._post_action')
    @patch('aster_sdk.exchange.get_timestamp_ms')
    def test_cancel_by_cloid(self, mock_timestamp, mock_post_action):
        """Test canceling an order by client order ID"""
        mock_timestamp.return_value = 1234567890
        mock_post_action.return_value = {"status": "cancelled"}
        
        # Mock the info module
        self.exchange.info.name_to_asset = {"BTC": 0}
        
        cloid = Cloid("my_order_1")
        response = self.exchange.cancel_by_cloid("BTC", cloid)
        
        assert response == {"status": "cancelled"}
        mock_post_action.assert_called_once()
    
    def test_set_expires_after(self):
        """Test setting expiration time"""
        self.exchange.set_expires_after(1234567890)
        assert self.exchange.expires_after == 1234567890
        
        self.exchange.set_expires_after(None)
        assert self.exchange.expires_after is None


class TestTypes:
    """Test type definitions"""
    
    def test_cloid(self):
        """Test Cloid class"""
        cloid = Cloid("my_order_1")
        assert cloid.to_raw() == "my_order_1"
        assert str(cloid) == "my_order_1"
        assert repr(cloid) == "Cloid('my_order_1')"


class TestErrorHandling:
    """Test error handling"""
    
    def test_client_error(self):
        """Test ClientError"""
        error = ClientError(400, "INVALID_REQUEST", "Bad request", {"header": "value"})
        assert error.status_code == 400
        assert error.code == "INVALID_REQUEST"
        assert error.message == "Bad request"
        assert error.headers == {"header": "value"}
    
    def test_server_error(self):
        """Test ServerError"""
        error = ServerError(500, "Internal server error")
        assert error.status_code == 500
        assert error.message == "Internal server error"


if __name__ == "__main__":
    pytest.main([__file__])
