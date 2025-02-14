import logging
import time
import subprocess

class NavigationTool:
    def __init__(self, device_id="emulator-5554"):
        """Initialize the Navigation Tool."""
        self.device_id = device_id
        self.logger = logging.getLogger("NavigationTool")
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging for NavigationTool."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def run_adb_command(self, command):
        """Run an ADB shell command and handle errors."""
        full_command = ["adb", "-s", self.device_id] + command.split()
        self.logger.debug(f"Running ADB command: {' '.join(full_command)}")

        try:
            result = subprocess.run(full_command, capture_output=True, text=True, check=True)
            self.logger.debug(f"ADB Output: {result.stdout.strip()}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ADB command failed: {e}")
            return None

    def tap_screen(self, x, y):
        """Tap a specific coordinate on the device."""
        self.run_adb_command(f"shell input tap {x} {y}")
        time.sleep(0.2)  # Allow UI time to update

    def validate_coordinates(self, kingdom, x, y):
        """Validate coordinates before navigation."""
        if not isinstance(kingdom, (int, type(None))) or not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Coordinates must be integers (kingdom, x, y).")
        if x < 0 or x > 511 or y < 0 or y > 1023:
            raise ValueError("X and Y coordinates must be between 0 and 1023.")
        self.logger.info(f"✅ Validated coordinates: Kingdom={kingdom}, X={x}, Y={y}")
        return True

    def navigate_to_coordinates(self, kingdom, x, y, last_kingdom=None, last_x=None, last_y=None, retries=3):
        """
        Navigate to a given set of coordinates in the game.

        Args:
            kingdom (int): The kingdom number.
            x (int): X coordinate.
            y (int): Y coordinate.
            last_kingdom (int): Previously used kingdom (avoid redundant updates).
            last_x (int): Previously used X coordinate.
            last_y (int): Previously used Y coordinate.
            retries (int): Number of retries before failing.
        """
        self.validate_coordinates(kingdom, x, y)

        # Tap positions for fields and "Go" button
        field_tap_positions = {
            "kingdom": (685, 335),  # Kingdom input field
            "x": (821, 335),        # X coordinate input field
            "y": (969, 335)         # Y coordinate input field
        }
        go_button_position = (765, 467)  # "Go" button

        for attempt in range(retries):
            try:
                self.logger.info(f"🗺️ Navigating to: Kingdom={kingdom}, X={x}, Y={y} (Attempt {attempt + 1})")

                # Tap navigation menu button
                self.tap_screen(843, 118)

                # Change kingdom only if it's different
                if last_kingdom != kingdom:
                    self.logger.info(f"🌍 Updating Kingdom to {kingdom}")
                    self._tap_and_enter(field_tap_positions["kingdom"], kingdom)

                # Change X coordinate only if it's different
                if last_x != x:
                    self.logger.info(f"📍 Updating X coordinate to {x}")
                    self._tap_and_enter(field_tap_positions["x"], x)

                # Change Y coordinate only if it's different
                if last_y != y:
                    self.logger.info(f"📍 Updating Y coordinate to {y}")
                    self._tap_and_enter(field_tap_positions["y"], y)

                # Tap the "Go" button
                self.logger.info("🚀 Pressing 'Go' button")
                self.tap_screen(*go_button_position)

                self.logger.info(f"✅ Successfully navigated to {x}, {y} in Kingdom {kingdom}")
                return True  # Exit after success

            except Exception as e:
                self.logger.error(f"❌ Navigation attempt {attempt + 1} failed: {e}")

        self.logger.critical(f"🚨 Navigation failed after {retries} attempts.")
        return False

    def _tap_and_enter(self, tap_position, value):
        """
        Tap on an input field and enter a numerical value using the on-screen keypad.

        Args:
            tap_position (tuple): (x, y) coordinates of the input field.
            value (int): The numerical value to enter.
        """
        keypad_positions = {
            "0": (1098, 619), "1": (1065, 379), "2": (1195, 367),
            "3": (1290, 367), "4": (1065, 430), "5": (1195, 430),
            "6": (1290, 430), "7": (1065, 530), "8": (1195, 530),
            "9": (1290, 530), "check": (1275, 630)  # Checkmark button
        }

        # Tap on the input field
        self.tap_screen(*tap_position)
        self.logger.info(f"🖊️ Entering value {value} at {tap_position}")

        # Enter each digit
        for digit in str(value):
            if digit in keypad_positions:
                key_x, key_y = keypad_positions[digit]
                self.tap_screen(key_x, key_y)
                self.logger.info(f"🔢 Tapped digit '{digit}' at ({key_x}, {key_y})")
            else:
                raise ValueError(f"❌ Invalid digit '{digit}' for keypad entry.")

        # Confirm input
        check_x, check_y = keypad_positions["check"]
        self.tap_screen(check_x, check_y)
        self.logger.info("✅ Confirmed input with checkmark button.")

