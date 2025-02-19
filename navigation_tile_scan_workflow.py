import json
import subprocess
from navigation_tool import NavigationTool

# Load navigation points from the JSON file
with open('navigation_points.json', 'r') as file:
    navigation_data = json.load(file)

navigation_points = navigation_data['points']

# Initialize the NavigationTool
nav_tool = NavigationTool()

# Iterate over each navigation point
for point in navigation_points:
    kingdom, x, y = point

    # Navigate to the point using the NavigationTool
    print(f"Navigating to Kingdom: {kingdom}, X: {x}, Y: {y}")
    nav_tool.navigate_to_coordinates(kingdom, x, y)

    # Run the workflow script
    print("Running workflow...")
    subprocess.run(['python', 'workflow_template_creation.py'])

    print(f"Completed navigation and template creation workflow for Kingdom: {kingdom}, X: {x}, Y: {y}\n") 