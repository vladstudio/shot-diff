from PIL import Image, ImageDraw
import os

# Create test images
def create_test_images():
    # Create base image
    img1 = Image.new('RGB', (800, 600), color='white')
    draw1 = ImageDraw.Draw(img1)
    
    # Add some content to base image
    draw1.rectangle([100, 100, 300, 200], fill='blue')
    draw1.rectangle([400, 150, 600, 250], fill='green')
    draw1.ellipse([200, 300, 400, 500], fill='red')
    
    # Create modified image
    img2 = img1.copy()
    draw2 = ImageDraw.Draw(img2)
    
    # Make some changes
    draw2.rectangle([100, 100, 300, 200], fill='yellow')  # Changed blue to yellow
    draw2.rectangle([450, 150, 650, 250], fill='green')   # Moved green rectangle
    draw2.ellipse([250, 320, 450, 520], fill='red')       # Moved red circle
    draw2.rectangle([600, 400, 750, 550], fill='purple')  # Added new rectangle
    
    # Save images
    img1.save('test_image1.png')
    img2.save('test_image2.png')
    print("Test images created: test_image1.png and test_image2.png")

if __name__ == "__main__":
    create_test_images()