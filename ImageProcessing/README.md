# Image Processing with OpenCV and Matplotlib

This project demonstrates basic image processing operations using OpenCV and Matplotlib.

## Features

- **Image Reading**: Load images using OpenCV
- **Display**: Show images using Matplotlib
- **Transformations**:
  - Rotation (45 degrees)
  - Scaling (0.7x)
  - Translation (50px right, 30px down)
- **Color Space Conversions**:
  - BGR to Grayscale
  - BGR to HSV

## Requirements

- Python 3.7+
- OpenCV
- Matplotlib
- NumPy

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place your image file in the project directory
2. Update the `image_path` variable in `image_processing.py`
3. Run the script:

```bash
python image_processing.py
```

If no image is found, the script will create a sample image for demonstration.

## For Google Colab

```python
!pip install opencv-python matplotlib numpy
# Upload the image_processing.py file or copy the code into a cell
```

## Output

The script displays a 2x3 grid showing:
1. Original image
2. Rotated image
3. Scaled image  
4. Translated image
5. Grayscale version
6. HSV version

## Feature Detection

Run `feature_detection.py` for advanced feature detection:

```bash
python feature_detection.py
```

### Features Detected:
- **Canny Edge Detection**: Finds edges using gradient thresholds
- **Harris Corner Detection**: Detects corner points (marked in red)
- **SIFT Features**: Scale-Invariant Feature Transform keypoints

### Output:
Displays a 2x3 grid showing:
1. Original image
2. Grayscale image
3. Canny edges
4. Harris corners (red dots)
5. SIFT keypoints (circles with orientation)
6. Summary statistics
