import cv2
import matplotlib.pyplot as plt
import numpy as np

def read_and_display_image(image_path):
    """Read and display an image using OpenCV and Matplotlib"""
    # Read image using OpenCV
    img_bgr = cv2.imread(image_path)
    
    if img_bgr is None:
        print(f"Error: Could not load image from {image_path}")
        return None
    
    # Convert BGR to RGB for matplotlib display
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Display original image
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 3, 1)
    plt.imshow(img_rgb)
    plt.title('Original Image')
    plt.axis('off')
    
    return img_bgr, img_rgb

def perform_transformations(img):
    """Perform rotation, scaling, and translation transformations"""
    height, width = img.shape[:2]
    
    # Rotation (45 degrees)
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, 45, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (width, height))
    
    # Scaling (0.7x)
    scaled = cv2.resize(img, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_LINEAR)
    
    # Translation (shift by 50 pixels right and 30 pixels down)
    translation_matrix = np.float32([[1, 0, 50], [0, 1, 30]])
    translated = cv2.warpAffine(img, translation_matrix, (width, height))
    
    return rotated, scaled, translated

def convert_color_spaces(img_bgr):
    """Convert image to grayscale and HSV color spaces"""
    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Convert to HSV
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    return gray, hsv

def main():
    # Path to your image (modify this path)
    image_path = "sample_image.png"  # Change this to your image path
    
    # Try to create a sample image if none exists
    try:
        # Read and display original image
        img_bgr, img_rgb = read_and_display_image(image_path)
        
        if img_bgr is None:
            # Create a sample image for demonstration
            print("Creating a sample image for demonstration...")
            sample_img = np.zeros((300, 400, 3), dtype=np.uint8)
            # Create some patterns
            cv2.rectangle(sample_img, (50, 50), (150, 150), (255, 0, 0), -1)
            cv2.circle(sample_img, (300, 100), 50, (0, 255, 0), -1)
            cv2.rectangle(sample_img, (200, 200), (350, 250), (0, 0, 255), -1)
            
            img_bgr = sample_img
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 3, 1)
            plt.imshow(img_rgb)
            plt.title('Sample Image')
            plt.axis('off')
        
        # Perform transformations
        rotated, scaled, translated = perform_transformations(img_rgb)
        
        # Display transformations
        plt.subplot(2, 3, 2)
        plt.imshow(rotated)
        plt.title('Rotated (45°)')
        plt.axis('off')
        
        plt.subplot(2, 3, 3)
        plt.imshow(scaled)
        plt.title('Scaled (0.7x)')
        plt.axis('off')
        
        plt.subplot(2, 3, 4)
        plt.imshow(translated)
        plt.title('Translated')
        plt.axis('off')
        
        # Convert color spaces
        gray, hsv = convert_color_spaces(img_bgr)
        
        # Display color space conversions
        plt.subplot(2, 3, 5)
        plt.imshow(gray, cmap='gray')
        plt.title('Grayscale')
        plt.axis('off')
        
        plt.subplot(2, 3, 6)
        plt.imshow(hsv)
        plt.title('HSV')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        print("Image processing completed successfully!")
        print(f"Original image shape: {img_rgb.shape}")
        print(f"Grayscale image shape: {gray.shape}")
        print(f"HSV image shape: {hsv.shape}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()