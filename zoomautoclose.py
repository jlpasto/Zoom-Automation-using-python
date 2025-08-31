from pywinauto import Desktop, keyboard
import time
import sys

watchdog = 0
qty_participants = 1

def answer_zoom_poll():
    try:
        time.sleep(2)
        print("Trying to answer poll")
        windows = Desktop(backend="uia").windows()
        for win in windows:
            title = win.window_text()
            if "Poll" in title:
                print(f"Found poll window: {title}")
                win.set_focus()
                options = [child for child in win.descendants()
                           if child.element_info.control_type == "RadioButton"]

                if 0 < qty_participants <= len(options):
                    selected = options[qty_participants - 1]
                    print(f"Selecting option {qty_participants}: {selected.window_text()}")
                    selected.select()
                else:
                    print(f"Invalid choice number: {qty_participants}")
                    return False

                submit = [child for child in win.descendants() if child.element_info.control_type == "Button" and "Submit" in child.window_text()]
                if submit:
                    print("Clicking Submit...")
                    submit[0].click_input()
                    return True
                else:
                    print("Submit button not found.")
                return False


    except Exception as e:
        print(f"Error: {e}")



def dismiss_stream_notification():

    try:
        time.sleep(2)
        zoom_windows = Desktop(backend="uia").windows(title_re=".*Zoom Meeting.*")
        if not zoom_windows:
            print("Zoom Meeting window not found.")
            return False

        zoom_win = zoom_windows[0]
        zoom_win.set_focus()

        def search_children_for_button(parent):
            try:
                for child in parent.children():
                    name = child.window_text()
                    ctrl_type = child.element_info.control_type

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
        print(f"Error: {e}")

def dismiss_audio_popup():
    """
    Dismisses the "Not hearing anything?" pop-up by targeting the button
    with "Turn up volume" text.
    It searches for the pop-up as a child of the main Zoom window and then clicks
    the designated button to dismiss it.
    """
    try:
        time.sleep(2)
        print("Trying to dismiss audio popup...")
        zoom_windows = Desktop(backend="uia").windows(title_re=".*Zoom Meeting.*")
        if not zoom_windows:
            print("Zoom Meeting window not found.")
            return False

        zoom_win = zoom_windows[0]
        zoom_win.set_focus()

        def search_children_for_popup(parent):
            try:
                for child in parent.children():
                    name = child.window_text()
                    ctrl_type = child.element_info.control_type

                    if "Not hearing anything?" in name:
                        print(f"Found popup text: {name}")
                        # Find the "Turn up volume" button within this specific popup
                        turn_up_button = [
                            grandchild for grandchild in child.children() 
                            if grandchild.window_text() == "Turn up volume" and grandchild.element_info.control_type == "Button"
                        ]
                        if turn_up_button:
                            print("Found 'Turn up volume' button. Clicking...")
                            turn_up_button[0].click_input()
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
            print("Could not find the Not hearing anything? popup or 'Turn up volume' button.")
            return False
    except Exception as e:
        print(f"Error dismissing audio popup: {e}")
    return False


if __name__ == '__main__':
    while True:
        stream_dismissed = False
        poll_answered = False
        audio_popup_dismissed = False
        watchdog += 1

        print("\n--- Iteration " + str(watchdog) + " ---")
        
        if answer_zoom_poll():
            poll_answered = True

        if dismiss_stream_notification():
            stream_dismissed = True
            
        if dismiss_audio_popup():
            audio_popup_dismissed = True

        # Break the loop if all tasks are done or the watchdog limit is reached
        if (stream_dismissed and poll_answered and audio_popup_dismissed) or watchdog > 500:
            print("\nDone. All required popups have been handled or watchdog limit reached.")
            break

        time.sleep(10)






