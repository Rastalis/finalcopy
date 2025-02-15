import json
import subprocess
from navigation_tool import NavigationTool

# Load the navigation points from the JSON file
with open('navigation_points.json', 'r') as file:
    try:
        data = json.load(file)
        navigation_points = data.get("points", [])
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
        navigation_points = []

# Instantiate the NavigationTool
nav_tool = NavigationTool()

# Iterate over each set of coordinates
for point in navigation_points:
    if isinstance(point, list) and len(point) == 3:
        kingdom, x, y = point

        # Navigate to the current set of coordinates using NavigationTool
        nav_tool.navigate_to_coordinates(kingdom, x, y)
        
        # Run grid_mapping_system.py
        subprocess.run(['python', 'grid_mapping_system.py'])
        
        # Run delete.py
        subprocess.run(['python', 'delete.py'])
    else:
        print(f"Invalid point format: {point}") 