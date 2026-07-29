import random

# Generate map for the current workflow.
def generate_map(duration, dificulty, level=1):
    # Random background selection from available options
    backgrounds = [
        "Aircraft_ backgound.png",
        "Ghetto_background.png",
        "London_background.png",
        "TimesSquare_background.png"
    ]
    # Use level as seed for consistency, but vary it
    random.seed(level)
    selected_background = random.choice(backgrounds)
    random.seed()  # Reset seed
    
    map_image = f"backgrounds/{selected_background}"
    map_data = {
        "image": map_image,
        "duration": duration,
        "dificulty": dificulty
    }
    return map_data 
