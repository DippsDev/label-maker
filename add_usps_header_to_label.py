"""
add_usps_header_to_label.py - Add USPS header to generated labels

This script demonstrates how to add the USPS header section to your labels
using PIL/Pillow to composite the header onto the label image.
"""

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from extract_usps_header_info import extract_usps_header_info, get_shipment_details

def create_usps_header_image(header_info, width=600, height=150):
    """
    Create the USPS header image section
    
    Layout:
    +----------+------------------------------------------+
    |          |  US POSTAGE PAID IMI                    |
    |    G     |  2026-01-07                             |
    |          |  75034                                  |
    |          |  C776182                                |
    |          |  Commercial                             |
    |          |  0.10 CUBIC ZONE 1                      |
    +----------+------------------------------------------+
    |          USPS GROUND ADVANTAGE™                    |
    +----------+------------------------------------------+
    """
    
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw borders
    border_color = 'black'
    border_width = 2
    
    # Outer border
    draw.rectangle(
        [(0, 0), (width-1, height-1)],
        outline=border_color,
        width=border_width
    )
    
    # Vertical divider for mail class box (left 20% of width)
    mail_class_box_width = int(width * 0.20)
    draw.line(
        [(mail_class_box_width, 0), (mail_class_box_width, int(height * 0.75))],
        fill=border_color,
        width=border_width
    )
    
    # Horizontal divider for service name (bottom 25% of height)
    service_line_y = int(height * 0.75)
    draw.line(
        [(0, service_line_y), (width, service_line_y)],
        fill=border_color,
        width=border_width
    )
    
    # Try to load fonts, fall back to default if not available
    try:
        # Large font for mail class letter
        mail_class_font = ImageFont.truetype("arial.ttf", 80)
        # Medium font for service name
        service_font = ImageFont.truetype("arialbd.ttf", 24)
        # Small font for details
        detail_font = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback to default font
        mail_class_font = ImageFont.load_default()
        service_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()
    
    # Draw mail class letter (centered in left box)
    mail_class = header_info.get('mail_class_code', 'G')
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), mail_class, font=mail_class_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    mail_class_x = (mail_class_box_width - text_width) // 2
    mail_class_y = (service_line_y - text_height) // 2
    
    draw.text(
        (mail_class_x, mail_class_y),
        mail_class,
        fill='black',
        font=mail_class_font
    )
    
    # Draw details in right section
    details_x = mail_class_box_width + 15
    details_y = 10
    line_height = 20
    
    details = [
        header_info.get('postage_paid_text', 'US POSTAGE PAID IMI'),
        header_info.get('mail_date', ''),
        header_info.get('origin_zip', ''),
        header_info.get('permit_number', ''),
        header_info.get('rate_type', 'Commercial'),
    ]
    
    # Add weight/cubic and zone on same line
    weight_cubic = header_info.get('weight_or_cubic', '')
    zone = header_info.get('zone', '')
    if weight_cubic:
        zone_text = f" ZONE {zone}" if zone else ""
        details.append(f"{weight_cubic}{zone_text}")
    
    for i, detail in enumerate(details):
        if detail:  # Only draw non-empty details
            draw.text(
                (details_x, details_y + (i * line_height)),
                detail,
                fill='black',
                font=detail_font
            )
    
    # Draw service name (centered in bottom section)
    service_name = header_info.get('service_name', 'USPS GROUND ADVANTAGE™')
    
    bbox = draw.textbbox((0, 0), service_name, font=service_font)
    text_width = bbox[2] - bbox[0]
    
    service_x = (width - text_width) // 2
    service_y = service_line_y + 15
    
    draw.text(
        (service_x, service_y),
        service_name,
        fill='black',
        font=service_font
    )
    
    return img

def add_header_to_label(label_image, header_image):
    """
    Composite the header image onto the top of the label
    
    Args:
        label_image: PIL Image of the original label
        header_image: PIL Image of the header to add
    
    Returns:
        PIL Image with header added
    """
    
    # Get dimensions
    label_width, label_height = label_image.size
    header_width, header_height = header_image.size
    
    # Resize header to match label width if needed
    if header_width != label_width:
        aspect_ratio = header_height / header_width
        new_height = int(label_width * aspect_ratio)
        header_image = header_image.resize((label_width, new_height), Image.Resampling.LANCZOS)
        header_height = new_height
    
    # Create new image with space for header
    new_height = label_height + header_height
    combined = Image.new('RGB', (label_width, new_height), 'white')
    
    # Paste header at top
    combined.paste(header_image, (0, 0))
    
    # Paste original label below header
    combined.paste(label_image, (0, header_height))
    
    return combined

def process_label_with_header(shipment_id, output_path='label_with_header.png'):
    """
    Complete workflow: Get shipment data, extract header info, 
    download label, add header, save result
    """
    
    print(f"\n{'='*60}")
    print("Processing Label with USPS Header")
    print(f"{'='*60}")
    
    # Step 1: Get shipment data
    print("\n[1/5] Fetching shipment data...")
    shipment_data = get_shipment_details(shipment_id)
    
    if not shipment_data:
        print("✗ Failed to get shipment data")
        return None
    
    print("✓ Shipment data retrieved")
    
    # Step 2: Extract header info
    print("\n[2/5] Extracting header information...")
    header_info = extract_usps_header_info(shipment_data)
    print("✓ Header info extracted")
    print(f"  Service: {header_info['service_name']}")
    print(f"  Mail Class: {header_info['mail_class_code']}")
    
    # Step 3: Download original label
    print("\n[3/5] Downloading original label...")
    label_url = shipment_data.get('postage_label', {}).get('label_url', '')
    
    if not label_url:
        print("✗ No label URL found in shipment")
        return None
    
    response = requests.get(label_url, timeout=30)
    if response.status_code != 200:
        print(f"✗ Failed to download label: {response.status_code}")
        return None
    
    label_image = Image.open(BytesIO(response.content))
    print(f"✓ Label downloaded ({label_image.size[0]}x{label_image.size[1]})")
    
    # Step 4: Create header image
    print("\n[4/5] Creating header image...")
    header_image = create_usps_header_image(header_info, width=label_image.size[0])
    print(f"✓ Header created ({header_image.size[0]}x{header_image.size[1]})")
    
    # Step 5: Combine and save
    print("\n[5/5] Combining header with label...")
    final_image = add_header_to_label(label_image, header_image)
    final_image.save(output_path)
    print(f"✓ Saved to: {output_path}")
    print(f"  Final size: {final_image.size[0]}x{final_image.size[1]}")
    
    print(f"\n{'='*60}")
    print("✓ SUCCESS! Label with header created")
    print(f"{'='*60}")
    
    return final_image

if __name__ == "__main__":
    print("USPS Label Header Generator")
    print("="*60)
    print("\nThis script adds the USPS header section to your labels")
    print("\nUsage:")
    print("  from add_usps_header_to_label import process_label_with_header")
    print("  process_label_with_header('shp_...', 'output.png')")
    print("\n" + "="*60)
    
    # Example: Create a sample header image
    sample_header_info = {
        'mail_class_code': 'G',
        'postage_paid_text': 'US POSTAGE PAID IMI',
        'mail_date': '2026-01-07',
        'origin_zip': '75034',
        'permit_number': 'C776182',
        'rate_type': 'Commercial',
        'weight_or_cubic': '0.10 CUBIC',
        'zone': '1',
        'service_name': 'USPS GROUND ADVANTAGE™',
        'mailer_id': '090100002534'
    }
    
    print("\nCreating sample header image...")
    header_img = create_usps_header_image(sample_header_info)
    header_img.save('sample_usps_header.png')
    print("✓ Saved sample header to: sample_usps_header.png")
