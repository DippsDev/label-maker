# tracking_scraper.py - Local tracking lookup via web scraping
# Replaces the labelmaker.cc/_/api/track endpoint

import re
import requests
from bs4 import BeautifulSoup
import json
import os

# ============================================================
# CONFIGURATION - Set your API key here or in environment variable
# ============================================================
# Get a free API key from: https://app.easypost.com/signup
# Then set it here or as environment variable EASYPOST_API_KEY
EASYPOST_API_KEY = os.environ.get('EASYPOST_API_KEY', 'EZTKd223430f11c547cbbeea528cc7886209PAxSvrKQ44MEKsUVnRiOIQ')

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def lookup_via_easypost(tracking_number, carrier='ups'):
    """
    #1 EasyPost API for tracking lookup.
    Sign up for free at: https://app.easypost.com/signup
    Cost: $0.01-0.02 per tracking lookup (no monthly fee)
    """
    if not EASYPOST_API_KEY:
        print("[TRACKING] No EasyPost API key configured")
        print("[TRACKING] Get a free key at: https://app.easypos``t.com/signup")
        print("[TRACKING] Set EASYPOST_API_KEY environment variable or edit tracking_scraper.py")
        return None
    
    try:
        # EasyPost carrier codes
        carrier_map = {
            'ups': 'UPS',
            'fedex': 'FedEx', 
            'usps': 'USPS',
        }
        carrier_code = carrier_map.get(carrier.lower(), carrier.upper())
        
        # Create tracker via EasyPost API
        url = 'https://api.easypost.com/v2/trackers'
        
        response = requests.post(
            url,
            auth=(EASYPOST_API_KEY, ''),
            json={
                'tracker': {
                    'tracking_code': tracking_number,
                    'carrier': carrier_code
                }
            },
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Extract destination from tracking details
            if 'tracking_details' in data and len(data['tracking_details']) > 0:
                # Look for destination in the last event or carrier details
                for detail in reversed(data['tracking_details']):
                    loc = detail.get('tracking_location', {})
                    city = loc.get('city', '')
                    state = loc.get('state', '')
                    zip_code = loc.get('zip', '')
                    
                    if city or zip_code:
                        return {
                            'city': city,
                            'state': state,
                            'zip': zip_code
                        }
            
            # Try carrier_detail for destination
            if 'carrier_detail' in data and data['carrier_detail']:
                cd = data['carrier_detail']
                dest = cd.get('destination_location', '')
                if dest:
                    # Parse "CITY, ST ZIP" format
                    match = re.match(r'([^,]+),\s*([A-Z]{2})(?:\s+(\d{5}))?', dest)
                    if match:
                        return {
                            'city': match.group(1).strip(),
                            'state': match.group(2).strip(),
                            'zip': match.group(3) or ''
                        }
        
        elif response.status_code == 401:
            print("[TRACKING] EasyPost API key invalid")
        else:
            print(f"[TRACKING] EasyPost error: {response.status_code} - {response.text[:200]}")
        
        return None
        
    except Exception as e:
        print(f"[TRACKING] EasyPost error: {e}")
        return None


def lookup_via_parcelsapp(tracking_number):
    """
    #2 ParcelsApp to lookup tracking info - works for UPS, FedEx, USPS, etc.
    This is a tracking aggregator that queries multiple carriers.
    """
    try:
        session = requests.Session()
        
        # First get the page to establish session
        session.get('https://parcelsapp.com/en', headers=HEADERS, timeout=10)
        
        # Then query their API
        api_url = 'https://parcelsapp.com/api/v3/shipments/tracking'
        
        payload = {
            'shipments': [{'trackingId': tracking_number}],
            'language': 'en',
            'apiKey': ''  # They have a free tier
        }
        
        api_headers = {
            **HEADERS,
            'Content-Type': 'application/json',
        }
        
        response = session.post(api_url, json=payload, headers=api_headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'shipments' in data and len(data['shipments']) > 0:
                shipment = data['shipments'][0]
                
                # Extract destination from shipment data
                if 'destination' in shipment:
                    dest = shipment['destination']
                    # Parse "City, ST" or "City, ST ZIP" format
                    match = re.match(r'([^,]+),\s*([A-Z]{2})(?:\s*(\d{5}))?', dest)
                    if match:
                        return {
                            'city': match.group(1).strip(),
                            'state': match.group(2).strip(),
                            'zip': match.group(3) or ''
                        }
                
                # Try to get from last event location
                if 'states' in shipment and len(shipment['states']) > 0:
                    for state in shipment['states']:
                        if 'location' in state:
                            loc = state['location']
                            match = re.match(r'([^,]+),\s*([A-Z]{2})(?:\s*(\d{5}))?', loc)
                            if match:
                                return {
                                    'city': match.group(1).strip(),
                                    'state': match.group(2).strip(),
                                    'zip': match.group(3) or ''
                                }
        
        return None
        
    except Exception as e:
        print(f"[TRACKING] ParcelsApp error: {e}")
        return None


def lookup_via_17track(tracking_number):
    """
    #3 17track.net to lookup tracking info.
    """
    try:
        session = requests.Session()
        
        # Get the tracking page
        url = f'https://t.17track.net/en#nums={tracking_number}'
        session.get('https://www.17track.net/en', headers=HEADERS, timeout=10)
        
        # Try their API
        api_url = 'https://t.17track.net/restapi/track'
        
        payload = {
            'data': [{'num': tracking_number}],
            'guid': '',
            'timeZoneOffset': -300
        }
        
        api_headers = {
            **HEADERS,
            'Content-Type': 'application/json',
        }
        
        response = session.post(api_url, json=payload, headers=api_headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Parse 17track response for destination
            if 'dat' in data and len(data['dat']) > 0:
                track_data = data['dat'][0]
                if 'track' in track_data and 'z0' in track_data['track']:
                    events = track_data['track']['z0']
                    # Look for destination in events
                    for event in events:
                        if 'a' in event:  # Location field
                            loc = event['a']
                            match = re.match(r'([^,]+),\s*([A-Z]{2})(?:\s*(\d{5}))?', loc)
                            if match:
                                return {
                                    'city': match.group(1).strip(),
                                    'state': match.group(2).strip(),
                                    'zip': match.group(3) or ''
                                }
        
        return None
        
    except Exception as e:
        print(f"[TRACKING] 17track error: {e}")
        return None


def lookup_from_zip(zip_code):
    """
    Use pyzipcode to get city/state from a ZIP code.
    This is a fallback when tracking lookup fails but user has the ZIP.
    """
    try:
        from pyzipcode import ZipCodeDatabase
        zcdb = ZipCodeDatabase()
        zipcode = zcdb[zip_code]
        if zipcode:
            return {
                'city': zipcode.city,
                'state': zipcode.state,
                'zip': zip_code
            }
    except Exception as e:
        print(f"[TRACKING] ZIP lookup error: {e}")
    return None


def lookup_ups_tracking(tracking_number):
    """
    Scrape UPS tracking page to get destination city/state/zip.
    UPS tracking numbers are typically 18 characters starting with 1Z.
    #4 UPS tracking lookup - Not fully reliable -
    
    NOTE: UPS heavily blocks automated requests. This may time out.
    """
    try:
        # Clean tracking number
        tracking_number = tracking_number.strip().replace(' ', '')
        
        # Try the UPS JSON API endpoint
        api_url = "https://www.ups.com/track/api/Track/GetStatus"
        
        session = requests.Session()
        
        # First get the main page to establish cookies (short timeout)
        try:
            session.get("https://www.ups.com/track", headers=HEADERS, timeout=5)
        except requests.exceptions.Timeout:
            print("[TRACKING] UPS initial page timeout - site may be blocking requests")
            return None
        
        # Then call the API
        api_headers = {
            **HEADERS,
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': session.cookies.get('X-XSRF-TOKEN-ST', ''),
        }
        
        payload = {
            "Locale": "en_US",
            "TrackingNumber": [tracking_number],
            "Requester": "st/trackdetails"
        }
        
        response = session.post(api_url, json=payload, headers=api_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Parse the response to extract destination
            if 'trackDetails' in data and len(data['trackDetails']) > 0:
                details = data['trackDetails'][0]
                
                # Try to get delivery address
                if 'deliveryAddress' in details:
                    addr = details['deliveryAddress']
                    return {
                        'city': addr.get('city', ''),
                        'state': addr.get('state', ''),
                        'zip': addr.get('zipCode', addr.get('postalCode', ''))
                    }
                
                # Try shipTo address
                if 'shipToAddress' in details:
                    addr = details['shipToAddress']
                    return {
                        'city': addr.get('city', ''),
                        'state': addr.get('state', ''),
                        'zip': addr.get('zipCode', addr.get('postalCode', ''))
                    }
        
        return None
        
    except requests.exceptions.Timeout:
        print("[TRACKING] UPS API timeout - site is blocking requests")
        return None
    except Exception as e:
        print(f"[TRACKING] UPS lookup error: {e}")
        return None


def scrape_ups_html(tracking_number):
    """Fallback HTML scraping for UPS - usually doesn't work due to JS requirement"""
    try:
        url = f"https://www.ups.com/track?loc=en_US&tracknum={tracking_number}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for delivery location in the page
        # UPS uses various class names, try multiple patterns
        patterns = [
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z]{2})\s*(\d{5})',  # City, ST 12345
            r'Delivering to[:\s]*([^,]+),\s*([A-Z]{2})\s*(\d{5})',
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'city': match.group(1).strip(),
                    'state': match.group(2).strip(),
                    'zip': match.group(3).strip()
                }
        
        return {'city': '', 'state': '', 'zip': ''}
        
    except Exception as e:
        print(f"[TRACKING] UPS HTML scrape error: {e}")
        return {'city': '', 'state': '', 'zip': ''}


def lookup_fedex_tracking(tracking_number):
    """
    Scrape FedEx tracking to get destination info.
    FedEx tracking numbers are typically 12-15 digits.
    #5 FedEx tracking lookup - Not fully reliable -
    """
    try:
        tracking_number = tracking_number.strip().replace(' ', '')
        
        # FedEx API endpoint
        api_url = "https://www.fedex.com/trackingCal/track"
        
        payload = {
            'data': f'{{"TrackPackagesRequest":{{"appType":"WTRK","uniqueKey":"","processingParameters":{{}},"trackingInfoList":[{{"trackNumberInfo":{{"trackingNumber":"{tracking_number}","trackingQualifier":"","trackingCarrier":""}}}}]}}}}',
            'action': 'trackpackages',
            'locale': 'en_US',
            'format': 'json',
            'version': '1'
        }
        
        response = requests.post(api_url, data=payload, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Navigate FedEx response structure
            if 'TrackPackagesResponse' in data:
                packages = data['TrackPackagesResponse'].get('packageList', [])
                if packages:
                    pkg = packages[0]
                    dest_city = pkg.get('destLocationCity', '')
                    dest_state = pkg.get('destLocationStateCD', '')
                    dest_zip = pkg.get('destLocationZip', '')
                    
                    return {
                        'city': dest_city,
                        'state': dest_state,
                        'zip': dest_zip
                    }
        
        return {'city': '', 'state': '', 'zip': ''}
        
    except Exception as e:
        print(f"[TRACKING] FedEx lookup error: {e}")
        return {'city': '', 'state': '', 'zip': ''}


def lookup_usps_tracking(tracking_number):
    """
    Scrape USPS tracking to get destination info.
    USPS tracking numbers are typically 20-22 digits.
    #6 USPS tracking lookup - Not fully reliable -
    """
    try:
        tracking_number = tracking_number.strip().replace(' ', '')
        
        # USPS tracking page
        url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
        
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for destination info
        dest_elem = soup.find('span', class_='dest_city')
        if dest_elem:
            # Parse "CITY, ST ZIP" format
            text = dest_elem.get_text().strip()
            match = re.match(r'([^,]+),\s*([A-Z]{2})\s*(\d{5})', text)
            if match:
                return {
                    'city': match.group(1).strip(),
                    'state': match.group(2).strip(),
                    'zip': match.group(3).strip()
                }
        
        return {'city': '', 'state': '', 'zip': ''}
        
    except Exception as e:
        print(f"[TRACKING] USPS lookup error: {e}")
        return {'city': '', 'state': '', 'zip': ''}


def lookup_tracking(tracking_number, slug='ups'):
    """
    Main entry point - looks up tracking based on carrier slug.
    Uses tracking aggregator services as fallback when direct carrier lookups fail.
    
    Args:
        tracking_number: The tracking number to lookup
        slug: Carrier identifier ('ups', 'fedex', 'usps')
    
    Returns:
        dict with 'city', 'state', 'zip' keys
    """
    slug = slug.lower().strip()
    tracking_number = tracking_number.strip().replace(' ', '')
    
    print(f"[TRACKING] Looking up {slug.upper()} tracking: {tracking_number}")
    
    result = None
    
    # PRIORITY 1: Try EasyPost API first (most reliable, $0.01/lookup)
    if EASYPOST_API_KEY:
        print("[TRACKING] Trying EasyPost API...")
        result = lookup_via_easypost(tracking_number, slug)
        if result and (result.get('city') or result.get('zip')):
            print(f"[TRACKING] EasyPost success: {result}")
            return result
    
    # PRIORITY 2: Try direct carrier lookup (often blocked)
    try:
        if slug == 'ups':
            result = lookup_ups_tracking(tracking_number)
        elif slug == 'fedex':
            result = lookup_fedex_tracking(tracking_number)
        elif slug == 'usps':
            result = lookup_usps_tracking(tracking_number)
        else:
            print(f"[TRACKING] Unknown carrier: {slug}")
    except Exception as e:
        print(f"[TRACKING] Direct lookup failed: {e}")
    
    # PRIORITY 3: If direct lookup failed, try free aggregator services
    if not result or (not result.get('city') and not result.get('zip')):
        print("[TRACKING] Direct lookup failed, trying aggregator services...")
        
        # Try ParcelsApp first
        agg_result = lookup_via_parcelsapp(tracking_number)
        if agg_result and (agg_result.get('city') or agg_result.get('zip')):
            result = agg_result
            print(f"[TRACKING] ParcelsApp success: {result}")
        else:
            # Try 17track as last resort
            agg_result = lookup_via_17track(tracking_number)
            if agg_result and (agg_result.get('city') or agg_result.get('zip')):
                result = agg_result
                print(f"[TRACKING] 17track success: {result}")
    
    # Ensure we always return a valid dict
    if not result:
        result = {'city': '', 'state': '', 'zip': ''}
    
    print(f"[TRACKING] Final result: {result}")
    return result


# Test function
if __name__ == '__main__':
    # Test with a sample tracking number (won't work without real number)
    test_tracking = input("Enter tracking number: ")
    test_slug = input("Enter carrier (ups/fedex/usps): ")
    result = lookup_tracking(test_tracking, test_slug)
    print(f"Result: {result}")
