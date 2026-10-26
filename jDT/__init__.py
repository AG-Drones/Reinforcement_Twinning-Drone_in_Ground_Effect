# TAG C
"""Differentiable Digital Twin used by the Reinforcement Twinning workflow."""

__all__ = ["build_environment", "run_dt", "run_dt_data", "run_postprocessing"]


def __getattr__(name):
    # Keep lightweight imports such as ``from jDT import params`` independent
    # from the complete JAX simulator and its circular import chain.
    if name in {"build_environment", "run_dt", "run_dt_data"}:
        from . import main

        return getattr(main, name)
    if name == "run_postprocessing":
        from .postprocessing import run_postprocessing

        return run_postprocessing
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
