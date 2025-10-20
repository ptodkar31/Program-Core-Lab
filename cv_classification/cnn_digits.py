from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn import datasets
import numpy as np
from typing import Tuple

class DigitsTorch(Dataset):
    def __init__(self, train: bool = True, train_fraction: float = 0.8, seed: int = 42):
        digits = datasets.load_digits()
        X = digits.images.astype(np.float32) / 16.0  # original digits pixels are 0..16
        y = digits.target.astype(np.int64)
        # Normalize to [0,1]; add channel dim
        X = X[:, None, :, :]  # (N,1,8,8)
        # Train/test split (deterministic)
        N = X.shape[0]
        gen = torch.Generator().manual_seed(seed)
        n_train = int(N * train_fraction)
        n_val = N - n_train
        # Create a fixed permutation
        perm = torch.randperm(N, generator=gen).numpy()
        Xp, yp = X[perm], y[perm]
        if train:
            self.X = torch.from_numpy(Xp[:n_train])
            self.y = torch.from_numpy(yp[:n_train])
        else:
            self.X = torch.from_numpy(Xp[n_train:])
            self.y = torch.from_numpy(yp[n_train:])

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class SmallCNN(nn.Module):
    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(32, num_classes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


def train_epoch(model, loader, opt, device):
    model.train()
    total, correct, loss_sum = 0, 0, 0.0
    crit = nn.CrossEntropyLoss()
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad()
        logits = model(xb)
        loss = crit(logits, yb)
        loss.backward()
        opt.step()
        loss_sum += loss.item() * xb.size(0)
        pred = logits.argmax(1)
        correct += (pred == yb).sum().item()
        total += xb.size(0)
    return loss_sum / total, correct / total


def eval_epoch(model, loader, device):
    model.eval()
    total, correct, loss_sum = 0, 0, 0.0
    crit = nn.CrossEntropyLoss()
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            loss = crit(logits, yb)
            loss_sum += loss.item() * xb.size(0)
            pred = logits.argmax(1)
            correct += (pred == yb).sum().item()
            total += xb.size(0)
    return loss_sum / total, correct / total


if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("Device:", device)

    train_ds = DigitsTorch(train=True)
    test_ds = DigitsTorch(train=False)

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=128, shuffle=False)

    model = SmallCNN(num_classes=10).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 10
    for ep in range(1, epochs + 1):
        tr_loss, tr_acc = train_epoch(model, train_loader, opt, device)
        te_loss, te_acc = eval_epoch(model, test_loader, device)
        print(f"Epoch {ep:02d} | train loss {tr_loss:.4f} acc {tr_acc:.4f} | test loss {te_loss:.4f} acc {te_acc:.4f}")

    # Show a few predictions
    model.eval()
    xb, yb = next(iter(test_loader))
    xb = xb.to(device)
    with torch.no_grad():
        pred = model(xb).argmax(1).cpu()
    print("Sample predictions:", pred[:20].tolist())
