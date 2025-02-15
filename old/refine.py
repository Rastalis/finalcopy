import json
import matplotlib.pyplot as plt

# Function to load the click_data.json file
def load_click_data(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

# Function to analyze and refine the click data
def refine_kxy_data(click_data):
    # Refined data to ensure each KXY has only one ADB click
    refined_data = {}
    
    # Iterate over each entry in the click_data
    for entry in click_data:
        kxy = entry.get('kxy', 'Not Available')
        
        if kxy != 'Not Available' and kxy not in refined_data:
            # Keep only the first ADB click for each unique KXY
            refined_data[kxy] = entry
    
    # Return refined data
    return list(refined_data.values())

# Function to save the refined data to a new JSON file
def save_refined_data(refined_data, file_path):
    try:
        with open(file_path, "w") as f:
            json.dump(refined_data, f, indent=4)
        print(f"Refined data saved to {file_path}.")
    except Exception as e:
        print(f"Error saving refined data: {e}")

# Function to plot the points on a 1600x900 layout
def plot_points(refined_data):
    x_coords = [entry['x'] for entry in refined_data]
    y_coords = [entry['y'] for entry in refined_data]

    # Plotting the points on a 1600x900 layout
    plt.figure(figsize=(10, 6))
    plt.scatter(x_coords, y_coords, c='blue', label='ADB Clicks')
    
    # Adding labels
    plt.title("ADB Click Points on 1600x900 Layout")
    plt.xlabel("X Coordinates")
    plt.ylabel("Y Coordinates")
    plt.xlim(0, 1600)
    plt.ylim(0, 900)

    # Show the plot
    plt.show()

# Main function to load, refine, save, and plot the data
def main():
    # Load the click data from the file
    file_path = "click_data.json"
    click_data = load_click_data(file_path)

    # Refine the KXY data to keep only one click per unique KXY tile
    refined_data = refine_kxy_data(click_data)

    # Save the refined data to refined.json
    refined_file_path = "refined.json"
    save_refined_data(refined_data, refined_file_path)

    # Plot the points on the 1600x900 layout
    plot_points(refined_data)

if __name__ == "__main__":
    main()
