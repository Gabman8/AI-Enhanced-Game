
def generate_map(terrain_type, size, obstacles, enemies):
    # Placeholder for map generation logic
    map_image = f"backgrounds/{terrain_type}.jpg"  # Example: Load a background image based on terrain type
    map_data = {
        "image": map_image,
        "size": size,
        "obstacles": obstacles,
        "enemies": enemies
    }
    return map_data 