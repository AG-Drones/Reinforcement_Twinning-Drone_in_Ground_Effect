"""Single entry point for the virtual design steps of the RT campaign.

Select one operation with ``--design``.  The names follow the five policy
design operations described in the paper; implementation modules are imported
lazily so that unrelated workflows do not initialize JAX or load datasets.
"""
from __future__ import annotations

import argparse


DESIGNS = (
    "informative",
    "model_based",
    "populate_reward",
    "expected_improvement",
    "generalized_expected_improvement",
)


def run_design(design: str) -> None:
    if design == "informative":
        from next_mission_design.informative_policy import generate_policy
        generate_policy(mode="information", source="design_next_experiment")
        return
    if design == "model_based":
        from next_mission_design.model_based_policy import main
        main()
        return
    if design == "populate_reward":
        from next_mission_design import expected_improvement_policy
        expected_improvement_policy.SEARCH_NEXT_MISSION = False
        expected_improvement_policy.main()
        return
    if design == "expected_improvement":
        from next_mission_design import expected_improvement_policy
        expected_improvement_policy.SEARCH_NEXT_MISSION = True
        expected_improvement_policy.main()
        return
    if design == "generalized_expected_improvement":
        from next_mission_design.generalized_policy import main
        main()
        return
    raise ValueError(f"Unknown design operation: {design}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Design the next physical interaction in the RT campaign.",
    )
    parser.add_argument("--design", required=True, choices=DESIGNS)
    args = parser.parse_args()
    run_design(args.design)


if __name__ == "__main__":
    main()
