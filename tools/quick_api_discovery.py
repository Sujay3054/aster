"""
Quick Aster API Endpoint Discovery (Non-interactive)
"""

import requests
import json
from datetime import datetime

def quick_api_discovery():
    """Run quick API endpoint discovery"""
    print("QUICK ASTER API ENDPOINT DISCOVERY")
    print("=" * 50)
    print(f"Base URL: https://fapi.asterdex.com")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "https://fapi.asterdex.com"
    discovered_endpoints = {
        'working': [],
        'auth_required': [],
        'not_found': [],
        'other_errors': []
    }
    
    # Test trading endpoints
    trading_endpoints = [
        # Account endpoints
        "/fapi/v1/account",
        "/fapi/v1/balance", 
        "/fapi/v1/positions",
        "/fapi/v1/positionRisk",
        
        # Order endpoints
        "/fapi/v1/order",
        "/fapi/v1/openOrders",
        "/fapi/v1/allOrders",
        "/fapi/v1/orderBook",
        "/fapi/v1/trades",
        
        # Market data endpoints
        "/fapi/v1/ticker/24hr",
        "/fapi/v1/ticker/price",
        "/fapi/v1/ticker/bookTicker",
        "/fapi/v1/klines",
        "/fapi/v1/depth",
        
        # Other endpoints
        "/fapi/v1/leverage",
        "/fapi/v1/marginType",
        "/fapi/v1/commissionRate",
        "/fapi/v1/fundingRate",
    ]
    
    print(f"\nTesting {len(trading_endpoints)} trading endpoints...")
    print("-" * 50)
    
    for endpoint in trading_endpoints:
        url = base_url + endpoint
        print(f"Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            
            result = {
                'endpoint': endpoint,
                'status': status,
                'url': url,
                'content_type': response.headers.get('content-type', ''),
                'response_size': len(response.content)
            }
            
            # Try to parse JSON
            try:
                if 'application/json' in result['content_type']:
                    result['json_response'] = response.json()
                else:
                    result['text_response'] = response.text[:100]
            except:
                result['text_response'] = response.text[:100]
            
            if status == 200:
                print(f"  OK {status} - Working")
                discovered_endpoints['working'].append(result)
            elif status == 401 or status == 403:
                print(f"  AUTH {status} - Authentication required")
                discovered_endpoints['auth_required'].append(result)
            elif status == 404:
                print(f"  NOT_FOUND {status} - Not found")
                discovered_endpoints['not_found'].append(result)
            else:
                print(f"  ERROR {status} - Other error")
                discovered_endpoints['other_errors'].append(result)
                
        except Exception as e:
            print(f"  EXCEPTION - {str(e)[:50]}")
            discovered_endpoints['other_errors'].append({
                'endpoint': endpoint,
                'error': str(e),
                'url': url
            })
    
    # Test alternative patterns
    print(f"\nTesting alternative endpoint patterns...")
    print("-" * 50)
    
    alt_endpoints = [
        "/api/v1/ping",
        "/api/v2/ping",
        "/v1/ping",
        "/ws",
        "/stream",
        "/health",
        "/status",
        "/version"
    ]
    
    for endpoint in alt_endpoints:
        url = base_url + endpoint
        print(f"Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            
            result = {
                'endpoint': endpoint,
                'status': status,
                'url': url,
                'content_type': response.headers.get('content-type', ''),
                'response_size': len(response.content)
            }
            
            if status == 200:
                print(f"  OK {status} - Working")
                discovered_endpoints['working'].append(result)
            elif status == 401 or status == 403:
                print(f"  AUTH {status} - Authentication required")
                discovered_endpoints['auth_required'].append(result)
            elif status == 404:
                print(f"  NOT_FOUND {status} - Not found")
                discovered_endpoints['not_found'].append(result)
            else:
                print(f"  ERROR {status} - Other error")
                discovered_endpoints['other_errors'].append(result)
                
        except Exception as e:
            print(f"  EXCEPTION - {str(e)[:50]}")
    
    # Analyze results
    print(f"\nDISCOVERY ANALYSIS")
    print("=" * 50)
    
    total_tested = (len(discovered_endpoints['working']) + 
                   len(discovered_endpoints['auth_required']) + 
                   len(discovered_endpoints['not_found']) + 
                   len(discovered_endpoints['other_errors']))
    
    print(f"Total endpoints tested: {total_tested}")
    print(f"Working endpoints: {len(discovered_endpoints['working'])}")
    print(f"Auth required: {len(discovered_endpoints['auth_required'])}")
    print(f"Not found (404): {len(discovered_endpoints['not_found'])}")
    print(f"Other errors: {len(discovered_endpoints['other_errors'])}")
    
    # Show working endpoints
    if discovered_endpoints['working']:
        print(f"\nWORKING ENDPOINTS:")
        for endpoint in discovered_endpoints['working']:
            print(f"  GET {endpoint['endpoint']}")
            if 'json_response' in endpoint:
                response_preview = str(endpoint['json_response'])[:80]
                print(f"    Response: {response_preview}...")
    
    # Show auth required endpoints
    if discovered_endpoints['auth_required']:
        print(f"\nAUTH REQUIRED ENDPOINTS:")
        for endpoint in discovered_endpoints['auth_required']:
            print(f"  GET {endpoint['endpoint']} (Status: {endpoint['status']})")
    
    # Export results
    results = {
        'timestamp': datetime.now().isoformat(),
        'base_url': base_url,
        'discovery_results': discovered_endpoints
    }
    
    filename = "aster_api_discovery.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nOK Discovery results exported to {filename}")
    
    print(f"\nDiscovery complete!")
    return discovered_endpoints

if __name__ == "__main__":
    quick_api_discovery()
