from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['grid_data']
collection = db['tiles']

# Function to insert tile data into MongoDB
def insert_tile_data(kxy_data, adb_coords, screenshot_path):
    tile_data = {
        "kxy": kxy_data,
        "adb_coords": adb_coords,
        "screenshot": screenshot_path
    }
    collection.insert_one(tile_data)

# Function to query MongoDB for specific tiles
def query_tile_data(kxy_data):
    return collection.find({"kxy": kxy_data})

# Example function to query tiles by coordinates
def query_by_coordinates(x, y):
    return collection.find({"adb_coords": {"x": x, "y": y}})
