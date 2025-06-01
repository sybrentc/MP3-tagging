import os
import sys
from PIL import Image

def resize_image(image_path, max_size=800):
    """
    Resizes an image so that its largest dimension is max_size pixels,
    while maintaining the aspect ratio. Only resizes if the image is larger
    than max_size. Overwrites the original image.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum dimension size in pixels (default: 800)
    """
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist")
        return False
        
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Get original dimensions
            width, height = img.size
            
            # Check if image needs resizing
            if width <= max_size and height <= max_size:
                print(f"Image is already smaller than {max_size}px in both dimensions ({width}x{height}). No resizing needed.")
                return True
            
            # Calculate new dimensions
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image, overwriting the original
            resized_img.save(image_path, quality=95)
            
            print(f"Successfully resized image from {width}x{height} to {new_width}x{new_height}")
            print(f"Original image has been replaced with the resized version")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python resize_image.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = resize_image(image_path)
    sys.exit(0 if success else 1) 