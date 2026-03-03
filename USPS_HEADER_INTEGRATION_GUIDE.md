# USPS Label Header Integration Guide

## Overview
This guide shows how to extract USPS header information from EasyPost and add it to your generated labels.

## What's in the USPS Header?

The header contains:
- **Mail Class Code** (G, P, F, E, etc.) - Large letter in left box
- **Postage Paid Text** - "US POSTAGE PAID IMI" or "US POSTAGE AND FEES PAID"
- **Mail Date** - Date label was created (YYYY-MM-DD)
- **Origin ZIP** - 5-digit ZIP where package was mailed from
- **Permit Number** - USPS permit ID (e.g., C776182)
- **Rate Type** - "Commercial" or "Retail"
- **Weight/Cubic Info** - "0.10 CUBIC ZONE 1" or "16 OZ"
- **Service Name** - "USPS GROUND ADVANTAGE™", "PRIORITY MAIL", etc.

## Files Created

1. **extract_usps_header_info.py** - Extracts header data from EasyPost API
2. **add_usps_header_to_label.py** - Creates header image and adds to labels
3. **USPS_HEADER_INTEGRATION_GUIDE.md** - This guide

## Quick Start

### Step 1: Install Required Packages

```bash
pip install pillow requests
```

### Step 2: Extract Header Info from EasyPost

```python
from extract_usps_header_info import extract_usps_header_info, get_shipment_details

# Get your shipment data
shipment_id = 'shp_...'  # From EasyPost create shipment response
shipment_data = get_shipment_details(shipment_id)

# Extract header information
header_info = extract_usps_header_info(shipment_data)

print(header_info)
# Output:
# {
#   'mail_class_code': 'G',
#   'postage_paid_text': 'US POSTAGE PAID IMI',
#   'mail_date': '2026-01-07',
#   'origin_zip': '75034',
#   'permit_number': 'C776182',
#   'rate_type': 'Commercial',
#   'weight_or_cubic': '0.10 CUBIC',
#   'zone': '1',
#   'service_name': 'USPS GROUND ADVANTAGE™',
#   'mailer_id': '090100002534'
# }
```

### Step 3: Add Header to Your Label

```python
from add_usps_header_to_label import process_label_with_header

# Complete workflow: download label, add header, save
process_label_with_header(
    shipment_id='shp_...',
    output_path='label_with_header.png'
)
```

## Integration with Your Label Maker App

### Option 1: Modify Label Generation Function

Add this to your label generation code:

```python
def generate_label_with_header(shipment_id):
    """Generate label with USPS header"""
    from extract_usps_header_info import extract_usps_header_info, get_shipment_details
    from add_usps_header_to_label import create_usps_header_image, add_header_to_label
    from PIL import Image
    import requests
    from io import BytesIO
    
    # Get shipment data
    shipment_data = get_shipment_details(shipment_id)
    header_info = extract_usps_header_info(shipment_data)
    
    # Download original label
    label_url = shipment_data['postage_label']['label_url']
    response = requests.get(label_url)
    label_image = Image.open(BytesIO(response.content))
    
    # Create and add header
    header_image = create_usps_header_image(header_info, width=label_image.size[0])
    final_label = add_header_to_label(label_image, header_image)
    
    # Save or return
    final_label.save('final_label.png')
    return final_label
```

### Option 2: Patch Your Existing App

Add this to your `run_patched.py` or create a new patch file:

```python
# usps_header_patch.py

def patch_label_generation(module_globals):
    """Patch label generation to add USPS header"""
    
    if 'generateLabel' in module_globals:
        original_generate = module_globals['generateLabel']
        
        def patched_generateLabel(*args, **kwargs):
            """Wrapper that adds USPS header to generated labels"""
            # Call original function
            result = original_generate(*args, **kwargs)
            
            # Add header if this is a USPS label
            if 'usps' in str(kwargs.get('carrier', '')).lower():
                try:
                    from add_usps_header_to_label import create_usps_header_image, add_header_to_label
                    from PIL import Image
                    
                    # Get header info from shipment data
                    shipment_id = kwargs.get('shipment_id')
                    if shipment_id:
                        # Extract and add header
                        # ... implementation here
                        pass
                except Exception as e:
                    print(f"[PATCH] Failed to add USPS header: {e}")
            
            return result
        
        module_globals['generateLabel'] = patched_generateLabel
        print("[*] Patched label generation to add USPS header")
```

## Customization

### Adjust Header Size

```python
# Create larger header
header_image = create_usps_header_image(
    header_info,
    width=800,   # Match your label width
    height=200   # Adjust height as needed
)
```

### Change Fonts

Edit `add_usps_header_to_label.py`:

```python
# Use different fonts
mail_class_font = ImageFont.truetype("path/to/font.ttf", 80)
service_font = ImageFont.truetype("path/to/bold.ttf", 24)
detail_font = ImageFont.truetype("path/to/regular.ttf", 16)
```

### Modify Layout

The header layout is defined in `create_usps_header_image()`. Adjust:
- `mail_class_box_width` - Width of left mail class box (default 20%)
- `service_line_y` - Position of service name section (default 75%)
- `line_height` - Spacing between detail lines (default 20px)

## Testing

### Test Header Extraction

```bash
python extract_usps_header_info.py
```

### Test Header Image Creation

```bash
python add_usps_header_to_label.py
```

This creates `sample_usps_header.png` with sample data.

### Test with Real Shipment

```python
from add_usps_header_to_label import process_label_with_header

# Use a real shipment ID from EasyPost
process_label_with_header('shp_1234567890abcdef', 'test_label.png')
```

## Troubleshooting

### "No permit number found"
- Permit numbers may not be in all EasyPost responses
- You can manually set it: `header_info['permit_number'] = 'YOUR_PERMIT'`

### "Font not found"
- The script falls back to default fonts if Arial isn't available
- Install custom fonts or specify font paths in the code

### "Label dimensions don't match"
- The header automatically resizes to match label width
- Adjust `height` parameter if header looks too tall/short

### "Missing mailer ID"
- Mailer IDs are part of Intelligent Mail barcodes
- May not be directly available in EasyPost API
- Can be left blank or manually added

## Next Steps

1. Test with a real EasyPost shipment
2. Integrate into your label maker app
3. Customize fonts and layout to match your needs
4. Add error handling for missing data

## Support

For issues or questions:
- Check EasyPost API docs: https://www.easypost.com/docs/api
- Review USPS IMb specs: https://postalpro.usps.com/mailing/intelligent-mail-barcode
