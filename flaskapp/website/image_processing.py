from PIL import Image
import sys

def analyze_image(image_path):
    try:
        # Open the image file
        with Image.open(image_path) as img:
            # Get image details
            width, height = img.size
            format = img.format
            mode = img.mode
            
            # Print image details
            print(f"Image Path: {image_path}")
            print(f"Dimensions: {width} x {height}")
            print(f"Format: {format}")
            print(f"Mode: {mode}")


    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]  # Get the image path from command-line arguments
        analyze_image(image_path)  # Call the function with the image path
