from pywinauto import Application
import time

def focus_and_click(window_title, x, y):
    try:
        app = Application().connect(title=window_title)
        window = app.window(title=window_title)
        window.set_focus()
        time.sleep(2)  # Ensure the window is focused
        window.click_input(coords=(x, y))
        print(f"Clicked at ({x}, {y}) in window '{window_title}'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    window_title = input("Enter the window title: ")
    focus_and_click(window_title, 100, 100)  # Example coordinates 