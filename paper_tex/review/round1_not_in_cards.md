# Round 1: what is not in the cards

These items came out of the material of round 1 (GPT review V2, panel, code check, literature, writing audit, independent check) but have no edit card. Round 2 starts from this list and from your decisions.

## Waiting for a decision of round 1

- **Sec. III-E rankings and numbers** (lines 944, 964, 973, Conclusions line 984). These depend on [Generalization: which reward]. The section now mixes two metrics: 0.57 and 0.83 use Eq. (reward), while Fig. 15 and the ranking at (1, 0.113) use the stored per-run metric.
- **π_MB provenance**:
  - the sentence at line 718;
  - the claim "optimized with the final identified DT" in the Introduction, in Sec. II-A (Eq. rt-mb-optimum) and in Sec. III-C;
  - the off-nominal model-based policies, which carry identification iteration 006.
  
  All of these follow [Which model designed the flown π_MB].
- **Campaign order**: Block 1 ("the first episode uses π_BL"), "first tested" (line 730) and "already available" (line 881). These follow [Campaign order]. The same records show EI_01–08 flown in two sessions, and runs It3, It6–It16 and It22 absent from the data.
- **Framing**: the list of simplifications for Sec. II-A follows [Framing]. It covers noise-free rewards, the two-stage fit, the incumbent, the fixed library, no held-out validation, the replay start state, and a nominal rollout instead of an expected reward (GPT-5).
- **Curvature indicator**: "confidence", "well constrained", and the episode-bootstrap analysis follow [Parameter uncertainty].

## New work

- **Analyses on existing data**: reward noise and the incumbent; surrogate ablations; the DT optimum without regularization; model-based policies from the classical and broad-domain coefficients; leave-one-episode-out identification; the identified f_GE against the Carter, Kan and Sanchez-Cuevas data; thrust reconstructed from the logs; the uncertainty of J_BL in the scores (GPT-12).
- **New flights**: interleaved confirmation flights of π_MB and π_EI★; the mission without the obstacle; a model-based policy from the Cheeseman–Bennett coefficients; Bayesian optimization without the DT prior.
- **Length (round 2, edit cards)**: the rigid-body and Adam equations, one version each of the duplicated Fisher, E-optimal, surrogate and EI equations, and the figure merges listed by the journal-fit seat.

## Questions only you can answer

- Is the table top 0.63 m above the floor? This is TABLE_HEIGHT_Z in the Lighthouse frame.
- Which Lighthouse version and estimator were used?
- Why does the vehicle settle at z/R ≈ 2 over the obstacle for 2.3 s despite the integral action (Sec. III-A)?
- Were the seven local policies drawn from the Sobol library or designed by hand? Two of them are near single-axis vectors.
- Was a model-uncertainty envelope used for the flown π_MB? The code comments mention a "robust envelope" for It6.
- The flight script rejects a DT-predicted clearance below 0.5R, but the information design admitted 0.3R. Did INF_07–10 pass the 0.5R check?
- What does "cleaned" mean for the mean trajectories, beyond alignment and averaging? Were any flights discarded?
- Is "selected sequentially by EI" right for EI_01–08, which were flown in two sessions?

## Smaller items not carded

- **Notation:** a nomenclature table, and the symbol clashes the audit lists:
  - χ_i (overlap fraction) and bold χ (operating condition);
  - m as mass, model-update index and Adam moment;
  - λ for the interpolation factor and for eigenvalues;
  - Φ for the normal distribution and for the clearance penalty;
  - D² and D_θ;
  - τ for moments and for the rpm time constant;
  - k for the time index and for the kernel;
  - L_p and J_p for the same loss;
  - the same symbol π★_EI for the nominal and the condition-specific best;
  - three transpose styles.
- **GPT-11 details:**
  - f_GE is floored at 0.05 and z_i at 0.05R;
  - χ_i depends on x only;
  - the analytic formula of χ_i is not given.
- **GPT-13:** the pooling of nominal and off-nominal data in the condition-aware GP, and its sensitivity to the length scales.
- **GPT-4:** EI_06 and EI_08 lie within 0.09 of the face a_B = +1. The card on the EI search reports only π_EI★, at 0.30 from the faces.
- **Figures to regenerate:**
  - legends with π_k and π_{k,i} (the text uses π_λ,i);
  - "near wall" in the legends of Figs. 3, 5 and 6;
  - Fig. 15 with the reward you choose;
  - panel (c) of Fig. 14: the text mentions three superposed paths, but the caption says π_EI★ only.
- **Style:** "Eq. (n)" is used throughout, where IEEE style is "(n)".
- **Mueller et al. 2012** (time-indexed iterative learning of feedforward corrections) and **Lopez-Sanchez et al. 2020** (excitation trajectories for quadrotor parameters) could be cited. The second was not verified beyond its DOI.
