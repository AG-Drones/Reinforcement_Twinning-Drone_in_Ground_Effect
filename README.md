# Reinforcement Twinning for Crazyflie Ground-Effect Control

This repository contains the digital twin, experimental processing pipeline,
parameter-identification workflow, policy-design tools, and paper figures for
the Crazyflie ground-effect Reinforcement Twinning campaign.

## Repository structure

- `jDT/`: differentiable physics-based Crazyflie digital twin.
- `EXP/`: retained raw experiments and paper-ready data in `EXP/CLEAN/`.
- `identification_output/`: final warm- and cold-start identification results.
- `next_mission_design/`: informative, model-based, Expected-Improvement, and
  generalized policy-design implementations.
- `paper/pp_paper.py`: generation of the paper figures as vector PDF files.
- `pp_EXP.py`: conversion of repeated raw experiments into averaged clean data,
  RMS profiles, reference profiles, and experimental rewards.
- `adjoint_identification.py`: sequential warm-start or complete cold-start
  identification of the static ground-effect model.
- `design_next_experiment.py`: command-line entry point for virtual policy
  design.
- `run_next_experiment.py`: Crazyflie execution and logging script.

## Python environment

Python 3.10 or newer is recommended. Install the required modules with:

```bash
python -m pip install numpy scipy matplotlib jax jaxlib cflib
```

The repository was last verified with NumPy 2.3.5, SciPy 1.16.3,
Matplotlib 3.10.6, JAX/JAXlib 0.10.2, and cflib 0.1.32. The `cflib` package is
only required to run experiments on Crazyflie hardware.

## Typical workflow

Process or regenerate the retained experimental datasets:

```bash
python pp_EXP.py --no-plot
```

Run sequential parameter identification by selecting `RUN_MODE =
"warm_start"` in `adjoint_identification.py`:

```bash
python adjoint_identification.py
```

The corresponding cold-start comparison is obtained with `RUN_MODE =
"cold_start"`.

Design the next virtual interaction with one of the available operations:

```bash
python design_next_experiment.py --design informative
python design_next_experiment.py --design model_based
python design_next_experiment.py --design populate_reward
python design_next_experiment.py --design expected_improvement
python design_next_experiment.py --design generalized_expected_improvement
```

Before a physical run, set `MISSION_PHASE`, `TRAJECTORY_NUMBER`, and the
paper-facing `EXPERIMENT_CASE` in `run_next_experiment.py`, then execute:

```bash
python run_next_experiment.py
```

Generate the selected paper figures by setting the flags at the beginning of
`paper/pp_paper.py` and running:

```bash
python paper/pp_paper.py
```

Only PDF figures are generated. `paper/figures/Real_comparison.png` is the
manually assembled experimental-video comparison and is therefore retained as
a raster source.

## Data conventions

Experimental cases use the paper nomenclature: `BL`, `INF_*`, `MB`,
`ALPHA_*`, `EI_*`, and the operating-condition suffixes `V020_Z25` and
`V050_Z10`. Metadata paths are repository-relative so the project can be moved
without editing the datasets.

`INF_11` and `INF_12` originate from archived averaged datasets for which the
individual repetitions were unavailable. Their RMS profiles are consequently
stored as zero and this assumption is recorded in their metadata.

