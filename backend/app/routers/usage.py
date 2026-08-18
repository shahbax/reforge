from fastapi import APIRouter, Depends

from app.deps import get_current_user, get_store
from app.store import Store, User

router = APIRouter(tags=["usage"])


@router.get("/usage")
def usage(
    store: Store = Depends(get_store),
    user: User = Depends(get_current_user),
) -> dict:
    """Aggregate token/cost usage across the user's projects, grouped by stage."""
    projects, _ = store.list_projects(user.id, limit=100_000)
    by_stage: dict[str, dict] = {}
    total_cost = 0.0
    total_in = 0
    total_out = 0
    for project in projects:
        for entry in project.stage_costs:
            agg = by_stage.setdefault(
                entry["stage"],
                {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "calls": 0},
            )
            agg["input_tokens"] += entry["input_tokens"]
            agg["output_tokens"] += entry["output_tokens"]
            agg["cost_usd"] += entry["cost_usd"]
            agg["calls"] += 1
            total_cost += entry["cost_usd"]
            total_in += entry["input_tokens"]
            total_out += entry["output_tokens"]

    current = store.get_user(user.id)
    return {
        "remaining_credits": current.credits if current else 0,
        "plan": current.plan if current else "free",
        "totals": {
            "cost_usd": round(total_cost, 6),
            "input_tokens": total_in,
            "output_tokens": total_out,
        },
        "by_stage": {
            stage: {**agg, "cost_usd": round(agg["cost_usd"], 6)}
            for stage, agg in by_stage.items()
        },
    }
