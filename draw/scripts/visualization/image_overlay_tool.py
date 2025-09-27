from PIL import Image
import os

def overlay_images(image1_path, image2_path, output_path):
    # Check if the image files exist
    if not os.path.exists(image1_path):
        print(f"Error: The file {image1_path} does not exist.")
        return
    if not os.path.exists(image2_path):
        print(f"Error: The file {image2_path} does not exist.")
        return

    # Open the two images and convert to RGBA to handle transparency
    image1 = Image.open(image1_path).convert("RGBA")
    image2 = Image.open(image2_path).convert("RGBA")

    # Set the transparency of each image to 50% (alpha value 128)
    image1.putalpha(128)  # 50% transparency
    image2.putalpha(128)  # 50% transparency

    # Ensure both images have the same size before overlaying
    if image1.size != image2.size:
        print(f"Warning: The images have different sizes. Resizing image2 to match image1.")
        image2 = image2.resize(image1.size)

    # Overlay the second image on top of the first one
    blended_image = Image.alpha_composite(image1, image2)

    # Save the resulting image
    blended_image.save(output_path)
    print(f"Overlay complete! Saved to {output_path}")

# Paths to your images
path = '/home/derrick/catkin_ws/src/code_llm/workspace/crossing/pic/'
img1 = 'success_vlm.json.png'
img2 = 'success_wo_vlm.json_debug.json.png'
output_path = path + 'vlm_debug_merged.png'

# Call the overlay function
overlay_images(path + img1, path + img2, output_path)
