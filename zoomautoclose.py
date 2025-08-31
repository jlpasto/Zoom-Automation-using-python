# This script uses the pywinauto library to automate interactions with the Zoom desktop application.
# It can automatically answer a poll, dismiss a "meeting is being recorded" notification,
# and close the "Not hearing anything?" audio pop-up.

from pywinauto import Desktop
import time
import sys

# Global variable for script control
qty_participants = 1

def answer_zoom_poll(qty_participants=1):
    """
    Finds and answers a Zoom poll window.
    Searches for a window with "Poll" in its title, selects a radio button based on
    qty_participants, and clicks the Submit button.
    """
    try:
        print("Trying to answer poll...")
        windows = Desktop(backend="uia").windows()
        for win in windows:
            title = win.window_text()
            if "Poll" in title:
                print(f"Found poll window: {title}")
                win.set_focus()
                
                # Find all radio button options within the poll window
                options = [child for child in win.descendants()
                           if child.element_info.control_type == "RadioButton"]

                if 0 < qty_participants <= len(options):
                    selected = options[qty_participants - 1]
                    print(f"Selecting option {qty_participants}: {selected.window_text()}")
                    selected.select()
                else:
                    print(f"Invalid choice number: {qty_participants}")
                    return False

                # Find and click the submit button
                submit = [child for child in win.descendants() 
                          if child.element_info.control_type == "Button" and "Submit" in child.window_text()]
                if submit:
                    print("Clicking Submit...")
                    submit[0].click_input()
                    return True
                else:
                    print("Submit button not found.")
                    return False
    except Exception as e:
        print(f"Error answering poll: {e}")
    return False

def dismiss_stream_notification(zoom_win):
    """
    Dismisses the "This meeting is being recorded" pop-up using a recursive search.
    Searches within the provided Zoom window for an "OK" button
    within the pop-up that contains recording-related text.
    """
    def search_children_for_button(parent):
        """Recursively searches for a button within a parent's children."""
        try:
            for child in parent.children():
                name = child.window_text()
                ctrl_type = child.element_info.control_type

                if ctrl_type in ("Text", "Pane", "Group") and "being recorded" in name:
                    print(f"Found notification text: {name}")

                if ctrl_type == "Button" and "OK" in name:
                    print(f"Found button: {name}. Clicking...")
                    child.click_input()
                    return True

                if search_children_for_button(child):
                    return True
        except Exception as e:
            # Traversal error, but continue searching other branches
            pass
        return False

    print("Trying to dismiss stream notification...")
    if search_children_for_button(zoom_win):
        print("Recording popup dismissed.")
        return True
    else:
        print("Could not find the recording button.")
        return False
    
def dismiss_audio_popup(zoom_win):
    """
    Dismisses the "Not hearing anything?" pop-up using a recursive search.
    It searches for the pop-up as a child of the main Zoom window and then clicks
    the designated "Close" button.
    """
    def search_children_for_popup(parent):
        """Recursively searches for a pop-up and clicks its button."""
        try:
            for child in parent.children():
                name = child.window_text()
                ctrl_type = child.element_info.control_type

                if ctrl_type in ("Text", "Pane", "Group") and "Not hearing anything?" in name:
                    print(f"Found notification text: {name}")

                if ctrl_type == "Button" and "Close" in name:
                    print(f"Found button: {name}. Clicking...")
                    child.click_input()
                    return True
                
                if search_children_for_popup(child):
                    return True
        except Exception as e:
            # Traversal error, but continue searching other branches
            pass
        return False

    print("Trying to dismiss audio popup...")
    if search_children_for_popup(zoom_win):
        print("Audio popup dismissed.")
        return True
    else:
        print("Could not find the audio popup or 'Close' button.")
        return False

if __name__ == '__main__':
    watchdog = 0
    while True:
        print(f"\n--- Iteration {watchdog} ---")
        
        # Find the Zoom window only once per loop
        zoom_windows = Desktop(backend="uia").windows(title_re=".*Zoom Meeting.*")
        if not zoom_windows:
            print("Zoom Meeting window not found. Please open Zoom.")
            time.sleep(10)
            continue
        
        zoom_win = zoom_windows[0]
        
        # Check for each pop-up and handle it if found
        answer_zoom_poll(qty_participants=1)
        dismiss_stream_notification(zoom_win)
        dismiss_audio_popup(zoom_win)
        
        watchdog += 1
        time.sleep(10)