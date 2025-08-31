# This script uses the pywinauto library to automate interactions with the Zoom desktop application.
# It can automatically answer a poll, dismiss a "meeting is being recorded" notification,
# and close the "Not hearing anything?" audio pop-up.

from pywinauto import Desktop
import time
import sys

# Global variables for script control
watchdog = 0
qty_participants = 1

def answer_zoom_poll():
    """
    Finds and answers a Zoom poll window.
    Searches for a window with "Poll" in its title, selects a radio button based on
    qty_participants, and clicks the Submit button.
    """
    try:
        time.sleep(2)
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
    Dismisses the "This meeting is being recorded" pop-up.
    Searches within the provided Zoom window for an "OK" button
    within the pop-up that contains recording-related text.
    """
    try:
        time.sleep(2)
        print("Trying to dismiss stream notification...")
        zoom_win.set_focus()

        def search_children_for_button(parent):
            try:
                for child in parent.children():
                    name = child.window_text()
                    ctrl_type = child.element_info.control_type

                    #print(f"Inspecting child name: {name}")
                    #print(f"Inspecting ctrl_type: {ctrl_type}")

                    if ctrl_type in ("Text", "Pane", "Group") and "being recorded" in name:
                        print(f"Found notification text: {name}")

                    if ctrl_type == "Button" and name in ("OK"):
                        print(f"Found button: {name}. Clicking...")
                        child.click_input()
                        return True

                    if search_children_for_button(child):
                        return True
            except Exception as e:
                print(f"Traversal error: {e}")
            return False

        if search_children_for_button(zoom_win):
            print("Recording popup dismissed.")
            return True
        else:
            print("Could not find the recording button.")
            return False
    except Exception as e:
        print(f"Error dismissing stream notification: {e}")
    return False
    
def dismiss_audio_popup(zoom_win):
    """
    Dismisses the "Not hearing anything?" pop-up by targeting the button
    with "Turn up volume" text.
    It searches for the pop-up as a child of the main Zoom window and then clicks
    the designated button to dismiss it.
    """
    try:
        time.sleep(2)
        print("Trying to dismiss audio popup...")
        zoom_win.set_focus()

        def search_children_for_popup(parent):
            try:
                for child in parent.children():
                    name = child.window_text()
                    ctrl_type = child.element_info.control_type

                    #print(f"Inspecting child name: {name}")
                    #print(f"Inspecting ctrl_type: {ctrl_type}")

                    if ctrl_type in ("Text", "Pane", "Group") and "Not hearing anything?" in name:
                        print(f"Found notification text: {name}")

                    if ctrl_type == "Button" and name in ("Close"):
                        print(f"Found button: {name}. Clicking...")
                        child.click_input()
                        return True
                    
                    if search_children_for_popup(child):
                        return True
            except Exception as e:
                print(f"Traversal error: {e}")
            return False

        if search_children_for_popup(zoom_win):
            print("Audio popup dismissed.")
            return True
        else:
            print("Could not find the audio popup or 'Turn up volume' button.")
            return False
    except Exception as e:
        print(f"Error dismissing audio popup: {e}")
    return False


if __name__ == '__main__':
        while True:
            # Get the active (foreground) window
            try:
                original_active_window = Desktop(backend="uia").window(active_only=True)
                print("Active window title:", original_active_window.window_text())
            except Exception as e:
                print(f"Could not get the active window. Skipping focus restore.")
                original_active_window = None
            
            stream_dismissed = False
            poll_answered = False
            audio_popup_dismissed = False
            watchdog += 1

            print("\n--- Iteration " + str(watchdog) + " ---")
            
            # Find the Zoom window only once per loop
            zoom_windows = Desktop(backend="uia").windows(title_re=".*Zoom Meeting.*")
            if not zoom_windows:
                print("Zoom Meeting window not found. Please open Zoom.")
                time.sleep(10)
                continue
            
            zoom_win = zoom_windows[0]
            
            if answer_zoom_poll():
                poll_answered = True
                if original_active_window and original_active_window.exists():
                    original_active_window.set_focus()

            if dismiss_stream_notification(zoom_win):
                stream_dismissed = True
                if original_active_window and original_active_window.exists():
                    original_active_window.set_focus()
                
            if dismiss_audio_popup(zoom_win):
                audio_popup_dismissed = True
                if original_active_window and original_active_window.exists():
                    original_active_window.set_focus()

            # Break the loop if all tasks are done or the watchdog limit is reached
            if (stream_dismissed and poll_answered and audio_popup_dismissed) or watchdog > 500:
                print("\nDone. All required popups have been handled or watchdog limit reached.")
                break

            time.sleep(10)
