# run_patched.py - Launches label maker with auth bypassed
# Run with: py -3.11 run_patched.py

import sys
import os

# Get script directory (use short path on Windows to avoid space issues)
script_dir = os.path.dirname(os.path.abspath(__file__))

# On Windows, convert to short path if it contains spaces
if os.name == 'nt' and ' ' in script_dir:
    try:
        import ctypes
        from ctypes import wintypes
        
        GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
        GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetShortPathNameW.restype = wintypes.DWORD
        
        buffer = ctypes.create_unicode_buffer(260)
        get_short_path_name = GetShortPathNameW(script_dir, buffer, 260)
        
        if get_short_path_name:
            script_dir = buffer.value
            print(f"[*] Using short path to avoid spaces: {script_dir}")
    except Exception as e:
        print(f"[!] Could not convert to short path: {e}")
        print("[!] Path contains spaces - this may cause issues")

# Add PYZ extracted modules to path AFTER standard library
pyz_path = os.path.join(script_dir, 'PYZ-00.pyz_extracted')

# We need to be careful - don't override standard library modules
# So we append instead of insert for the PYZ path
sys.path.append(pyz_path)
sys.path.append(script_dir)

# Change to script directory (app expects resources there)
os.chdir(script_dir)

print("[*] Label Maker Patcher")
print(f"[*] Python version: {sys.version}")
print(f"[*] Working dir: {os.getcwd()}")

# Verify we can write to the directory
try:
    test_file = os.path.join(script_dir, 'temp_test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("[*] Write permissions: OK")
except Exception as e:
    print(f"[!] WARNING: Cannot write to directory: {e}")
    print("[!] The app may fail when generating labels!")

# ============================================================
# IMPORT LOCAL TRACKING SCRAPER
# ============================================================
from tracking_scraper import lookup_tracking

# ============================================================
# IMPORT CENTER-ALIGN PATCH FOR SHIP TO ADDRESS
# ============================================================
import center_patch_runtime

# ============================================================
# IMPORT TRACKING LOOKUP FIX
# ============================================================
from fix_tracking_lookup import apply_patch_to_module

# ============================================================
# PATCH REQUESTS MODULE TO RETURN FAKE LICENSE RESPONSES
# ============================================================
import requests

# Save original post function
_original_post = requests.post

class FakeResponse:
    """Fake response object that mimics requests.Response"""
    def __init__(self, json_data, status_code=200):
        import json as json_module
        self._json = json_data
        self.status_code = status_code
        self.text = json_module.dumps(json_data)  # Properly serialize to JSON string
        self.ok = True
    
    def json(self):
        return self._json

def patched_post(url, *args, **kwargs):
    """Intercept POST requests to license server and logging APIs"""
    print(f"[INTERCEPT] POST to: {url}")
    
    # Check if this is the LOGGING API - block it completely (privacy!)
    if 'labelmaker.cc/_/api/log' in url:
        print("[BLOCKED] Logging API call blocked - not sending your data!")
        return FakeResponse({"status": "blocked"})
    
    # Check if this is the TRACKING LOOKUP API
    if 'labelmaker.cc/_/api/track' in url:
        print("[INTERCEPT] Tracking lookup API - using local scraper")
        
        # Extract tracking number and carrier from the request
        try:
            # Determine carrier from URL
            carrier_slug = 'ups'  # default
            if 'track_ups' in url:
                carrier_slug = 'ups'
            elif 'track_fedex' in url:
                carrier_slug = 'fedex'
            elif 'track_usps' in url:
                carrier_slug = 'usps'
            
            # Get JSON data from kwargs or args
            json_data = kwargs.get('json', {})
            
            # Also check 'data' parameter for form data
            data_param = kwargs.get('data', {})
            
            # Handle if data_param is bytes (need to decode/parse it)
            if isinstance(data_param, bytes):
                try:
                    import json as json_module
                    data_param = json_module.loads(data_param.decode('utf-8'))
                except:
                    data_param = {}
            
            # Ensure data_param is a dict
            if not isinstance(data_param, dict):
                data_param = {}
            
            # Handle different API parameter names
            tracking_number = (
                json_data.get('trackingNumber') or 
                json_data.get('tracking_number') or 
                json_data.get('tracking') or
                data_param.get('trackingNumber') or
                data_param.get('tracking_number') or
                data_param.get('tracking') or
                ''
            )
            
            if tracking_number:
                print(f"[TRACKING] Looking up: {tracking_number} ({carrier_slug})")
                result = lookup_tracking(tracking_number, carrier_slug)
                print(f"[TRACKING] Result: {result}")
                return FakeResponse(result)
            else:
                print("[TRACKING] No tracking number provided")
                print(f"[TRACKING] URL: {url}")
                print(f"[TRACKING] JSON data: {json_data}")
                print(f"[TRACKING] Form data: {data_param}")
        except Exception as e:
            print(f"[TRACKING] Error during lookup: {e}")
            import traceback
            traceback.print_exc()
        
        # Return empty data if lookup fails
        return FakeResponse({
            "city": "",
            "state": "",
            "zip": ""
        })
    
    # Check if this is a license check request
    if 'labelmaker.cc' in url or 'api/connect' in url:
        print("[BYPASS] Returning fake license response!")
        # The API expects nested structure:
        # res['status']['success'] = "True" (string)
        # res['license'][...] = license details
        # res['links'][...] = support links
        fake_response = {
            "status": {
                "success": "True",  # Must be string "True"
                "message": ""
            },
            "license": {
                "name": "Licensed User",
                "license_id": "BYPASS-1234-5678-9ABC",
                "license_key": "BYPASS-KEY-1234-5678",
                "expiration_date": "None",
                "current_machines": "1",
                "max_machines": "99",
                "product": "5218ed30-0b15-4a1c-8e64-0831e8081240"
            },
            "links": {
                "telegram": "",
                "signal": "",
                "main": "",
                "telegram_support": "",
                "signal_support": ""
            }
        }
        return FakeResponse(fake_response)
    
    # For all other requests, use the original function
    return _original_post(url, *args, **kwargs)

# Apply the patch
requests.post = patched_post
print("[*] Patched requests.post()")

# ============================================================
# LOAD AND EXECUTE THE APP
# ============================================================
import marshal

print("[*] Loading edit.pyc...")

pyc_path = os.path.join(script_dir, 'edit.pyc')
with open(pyc_path, 'rb') as f:
    # Skip pyc header (16 bytes for Python 3.11)
    f.read(16)
    code = marshal.load(f)

print("[*] Starting application...")
print("=" * 50)

import builtins
module_globals = {
    '__name__': '__main__',
    '__file__': pyc_path,
    '__builtins__': builtins,
}

try:
    # First execute the code to load all functions
    exec(code, module_globals)
    
    # Then immediately patch the function inline
    if 'reverseTrackingLookup' in module_globals:
        original_func = module_globals['reverseTrackingLookup']
        
        def patched_reverseTrackingLookup(slug=None):
            """Wrapper that provides default slug if not provided"""
            if slug is None:
                slug = 'ups'
                print(f"[PATCH] reverseTrackingLookup called without slug, defaulting to: {slug}")
            return original_func(slug)
        
        module_globals['reverseTrackingLookup'] = patched_reverseTrackingLookup
        print("[*] Successfully patched reverseTrackingLookup")
    
    # Apply the first tracking number only patch
    from first_tracking_only_patch import patch_tracking_collection
    patch_tracking_collection(module_globals)
    
except SystemExit as e:
    print(f"[*] App exited with code: {e.code}")
except Exception as e:
    print(f"[!] Error: {e}")
    import traceback
    traceback.print_exc()
