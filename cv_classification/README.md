# Computer Vision Classification – SVM and CNN (Digits dataset)

This project demonstrates two approaches to image classification on the classic scikit-learn Digits dataset (8x8 grayscale images, 10 classes):
- SVM classifier (scikit-learn)
- CNN classifier (PyTorch)

Setup:
1) Optional: create/activate a virtual environment
2) Install deps:  pip install -r requirements.txt

Run:
- SVM:  python ".\svm_digits.py"
- CNN:  python ".\cnn_digits.py"

Notes:
- The Digits dataset ships with scikit-learn (no download needed).
- CNN trains quickly on CPU due to small images; it auto-detects CUDA if available.
