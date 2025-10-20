from __future__ import annotations
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

# Load digits dataset (1797 samples, 8x8 grayscale images)
digits = datasets.load_digits()
X = digits.data  # shape (n_samples, 64)
y = digits.target

# Train / test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Standardize features (mean=0, var=1)
scaler = StandardScaler()
X_train_std = scaler.fit_transform(X_train)
X_test_std = scaler.transform(X_test)

# SVM with RBF kernel
clf = SVC(C=10.0, kernel='rbf', gamma='scale', random_state=42)
clf.fit(X_train_std, y_train)

# Evaluate
y_pred = clf.predict(X_test_std)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")
print("\nClassification report:\n", classification_report(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
