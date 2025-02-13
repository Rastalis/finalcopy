import pygetwindow
import pyautogui
import time

# Get the Chrome window
chrome_window = pygetwindow.getWindowsWithTitle('Chrome')[0]

# Activate the Chrome window
chrome_window.activate()

# Wait for 1 second to ensure the window is in focus
time.sleep(1)

# Wait for 5 seconds
time.sleep(5)

# Get the initial mouse position
initial_position = pyautogui.position()

# Click the mouse repeatedly
while True:
    # Get the current mouse position
    current_position = pyautogui.position()

    # If the mouse has moved, stop the script
    if current_position != initial_position:
        break

    pyautogui.click()
    time.sleep(0.1)  # Adjust this value to change the click speed
