import json

# Function to check if the point is inside any of the bad areas
def is_point_in_bad_area(x, y):
    # Define bad areas
    bad_areas = [
        ((396, 0), (1382, 82)),
        ((0, 589), (84, 765)),
        ((1468, 779), (1594, 894)),
        ((1522, 281), (1585, 335)),
    ]
    
    # Check if the point is within any of the bad areas
    for area in bad_areas:
        (x1, y1), (x2, y2) = area
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    return False

# Function to plot ADB points
def plot_adb_points(start_x, start_y, num_steps_x, num_steps_y, step_size):
    total_points = 0
    skipped_points = 0
    valid_points = []

    # Loop through the grid and calculate the ADB points
    for i in range(num_steps_x):
        for j in range(num_steps_y):
            # Calculate the ADB point
            x = start_x + i * step_size
            y = start_y + j * step_size

            # Check if the point is in the bad area
            if is_point_in_bad_area(x, y):
                skipped_points += 1
                continue  # Skip the bad area point

            total_points += 1
            valid_points.append((x, y))  # Add valid point

    # Output results
    print(f"Total ADB points (including skipped): {num_steps_x * num_steps_y}")
    print(f"Valid points (after skipping bad areas): {total_points}")
    print(f"Points skipped due to bad areas: {skipped_points}")
    
    # Optionally, print the valid points
    print("\nValid ADB points:")
    for point in valid_points:
        print(f"ADB Point: ({point[0]}, {point[1]})")

# Input parameters for the plotting
start_x = 100
start_y = 100
num_steps_x = 15
num_steps_y = 15
step_size = 100

# Plot the points
plot_adb_points(start_x, start_y, num_steps_x, num_steps_y, step_size)
