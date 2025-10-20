from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ------------------------------------------------------------
# Knapsack solvers
# ------------------------------------------------------------

def knapsack_01(values: List[float], weights: List[int], capacity: int) -> Tuple[float, List[int]]:
    """
    0/1 Knapsack using DP.
    - values: value per item
    - weights: integer weights (capacity units)
    - capacity: integer capacity
    Returns: (max_value, picked_indices)
    """
    n = len(values)
    if n == 0 or capacity <= 0:
        return 0.0, []

    # DP table of size (n+1) x (capacity+1)
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

    # Reconstruct solution
    picked: List[int] = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            picked.append(i - 1)
            c -= weights[i - 1]
    picked.reverse()
    return dp[n][capacity], picked


def fractional_knapsack(values: List[float], weights: List[float], capacity: float) -> Tuple[float, List[Tuple[int, float]]]:
    """
    Fractional knapsack (greedy by value/weight).
    Returns: (total_value, list of (index, fraction_taken in [0,1])).
    """
    n = len(values)
    items = list(range(n))
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

# ------------------------------------------------------------
# Real-world mappings (problem statements + adapters)
# ------------------------------------------------------------

@dataclass
class Project:
    name: str
    cost: int  # e.g., budget units (integer)
    benefit: float  # e.g., ROI score or expected value


def select_projects_for_budget(projects: List[Project], budget: int) -> Dict:
    """
    Problem statement: Given a set of projects with costs and expected benefits, choose a subset
    that maximizes total benefit without exceeding a fixed budget (resource allocation).
    Maps to 0/1 knapsack with weight=cost and value=benefit.
    """
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
    price: float  # capital required per unit (can be fractional; fractional purchase allowed if using fractional knapsack)
    expected_return: float  # expected return


def select_portfolio_by_budget(assets: List[Asset], budget: float, allow_fractional: bool = True) -> Dict:
    """
    Problem statement: Choose assets to maximize expected return under a capital budget.
    - If allow_fractional=True, we can buy fractional quantities (fractional knapsack).
    - If allow_fractional=False, we buy whole units (0/1 knapsack); prices are scaled to cents.
    """
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
            "positions": selection,  # (name, fraction, capital, contribution)
        }
    else:
        # Scale to cents to use integer DP
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
    duration: int  # time units (integer)
    reward: float  # value gained by completing the task


def schedule_tasks_with_time_limit(tasks: List[Task], time_limit: int) -> Dict:
    """
    Problem statement: Given tasks each with a duration and reward, choose a subset to complete
    within a total time limit to maximize reward (simple scheduling under a budgeted resource: time).
    Maps to 0/1 knapsack with weight=duration and value=reward.
    """
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


# ------------------------------------------------------------
# Example usage / demo
# ------------------------------------------------------------
if __name__ == "__main__":
    # Resource allocation (projects)
    projects = [
        Project("CRM Upgrade", cost=7, benefit=16.0),
        Project("Mobile App", cost=5, benefit=10.0),
        Project("Data Lake", cost=8, benefit=12.0),
        Project("Security Audit", cost=3, benefit=6.0),
        Project("A/B Testing", cost=4, benefit=7.0),
    ]
    budget = 15
    res_alloc = select_projects_for_budget(projects, budget)
    print("Projects -> Budget:", res_alloc)

    # Portfolio optimization (fractional allowed)
    assets = [
        Asset("ETF_A", price=50.0, expected_return=5.5),
        Asset("ETF_B", price=40.0, expected_return=4.0),
        Asset("Bond_Fund", price=30.0, expected_return=2.7),
        Asset("Growth_Fund", price=70.0, expected_return=7.5),
    ]
    capital = 120.0
    portfolio_frac = select_portfolio_by_budget(assets, capital, allow_fractional=True)
    print("Portfolio (fractional):", portfolio_frac)

    # Portfolio optimization (0/1, whole units only)
    portfolio_01 = select_portfolio_by_budget(assets, capital, allow_fractional=False)
    print("Portfolio (0/1):", portfolio_01)

    # Scheduling (time-limited tasks)
    tasks = [
        Task("Write Report", duration=4, reward=6.0),
        Task("Implement Feature", duration=7, reward=15.0),
        Task("Fix Bugs", duration=3, reward=9.0),
        Task("Team Training", duration=6, reward=10.0),
        Task("Client Meeting", duration=2, reward=4.0),
    ]
    time_limit = 10
    schedule = schedule_tasks_with_time_limit(tasks, time_limit)
    print("Scheduling -> Time Limit:", schedule)
