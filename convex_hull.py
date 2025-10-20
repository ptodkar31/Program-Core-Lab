from typing import List, Tuple
import math

Point = Tuple[float, float]

def cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def dist2(a: Point, b: Point) -> float:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx * dx + dy * dy

def convex_hull_jarvis(points: List[Point]) -> List[Point]:
    pts = sorted(set(points))
    n = len(pts)
    if n <= 1:
        return pts[:]
    leftmost = min(pts, key=lambda p: (p[0], p[1]))
    hull: List[Point] = []
    p = leftmost
    while True:
        hull.append(p)
        # initial candidate
        q = pts[0] if pts[0] != p else pts[1]
        for r in pts:
            if r == p:
                continue
            c = cross(p, q, r)
            if c > 0 or (c == 0 and dist2(p, r) > dist2(p, q)):
                q = r
        p = q
        if p == leftmost:
            break
    return hull

def convex_hull_graham(points: List[Point]) -> List[Point]:
    pts = sorted(set(points))
    n = len(pts)
    if n <= 1:
        return pts[:]
    # Anchor: lowest y, then lowest x
    anchor = min(pts, key=lambda p: (p[1], p[0]))
    ax, ay = anchor

    def angle(p: Point) -> float:
        return math.atan2(p[1] - ay, p[0] - ax)

    others = [p for p in pts if p != anchor]
    others.sort(key=lambda p: (angle(p), dist2(p, anchor)))

    # keep only farthest for collinear with anchor
    filtered: List[Point] = []
    for p in others:
        while filtered and cross(anchor, filtered[-1], p) == 0:
            filtered.pop()
        filtered.append(p)

    if not filtered:
        return [anchor]

    hull: List[Point] = [anchor]
    for p in filtered:
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return hull

if __name__ == "__main__":
    pts: List[Point] = [(0,0), (1,1), (2,2), (2,0), (2,1), (0,2), (1,0)]
    print("Jarvis:", convex_hull_jarvis(pts))
    print("Graham:", convex_hull_graham(pts))
