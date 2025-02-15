import unittest
from unittest.mock import patch, MagicMock
import pygetwindow as gw
from grid_mapping_system import (
    adb_command,
    take_screenshot,
    close_popup,
    is_popup_present,
    extract_metadata_from_screenshot,
    load_tile_coordinates,
    is_point_in_bad_area,
    focus_target_window
)

class TestGridMappingSystem(unittest.TestCase):

    @patch('grid_mapping_system.subprocess.run')
    def test_adb_command(self, mock_run):
        # Mock the subprocess.run method
        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')
        result = adb_command('adb shell input tap 100 100')
        self.assertEqual(result, 'Success')
        mock_run.assert_called_once_with('adb shell input tap 100 100', shell=True, capture_output=True, text=True)

    @patch('grid_mapping_system.adb_command')
    def test_take_screenshot(self, mock_adb_command):
        # Mock adb_command to simulate taking a screenshot
        mock_adb_command.return_value = 'Success'
        take_screenshot('test_screenshot.png')
        mock_adb_command.assert_any_call('adb shell screencap -p /sdcard/screenshot.png')
        mock_adb_command.assert_any_call('adb pull /sdcard/screenshot.png test_screenshot.png')

    @patch('grid_mapping_system.adb_command')
    @patch('grid_mapping_system.is_popup_present')
    def test_close_popup(self, mock_is_popup_present, mock_adb_command):
        # Mock adb_command and is_popup_present
        mock_adb_command.return_value = 'Success'
        mock_is_popup_present.side_effect = [True, False]  # Simulate pop-up being closed on second attempt
        close_popup(is_monster_tile=True)
        self.assertEqual(mock_adb_command.call_count, 2)  # Should attempt twice
        mock_adb_command.assert_called_with('adb shell input tap 1542 60')

    @patch('grid_mapping_system.Image.open')
    @patch('grid_mapping_system.pytesseract.image_to_string')
    def test_extract_metadata_from_screenshot(self, mock_image_to_string, mock_image_open):
        # Mock Image.open and pytesseract.image_to_string
        mock_image_open.return_value = MagicMock()
        # Ensure the test data includes the expected keywords
        mock_image_to_string.return_value = "K:914 X:1 Y:7\nMonster Hunt DMG Boost"
        text, kxy_data, is_monster_tile = extract_metadata_from_screenshot('test_screenshot.png')
        self.assertEqual(kxy_data, "K:914 X:1 Y:7")
        self.assertTrue(is_monster_tile, "Expected is_monster_tile to be True")

    def test_is_point_in_bad_area(self):
        # Test points within and outside bad areas
        self.assertTrue(is_point_in_bad_area(400, 50))  # Inside a bad area
        self.assertFalse(is_point_in_bad_area(200, 200))  # Outside bad areas

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"tiles": [{"x": 100, "y": 200}]}')
    def test_load_tile_coordinates(self, mock_open):
        # Test loading tile coordinates from a JSON file
        coordinates = load_tile_coordinates('tile_coordinates.json')
        self.assertEqual(coordinates, [{"x": 100, "y": 200}])

    @patch('grid_mapping_system.gw.getWindowsWithTitle')
    def test_focus_target_window(self, mock_get_windows):
        mock_window = MagicMock()
        mock_get_windows.return_value = [mock_window]
        
        focus_target_window("Test Window")
        mock_window.activate.assert_called_once()
        
        # Test when window is not found
        mock_get_windows.return_value = []
        with self.assertLogs('grid_mapping_system', level='ERROR') as log:
            focus_target_window("Nonexistent Window")
            if log.output:  # Check if log output is not empty
                self.assertIn("Window with title 'Nonexistent Window' not found.", log.output[0])
            else:
                self.fail("Expected log message not found.")

if __name__ == '__main__':
    unittest.main()
