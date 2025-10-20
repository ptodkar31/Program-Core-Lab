from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import math

# ---------------------- Core solvers ----------------------

def knapsack_01(values: List[float], weights: List[int], capacity: int) -> Tuple[float, List[int]]:
    n = len(values)
    if n == 0 or capacity <= 0:
        return 0.0, []
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for c in range(capacity + 1):
            best = dp[i - 1][c]
            if w <= c:
                cand = dp[i - 1][c - w] + v
                if cand > best:
                    best = cand
            dp[i][c] = best
    picked: List[int] = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            picked.append(i - 1)
            c -= weights[i - 1]
    picked.reverse()
    return dp[n][capacity], picked


def fractional_knapsack(values: List[float], weights: List[float], capacity: float) -> Tuple[float, List[Tuple[int, float]]]:
    items = list(range(len(values)))
    items.sort(key=lambda i: (values[i] / weights[i]) if weights[i] > 0 else float('inf'), reverse=True)
    total_value = 0.0
    taken: List[Tuple[int, float]] = []
    remaining = capacity
    for i in items:
        if remaining <= 0:
            break
        w = weights[i]
        v = values[i]
        if w <= 0:
            continue
        take = min(1.0, remaining / w)
        total_value += v * take
        remaining -= w * take
        taken.append((i, take))
    return total_value, taken

# ---------------------- Real-world adapters ----------------------

@dataclass
class Project:
    name: str
    cost: int
    benefit: float


def select_projects_for_budget(projects: List[Project], budget: int) -> Dict:
    values = [p.benefit for p in projects]
    weights = [p.cost for p in projects]
    best, picked_idx = knapsack_01(values, weights, budget)
    chosen = [projects[i] for i in picked_idx]
    return {
        "max_benefit": best,
        "chosen_projects": [(p.name, p.cost, p.benefit) for p in chosen],
        "used_budget": sum(p.cost for p in chosen),
        "remaining_budget": budget - sum(p.cost for p in chosen),
    }


@dataclass
class Asset:
    name: str
    price: float
    expected_return: float


def select_portfolio_by_budget(assets: List[Asset], budget: float, allow_fractional: bool = True) -> Dict:
    values = [a.expected_return for a in assets]
    prices = [a.price for a in assets]
    if allow_fractional:
        best, taken = fractional_knapsack(values, prices, budget)
        selection = []
        capital_used = 0.0
        for idx, frac in taken:
            selection.append((assets[idx].name, frac, prices[idx] * frac, values[idx] * frac))
            capital_used += prices[idx] * frac
        return {
            "total_expected_return": best,
            "capital_used": capital_used,
            "remaining_capital": budget - capital_used,
            "positions": selection,
        }
    else:
        factor = 100
        int_prices = [int(round(p * factor)) for p in prices]
        int_budget = int(round(budget * factor))
        best, picked_idx = knapsack_01(values, int_prices, int_budget)
        chosen = [assets[i] for i in picked_idx]
        used = sum(a.price for a in chosen)
        return {
            "total_expected_return": best,
            "capital_used": used,
            "remaining_capital": budget - used,
            "positions": [(a.name, 1.0, a.price, a.expected_return) for a in chosen],
        }


@dataclass
class Task:
    name: str
    duration: int
    reward: float


def schedule_tasks_with_time_limit(tasks: List[Task], time_limit: int) -> Dict:
    values = [t.reward for t in tasks]
    durations = [t.duration for t in tasks]
    best, picked_idx = knapsack_01(values, durations, time_limit)
    chosen = [tasks[i] for i in picked_idx]
    return {
        "max_reward": best,
        "chosen_tasks": [(t.name, t.duration, t.reward) for t in chosen],
        "time_used": sum(t.duration for t in chosen),
        "time_remaining": time_limit - sum(t.duration for t in chosen),
    }
