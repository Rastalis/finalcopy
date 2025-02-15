import json

# Load the refined data
with open('refined.json', 'r') as f:
    refined_data = json.load(f)

# Create a dictionary to store the ADB X and Y for each KXY
kxy_to_adb_xy = {}

# Iterate over the refined data
for entry in refined_data:
    kxy = entry.get('kxy', 'Not Available')
    adb_xy = (entry.get('x', 'Not Available'), entry.get('y', 'Not Available'))

    if kxy != 'Not Available' and adb_xy != ('Not Available', 'Not Available'):
        if kxy in kxy_to_adb_xy:
            print(f"Warning: Multiple ADB X and Y for KXY {kxy}: {adb_xy} and {kxy_to_adb_xy[kxy]}")
        else:
            kxy_to_adb_xy[kxy] = adb_xy

# Save the results as a new JSON file
with open('kxy_to_adb_xy.json', 'w') as f:
    json.dump(kxy_to_adb_xy, f, indent=4)

# Print the KXY and ADB X and Y for each tile
for kxy, adb_xy in kxy_to_adb_xy.items():
    print(f"KXY {kxy}: ADB X and Y {adb_xy}") 