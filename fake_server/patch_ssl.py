# patch_ssl.py - Run this BEFORE launching the label maker app
# This patches the requests library to disable SSL verification

import ssl
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Monkey-patch requests to always use verify=False
_original_request = requests.Session.request

def _patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)

requests.Session.request = _patched_request

# Also patch the module-level functions
_original_post = requests.post
_original_get = requests.get

def patched_post(url, **kwargs):
    kwargs['verify'] = False
    return _original_post(url, **kwargs)

def patched_get(url, **kwargs):
    kwargs['verify'] = False
    return _original_get(url, **kwargs)

requests.post = patched_post
requests.get = patched_get

print("[+] SSL verification disabled for requests library")
print("[+] Now import/run your main application")
