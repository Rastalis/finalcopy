import os

# Path to the screenshots folder
screenshot_folder = "screenshots"

# Function to delete all files in the folder
def delete_all_screenshots():
    # Check if the folder exists
    if os.path.exists(screenshot_folder):
        # Loop through the files in the folder
        for filename in os.listdir(screenshot_folder):
            file_path = os.path.join(screenshot_folder, filename)
            try:
                # Check if it's a file (not a subdirectory) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
                else:
                    print(f"Skipping directory: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    else:
        print(f"The folder '{screenshot_folder}' does not exist.")

# Run the function to delete files
delete_all_screenshots()

