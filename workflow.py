import os
import subprocess
from datetime import datetime
import time
# Create the screenshots directory if it doesn't exist
os.makedirs('screenshots', exist_ok=True)

# Define the coordinates
coordinates = [
    (99, 451),
    (332, 451),
    (568, 451),
    (802, 451),
    (1031, 451),
    (1262, 451),
    (1479, 451),
    (99, 893),
    (332, 893),
    (568, 893),
    (802, 893),
    (1031, 893),
    (1262, 893),
    (1470, 889),
    (15, 850),
    (215, 850),
    (450, 850),
    (684, 850),
    (916, 850),
    (1145, 850),
    (1377, 850),
    (99, 451),
    (332, 451),
    (568, 451),
    (802, 451),
    (1031, 451),
    (1262, 451),
    (1479, 451),
    (99, 893),
    (332, 893),
    (568, 893),
    (802, 893),
    (1031, 893),
    (1262, 893),
    (1470, 889),
    (15, 850),
    (215, 850),
    (450, 850),
    (684, 850),
    (916, 850),
    (1145, 850),
    (1377, 850),
    (99, 795),
    (332, 795),
    (568, 795),
    (802, 795),
    (1031, 795),
    (1262, 795),
    (1470, 795),
    (215, 734),
    (450, 734),
    (684, 734),
    (916, 734),
    (1145, 734),
    (1377, 734),
    (1581, 734),
    (99, 678),
    (332, 678),
    (568, 678),
    (802, 678),
    (1031, 678),
    (1262, 678),
    (1479, 678),
    (215, 620),
    (450, 620),
    (684, 620),
    (916, 620),
    (1145, 620),
    (1377, 620),
    (1581, 620),
    (99, 562),
    (332, 562),
    (568, 562),
    (802, 562),
    (1031, 562),
    (1262, 562),
    (1479, 562),
    (8, 505),
    (215, 505),
    (450, 505),
    (684, 505),
    (916, 505),
    (1145, 505),
    (1377, 505),
    (1581, 505),
    (8, 394),
    (215, 394),
    (450, 394),
    (684, 394),
    (916, 394),
    (1145, 394),
    (1377, 394),
    (1581, 394),
    (99, 338),
    (332, 338),
    (568, 338),
    (802, 338),
    (1031, 338),
    (1262, 338),
    (1479, 338),
    (8, 281),
    (215, 281),
    (450, 281),
    (684, 281),
    (916, 281),
    (1145, 281),
    (1377, 281),
    (1581, 265),
    (99, 225),
    (332, 225),
    (568, 225),
    (802, 225),
    (1031, 225),
    (1262, 225),
    (1479, 225),
    (8, 168),
    (215, 168),
    (450, 168),
    (684, 168),
    (916, 168),
    (1145, 168),
    (1377, 168),
    (1581, 168),
    (99, 112),
    (332, 112),
    (568, 112),
    (799, 89),
    (1012, 89),
    (1262, 112),
    (1442, 101),
    (8, 61),
    (215, 61),
    (373, 61),
    (1392, 61)
    # Add more coordinates as needed
]

# Loop through each coordinate
for x, y in coordinates:
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Tap on the coordinate
    subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)])
    time.sleep(0.2)
    # Take a screenshot on the device
    subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])

    # Pull the screenshot to the local machine
    subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', f'./screenshots/screenshot_{timestamp}.png'])

    # Optionally, remove the screenshot from the device
    subprocess.run(['adb', 'shell', 'rm', '/sdcard/screenshot.png'])

    # Log the screenshot
    print(f"Screenshot saved as screenshots/screenshot_{timestamp}.png")

    
    # Send the escape key event
    subprocess.run(['adb', 'shell', 'input', 'keyevent', '111'])
