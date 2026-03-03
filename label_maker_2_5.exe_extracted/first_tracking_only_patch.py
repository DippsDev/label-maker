# first_tracking_only_patch.py - Ensures only the first tracking number is used

def patch_tracking_collection(module_globals):
    """
    Patches the tracking number collection functions to only use the first tracking number found.
    This prevents issues when multiple barcodes are detected on a label.
    """
    
    print("[*] Patching tracking collection to use only first tracking number...")
    
    # Patch collectTrackingNumberUPS
    if 'collectTrackingNumberUPS' in module_globals:
        original_ups = module_globals['collectTrackingNumberUPS']
        
        def patched_collectTrackingNumberUPS(fileName):
            """Wrapper that ensures only first tracking number is used"""
            result = original_ups(fileName)
            
            # Check if ups_tracking_number is a list with multiple items
            if 'ups_tracking_number' in module_globals:
                tracking_list = module_globals['ups_tracking_number']
                if isinstance(tracking_list, list) and len(tracking_list) > 1:
                    print(f"[PATCH] Multiple UPS tracking numbers found: {len(tracking_list)}")
                    print(f"[PATCH] Using only first tracking number: {tracking_list[0]}")
                    module_globals['ups_tracking_number'] = [tracking_list[0]]
            
            return result
        
        module_globals['collectTrackingNumberUPS'] = patched_collectTrackingNumberUPS
        print("[*] Patched collectTrackingNumberUPS")
    
    # Patch collectTrackingNumberFedEx
    if 'collectTrackingNumberFedEx' in module_globals:
        original_fedex = module_globals['collectTrackingNumberFedEx']
        
        def patched_collectTrackingNumberFedEx(fileName):
            """Wrapper that ensures only first tracking number is used"""
            result = original_fedex(fileName)
            
            # Check if fedex_tracking_number is a list with multiple items
            if 'fedex_tracking_number' in module_globals:
                tracking_list = module_globals['fedex_tracking_number']
                if isinstance(tracking_list, list) and len(tracking_list) > 1:
                    print(f"[PATCH] Multiple FedEx tracking numbers found: {len(tracking_list)}")
                    print(f"[PATCH] Using only first tracking number: {tracking_list[0]}")
                    module_globals['fedex_tracking_number'] = [tracking_list[0]]
            
            return result
        
        module_globals['collectTrackingNumberFedEx'] = patched_collectTrackingNumberFedEx
        print("[*] Patched collectTrackingNumberFedEx")
    
    # Patch collectTrackingNumberUSPS
    if 'collectTrackingNumberUSPS' in module_globals:
        original_usps = module_globals['collectTrackingNumberUSPS']
        
        def patched_collectTrackingNumberUSPS(fileName, service):
            """Wrapper that ensures only first tracking number is used"""
            result = original_usps(fileName, service)
            
            # Check if usps_tracking_number is a list with multiple items
            if 'usps_tracking_number' in module_globals:
                tracking_list = module_globals['usps_tracking_number']
                if isinstance(tracking_list, list) and len(tracking_list) > 1:
                    print(f"[PATCH] Multiple USPS tracking numbers found: {len(tracking_list)}")
                    print(f"[PATCH] Using only first tracking number: {tracking_list[0]}")
                    module_globals['usps_tracking_number'] = [tracking_list[0]]
            
            return result
        
        module_globals['collectTrackingNumberUSPS'] = patched_collectTrackingNumberUSPS
        print("[*] Patched collectTrackingNumberUSPS")
    
    # Patch collectTrackingNumberCanadaPost
    if 'collectTrackingNumberCanadaPost' in module_globals:
        original_canada = module_globals['collectTrackingNumberCanadaPost']
        
        def patched_collectTrackingNumberCanadaPost(fileName):
            """Wrapper that ensures only first tracking number is used"""
            result = original_canada(fileName)
            
            # Check if canada_post_tracking_number is a list with multiple items
            if 'canada_post_tracking_number' in module_globals:
                tracking_list = module_globals['canada_post_tracking_number']
                if isinstance(tracking_list, list) and len(tracking_list) > 1:
                    print(f"[PATCH] Multiple Canada Post tracking numbers found: {len(tracking_list)}")
                    print(f"[PATCH] Using only first tracking number: {tracking_list[0]}")
                    module_globals['canada_post_tracking_number'] = [tracking_list[0]]
            
            return result
        
        module_globals['collectTrackingNumberCanadaPost'] = patched_collectTrackingNumberCanadaPost
        print("[*] Patched collectTrackingNumberCanadaPost")
    
    print("[*] Tracking collection patches applied successfully")
