import json
import random
import subprocess
from navigation_tool import NavigationTool

# Load navigation points from the JSON file
with open('navigation_points.json', 'r') as file:
    navigation_data = json.load(file)

navigation_points = navigation_data['points']

# Select 10% of the points randomly
random.seed(42)  # Optional: Ensures reproducibility
sample_size = max(1, len(navigation_points) // 10)  # Ensure at least 1 point is selected
selected_points = random.sample(navigation_points, sample_size)

# Initialize the NavigationTool
nav_tool = NavigationTool()

# Iterate over the selected navigation points
for kingdom, x, y in selected_points:
    print(f"Navigating to Kingdom: {kingdom}, X: {x}, Y: {y}")
    
    # Navigate using NavigationTool
    nav_tool.navigate_to_coordinates(kingdom, x, y)

    # Run the workflow script
    print("Running workflow...")
    subprocess.run(['python', 'workflow_template_creation.py'])

    print(f"✅ Completed workflow for Kingdom: {kingdom}, X: {x}, Y: {y}\n")
