import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(image_path):
    """Load image and convert to grayscale"""
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        # Create a sample image with various features for demonstration
        print("Creating a sample image with features...")
        sample_img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Add rectangles
        cv2.rectangle(sample_img, (50, 50), (200, 150), (255, 255, 255), -1)
        cv2.rectangle(sample_img, (250, 100), (400, 200), (200, 200, 200), -1)
        
        # Add circles
        cv2.circle(sample_img, (150, 300), 60, (255, 255, 255), -1)
        cv2.circle(sample_img, (450, 300), 40, (150, 150, 150), -1)
        
        # Add some lines
        cv2.line(sample_img, (100, 350), (500, 350), (255, 255, 255), 3)
        cv2.line(sample_img, (300, 50), (300, 380), (255, 255, 255), 2)
        
        # Add text for more features
        cv2.putText(sample_img, 'SAMPLE', (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        img = sample_img
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    return img, gray

def canny_edge_detection(gray_img, low_threshold=50, high_threshold=150):
    """Apply Canny edge detection"""
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, low_threshold, high_threshold)
    
    return edges

def harris_corner_detection(gray_img, block_size=2, ksize=3, k=0.04):
    """Detect corners using Harris corner detector"""
    # Harris corner detection
    harris_corners = cv2.cornerHarris(gray_img, block_size, ksize, k)
    
    # Dilate corner image to enhance corner points
    harris_corners = cv2.dilate(harris_corners, None)
    
    # Create a copy of original image to mark corners
    img_with_corners = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
    
    # Mark corners in red (threshold for optimal value, may vary depending on image)
    img_with_corners[harris_corners > 0.01 * harris_corners.max()] = [0, 0, 255]
    
    return harris_corners, img_with_corners

def sift_feature_detection(gray_img):
    """Detect and compute SIFT features"""
    try:
        # Create SIFT detector
        sift = cv2.SIFT_create()
        
        # Detect keypoints and compute descriptors
        keypoints, descriptors = sift.detectAndCompute(gray_img, None)
        
        # Draw keypoints on the image
        img_with_keypoints = cv2.drawKeypoints(gray_img, keypoints, None, 
                                             flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        return keypoints, descriptors, img_with_keypoints
    
    except cv2.error as e:
        print(f"SIFT error: {e}")
        print("SIFT may not be available in your OpenCV version.")
        return None, None, gray_img

def display_results(original_img, gray_img, edges, harris_result, sift_result, keypoints):
    """Display all results in a subplot"""
    plt.figure(figsize=(15, 10))
    
    # Original image
    plt.subplot(2, 3, 1)
    plt.imshow(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB))
    plt.title('Original Image')
    plt.axis('off')
    
    # Grayscale image
    plt.subplot(2, 3, 2)
    plt.imshow(gray_img, cmap='gray')
    plt.title('Grayscale Image')
    plt.axis('off')
    
    # Canny edges
    plt.subplot(2, 3, 3)
    plt.imshow(edges, cmap='gray')
    plt.title('Canny Edge Detection')
    plt.axis('off')
    
    # Harris corners
    plt.subplot(2, 3, 4)
    plt.imshow(cv2.cvtColor(harris_result, cv2.COLOR_BGR2RGB))
    plt.title('Harris Corner Detection')
    plt.axis('off')
    
    # SIFT features
    plt.subplot(2, 3, 5)
    if sift_result.ndim == 3:
        plt.imshow(cv2.cvtColor(sift_result, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(sift_result, cmap='gray')
    plt.title(f'SIFT Features ({len(keypoints) if keypoints else 0} keypoints)')
    plt.axis('off')
    
    # Feature summary
    plt.subplot(2, 3, 6)
    plt.text(0.1, 0.8, f'Feature Detection Summary:', fontsize=14, weight='bold')
    plt.text(0.1, 0.7, f'• Canny Edges: Detected', fontsize=12)
    plt.text(0.1, 0.6, f'• Harris Corners: Detected', fontsize=12)
    plt.text(0.1, 0.5, f'• SIFT Keypoints: {len(keypoints) if keypoints else 0}', fontsize=12)
    plt.text(0.1, 0.3, 'Parameters Used:', fontsize=12, weight='bold')
    plt.text(0.1, 0.2, '• Canny: low=50, high=150', fontsize=10)
    plt.text(0.1, 0.1, '• Harris: blockSize=2, k=0.04', fontsize=10)
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    # Path to your image
    image_path = "sample_image.png"
    
    print("Loading image...")
    original_img, gray_img = load_image(image_path)
    
    print("Applying Canny edge detection...")
    edges = canny_edge_detection(gray_img)
    
    print("Detecting Harris corners...")
    harris_corners, harris_result = harris_corner_detection(gray_img)
    
    print("Detecting SIFT features...")
    keypoints, descriptors, sift_result = sift_feature_detection(gray_img)
    
    # Display results
    display_results(original_img, gray_img, edges, harris_result, sift_result, keypoints)
    
    # Print statistics
    print("\n" + "="*50)
    print("FEATURE DETECTION RESULTS")
    print("="*50)
    print(f"Image dimensions: {gray_img.shape}")
    print(f"Canny edges detected: {np.sum(edges > 0)} pixels")
    print(f"Harris corner response max: {harris_corners.max():.6f}")
    
    if keypoints:
        print(f"SIFT keypoints detected: {len(keypoints)}")
        print(f"SIFT descriptors shape: {descriptors.shape if descriptors is not None else 'None'}")
    else:
        print("SIFT features: Not available")
    
    print("="*50)
    print("Feature detection completed successfully!")

if __name__ == "__main__":
    main()