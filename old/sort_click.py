import json

# Load the click data from the original JSON file
log_file = "click_data.json"
with open(log_file, "r") as f:
    click_data = json.load(f)

# Function to extract KXY from metadata (assuming it's in a format like 'K#### X### Y###')
def extract_kxy(kxy_data):
    # Split by space and extract the parts (KXY format: 'K#### X### Y###')
    if kxy_data:
        parts = kxy_data.split()
        if len(parts) == 3:
            try:
                k = int(parts[0][1:])  # Remove 'K' and convert to int
                x = int(parts[1][1:])  # Remove 'X' and convert to int
                y = int(parts[2][1:])  # Remove 'Y' and convert to int
                return (k, x, y)
            except ValueError:
                return (0, 0, 0)  # Default to (0,0,0) if parsing fails
    return (0, 0, 0)  # Return a default value if no KXY data is available

# Sort the click data by the KXY values
sorted_click_data = sorted(click_data, key=lambda entry: extract_kxy(entry['kxy']))

# Save the sorted data into a new JSON file
sorted_log_file = "sorted_click_data.json"
with open(sorted_log_file, "w") as f:
    json.dump(sorted_click_data, f, indent=4)

print(f"Data sorted by KXY and saved to {sorted_log_file}")
