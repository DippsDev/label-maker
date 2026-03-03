import requests
import json

# Your EasyPost Production API Key
EASYPOST_API_KEY = "EZTKd223430f11c547cbbeea528cc7886209PAxSvrKQ44MEKsUVnRiOIQ"

def test_easypost_tracking(tracking_number, carrier='UPS'):
    """Test EasyPost API with a tracking number"""
    print(f"\n{'='*60}")
    print(f"Testing EasyPost API")
    print(f"{'='*60}")
    print(f"Tracking Number: {tracking_number}")
    print(f"Carrier: {carrier}")
    print(f"API Key: {EASYPOST_API_KEY[:20]}...")
    
    try:
        url = 'https://api.easypost.com/v2/trackers'
        
        response = requests.post(
            url,
            auth=(EASYPOST_API_KEY, ''),
            json={
                'tracker': {
                    'tracking_code': tracking_number,
                    'carrier': carrier
                }
            },
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("\n✓ SUCCESS! API key is working.")
            print(f"\nTracking Details:")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Carrier: {data.get('carrier', 'N/A')}")
            print(f"  Tracking Code: {data.get('tracking_code', 'N/A')}")
            print(f"  Est. Delivery: {data.get('est_delivery_date', 'N/A')}")
            
            if data.get('tracking_details'):
                latest = data['tracking_details'][0]
                print(f"\nLatest Update:")
                print(f"  Message: {latest.get('message', 'N/A')}")
                print(f"  Status: {latest.get('status', 'N/A')}")
                print(f"  Location: {latest.get('tracking_location', {}).get('city', 'N/A')}, {latest.get('tracking_location', {}).get('state', 'N/A')}")
                print(f"  Date: {latest.get('datetime', 'N/A')}")
            
            print(f"\n✓ Full Response:")
            print(json.dumps(data, indent=2))
            return True
            
        elif response.status_code == 401:
            print("\n✗ FAILED: Invalid API key")
            print("Check that your production key is correct")
            return False
            
        elif response.status_code == 422:
            print("\n✗ FAILED: Invalid tracking number or carrier")
            print(f"Response: {response.text}")
            return False
            
        else:
            print(f"\n✗ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    # Test with a sample UPS tracking number
    # Replace with a real tracking number for actual testing
    test_tracking = "1Z999AA10123456784"  # Sample UPS format
    
    print("EasyPost API Test")
    print("Note: Use a real tracking number for actual results")
    
    test_easypost_tracking(test_tracking, 'UPS')
    
    print("\n" + "="*60)
    print("To test with your own tracking number, run:")
    print("  python test_easypost.py")
    print("Then edit the test_tracking variable with your number")
    print("="*60)
