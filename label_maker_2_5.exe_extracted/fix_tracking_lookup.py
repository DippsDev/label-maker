# fix_tracking_lookup.py - Patches the reverseTrackingLookup function to handle missing slug

import sys
import types

def patch_reverse_tracking_lookup():
    """
    Monkey-patch to fix reverseTrackingLookup being called without slug argument.
    This wraps the original function to provide a default slug if not provided.
    """
    
    # We need to patch this after the module is loaded
    # This will be called from run_patched.py after exec()
    
    print("[*] Patching reverseTrackingLookup to handle missing slug argument...")
    
    # The patch will be applied by wrapping the function in the module globals
    # after the bytecode is executed
    
    return True

# This function will be called from run_patched.py to patch the module
def apply_patch_to_module(module_globals):
    """Apply the patch to the loaded module's globals"""
    
    if 'reverseTrackingLookup' not in module_globals:
        print("[!] reverseTrackingLookup not found in module globals")
        return
    
    original_func = module_globals['reverseTrackingLookup']
    
    def patched_reverseTrackingLookup(slug=None):
        """Wrapper that provides default slug if not provided"""
        # If no slug provided, try to determine from the active carrier selection
        if slug is None:
            # Default to 'ups' if we can't determine the carrier
            slug = 'ups'
            print(f"[PATCH] reverseTrackingLookup called without slug, defaulting to: {slug}")
        return original_func(slug)
    
    module_globals['reverseTrackingLookup'] = patched_reverseTrackingLookup
    print("[*] Successfully patched reverseTrackingLookup with default slug handling")
