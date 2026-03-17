# preview_patch.py - Adds dynamic label preview based on active carrier tab

from PIL import Image, ImageTk
import customtkinter as cs

# Global variables to track preview state
preview_label_widget = None
current_carrier = 'ups'
preview_update_scheduled = False

def create_preview_widget(parent_frame, row=0, column=0):
    """
    Creates a preview label widget that displays a sample label.
    This should be called during UI initialization.
    """
    global preview_label_widget
    
    # Create a frame for the preview
    preview_frame = cs.CTkFrame(parent_frame, width=400, height=600)
    preview_frame.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')
    
    # Create label for preview title
    preview_title = cs.CTkLabel(preview_frame, text="Label Preview", font=('Arial', 16, 'bold'))
    preview_title.pack(pady=5)
    
    # Create label for the preview image
    preview_label_widget = cs.CTkLabel(preview_frame, text="Preview will appear here")
    preview_label_widget.pack(pady=10, padx=10, fill='both', expand=True)
    
    print("[PREVIEW] Preview widget created")
    return preview_frame

def update_preview_for_carrier(carrier, module_globals):
    """
    Updates the preview to show a sample label for the specified carrier.
    
    Args:
        carrier: One of 'ups', 'fedex', 'usps', 'canada_post', 'purolator'
        module_globals: The module's global namespace to access widgets
    """
    global preview_label_widget, current_carrier
    
    if preview_label_widget is None:
        print("[PREVIEW] Preview widget not initialized")
        return
    
    current_carrier = carrier
    print(f"[PREVIEW] Updating preview for carrier: {carrier}")
    
    try:
        # Load the appropriate template based on carrier
        import os
        dir_path = os.getcwd()
        
        template_map = {
            'ups': '/resources/ups_master.png',
            'fedex': '/resources/fedex_master.png',
            'usps': '/resources/usps_master.png',
            'canada_post': '/resources/canada_3_master.png',
            'purolator': '/resources/purolator_master.png'
        }
        
        template_path = dir_path + template_map.get(carrier, '/resources/ups_master.png')
        
        if os.path.exists(template_path):
            # Load and resize the template for preview
            img = Image.open(template_path)
            
            # Resize to fit preview area (maintain aspect ratio)
            max_width = 380
            max_height = 550
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Update the preview label
            preview_label_widget.configure(image=photo, text="")
            preview_label_widget.image = photo  # Keep a reference
            
            print(f"[PREVIEW] Loaded template: {template_path}")
        else:
            preview_label_widget.configure(text=f"Template not found:\n{template_path}", image=None)
            print(f"[PREVIEW] Template not found: {template_path}")
            
    except Exception as e:
        print(f"[PREVIEW] Error updating preview: {e}")
        import traceback
        traceback.print_exc()
        preview_label_widget.configure(text=f"Preview error:\n{str(e)}", image=None)

def patch_tab_switching(module_globals):
    """
    Patches the tab control to update preview when tabs are switched.
    This should be called after the UI is initialized.
    """
    print("[PREVIEW] Patching tab switching for preview updates...")
    
    # Check if tabControl exists
    if 'tabControl' not in module_globals:
        print("[PREVIEW] tabControl not found in module globals")
        return False
    
    tab_control = module_globals['tabControl']
    
    # Save original tab change handler if it exists
    original_command = None
    try:
        # For CTkTabview, we need to hook into the tab selection
        # We'll create a wrapper that monitors tab changes
        
        def create_tab_monitor():
            """Creates a function that monitors tab changes"""
            import time
            last_tab = None
            
            def monitor():
                nonlocal last_tab
                try:
                    # Get current tab
                    current_tab = tab_control.get()
                    
                    if current_tab != last_tab:
                        last_tab = current_tab
                        
                        # Map tab names to carrier identifiers
                        tab_carrier_map = {
                            'UPS': 'ups',
                            'FedEx': 'fedex',
                            'USPS': 'usps',
                            'Canada Post': 'canada_post',
                            'Purolator': 'purolator'
                        }
                        
                        carrier = tab_carrier_map.get(current_tab)
                        if carrier:
                            print(f"[PREVIEW] Tab switched to: {current_tab}")
                            update_preview_for_carrier(carrier, module_globals)
                
                except Exception as e:
                    print(f"[PREVIEW] Error in tab monitor: {e}")
                
                # Schedule next check
                if 'root' in module_globals:
                    module_globals['root'].after(500, monitor)
            
            return monitor
        
        # Start the monitor
        monitor_func = create_tab_monitor()
        if 'root' in module_globals:
            module_globals['root'].after(1000, monitor_func)
            print("[PREVIEW] Tab monitor started")
            return True
        else:
            print("[PREVIEW] Root window not found")
            return False
            
    except Exception as e:
        print(f"[PREVIEW] Error setting up tab monitor: {e}")
        import traceback
        traceback.print_exc()
        return False

def inject_preview_into_ui(module_globals):
    """
    Injects the preview widget into the existing UI.
    This should be called after the main UI is created.
    """
    print("[PREVIEW] Attempting to inject preview widget into UI...")
    
    try:
        # Try to find a suitable parent frame
        # The design_tab might be a good place for the preview
        if 'design_tab' in module_globals:
            design_tab = module_globals['design_tab']
            create_preview_widget(design_tab, row=0, column=1)
            print("[PREVIEW] Preview widget injected into design_tab")
            return True
        elif 'root' in module_globals:
            # Fallback: create in a new window
            root = module_globals['root']
            preview_window = cs.CTkToplevel(root)
            preview_window.title("Label Preview")
            preview_window.geometry("420x650")
            create_preview_widget(preview_window, row=0, column=0)
            print("[PREVIEW] Preview widget created in separate window")
            return True
        else:
            print("[PREVIEW] Could not find suitable parent for preview widget")
            return False
            
    except Exception as e:
        print(f"[PREVIEW] Error injecting preview widget: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_preview_patch(module_globals):
    """
    Main function to apply all preview-related patches.
    Call this after the UI is fully initialized.
    """
    print("[*] Applying preview patch...")
    
    # Inject preview widget
    if inject_preview_into_ui(module_globals):
        # Set up tab monitoring
        if patch_tab_switching(module_globals):
            # Initialize with UPS preview
            update_preview_for_carrier('ups', module_globals)
            print("[*] Preview patch applied successfully!")
            return True
    
    print("[!] Preview patch failed to apply")
    return False
