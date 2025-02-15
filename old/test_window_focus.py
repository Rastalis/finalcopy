import pygetwindow as gw
import pyautogui
import time

def focus_and_click(window_title, x, y):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window with title '{window_title}' found.")
        return
    window = windows[0]
    window.activate()
    time.sleep(2)  # Ensure the window is focused
    if window.isActive:
        print(f"Window '{window_title}' is active. Clicking at ({x}, {y}).")
        pyautogui.click(x, y)
    else:
        print(f"Window '{window_title}' is not active.")

if __name__ == "__main__":
    window_title = input("Enter the window title: ")
    focus_and_click(window_title, 100, 100)  # Example coordinates 