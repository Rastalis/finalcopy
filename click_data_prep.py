import json

# Function to load the click_data.json file
def load_click_data(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

# Function to print the metadata for each click
def print_metadata(click_data):
    for click in click_data:
        print(f"Metadata for click at ({click['x']}, {click['y']}):")
        print(click['metadata'])
        print()

def main():
    file_path = "click_data.json"  # Replace with the full path to your click_data.json file
    click_data = load_click_data(file_path)
    print_metadata(click_data)

if __name__ == "__main__":
    main()
