import json
import time

# Function to print the report in a readable format
def print_report(report):
    print("\n--- KXY Data Analysis Report ---")
    print(f"Total ADB Clicks: {report['total_clicks']}")
    print(f"Unique KXY Tiles: {report['unique_kxy_count']}")
    print(f"Tiles with Missing KXY Data: {report['missing_kxy_count']}")
    
    print("\nUnique KXY Data and Click Counts:")
    for kxy, count in report['kxy_data'].items():
        print(f"KXY: {kxy}, Clicks: {count}")
    
    print("\nSummary:")
    for kxy, count in report['kxy_data'].items():
        if count > 1:
            print(f"KXY: {kxy}")
            if kxy in report['adbxy_data']:
                for adbxy in report['adbxy_data'][kxy]:
                    print(f"ADBXY: {adbxy}")
    
    # Calculate the percentage of the total map scanned
    total_tiles_scanned = 0  # Replace with the actual total number of tiles clicked on
    total_tiles_in_grid = 511 * 1023
    percentage_scanned = (total_tiles_scanned / total_tiles_in_grid) * 100

    print(f"Percentage of the total map scanned: {percentage_scanned:.2f}%")

    print("\nReport generated successfully.")

# Function to analyze the click data
def analyze_kxy_data(click_data):
    kxy_data = {}
    adbxy_data = {}
    missing_kxy_data = 0
    total_clicks = len(click_data)

    # Iterate over each entry in the click_data
    for entry in click_data:
        kxy = entry.get('kxy', 'Not Available')
        adbxy = entry.get('adbxy', 'Not Available')
        
        if kxy != 'Not Available':
            # Count unique KXY values and the number of clicks for each
            if kxy in kxy_data:
                kxy_data[kxy] += 1
            else:
                kxy_data[kxy] = 1
        else:
            missing_kxy_data += 1
        
        if adbxy != 'Not Available':
            # Add adbxy data to the dictionary
            if kxy in adbxy_data:
                adbxy_data[kxy].append(adbxy)
            else:
                adbxy_data[kxy] = [adbxy]

    # Remove extra clicks from the tile_coordinates
    for kxy, adbxy_list in adbxy_data.items():
        if len(adbxy_list) > kxy_data[kxy]:
            adbxy_data[kxy] = adbxy_list[:kxy_data[kxy]]

    # Return results
    return {
        "total_clicks": total_clicks,
        "unique_kxy_count": len(kxy_data),
        "kxy_data": kxy_data,
        "adbxy_data": adbxy_data,
        "missing_kxy_count": missing_kxy_data,
    }

# Function to load the click_data.json file
def load_click_data(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def main():
    file_path = "C:/Users/brian/finalcopy/click_data.json"  # Replace with the full path to your click_data.json file
    click_data = load_click_data(file_path)
    report = analyze_kxy_data(click_data)
    print_report(report)

if __name__ == "__main__":
    main()