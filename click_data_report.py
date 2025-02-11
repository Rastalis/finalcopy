import json
import numpy as np

# Function to load the click_data.json file
def load_click_data(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

# Function to analyze the click data and return insights
def analyze_grid_mapping(click_data):
    x_coords = [entry['x'] for entry in click_data]
    y_coords = [entry['y'] for entry in click_data]
    
    # Unique tiles based on KXY
    unique_tiles = set(entry.get('kxy', 'Not Available') for entry in click_data)
    unique_tiles = {tile for tile in unique_tiles if tile != 'Not Available'}
    
    # Calculate the mean and standard deviation of x and y coordinates
    x_mean = np.mean(x_coords)
    y_mean = np.mean(y_coords)
    
    x_std = np.std(x_coords)
    y_std = np.std(y_coords)

    # Return the insights
    return {
        "x_mean": x_mean,
        "y_mean": y_mean,
        "x_std": x_std,
        "y_std": y_std,
        "unique_tiles_count": len(unique_tiles),
        "missing_kxy_count": sum(1 for entry in click_data if entry.get('kxy', 'Not Available') == 'Not Available')
    }

# Function to adjust the next grid mapping based on analysis
def adjust_grid_mapping(analysis, current_start_x, current_start_y, current_step_size, current_num_steps_x, current_num_steps_y):
    # Adjust the starting point based on mean values (for more central coverage)
    adjusted_start_x = current_start_x + (analysis['x_mean'] - current_start_x) * 0.5
    adjusted_start_y = current_start_y + (analysis['y_mean'] - current_start_y) * 0.5

    # Adjust step size based on standard deviation (larger deviation, smaller steps)
    adjusted_step_size = max(current_step_size, analysis['x_std'] // 2, analysis['y_std'] // 2)

    # Adjust number of steps based on the unique tile count and missing KXY data
    if analysis['unique_tiles_count'] < 10:
        adjusted_num_steps_x = current_num_steps_x + 2  # Increase number of steps
        adjusted_num_steps_y = current_num_steps_y + 2
    else:
        adjusted_num_steps_x = current_num_steps_x
        adjusted_num_steps_y = current_num_steps_y

    # Print the adjusted parameters
    print(f"Adjusted Starting Point: X={adjusted_start_x}, Y={adjusted_start_y}")
    print(f"Adjusted Step Size: {adjusted_step_size}")
    print(f"Adjusted Number of Steps: X={adjusted_num_steps_x}, Y={adjusted_num_steps_y}")

    # Return the new parameters for the next grid mapping
    return adjusted_start_x, adjusted_start_y, adjusted_step_size, adjusted_num_steps_x, adjusted_num_steps_y

# Main function to load data, analyze, and adjust the grid mapping
def main():
    file_path = "click_data.json"

    # Load the click data from the file
    click_data = load_click_data(file_path)

    # Analyze the click data
    analysis = analyze_grid_mapping(click_data)

    # Current grid mapping parameters (modify these as needed)
    current_start_x = 16
    current_start_y = 33
    current_step_size = 75
    current_num_steps_x = 16
    current_num_steps_y = 12

    # Adjust the next grid mapping based on analysis
    adjusted_params = adjust_grid_mapping(analysis, current_start_x, current_start_y, current_step_size, current_num_steps_x, current_num_steps_y)

    # Output the adjusted parameters for the next scan
    print(f"New Grid Mapping Parameters: {adjusted_params}")

if __name__ == "__main__":
    main()
