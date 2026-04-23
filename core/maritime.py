from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import math
import random
from typing import Dict, List, Tuple

from .schema import EventRecord, TimeRecord, LocationRecord, EvidenceRecord

PROTECTED_WATERS = [
    (-122.72, 37.78),
    (-122.62, 37.78),
    (-122.62, 37.84),
    (-122.72, 37.84),
]

VESSELS = [
    {
        "vessel_id": "vessel_01",
        "name": "Foreign Surface Vessel 1",
        "kind": "foreign_surface",
        "waypoints": [
            (-122.75, 37.746),
            (-122.71, 37.749),
            (-122.67, 37.752),
            (-122.63, 37.755),
        ],
    },
    {
        "vessel_id": "vessel_02",
        "name": "Foreign Surface Vessel 2",
        "kind": "foreign_surface",
        "waypoints": [
            (-122.76, 37.805),
            (-122.73, 37.807),
            (-122.70, 37.809),
            (-122.685, 37.8095),
            (-122.67, 37.810),
            (-122.64, 37.812),
            (-122.62, 37.813),
            (-122.59, 37.815),
        ],
    },
    {
        "vessel_id": "vessel_03",
        "name": "Foreign Surface Vessel 3",
        "kind": "foreign_surface",
        "waypoints": [
            (-122.75, 37.853),
            (-122.71, 37.849),
            (-122.67, 37.846),
            (-122.63, 37.848),
        ],
    },
]

AMERICAN_SUB_POSITION = (-122.67, 37.81)

INTERCEPTORS = {
    "surface_patrol": {
        "id": "interceptor_surface_01",
        "name": "USCG Station Golden Gate Response Boat",
        "kind": "surface_patrol",
        "origin_name": "USCG Station Golden Gate",
        "origin": {"lat": 37.8339, "lon": -122.4786},
    },
    "air_asset": {
        "id": "interceptor_air_01",
        "name": "USCG Air Station San Francisco MH-65",
        "kind": "air_asset",
        "origin_name": "USCG Air Station San Francisco",
        "origin": {"lat": 37.6316, "lon": -122.3904},
    }
}

def point_in_polygon(x: float, y: float, polygon: List[Tuple[float, float]]) -> bool:
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) + 1e-12) + x1
        )
        if intersects:
            inside = not inside
    return inside

def _segment_lengths(waypoints: List[Tuple[float, float]]) -> List[float]:
    out = []
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        out.append(math.hypot(x2 - x1, y2 - y1))
    return out

def _interpolate_waypoints(waypoints: List[Tuple[float, float]], alpha: float) -> Tuple[float, float]:
    if alpha <= 0:
        return waypoints[0]
    if alpha >= 1:
        return waypoints[-1]

    lengths = _segment_lengths(waypoints)
    total = sum(lengths)
    if total <= 1e-12:
        return waypoints[-1]

    target = alpha * total
    cumulative = 0.0
    for i, seg_len in enumerate(lengths):
        if cumulative + seg_len >= target:
            local_alpha = (target - cumulative) / max(seg_len, 1e-12)
            x1, y1 = waypoints[i]
            x2, y2 = waypoints[i + 1]
            return x1 + (x2 - x1) * local_alpha, y1 + (y2 - y1) * local_alpha
        cumulative += seg_len
    return waypoints[-1]

def vessel_position(vessel_index: int, step: int, total_steps: int, speed: float = 1.0):
    vessel = VESSELS[vessel_index]
    alpha = min((step * speed) / max(1, total_steps - 1), 1.0)
    lon, lat = _interpolate_waypoints(vessel["waypoints"], alpha)

    if vessel["vessel_id"] == "vessel_02":
        lat += 0.00045 * math.sin(step / 5)
    elif vessel["vessel_id"] == "vessel_01":
        lat += 0.00035 * math.sin(step / 7)
    elif vessel["vessel_id"] == "vessel_03":
        lon += 0.00035 * math.sin(step / 4)

    return lon, lat

def generate_simulation(turns: int = 30, seed: int = 7, speed: float = 1.0) -> Dict:
    rng = random.Random(seed)
    start_time = datetime(2026, 4, 22, 12, 0, 0, tzinfo=timezone.utc)
    vessel_tracks = {v["vessel_id"]: [] for v in VESSELS}
    records = []
    events = []
    counters = {"entry": 0, "exit": 0, "dwell": 0, "revisit": 0}
    states = {v["vessel_id"]: "OUTSIDE" for v in VESSELS}
    entry_times = {v["vessel_id"]: None for v in VESSELS}
    revisit_counts = {v["vessel_id"]: 0 for v in VESSELS}
    record_idx = 1

    for step in range(turns):
        t = start_time + timedelta(minutes=10 * step)

        for i, vessel in enumerate(VESSELS):
            lon, lat = vessel_position(i, step, turns, speed=speed)
            lon += rng.uniform(-0.0002, 0.0002)
            lat += rng.uniform(-0.0002, 0.0002)

            inside = point_in_polygon(lon, lat, PROTECTED_WATERS)
            state = "INSIDE" if inside else "OUTSIDE"

            vessel_tracks[vessel["vessel_id"]].append({
                "step": step,
                "timestamp": t.isoformat(),
                "lon": lon,
                "lat": lat,
                "state": state
            })

            prev = states[vessel["vessel_id"]]

            if prev == "OUTSIDE" and state == "INSIDE":
                revisit_counts[vessel["vessel_id"]] += 1
                entry_times[vessel["vessel_id"]] = t
                counters["entry"] += 1
                events.append({
                    "timestamp": t.isoformat(),
                    "vessel_id": vessel["vessel_id"],
                    "event_type": "zone_entry_event",
                    "lon": lon,
                    "lat": lat,
                    "step": step
                })

                records.append(EventRecord(
                    record_id=f"evt_{record_idx:06d}",
                    objects=[vessel["vessel_id"], "protected_waters_01"],
                    agents=[vessel["kind"]],
                    events=["zone_entry_event", "restricted_polygon_intersection_event"],
                    structure={"source_type": "maritime_simulation", "use_case": "maritime_monitoring"},
                    information={"interpretation": f"{vessel['vessel_id']} entered protected waters"},
                    time=TimeRecord(
                        chronometric={"start": t.isoformat(), "step": step, "source": "simulation"},
                        state_based={"phase": "zone_entry_event"}
                    ),
                    location=LocationRecord(
                        text="protected waters",
                        normalized="protected_waters_01",
                        geometry={"type": "point", "lon": lon, "lat": lat}
                    ),
                    evidence=[EvidenceRecord(modality="simulation", source_id=vessel["vessel_id"], content="entry", span={"step": step})],
                    provenance={"method": "point_in_polygon + transition_logic"},
                    notes={"revisit_count": revisit_counts[vessel["vessel_id"]]}
                ))
                record_idx += 1

            elif prev == "INSIDE" and state == "OUTSIDE":
                counters["exit"] += 1
                dwell_min = None
                if entry_times[vessel["vessel_id"]] is not None:
                    dwell_min = (t - entry_times[vessel["vessel_id"]]).total_seconds() / 60.0

                events.append({
                    "timestamp": t.isoformat(),
                    "vessel_id": vessel["vessel_id"],
                    "event_type": "zone_exit_event",
                    "lon": lon,
                    "lat": lat,
                    "step": step
                })

                records.append(EventRecord(
                    record_id=f"evt_{record_idx:06d}",
                    objects=[vessel["vessel_id"], "protected_waters_01"],
                    agents=[vessel["kind"]],
                    events=["zone_exit_event", "restricted_area_occupancy_interval"],
                    structure={"source_type": "maritime_simulation", "use_case": "maritime_monitoring"},
                    information={"interpretation": f"{vessel['vessel_id']} exited protected waters"},
                    time=TimeRecord(
                        chronometric={"start": t.isoformat(), "step": step, "source": "simulation"},
                        state_based={"phase": "zone_exit_event"}
                    ),
                    location=LocationRecord(
                        text="protected waters",
                        normalized="protected_waters_01",
                        geometry={"type": "point", "lon": lon, "lat": lat}
                    ),
                    evidence=[EvidenceRecord(modality="simulation", source_id=vessel["vessel_id"], content="exit", span={"step": step})],
                    provenance={"method": "point_in_polygon + transition_logic"},
                    notes={"dwell_minutes": dwell_min, "revisit_count": revisit_counts[vessel["vessel_id"]]}
                ))
                record_idx += 1

            states[vessel["vessel_id"]] = state

    return {
        "tracks": vessel_tracks,
        "events": events,
        "records": [asdict(r) for r in records],
        "counters": counters,
        "protected_polygon": PROTECTED_WATERS,
        "vessels": VESSELS,
        "american_sub_position": AMERICAN_SUB_POSITION,
        "interceptors": INTERCEPTORS,
        "parameters": {"turns": turns, "seed": seed, "speed": speed}
    }
