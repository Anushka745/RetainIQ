"""
services/funnel_engine.py
Computes funnel conversion and drop-off metrics across:
Visit -> Signup -> Activation -> Purchase
"""

from typing import Dict, List

import models

FUNNEL_STAGES = ["Visit", "Signup", "Activation", "Purchase"]

# Maps a funnel stage to the event_name(s) in the Event table that represent it.
STAGE_EVENT_MAP: Dict[str, str] = {
    "Visit": "visit",
    "Signup": "signup",
    "Activation": "activation",
    "Purchase": "purchase",
}


def compute_funnel(events: List[models.Event]) -> List[dict]:
    """
    Computes count, conversion %, and drop-off % for each funnel stage based on
    distinct end-user counts reaching each stage.
    """
    stage_user_sets: Dict[str, set] = {stage: set() for stage in FUNNEL_STAGES}

    for event in events:
        for stage, event_name in STAGE_EVENT_MAP.items():
            if event.event_name == event_name:
                stage_user_sets[stage].add(event.end_user_id)

    counts = [len(stage_user_sets[stage]) for stage in FUNNEL_STAGES]
    top_count = counts[0] if counts[0] > 0 else 1

    results = []
    for i, stage in enumerate(FUNNEL_STAGES):
        count = counts[i]
        conversion_pct = round((count / top_count) * 100, 2)
        if i == 0:
            drop_off_pct = 0.0
        else:
            prev_count = counts[i - 1] if counts[i - 1] > 0 else 1
            drop_off_pct = round((1 - (count / prev_count)) * 100, 2)
        results.append(
            {
                "stage": stage,
                "count": count,
                "conversion_pct": conversion_pct,
                "drop_off_pct": max(drop_off_pct, 0.0),
            }
        )
    return results
