"""
extract_usps_header_info.py - Extract USPS label header information from EasyPost API

This script shows how to extract and format the USPS label header information
that appears at the top of USPS labels (Mail Class, Postage Paid, Service info, etc.)
"""

import requests
import json
from datetime import datetime

EASYPOST_API_KEY = "EZTKd223430f11c547cbbeea528cc7886209PAxSvrKQ44MEKsUVnRiOIQ"

# Mail class indicator mapping
MAIL_CLASS_CODES = {
    'First': 'F',
    'Priority': 'P',
    'Express': 'E',
    'Ground': 'G',
    'GroundAdvantage': 'G',
    'ParcelSelect': 'PS',
    'MediaMail': 'M',
    'LibraryMail': 'L'
}

def get_shipment_details(shipment_id):
    """
    Retrieve full shipment details from EasyPost
    This contains all the information needed for the label header
    """
    url = f'https://api.easypost.com/v2/shipments/{shipment_id}'
    
    response = requests.get(
        url,
        auth=(EASYPOST_API_KEY, ''),
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching shipment: {response.status_code}")
        print(response.text)
        return None

def extract_usps_header_info(shipment_data):
    """
    Extract USPS label header information from EasyPost shipment data
    
    Returns a dictionary with:
    - mail_class_code: Single letter code (G, P, F, etc.)
    - postage_paid_text: "US POSTAGE PAID IMI" or "US POSTAGE AND FEES PAID"
    - mail_date: Date the label was created
    - origin_zip: 5-digit origin ZIP
    - permit_number: USPS permit number
    - rate_type: "Commercial" or "Retail"
    - service_name: Full service name (e.g., "USPS GROUND ADVANTAGE™")
    - zone: Shipping zone (if available)
    - weight_or_cubic: Weight or cubic pricing info
    - mailer_id: Intelligent Mail barcode mailer ID
    """
    
    header_info = {}
    
    # Get the selected rate (the one that was purchased)
    selected_rate = shipment_data.get('selected_rate', {})
    
    # Service name and mail class
    service = selected_rate.get('service', '')
    carrier = selected_rate.get('carrier', '')
    
    # Map service to mail class code
    mail_class = 'G'  # Default to Ground
    if 'Priority' in service and 'Express' not in service:
        mail_class = 'P'
    elif 'Express' in service:
        mail_class = 'E'
    elif 'First' in service:
        mail_class = 'F'
    elif 'Ground' in service or 'GroundAdvantage' in service:
        mail_class = 'G'
    elif 'ParcelSelect' in service:
        mail_class = 'PS'
    elif 'Media' in service:
        mail_class = 'M'
    
    header_info['mail_class_code'] = mail_class
    header_info['service_name'] = service.upper()
    
    # Postage paid text (IMI for commercial, standard for retail)
    rate_type = selected_rate.get('rate_type', 'commercial')
    if rate_type.lower() == 'commercial':
        header_info['postage_paid_text'] = 'US POSTAGE PAID IMI'
    else:
        header_info['postage_paid_text'] = 'US POSTAGE AND FEES PAID'
    
    header_info['rate_type'] = rate_type.capitalize()
    
    # Mail date (creation date)
    created_at = shipment_data.get('created_at', '')
    if created_at:
        # Parse ISO format: 2026-01-07T12:34:56Z
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            header_info['mail_date'] = dt.strftime('%Y-%m-%d')
        except:
            header_info['mail_date'] = datetime.now().strftime('%Y-%m-%d')
    else:
        header_info['mail_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Origin ZIP code
    from_address = shipment_data.get('from_address', {})
    origin_zip = from_address.get('zip', '')
    if origin_zip and len(origin_zip) >= 5:
        header_info['origin_zip'] = origin_zip[:5]
    else:
        header_info['origin_zip'] = ''
    
    # Permit number - This is typically in the rate details or options
    # EasyPost may not always provide this, as it's carrier-specific
    options = shipment_data.get('options', {})
    header_info['permit_number'] = options.get('permit_number', '')
    
    # If not in options, check carrier_accounts or forms
    if not header_info['permit_number']:
        forms = shipment_data.get('forms', [])
        for form in forms:
            if 'permit' in form.get('form_type', '').lower():
                header_info['permit_number'] = form.get('permit_number', '')
                break
    
    # Zone information
    header_info['zone'] = selected_rate.get('zone', '')
    
    # Weight or cubic pricing
    parcel = shipment_data.get('parcel', {})
    weight = parcel.get('weight', 0)
    
    # Check if cubic pricing
    if 'cubic' in service.lower() or options.get('cubic_pricing'):
        # Calculate cubic feet if dimensions available
        length = parcel.get('length', 0)
        width = parcel.get('width', 0)
        height = parcel.get('height', 0)
        
        if length and width and height:
            cubic_feet = (length * width * height) / 1728  # Convert cubic inches to cubic feet
            header_info['weight_or_cubic'] = f'{cubic_feet:.2f} CUBIC'
        else:
            header_info['weight_or_cubic'] = 'CUBIC'
    else:
        # Weight in ounces
        header_info['weight_or_cubic'] = f'{weight} OZ'
    
    # Mailer ID - This is part of the Intelligent Mail barcode
    # EasyPost provides this in the postage_label or tracker data
    tracker = shipment_data.get('tracker', {})
    header_info['mailer_id'] = tracker.get('mailer_id', '')
    
    # If not in tracker, it might be in the label details
    postage_label = shipment_data.get('postage_label', {})
    if not header_info['mailer_id'] and 'integrated_form' in postage_label:
        # The mailer ID is often embedded in the label data
        header_info['mailer_id'] = ''  # Would need to parse from label
    
    return header_info

def format_usps_header(header_info):
    """
    Format the header information for display/printing
    """
    lines = []
    lines.append(f"Mail Class: [{header_info['mail_class_code']}]")
    lines.append(f"{header_info['postage_paid_text']}")
    lines.append(f"Date: {header_info['mail_date']}")
    lines.append(f"Origin ZIP: {header_info['origin_zip']}")
    
    if header_info['permit_number']:
        lines.append(f"Permit: {header_info['permit_number']}")
    
    lines.append(f"Rate: {header_info['rate_type']}")
    
    if header_info['weight_or_cubic']:
        zone_text = f" ZONE {header_info['zone']}" if header_info['zone'] else ""
        lines.append(f"{header_info['weight_or_cubic']}{zone_text}")
    
    lines.append(f"Service: {header_info['service_name']}")
    
    if header_info['mailer_id']:
        lines.append(f"Mailer ID: {header_info['mailer_id']}")
    
    return '\n'.join(lines)

def test_with_shipment_id(shipment_id):
    """Test extraction with a shipment ID"""
    print(f"\n{'='*60}")
    print(f"Extracting USPS Header Info from Shipment")
    print(f"{'='*60}")
    print(f"Shipment ID: {shipment_id}")
    
    shipment_data = get_shipment_details(shipment_id)
    
    if not shipment_data:
        print("Failed to retrieve shipment data")
        return None
    
    print("\n✓ Shipment data retrieved")
    
    header_info = extract_usps_header_info(shipment_data)
    
    print("\n" + "="*60)
    print("EXTRACTED HEADER INFORMATION")
    print("="*60)
    print(format_usps_header(header_info))
    print("="*60)
    
    print("\n\nRaw header data:")
    print(json.dumps(header_info, indent=2))
    
    return header_info

if __name__ == "__main__":
    print("USPS Label Header Information Extractor")
    print("="*60)
    print("\nThis script extracts the header information that appears")
    print("at the top of USPS labels (Mail Class, Postage Paid, etc.)")
    print("\nTo use:")
    print("1. Create a shipment using EasyPost API")
    print("2. Get the shipment ID from the response")
    print("3. Call: test_with_shipment_id('shp_...')")
    print("\nExample:")
    print("  python extract_usps_header_info.py")
    print("="*60)
    
    # Example usage - replace with actual shipment ID
    # test_with_shipment_id('shp_1234567890abcdef')
