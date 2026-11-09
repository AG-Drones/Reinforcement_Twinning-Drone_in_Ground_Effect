# Code and data check of the current manuscript (`main_lf.tex`, 997 lines)

**Scope.** I checked Sections II and III in full, plus the Abstract, the Introduction and the Conclusions. I compared their numerical and factual claims with `/home/claude/R1/code`.

**Line numbers.**
- `l. N` refers to `/home/claude/R1/material/main_lf.tex`.
- `file:line` refers to files under `/home/claude/R1/code/`.

**How I recomputed numbers.**
- Recomputations ran on a copy of the code in `/home/claude/R1/code/_check/code_copy/`, so the JAX cache did not write into `code/`.
- The scripts are in `/home/claude/R1/code/_check/`:
  - `lam_min_fwd.py`
  - `exp_rewards.py`
  - `dt_rewards.py`
  - `a_vectors.py`
  - `mb_provenance.py`
- Their outputs are in `/home/claude/R1/code/_check/out/*.json|*.log`.

**Figures.**
- The figures in the current manuscript are the PDFs in `/home/claude/R1/paper/Results/`.
- I read marker coordinates from these vector PDFs with pdfplumber, calibrated against the tick marks. Accuracy is about ±0.003.
- The workspace `paper/pp_paper.py` is older than these PDFs:
  - The Fig. 4 PDF has two panels with numeric episode ticks 0–13. The code draws four panels labeled "C&B, BL, 1…12".
  - The Fig. 15 legend uses (z*/R, v_x*/v_h).
- Figures were therefore checked from the PDFs directly.

**Grades.** As in the earlier audit:
- **A**: a reader is misled, or a number is wrong.
- **B**: should be fixed.
- **C**: minor.

**Reward definitions used below (all in code).**
- **J370**: mean of [(z−z*)/R]² over the samples of the *repetition-averaged* CLEAN record with 2.20 ≤ x ≤ 3.70 m.
  - Source: `next_mission_design/expected_improvement_policy.py:69,72,260-274`, used in `replay_rows` at `:595,:603`.
  - The paper's reward axes plot R = 1 − J370 (`paper/pp_paper.py:1271-1273,1326-1327`).
- **J400**: the same mean over 2.20 ≤ x ≤ 4.00 m. This is the MB optimization cost (`next_mission_design/model_based_policy.py:61,103-112`).
- **v1** (`vertical_tracking_v1`): J400 + MSE(3.01–4.00 m) + 0.25·max e² (`jDT/postprocessing.py:20-33,95-123`).
  - It is computed per repetition and then averaged (`pp_EXP.py:620-636`).
  - The result is the `mean_experimental_reward` stored in `EXP/CLEAN/*_reward.json`.

---

## 1. Earlier audit (C1–C24) mapped to the current text

| C | Topic | Current text | Status | Comment (current evidence) |
|---|---|---|---|---|
| C1 | Reward definition and plotted axes | Eq. (reward) l. 709–717; Eq. (normalized-score) l. 762–768; Figs. 13–15 | **Changed, partly fixed (A remains)** | The Italian note is gone. R = 1 − J now has the same form as Figs. 13–14, which use J370. Ω_R and N_R are still undefined. MB is optimized with J400 (N7). Fig. 15 now uses v1 for every condition (N4). |
| C2 | Start and hover position; definition of z | l. 372 | **Still present (C)** | Hover is at x = 0.20 m, not x = 0 (`jDT/params.py:64`; `run_next_experiment.py:305-308,1054-1070`). z is the rotor-plane height above the obstacle top (`pp_EXP.py:340-344`); the text says "distance of the vehicle". |
| C3 | DT parameter table | l. 432, 503–526 | **Changed (B), worse at l. 432 (see N9, A)** | τ_rpm was added (l. 522). m is labeled as adopted from Richardson et al. but was measured (`jDT/params.py:32`). The calibrated T_max = 0.1148 N is still absent (`params.py:34-38`). Products of inertia are omitted (`params.py:169-173`). Drag C_D = 0 is not stated (`params.py:179`). |
| C4 | Battery-voltage correction | l. 503, 505; Table I row V_ref (l. 523) | **Still present (A)** | `battery_omega_factor` is never called (`jDT/simulator.py:331-333`). The thrust map is linear: T_i = 0.1148·c_i/65535 N and Ω_i = (T_i/k_T)^½ (`simulator.py:335-346`; `jDT/propulsion.py:3-7,21-30`). |
| C5 | GE model details | l. 529–551 | **Still present (C)** | z_i is the height of the tilted rotor center, including the 8.5 mm rotor-plane offset (`simulator.py:358-372`). z_i is floored at 0.05R and f_GE at 0.05 (`jDT/GE_correction.py:25-31,48-53`). χ_i depends only on x. Only thrust is corrected, not Q_i (`simulator.py:374-384`). |
| C6 | Identification loss, initial state, Θ | l. 114, 425, 571, 577–598, 635 | **Partly fixed (B)** | The obstacle window is now stated at l. 425 but not in Eq. (identification-loss). "Reconstructed initial condition" (l. 114, 571, 577) is still wrong: replay starts at x = 1.70 m from the nominal steady out-of-ground-effect (OGE) state (`adjoint_identification.py:651-694`). Θ is not given; the code uses 0 ≤ p ≤ 6 and A ≥ −0.95·0.5^p (`:120-122,761-766`). The 100-iteration minimum is not stated (`:133`). |
| C7 | Covariance | l. 637–660 | **Fixed** | Eigenvalue floor 10⁻⁶ and J_p scaling, exactly as in `adjoint_identification.py:1591-1603`. |
| C8 | Fisher information and E-optimal selection | l. 161–181, 575, 662–693, 809 | **Partly fixed (A remains)** | l. 680 now states that Fig. 4b is re-evaluated post hoc with the final DT. The selection rule is still misdescribed: the code forms no F_{1:N}, selects batches of three, and applies novelty gates (N8). l. 575 still presents the post-hoc diagnostic as the trigger for the domain switch, but the switch is the manual flag `REFERENCE_REGION_MODE` (`informative_policy.py:43`). |
| C9 | Number and split of INF policies | l. 573–575, 798, 807 | **Changed (A remains)** | The 9+3 split is now 6+6, which matches the Fig. 4 shading. The near-wall code domain is 0.3–1.5R, and INF_09/10 references reach 0.34R. INF_11/12 are legacy records at other conditions and were not designed by this code (N8). |
| C10 | Warm vs cold start | — | **Still missing (B)** | The word "cold" does not occur. Cold start from (0,0): A = 0.12028, p = 1.96955, J_p = 0.0346547, 2195 iterations. Warm start: A = 0.12100, p = 1.98042, J_p = 0.0346530 (`identification_output/Cold_start/cold_start_summary.json`; `Warm_start/E12`). |
| C11 | MB policy | l. 62, 185–196, 697–726, 855, 861 | **Changed; now explicitly contradicted (A)** | l. 718: "optimized with the single final identified DT". The code uses the manual coefficients (0.2304, 3.136) (`model_based_policy.py:46-52`). Window, norm and grid also differ (N7). |
| C12 | Interpolation policies | l. 730, 881, Fig. 11 caption l. 886 | **Text fixed; figures not (C)** | The text uses π_{λ,i} with λ ∈ {1/3, 2/3}. The PDFs use π_{k,i} with "k = 1/3" (Fig. 11) and π_k (Fig. 13). "First tested" conflicts with the run order (C15). |
| C13 | Basis, Sobol library, α policies | l. 730, 892, 897 | **Partly fixed (B/C)** | Centers and roles are now correct (l. 892). "2000" should be 2048 (`expected_improvement_policy.py:58`). The Fig. 12 "Safe Sobol library" is 256 *unscreened* samples with \|a_j\| ≤ 0.8 (`pp_paper.py:94-95,1365-1371`; the PDF has about 256 curves). The selection rule for the seven α policies is not in the code (N11). |
| C14 | Surrogate and EI details | l. 224–234, 740–760 | **Mostly fixed (C remains)** | Ordinary least squares (OLS), Matérn-3/2, scale 0.30, floor 0.05², deterministic data, jitter 10⁻⁸ and ξ = 0 now agree. Remaining wording issues, and the generalized GP, are covered in N6. |
| C15 | Chronology ("consecutive phases") | l. 62, 158, 358, 563, 566, 730 | **Still present (A)** | Legacy run numbers (`EXP/legacy_name_map.json`): ALPHA_01–07 and EI_01–02 in It17, EI_03–08 in It18, then BL, INT_01, INT_02 and MB in It19. INF batches are It1, It2, It4 and It5; It3 and It6 were MB designs (`model_based_policy.py:46-52`; `expected_improvement_policy.py:692-695`). **Correction to the earlier audit:** "It27" for INF_11/12 is a bookkeeping slot. Their metadata say "Imported from the legacy campaign" `GE_rg_a`, source files `…RG_It5.txt` and `…RG_It4.txt`. Their acquisition date is therefore not determinable; "acquired last" is unsupported. |
| C16 | Generalization | l. 768, 771, 942–975, 984 | **Changed (A)** | Two conditions now (fixed). The transfer rule is misdescribed (N5). Values and orderings mix two reward definitions (N4). |
| C17 | Logging | l. 425 | **Still present (B)** | Data are radio-streamed via cflib, not recorded by the firmware (`run_next_experiment.py:567-725`). Periods: position 20 ms; most channels 50 ms; PID internals 100 ms. Stored rows are about 10 Hz (CLEAN Δt ≈ 0.10 s). |
| C18 | Controller | l. 427 | **Still present (B)** | x and y are velocity-commanded through `send_hover_setpoint(vx(x), vy, 0, z)` (`run_next_experiment.py:1006-1008`). The DT uses `XY_VELOCITY_MODE` (`jDT/controller.py:184-187`; `jDT/main.py:57`). Only z uses the position loop. |
| C19.1 | "It20" | — | **Fixed** | |
| C19.2 | Kan et al. cited both ways | l. 45 vs l. 544 | **Softened (C)** | l. 45 "velocity changes the response" vs l. 544 "velocity dependence is limited…". The code has no velocity dependence (`simulator.py:315-324` stores `ge_velocity_*` but never uses them). |
| C19.3 | "After every flight" | l. 571, 575, 693 | **Still present (B)** | See N8. |
| C19.4 | Termination criterion | l. 183, 693, 828 | **Still present (B)** | No such test exists in the code. |
| C19.5 | z/R ≥ 0.5 | l. 986 | **Still present (B)** | See N12. |
| C20 | Coefficients not reported | l. 811, 824 | **Fixed** | Optional: σ_A = 0.084 and σ_p = 1.09 at E12; both marginal 2σ intervals include zero (`Warm_start/E12/adjoint_results.npz`). |
| C21 | Conditional-gain panel undefined | Fig. 4 | **Resolved** | The panel was removed (the PDF has panels a and b only). The ρ_{A,p} values quoted at l. 811 and 826 are now shown in no figure (C). |
| C22 | Reward-transfer band | captions l. 906, 915 | **Still present (C)** | The band is the envelope of μ ± 1.645σ over all training descriptors (`pp_paper.py:1286-1308`). |
| C23 | LaTeX and typos | — | **Fixed; new ones (C)** | l. 40: "hass grown", "substituting or support", "These includes", "small onboard sensor", "if retained necessary". l. 892: "changes-such as" should use an em dash. l. 56: "the remaining GP discrepancy". l. 60 "Richardson and Pretorius" vs "Richardson et al." elsewhere. |
| C24 | Unmodeled DT terms | l. 503 | **Partly fixed (C)** | τ_rpm is stated. C_D = 0, RK4 at 2 ms and the rpm rate limit of 2·10⁵ rpm/s are not (`params.py:94,116,179`; `simulator.py:412-420`). |

---

## 2. Checks of the current text

### N1. Number of repetitions. Grade A. Verdict: Disagrees

**Text.**
- l. 782: "…the mean experimental trajectory EXP_BL obtained from five repetitions … with N_r=5."
- l. 789 (caption): "…over five repetitions."
- l. 928: "…the curves in Fig. … are obtained by averaging five repetitions of each case…"

**Evidence.** `number_of_repetitions` and `repetition_rewards` in `EXP/CLEAN/*_reward.json` are written by `pp_EXP.py:620-636` from the raw files that were actually averaged. BL, MB and EI_09 each have **3**. Every case:

| Case | n | Case | n | Case | n |
|---|---|---|---|---|---|
| BL | 3 | EI_01 | 6 | BL_V020_Z25 | 2 |
| INT_01 | 4 | EI_02 | 4 | MB_V020_Z25 | 2 |
| INT_02 | 4 | EI_03 | 3 | EI_TR_V020_Z25 | 3 |
| MB | 3 | EI_04 | 4 | BL_V050_Z10 | 3 |
| ALPHA_01 | 3 | EI_05 | 3 | MB_V050_Z10 | 2 |
| ALPHA_02 | 4 | EI_06 | 3 | EI_TR_V050_Z10 | 3 |
| ALPHA_03 | 4 | EI_07 | 4 | EI_01_V050_Z10 | 3 |
| ALPHA_04 | 5 | EI_08 | 3 | EI_STAR_V050_Z10 | 4 |
| ALPHA_05 | 3 | **EI_09** | **3** | INF_01–10 | 3 each |
| ALPHA_06 | 4 | EI_10 | 4 | INF_11 / INF_12 | 4 / 3 (archived means only; RMS stored as zero) |
| ALPHA_07 | 4 | | | | |

The RMS formula with 1/N_r agrees with `pp_EXP.py:315`. However, the repetitions are interpolated on the time grid of the first run, after aligning the time at which each run crosses x = 2.20 m (`pp_EXP.py:268-316`). The RMS is not evaluated "at each streamwise position" (C).

**Corrected text.**
- l. 782: "…obtained from three repetitions, while the surrounding shaded region represents the corresponding ±RMS run-to-run dispersion. After the repetitions are aligned at the leading-edge crossing, this quantity is defined at each sample as RMS = [N_r⁻¹ Σ_j (z_j − z̄)²]^{1/2}, with N_r = 3."
- l. 789: "…over three repetitions."
- l. 928: "Whereas the curves in Fig. X are averages of three repetitions of each case, …"

---

### N2. Information-phase numbers (Sec. III-B). Grade: values Agree; B for the ρ narrative; C for "twelve repetitions"

**Recomputation.** I re-implemented `pp_paper.py:551-663` exactly, but with `jax.jacfwd` in place of `jacrev`. The Jacobian is identical; `jacrev` ran out of memory. Script: `_check/lam_min_fwd.py`; output: `_check/out/lam_min_fwd.json`. The digitized Fig. 4b PDF gives the same numbers (±0.003).

| Cumulative episode (Fig. 4 axis) | Added record | λ_min(F_n) of this record alone | λ_min, designed | λ_min, repeated BL | A | p | ρ_{A,p} |
|---|---|---|---|---|---|---|---|
| 1 | BL (E00) | 0.0298 | 0.0298 | 0.0298 | 0.1036 | 1.336 | **0.974** |
| 2 | INF_01 | 0.642 | **0.676** | **0.060** | 0.1675 | 2.296 | 0.783 |
| 3 | INF_02 | 0.103 | 0.779 | 0.089 | 0.1718 | 2.322 | 0.829 |
| 4 | INF_03 | 0.005 | 0.839 | 0.119 | 0.1813 | 2.542 | 0.848 |
| 5 | INF_04 | 0.034 | 0.894 | 0.149 | 0.1852 | 2.594 | 0.860 |
| 6 | INF_05 | 0.003 | 0.942 | 0.179 | 0.2003 | 2.761 | 0.857 |
| 7 | INF_06 | 0.055 | **0.9998** | 0.209 | **0.2176** | **2.792** | **0.883** |
| 8 | INF_07 | 0.273 | 1.417 | 0.238 | 0.1651 | 2.468 | 0.860 |
| 9 | INF_08 | 0.068 | 1.530 | 0.268 | 0.1658 | 2.427 | 0.872 |
| 10 | INF_09 | 0.400 | 2.089 | 0.298 | 0.1314 | 2.122 | 0.847 |
| 11 | INF_10 | 0.413 | 2.509 | 0.328 | 0.1166 | 1.947 | 0.831 |
| 12 | INF_11 (legacy) | 0.009 | 2.912 | 0.358 | 0.1195 | 1.968 | 0.822 |
| 13 | INF_12 (legacy) | 0.012 | **3.242** | **0.387** | **0.1210** | **1.980** | **0.818** |

A, p and ρ come from `identification_output/Warm_start/E00…E12/adjoint_results.npz`.

**Verdicts.**
- 0.676 / 0.060 (l. 809), 1.000 (l. 811), 3.242 (l. 824), A = 0.218 and p = 2.792 (l. 811), ρ = 0.974 / 0.883 / 0.818, and final A = 0.121, p = 1.980: **Agree**.
- **Is 1.000 a normalization? No.**
  - There is no normalization anywhere in `pp_paper.py:587-652`.
  - The value is 0.9998. That it is close to 1 is a coincidence of the units:
    - S is scaled by √diag Σ_E12 = (0.0844, 1.0866).
    - F is divided by σ_e² = J_p(E12) = 0.034653 and by K_n.
- **"Twelve repetitions of the baseline would instead reach only 0.387" (l. 824): Partly (C).** 0.387 = 13 × 0.02979. The counterfactual at cumulative episode 13 counts the baseline record 13 times. Twelve copies would give 0.357.
  - Fix: "Repeating the baseline record for the same 13 cumulative episodes would instead reach only 0.387."
- **ρ narrative (l. 811): Partly (B).** ρ is lowest (0.783) after the *first* informative episode and then *rises* through the broad stage to 0.883. The final 0.818 is still above 0.783. "The reduction supports…" therefore credits the broad stage with a decrease that happened at its first episode only.
  - Proposed: "The estimated correlation drops from ρ_{A,p} = 0.974 for the baseline record to 0.783 after the first informative episode. It then rises to 0.883 over the remaining broad-domain episodes, as further broad-domain data mainly reinforce the same coupled direction."
  - At l. 826: "The correlation then decreases to ρ_{A,p} = 0.818 at the end of the near-wall stage."
- **Note.** INF_11 and INF_12 (legacy, see N8) add 0.403 and 0.330 to λ_min. That is 0.733 of the 2.242 gained after episode 7, i.e. 33 %. The near-wall gain, and the claim at l. 980 that the restriction "restored information gain", rely partly on these two legacy records.

**Exactly how the repeated-BL counterfactual is computed** (`pp_paper.py:587-652`):
1. The measured BL record (time base, x samples, nominal 0.35 m/s) is copied with `CONTROL_MODE=0` (PID) and a zero feed-forward. The BL reference correction is identically zero (`EXP_BL_RG_input.txt`), so this is the same replay as the designed episode 1.
2. It is replayed in the DT with the **final** E12 coefficients, starting from the nominal OGE state at x = 1.70 m (`adjoint_identification.py:617-719`).
3. S = ∂(z_rotor/R)/∂[A, p] is evaluated at the experimental x samples. It is restricted to 2.20 ≤ x ≤ 3.01 m (K = 21 samples for BL) and scaled column-wise by √diag Σ_E12.
4. F_BL = SᵀS/(K σ_e²), with σ_e² = J_p(E12) = 0.034653. λ_min(F_BL) = 0.02979.
5. The "repeated BL" curve is λ_min(N F_BL) = N·0.02979.
6. The designed curve uses the same final model, scaling and σ_e² for every episode. **Both curves are post-hoc; no prior information F_0 is included.**
7. l. 680 states this correctly.

---

### N3. Rewards in Secs. III-C and III-D. Grade: values Agree; definition B

**Text.**
- l. 861: "The DT reward increases from approximately R_∘=0.68 for π_BL to R_∘=0.97 for π_MB. The corresponding physical reward increases from approximately R_•=0.54 to R_•=0.85."
- l. 910: "…its DT reward increases only from approximately 0.968 to 0.978, whereas the physical reward rises from approximately 0.855 to 0.952."

**Computation.** Scripts: `_check/exp_rewards.py` and `_check/dt_rewards.py`. DT values come from factual replay with the final E12 coefficients.

| Case | R_∘ = 1−J370 (DT, E12) | R_• = 1−J370 (EXP, averaged trajectory) | Fig. 14 PDF marker | v1, mean ± SD over repetitions | R = 1−J400 (EXP) |
|---|---|---|---|---|---|
| BL | **0.676** | **0.544** | (0.676, 0.544) | −1.096 ± 0.124 (n = 3) | 0.617 |
| MB | **0.968** | **0.855** | (0.968, 0.855) | −0.598 ± 0.096 (n = 3) | 0.876 |
| EI_09 | **0.978** | **0.952** | (0.978, 0.953) | −0.173 ± 0.036 (n = 3) | 0.959 |

**Verdict.** The numbers agree with **R = 1 − J370**. In that definition:
- Ω_R = {2.20 ≤ x ≤ 3.70 m}, i.e. 21.7 ≤ x/R ≤ 87.0 in the shifted coordinate. This is `RT_REWARD_END_M = 3.70`.
- N_R is the number of samples of the repetition-averaged CLEAN record in Ω_R, at about 10 Hz: 41–42 at the nominal condition, 72–74 at (2.5, 0.045) and 24–30 at (1, 0.113).
- z_BL = z* is the nominal clearance.
- The DT is interpolated at the same experimental x_k (`adjoint_identification.py:712-719`).

The reward is evaluated on the *averaged* trajectory, not averaged over repetitions. A per-repetition J370 cannot be computed because the raw repetitions are absent.

Eq. (reward) leaves Ω_R and N_R undefined (B). l. 861, "the same reward definition used throughout the subsequent policy search", holds for the nominal EI surrogate only:
- MB optimization uses J400 (N7).
- The condition-aware surrogate and Fig. 15 use v1 (N4, N6).

**Corrected text.** Add after Eq. (reward):

> "Here Ω_R is the interval 2.20 ≤ x ≤ 3.70 m (21.7 ≤ x/R ≤ 87.0), N_R is the number of samples in Ω_R, and z_k is taken from the repetition-averaged trajectory; DT rewards are evaluated at the same streamwise samples by factual replay with the final identified coefficients."

---

### N4. Generalization scores and statements. Grade A. Verdict: Disagrees (two reward definitions are mixed)

**Text.**
- l. 944: "At (2.5,0.045), the transferred policy provides a further, albeit modest, improvement. At … (1,0.113), however, its physical reward is slightly lower than that of the model-based policy."
- l. 964: "The transferred-policy diamond improves slightly on the model-based-policy square at the low-speed, larger-clearance condition. At the higher-speed, small-clearance condition, the ordering is reversed…"
- l. 973: "…yielding approximately S_•=0.57… reaches … approximately S_•=0.83…"
- l. 984 (Conclusions): "…a modest gain at one operating condition but slightly underperformed … at the other."

**Evidence.** The **current** Fig. 15 PDF (`paper/Results/stage_6_PID_normalized_reward_generalization.pdf`) uses **v1 for every condition**:
- EXP: `mean_experimental_reward`, the mean over repetitions.
- DT: v1 of the E12 replay.

This matches the current code path `pp_paper.py:1225-1247` → `generalized_policy.build_general_replay` (`generalized_policy.py:139-185`). There, `lookup.update` overwrites the nominal rows as well. The numbers 0.57 and 0.83 instead come from **J370**, which is what the older PNG used for all conditions. This also resolves the earlier audit's remark that the off-nominal PNG values "match no metric": they match J370.

| Policy | S_∘ (v1, DT) | S_• (v1) = current Fig. 15 | Fig. 15 PDF marker (S_∘, S_•) | S_∘ (J370, DT) | S_• (J370) | Earlier PNG |
|---|---|---|---|---|---|---|
| (1.5, 0.079) MB | 0.910 | 0.455 | (0.910, 0.455) | 0.900 | 0.681 | (0.901, 0.681) |
| (1.5, 0.079) EI_09 | 0.926 | 0.843 | (0.926, 0.845) | 0.931 | 0.894 | (0.930, 0.896) |
| (2.5, 0.045) MB | 0.982 | 0.539 | (0.982, 0.539) | 0.983 | 0.622 | (0.984, 0.620) |
| (2.5, 0.045) TR | 0.768 | **0.679** | (0.768, 0.679) | 0.748 | 0.671 | (0.748, 0.671) |
| (1, 0.113) MB | 0.887 | **0.680** | (0.887, 0.680) | 0.856 | **0.740** | (0.855, 0.738) |
| (1, 0.113) TR | 0.888 | **0.651** | (0.888, 0.651) | 0.898 | **0.772** | (0.898, 0.773) |
| (1, 0.113) EI_01 | 0.880 | **0.365** | (0.880, 0.365) | 0.898 | **0.575** | (0.898, 0.575) |
| (1, 0.113) EI★ | 0.913 | **0.757** | (0.913, 0.760) | 0.908 | **0.827** | (0.907, 0.830) |

**What follows.**
- With v1 (the current figure):
  - At (1, 0.113) the transferred policy is slightly worse than MB (0.651 vs 0.680) ✓.
  - At (2.5, 0.045) it is markedly better, not "modestly": 0.539 → 0.679.
  - The two EI points are 0.365 and 0.757, not 0.57 and 0.83.
- With J370, the definition of Eq. (reward):
  - The transferred policy beats MB at **both** conditions (0.671 vs 0.622; 0.772 vs 0.740).
  - The reversal at (1, 0.113) and the rationale "When direct transfer fails to improve that policy" (l. 975) disappear.
- The difference at (1, 0.113) is within run-to-run scatter in v1: −0.452 ± 0.014 (n = 2) vs −0.492 ± 0.111 (n = 3).
- Fig. 14 and Fig. 15 now show different scores for the same nominal policies. Applying Eq. (normalized-score) to the Fig. 14 values gives S_•(MB) = 0.681, but Fig. 15 plots 0.455.

**Corrected text.** The author must choose one definition.

*Option 1 (recommended: consistent with Eq. (reward) and Figs. 13–14).* Regenerate Fig. 15 with J370. Then:
- l. 944: "At (2.5,0.045), the transferred policy improves on the model-based policy (S_• = 0.67 versus 0.62). At (1,0.113), it also improves slightly (0.77 versus 0.74), but by less than the run-to-run dispersion."
- l. 964: replace the reversal sentence with: "At both conditions the transferred-policy diamond lies above the model-based square, but only marginally at the higher-speed, small-clearance condition."
- l. 973: keep 0.57 and 0.83.
- l. 975: replace "When direct transfer fails to improve that policy" with "When direct transfer yields only a marginal gain".
- l. 984: "Directly transferring the nominal correction improved on the model-based policy at both conditions, markedly at one and marginally at the other."

*Option 2 (keep the current v1 figure).* Then define v1 next to Eq. (normalized-score): "J = MSE(2.20–4.00 m) + MSE(3.01–4.00 m) + 0.25 max_k e_k², averaged over repetitions". Then:
- l. 944: "…the transferred policy provides a substantial further improvement (S_• = 0.68 versus 0.54)…"
- l. 973: "…yielding approximately S_•=0.36…" and "…reaches … approximately S_•=0.76…"

---

### N5. Transfer rule. Grade A. Verdict: Disagrees

**Text.**
- l. 942: "The nominal best correction is then transferred by applying the same three coefficients a=[a_A,a_B,a_C]ᵀ relative to the condition-specific model-based policy. This scaling preserves the learned correction structure…"
- l. 768: "Policy coordinates are defined relative to the local MB deformation."
- l. 771: "…transferred in the coordinates of the condition-specific model-based reference correction…"

**Rule implemented** (`next_mission_design/transfer_calibration.py:200-223,431-439`, with the basis from `expected_improvement_policy.py:204-232`):

1. **Basis.** The basis is b_j(x) = g_j(x)·sin²[π(x−2.00)/2.00], normalized to unit peak, with Gaussian g_j centered at 2.50, 2.95 and 3.30 m and widths σ = 0.25, 0.20 and 0.25 m.
2. **Source coordinates.** a★ = argmin_a Σ_k [b(x_k)ᵀa − (Δz_EI★(x_k) − Δz_MB(x_k))/R]², over 161 points on 2.00–4.00 m. The nominal measured references are used, which gives a★ = (−0.664, +0.699, +0.200).
3. **Local MB amplitude per basis.** m_j(Δz) = [Σ_k b_j(x_k)(Δz(x_k)/R)² / Σ_k b_j(x_k)]^{1/2}, on the 81-node grid x_k ∈ [2.00, 4.00] m.
4. **Scaling.** s_j = m_j(Δz_MB^χ) / m_j(Δz_MB^nom), and a_j^tr = s_j a★_j.
5. **Transferred policy.** Δz_tr(x) = Δz_MB^χ(x) + R Σ_j a_j^tr b_j(x), with the first and last nodes set to zero.

| Condition | s | a^tr = s ⊙ a★ | Projection of the flown EI_TR reference |
|---|---|---|---|
| (2.5, 0.045) | (0.407, 0.527, 0.428) | (−0.270, +0.368, +0.086) | (−0.271, +0.337, +0.099) |
| (1, 0.113) | (1.845, 1.508, 1.604) | (−1.225, +1.053, +0.321) | (−1.195, +0.920, +0.406) |

The flown EI_TR references match the scaled rule to within 0.03R and 0.10R; with the *unscaled* a★ the deviation would be 0.34R and 0.49R. At (1, 0.113) the transferred a lies **outside** the nominal box |a_j| ≤ 1.

For the condition-aware GP the coordinates are β_j = a_j / max(m_j(Δz_MB^χ), 0.05) (`generalized_policy.py:118-132`).

**Corrected text** (l. 942):
> "The nominal best correction is then transferred basis by basis. Its coefficients a★ are multiplied by s_j, the ratio of the local root-mean-square amplitude of the condition-specific model-based correction to that of the nominal one within the support of b_j: a_j^tr = s_j a★_j, and Δz_tr = Δz_MB^χ + R bᵀa^tr. This scaling preserves the learned correction structure without imposing the nominal reference correction as a fixed altitude offset."

Optionally add: "s = (0.41, 0.53, 0.43) at (2.5,0.045) and (1.85, 1.51, 1.60) at (1,0.113)."

At l. 768, replace "Policy coordinates are defined relative to the local MB deformation" with:
> "Policy coordinates are measured relative to the condition-specific MB correction and divided by its local amplitude in each basis."

---

### N6. GP description. Grade: Partly; B for the generalized GP, C for the wording items

| Claim | Code | Verdict |
|---|---|---|
| "each coordinate scaled by 0.30R" (l. 740) | feature = a/0.30, where a is already dimensionless in units of R (`expected_improvement_policy.py:97,242-246`) | Partly (C). Write "with a length scale of 0.30 for each a_j". |
| Signal variance "initialized from the empirical variance of the affine residuals and bounded below by 0.05²" | `self.signal = max(var(residual), 0.05**2)`, fixed; no hyperparameter is optimized (`:315-317`) | Partly (C). Write "set to" instead of "initialized from". |
| Jitter 10⁻⁸; no noise | `self.noise = zeros`; `kernel += diag(noise + 1e-8)` (`:303-306,318`) | Agrees |
| OLS affine fit | unit weights (`:307-314`) | Agrees |
| EI with ξ = 0 | `expected_improvement(mean, std, incumbent)` (`:332-337`) | Agrees |
| "zero improvement assigned to a vanishing posterior variance" (l. 760); "EI is set to zero when σ=0" (l. 234) | Returns max(μ − R⁺, 0) when σ ≤ 10⁻⁹. The variance is floored at 10⁻⁸ (`:328`), so σ ≥ 10⁻⁴ and this branch never runs. | Disagrees but immaterial (C). Delete the clause, or write "the posterior variance is floored at 10⁻⁸". |
| Incumbent R⁺ | best measured J370 reward among all nominal-condition training rows: BL, INT, MB, ALPHA, EI (`:918-920`) | Agrees |
| Units and bounds of a | Δz = Δz_MB + R B a, with b_j normalized to unit peak, so a_j is a peak amplitude in rotor radii. The search box is −1 ≤ a_j ≤ 1 (`:93-94,620-655`). | Agrees. State the units explicitly. |
| Candidate set (nominal) | 2048 scrambled Sobol points (seed 17), 6 axis seeds at ±0.25, the projected historical coordinates, and 128 local Gaussian moves (σ = 0.10) around the four best. Admissible if the DT lowest-rotor clearance is ≥ 0.5R (`:937-942`). One maximizer per run (`:1037-1040`). | "2000" should be 2048 (C) |

**Condition-aware GP, used for the two EI steps at (1, 0.113)** (`generalized_policy.py:188-310,452-561`). It differs from the text at l. 747 and 955–962 (B):
- **Inputs.** Six features [β₁, β₂, β₃, projection RMSE, v_x (m/s), z*/R]. They are standardized by their training mean and by max(std, (0.25, 0.25, 0.25, 0.05, 0.10, 0.50)), with a unit-length-scale Matérn-3/2 kernel (`:253-302`). The policy input is β (N5), not a.
- **Data.** EXP scores use v1, averaged over repetitions (`:170-172,224-225`), not the cleaned mean trajectory.
- **Affine part.** Weighted least squares with weights 1/noise_i², where noise_i = max(SD_rep,i/|R_BL|, 0.01) (`:226-229,273-280`).
- **Noise.** A noise term is used: kernel diagonal = noise_i² + 10⁻⁷ (`:284`).
- **Signal variance.** max(var, 0.02²) (`:282`).
- **EI.** ξ = 0; the incumbent is the best measured S_• at the target condition (`:503-506`).
- **Candidates.**
  - 2048 Sobol points (seed 31), truncated to the first 2000. They lie in a β box spanning the historical min/max ± 35 % of the span, with span ≥ 0.6, clipped to ±3.
  - Plus 5 points (−0.5, −0.25, 0.25, 0.5, 0.75)·β_TR along the failed-transfer direction (`:313-330`).
  - Screening: \|Δz\| ≤ 4.55R and DT clearance ≥ 0.5R.
  - **Three** mutually distinct maximizers are saved per round (`:43,333-344`). Only trajectory 2 of runs It25 and It26 is in the dataset.
  - EI★ at (1, 0.113) has β = (−0.35, 0.20, 0.11) ≈ 0.22 β_TR, which is close to the 0.25·β_TR line candidate.

**Proposed text.** Add one sentence to the generalization paragraph (l. 955–962):
> "In the condition-aware surrogate, δ̂ takes as inputs the amplitude-normalized coordinates β_j = a_j/m_j(Δz_MB^χ), the projection residual, v_x and z*/R, each standardized; the scores are the per-repetition means of the tracking cost, and their standard error (at least 0.01) enters both the weighted affine fit and the GP noise."

---

### N7. Model-based policy. Grade A. Verdict: Disagrees

| Item | Text | Code | Verdict |
|---|---|---|---|
| Control points | "Δx=R, over the complete crossing" (l. 704) | 0.025 m = 1.09R on 2.00–4.00 m, 81 nodes; Δz = 0 outside (`model_based_policy.py:54,88-90,98-100`) | Partly (C) |
| Bound | \|Δz\| ≤ 3R | `DELTA_Z_MIN/MAX = ∓3R`, clip each step (`:64-65,327`) | Agrees |
| Clearance | 0.5R, lowest rotor | while the CoM x is above the obstacle; hard post-check (`:70-71,244-269,392-397`) | Agrees |
| Weights | 0.10, 2.0, 10⁵ with ‖·‖₂² | Same weights, but on **means**: amplitude = mean over 81 nodes, curvature = mean over 79 second differences, clearance = mean over samples above the obstacle (`:232-235,263-269,279-285`) | Disagrees (B). Write (1/N)‖·‖₂², or "mean square". |
| J_trk inside J_MB | same J_trk as Eq. (reward) (l. 709–720) | J400, i.e. **2.20–4.00 m** (`:103-112`), not the 2.20–3.70 m of the reported rewards | Disagrees (B) |
| Adam | not stated | 150 iterations, learning rate 10⁻³, β = (0.9, 0.999), ε = 10⁻⁸, Δz₀ = 0, no convergence test (`:53,55,304-331`) | (C) Add. |
| GE coefficients | "optimized with the single final identified DT" (l. 718); also l. 62, 185, 697, 855 | `GE_COEFFICIENT_SOURCE = "manual"`, (A, p) = (0.230416, 3.136230), labeled "historical first-identification model … used to design the original It3 policy" (`:46-49`) | **Disagrees (A)** |
| Robustness | "no model-uncertainty ensemble is used" (l. 718) | `ROBUST_MB_POLICY = False` now, but the comments at `:50-52,173-175` say It6 was designed with a "robust envelope" | Not determinable for the flown record |

**Was the flown MB record (EXP_MB) designed with the final model? The evidence says no.**
1. EXP_MB is It19_4 with metadata `"identification_iteration": "iteration_006"` and `"mission_design": "rt_calibration"`. The flight script accepts an `rt_calibration` policy only if `transfer_calibration.py` packaged it (`run_next_experiment.py:224-228`), and that script's `video_repeats` mode re-packages the reference of an earlier experiment (`transfer_calibration.py:39-49,268-346`).
2. `expected_improvement_policy.py:692-695` calls the RT anchor "the archived It6 MPC file", whose applied reference is `EXP_MB_RG_input.txt`.
3. Every RT flight (ALPHA, EI, nominal BL/INT/MB, and the generalization BL/MB/TR at It23 and It24) carries `identification_iteration: iteration_006`. E12 is a post-campaign replay that includes INF_11 and INF_12 (`adjoint_identification.py:1,61-67`).
4. Re-optimization test (`_check/mb_provenance.py`, `_check/out/mb_manual.json`, `_check/out/mb_E12.json`). I ran the current optimizer (nominal model, 150 Adam iterations) with each coefficient set and compared the result with the flown `EXP_MB_RG_input.txt`:

   | Coefficients used | Δz/R min / max | RMS (max) difference from the flown reference | RMS after best amplitude scaling |
   |---|---|---|---|
   | Flown reference | −0.84 / +1.03 | — | — |
   | Manual (0.230, 3.136) | −0.97 / +1.18 | 0.081R (0.20R) | 0.046R (k = 0.89) |
   | E12 (0.121, 1.980) | −1.03 / +1.19 | 0.099R (0.22R) | 0.042R (k = 0.85) |

   - The two optima have the same shape and differ by only 0.04R RMS.
   - Both are about 10–15 % larger in amplitude than the flown reference, as expected if the flown It6 design used the robust envelope.
   - **The re-optimization therefore cannot tell which coefficients were used** (not determinable from the DT).
   - The provenance therefore rests on items 1–3, which all point to an interim model (identification iteration 006, nominal coefficients 0.230 and 3.136). They contradict "optimized with the single final identified DT":
     - E12 is labeled a post-campaign identification (`adjoint_identification.py:1`).
     - The code comments state that It6 used a model-uncertainty envelope (`model_based_policy.py:50-52`).
   - Practically, the shape and amplitude of the flown MB are close to the E12 nominal optimum. This weakens the consequences for the results, but not the factual error in l. 718.

**DT reward 0.97 for MB (l. 861).** It is computed with the **final E12** coefficients by factual replay of the measured MB reference (`pp_paper.py:1225-1233` → `replay_rows`). R_∘ = 1 − 0.0323 = 0.968. Replaying the same reference with the manual (0.230, 3.136) model gives 0.964; BL gives 0.676 with E12 and 0.724 with the manual model.

**Corrected text.**
- l. 718: replace with "The flown π_MB was optimized with a single nominal model (no uncertainty ensemble) using the coefficients identified after the first two informative batches, (A,p)=(0.230,3.14); it was not re-optimized after the final identification, but all DT rewards reported here are recomputed with the final model."
- l. 720–726:
  > "J_MB = J_trk^{[2.20,4.00]} + 0.10 N_x⁻¹‖Δz_π/R‖₂² + 2.0 (N_x−2)⁻¹‖D²Δz_π/R‖₂² + 10⁵ Φ_clr, where the tracking term is evaluated over 2.20 ≤ x ≤ 4.00 m and N_x = 81 nodes spaced 25 mm (≈1.1R) over 2.00 ≤ x ≤ 4.00 m; Adam (learning rate 10⁻³) runs for 150 iterations from Δz = 0."
- l. 62, 185, 697 and 855 must also be reconciled with the provenance, or the MB policy must be re-optimized and re-flown.

---

### N8. Information phase. Grade A. Verdict: Disagrees

**Text.**
- l. 573: "twelve information-oriented policies … added sequentially … The first six … 0.5<z/R<6"
- l. 575: "…restricted to 0.5<z/R<1.5 for the remaining six policies … After every flight, the new record is appended … warm-started"
- l. 798: "…the upper bound is reduced to z/R=1.5 for the remaining six episodes"
- Eq. (e-optimal-design), l. 682–691: λ_min(F_{1:N}+F(π)), with "A separate novelty check may nevertheless select a slightly less informative candidate…"

**Data** (flown references are `EXP/CLEAN/EXP_INF_*_RG_input.txt` + z*; metadata are `EXP_INF_*_metadata.json`):

| Records | Run (design batch) | Condition | Design domain in code | Flown reference z_ref/R (1.70–4.00 m) |
|---|---|---|---|---|
| INF_01–03 | It1 (identification_iteration 001) | (1.5, 0.079) | "wide" 0.5–6R (`informative_policy.py:62-63,368-383`) | 0.60–5.73 |
| INF_04–06 | It2 (002) | (1.5, 0.079) | wide | 0.94–5.82 |
| INF_07–09 | It4 (004) | (1.5, 0.079) | "near_wall" **0.3–1.5R** (`:64-65,385-391`) | 0.34–1.46 (INF_09 min **0.34**) |
| INF_10 | It5_3 (005) | (1.5, 0.079) | near_wall | 0.35–1.31 |
| INF_11 | legacy campaign `GE_rg_a` (`…RG_It5`) | **(1, 0.091)**, v_x = 0.40 m/s | not produced by this code | **−0.99 to 2.90**, MB-like shape |
| INF_12 | legacy campaign `GE_rg_a` (`…RG_It4`) | **(1, 0.102)**, v_x = 0.45 m/s | not produced by this code | **−1.05 to 2.78** |

INF_11 and INF_12 are archived means only (`raw_repetitions_available: false`; RMS set to zero).

**Selection rule actually implemented** (`informative_policy.py:312-603`). Each design iteration produces **three** policies at once from 68 DT-screened candidates (64 scrambled Sobol points, seed 17, plus 4 structured shapes).
- **Candidate screening:** |v_z,ref| ≤ 0.5 m/s, |a_z,ref| ≤ 2 m/s², a finite rollout reaching 4.0 m, and lowest-rotor clearance ≥ **0.3R**. There is no actuator check in this screening.
- **Sensitivities:** of the predicted rotor-plane z/R at 80 points over 1.70–4.00 m. They are scaled by √diag Σ (the D_θ of the text ✓) and the Fisher matrix is **averaged over up to 5 sigma-point parameter samples** (`:148-162,420-434`).
- **Fisher normalization:** σ_e² = max(J_p, 10⁻⁸) and K = the number of evaluation points in 2.20–3.01 m. A second "exit" Fisher matrix covers 3.01–3.40 m.
- **Mission 1:** take the top 30 % of candidates by λ_min of the candidate's **own** F (each at least 50 % of the maximum), keep the half of that pool with the highest GE novelty, then take the maximum λ_min.
- **Mission 2:** the same gate on λ_min(F_mission1 + F_candidate).
- **Mission 3:** maximum post-exit response novelty (≥ 0.30R), subject to adaptive GE and exit-information gates.
- **No accumulated F_{1:N} of past experiments is ever formed.** Past data enter only through the novelty distance to all measured CLEAN trajectories (`:92-106,447-462`).

The identification used for design was updated **per batch**: every record of a batch carries the same identification_iteration. The per-flight E00–E12 sequence is a post-campaign replay (`adjoint_identification.py:1,41-45,70-83`).

**Corrected text.**
- l. 573:
  > "Starting from the baseline record, twelve informative records are added to the cumulative dataset. Ten were designed in this campaign in four batches: six over the broad range 0.5 ≤ z_ref/R ≤ 6 and four over the near-wall range 0.3 ≤ z_ref/R ≤ 1.5. Two further near-wall records come from an earlier campaign at z*/R = 1 and v_x*/v_h = 0.091 and 0.102, for which only averaged trajectories are available."
- l. 575, last sentence:
  > "In this post-campaign analysis the records are appended one at a time and the identification is warm-started from the preceding estimate; during the campaign the model was updated after each batch."
- l. 798: "…reduced to z/R=1.5 for the remaining records…"
- l. 807: "…while those using the near-wall domain 0.3 < z/R < 1.5 occupy the green region…"
- l. 682–691:
  > "Each design iteration selects three policies from 68 DT-screened candidates. The first maximizes λ_min of its own predicted Fisher matrix within a novelty-filtered pool, the second maximizes λ_min of the joint matrix with the first, and the third maximizes the novelty of the predicted post-exit response, subject to minimum information levels. Sensitivities are averaged over sigma-point samples of θ_p."

  Alternatively, keep Eq. (e-optimal-design) and say that it is the idealized criterion that the batch rule approximates.

---

### N9. DT provenance and parameters. Grade A. Verdict: Disagrees

| Text | Code | Verdict |
|---|---|---|
| l. 432: "Their parameters are inherited unchanged from Richardson et al.; they are neither reidentified nor independently revalidated" | m = 0.03242 kg is "measured on a precision scale" (`jDT/params.py:32`). The command-to-thrust gain FIRMWARE_THRUST_MAX_PER_MOTOR = 0.1148 N is "calibrated from the measured mass and the pre-obstacle steady-hover collective command"; the platform value 0.12 N "overestimates … by about 4.3 %" (`params.py:34-38`; `jDT/propulsion.py:15-18`). | **Disagrees (A)** |
| l. 503, 505: η_V = V_b/V_ref, Ω_cmd = η_V Ω_PWM, "retains the battery-voltage correction" | Never used (`simulator.py:331-333` is not called). Ω_i = [(c_i/65535)·0.1148/k_T]^{1/2} (`simulator.py:335-346`); firmware battery compensation is assumed (`propulsion.py:3-7`). | **Disagrees (A)** |
| τ_rpm = 0.020 s | `TAU_RPM = 0.02` (`params.py:115`), plus a rate limit of 2·10⁵ rpm/s (`:116`) | Agrees; add the rate limit (C) |
| Table I values | m, R, d, diag(I), k_T, k_Q, τ_rpm, V_ref agree with `params.py:32-33,62,99,102,114-115,169-173` | Agrees, but V_ref is unused, T_max is missing, products of inertia (up to 1.80·10⁻⁶) are omitted, and the caption is wrong for m |
| d = "motor-to-motor distance" | rotors at (±d/2, ±d/2) (`simulator.py:304-314`), so d = 0.065 m is the **adjacent**-motor spacing; the diagonal is 0.092 m. The comment at `params.py:97` ("opposite motors") is wrong. | Partly (C) |

**Corrected text.**
- l. 432:
  > "The rigid-body, inertia, rotor-coefficient, actuator, and controller parameters are inherited from Richardson et al.; the vehicle mass was measured, and the effective command-to-thrust gain T_max = 0.1148 N per motor was calibrated from the measured mass and the steady-hover collective command before the obstacle. No other parameter is reidentified."
- l. 503:
  > "With the firmware battery compensation enabled, each motor command is a voltage-independent thrust request. The DT therefore maps it linearly to rotor thrust, T_i = T_max c_i/65535, and sets the commanded speed Ω_i = (T_i/k_T)^{1/2}; the realized speed follows through a first-order lag with τ_rpm = 0.020 s and a rate limit of 2×10⁵ rpm/s."
- Delete l. 505 ("The nominal propulsion model retains…").
- Table I: retitle "DT parameters", replace V_ref by "T_max 0.1148 N (calibrated)", and mark m as measured.
- l. 500: "where d is the distance between adjacent motors".

---

### N10. Mission and setup. Grade B/C. Verdict: Partly

| Text | Code | Verdict |
|---|---|---|
| l. 372: "Each test begins at x=0 m, where the MAV … hovers for 10 s" | Takeoff 2 s, `go_to` A 2 s, then hold 10 s at **x = 0.20 m** (`run_next_experiment.py:128-130,305-308,1054-1070`) | Disagrees (C) |
| l. 372: speed reached "around x=1.0–1.2 m"; lands "around x=4.20 m" | Smoothstep from 0.05 m/s at x = 0.20 m to v at x = 1.10 m; decelerate 4.00 → 4.20 m; hold 0.5 s; land (`:951-1016,1086`) | Agrees |
| l. 374: two Lighthouse stations | not in code | Not determinable |
| l. 425: "the Crazyflie firmware records…" | Radio-streamed by cflib (`:567-725`). Periods: position 20 ms; velocity, attitude, rates, acceleration, V_bat, thrust, motors, rpm and geFF 50 ms; posCtl 100 ms. Rows are about 10 Hz. | Disagrees (B) |
| l. 427: "An outer position loop tracks x* and generates the corresponding velocity references" | Horizontal motion is velocity-commanded (`:1006-1008`); the DT uses `XY_VELOCITY_MODE` (`controller.py:184-187`). Position and velocity loops run at 100 Hz, attitude and rate loops at 500 Hz (`:179-239`). | Disagrees (B) |
| l. 561: v_h ≃ 4.42 m/s; 0.079, 0.045, 0.113 | v_h = 4.419 m/s; 0.35/v_h = 0.0792, 0.20/v_h = 0.0453, 0.50/v_h = 0.1131 | Agrees |

**Corrected text.**
- l. 372: "After takeoff, the MAV moves to x = 0.20 m, y = 0, and hovers there for 10 s at the prescribed altitude."
- l. 425: "Flight data are streamed by radio to the ground station: position at 50 Hz, the other channels at 20 Hz, and altitude-controller internals at 10 Hz; synchronized records are stored at about 10 Hz."
- l. 427: "During the crossing, the horizontal channels are velocity-commanded (v_x scheduled with measured x and v_y = −y, limited to 0.15 m/s), while the altitude is tracked by the cascaded position–velocity loop. The DT reproduces this mode and the firmware loop rates (100 Hz outer and 500 Hz inner)."

---

### N11. Basis functions, Sobol library and the a vectors. Grade B/C. Verdict: Partly

**Basis** (`expected_improvement_policy.py:84-89,204-213`):
- Gaussian centers 2.50, 2.95 and 3.30 m, i.e. **x/R = 34.8, 54.3, 69.6** in the shifted coordinate ✓ (l. 892).
- Widths σ = 0.25, 0.20 and 0.25 m (10.9R, 8.7R, 10.9R).
- Each Gaussian is multiplied by sin²[π(x−2.00)/2.00] and normalized to unit peak. The effective peaks are therefore at x/R = **40.4, 54.7, 66.4**, with FWHM of 21R, 19R and 22R.
- "First two above the obstacle" ✓: the obstacle spans 21.7–57.0. B is 2.7R upstream of the trailing edge.

**Sobol library.**
- Nominal EI: **2048 = 2¹¹** points, scrambled, seed 17, fixed by the seed (`:58,63,620-640`).
- The generalized search uses 2000 of 2048 points (seed 31; `generalized_policy.py:42,323-325`).
- Text "2000" (l. 730) → write 2048 (C).
- Fig. 12 shows 256 **unscreened** samples with |a_j| ≤ 0.8 (`pp_paper.py:94-95,1365-1371`) → caption "Representative unscreened Sobol samples (|a_j| ≤ 0.8)" (C).

**How the seven α policies were chosen.** No code in the repository selects them (not determinable). The a vectors suggest a hand-designed set rather than Sobol draws: ALPHA_04 ≈ 0.44 e_B and ALPHA_05 ≈ 0.36 e_C are near single-axis perturbations. ALPHA_07 (a_A > 0, a_C < 0) is the "apparently unfavorable" case cited at l. 892 ✓. EI_01 and EI_02 were flown in the same run (It17_4, It17_5) between ALPHA_03 and ALPHA_04.

**a vectors** (`_check/a_vectors.py`). Each is the projection of the flown reference minus the flown MB reference onto the basis, using exactly `policy_coordinates`. The projection residual is ≤ 0.021R for all ALPHA and EI policies, so they lie in the 3-D span. "Dist. to face" = min_j(1 − |a_j|).

| Case | a_A | a_B | a_C | Dist. to face | R_• (J370) | v1 (mean, n) |
|---|---|---|---|---|---|---|
| ALPHA_01 | −0.839 | +0.482 | +0.160 | 0.161 | 0.887 | −0.515 (3) |
| ALPHA_02 | −0.576 | +0.813 | +0.166 | 0.187 | 0.932 | −0.221 (4) |
| ALPHA_03 | −0.574 | +0.491 | −0.134 | 0.426 | 0.891 | −0.419 (4) |
| ALPHA_04 | −0.004 | +0.442 | +0.011 | 0.558 | 0.860 | −0.330 (5) |
| ALPHA_05 | +0.000 | −0.010 | +0.355 | 0.645 | 0.854 | −0.422 (3) |
| ALPHA_06 | −0.298 | +0.292 | −0.295 | 0.702 | 0.867 | −0.423 (4) |
| ALPHA_07 | +0.438 | +0.029 | −0.462 | 0.538 | 0.771 | −0.711 (4) |
| EI_01 | −0.842 | +0.706 | +0.167 | 0.158 | 0.918 | −0.370 (6) |
| EI_02 | −0.843 | +0.473 | −0.073 | 0.157 | 0.868 | −0.561 (4) |
| EI_03 | −0.839 | +0.504 | +0.175 | 0.161 | 0.894 | −0.471 (3) |
| EI_04 | −0.840 | +0.697 | +0.180 | 0.160 | 0.921 | −0.333 (4) |
| EI_05 | −0.644 | +0.712 | +0.176 | 0.288 | 0.947 | −0.191 (3) |
| EI_06 | −0.651 | +0.911 | +0.179 | 0.089 | 0.928 | −0.232 (3) |
| EI_07 | −0.448 | +0.717 | +0.175 | 0.283 | 0.866 | −0.400 (4) |
| EI_08 | −0.450 | +0.919 | +0.178 | 0.081 | 0.835 | −0.517 (3) |
| **EI_09 (π_EI★)** | **−0.664** | **+0.699** | **+0.200** | **0.301** | **0.952** | **−0.173 (3)** |
| EI_10 | −0.701 | +0.029 | +0.578 | 0.299 | 0.885 | −0.440 (4) |

**Answer to the "near a face?" question.**
- π_EI★ is interior. Its closest face is a_B = +1, at distance 0.30; a_A is 0.34 from −1. The search box is therefore not binding at the best policy.
- Four EI policies and ALPHA_01 cluster at a_A ≈ −0.84. EI_06 and EI_08 are within 0.09 of a_B = +1.
- EI_05 (−0.644, +0.712, +0.176) lies within 0.04 of EI★ and is statistically indistinguishable from it (v1 −0.191 ± 0.038 vs −0.173 ± 0.036; J370 0.947 vs 0.952). This supports l. 910: "Other high-reward evaluations approach a similar reference shape".

---

### N12. Other statements in Secs. II–IV and the Conclusions

| # | Text | Evidence | Verdict / grade | Proposed fix |
|---|---|---|---|---|
| 1 | l. 62, 158, 358, 563, 566, 730, 881 ("consecutive phases", "all information-oriented missions are performed first", "first interaction uses π_BL", "five consecutive blocks", "first record in the replay buffer", "first tested", "the two performance-oriented policies already available") | Run order from the legacy map (C15): BL, INT and MB were flown in It19, after ALPHA (It17) and EI_01–08 (It17–18). MB designs were made at It3 (between INF batches It2 and It4) and It6 (after It5). | Disagrees, **A** | Add: "For clarity, the campaign is presented by stage rather than in acquisition order: an interim model-based policy was designed between the informative batches, and the baseline, interpolation and model-based records used for reward transfer were flown after the first local exploration and EI policies; the sequential identification of Fig. 4 is a post-campaign replay in the order BL, INF_01–INF_12." |
| 2 | l. 942: "a new model-based policy is computed using the same frozen parameter vector θ̂_p identified at the end of the information phase" | MB_V020 and MB_V050 metadata: identification_iteration `iteration_006` (It23, It24); the current `transfer_calibration.py:394-423` would use E12 | Not supported, **B** (not determinable exactly) | Name the coefficients used, as in N7. |
| 3 | l. 973–975: "Two EI-guided physical evaluations…" | `generalized_policy.py:43,333-344,561-567` saves three distinct candidates per round; only candidate 2 of rounds It25 and It26 is in the data | Partly, **B** | "Each EI round proposed three distinct candidates, of which one was flown." |
| 4 | l. 986: "The physical experiments were constrained to z/R≥0.5" | The flight script refuses a DT-predicted lowest-rotor clearance below 0.5R (`run_next_experiment.py:247-252`), but the informative design admitted 0.3R (`informative_policy.py:68`). Flown references reach 0.34R (INF_09/10) and below the obstacle top (INF_11/12). The lowest measured mean clearance over the obstacle is 0.68R (INF_09). | Partly, **B** | "The DT-predicted lowest-rotor clearance above the obstacle was at least 0.5R for every flown policy, and the lowest measured mean clearance was 0.68R." Check the 0.5R predicted clearance for INF_07–10 first. |
| 5 | l. 782–784: rise "to approximately z/R=2.5", settles "around z/R=2", "undershoot down to approximately z/R=0.5", recovery "about 40R downstream" | EXP_BL: max 2.56 at x/R = 32; mean 1.96 over the second half of the obstacle; minimum **0.41** at x/R = 62.8; within 0.1R of 1.5 from x/R ≈ 91, i.e. **≈ 34R** after the trailing edge | Partly, **C** | "…down to approximately z/R=0.4…", "…about 35R downstream…" |
| 6 | l. 859: MB local minimum "comparable to that obtained under π_BL" | MB min 0.53 vs BL 0.41 | Agrees | — |
| 7 | l. 837: amplitude "almost twice the classical value" | 0.121/0.0625 = 1.94 | Agrees | — |
| 8 | l. 824: A and p "stabilize from approximately cumulative episode 11" | E10→E12: ΔA ≤ 0.004, Δp ≤ 0.033 | Agrees | — |
| 9 | l. 813, 828: uncertainty statements | 2σ_f/f, E06 → E12: 45 % → 15 % at z/R = 1; 9.9 % → 4.3 % at 1.5; 3.6 % → 2.6 % at 2. f_GE(1): 1.218 (E06) vs 1.121 (E12). | Agrees | Optionally quote these numbers. |
| 10 | Fig. 6 legend vs l. 813 | The PDF legend says "f_GE (only broad domain)" and "(broad + near wall domains)"; the text says f_GE(0.5<z/R<6) | **C** | Align. |
| 11 | l. 691: candidates "that violate state, reference-rate, acceleration, actuator, or clearance constraints are discarded" | Informative screening checks reference rate, acceleration, rollout completion and clearance (0.3R) only (`informative_policy.py:403-419`) | Partly, **C** | Drop "actuator", or state the 0.3R design threshold. |
| 12 | l. 672: σ_e² = max[J_p, 10⁻¹²] | Design code uses max(J_p, 10⁻⁸) (`informative_policy.py:317`); the post-hoc figure uses 10⁻¹² (`pp_paper.py:591`) | **C** | — |
| 13 | l. 980 (Conclusions): restricting to the near-wall domain "restored information gain as the former began to saturate" | Post-hoc diagnostic only; 33 % of the post-switch gain comes from the two legacy records (N2) | Partly, **B** | "…a retrospective evaluation with the final model shows that the near-wall records, including two archived ones, increased the weakest-direction information from 1.00 to 3.24…" |
| 14 | l. 984 (Conclusions) | Depends on the reward definition (N4) | **A** | See N4. |
| 15 | l. 505: "both physical and DT missions start with a fully charged battery" | The flight script logs V_bat before takeoff but performs no full-charge check; the DT ignores battery state (N9) | Not determinable, **C** | — |
| 16 | l. 60 vs l. 432 | "Richardson and Pretorius" vs "Richardson et al." | **C** | Use one form. |
| 17 | l. 910: "after only a few EI-guided evaluations, the search identifies π_EI★" | π_EI★ is EI_09, the ninth of ten EI policies; EI_01–08 were flown in two runs (It17, It18) | Partly, **C** | "…after nine EI-guided evaluations…" |
| 18 | l. 919: EI★ keeps a lower reference over the obstacle, rises earlier near the trailing edge, and markedly reduces the undershoot | a_A = −0.66 (lower over the obstacle), a_B = +0.70 (raise near the trailing edge). Post-edge minimum z/R: EI_09 1.11 vs MB 0.53 | Agrees | — |

---

## 3. Facts to give the author

1. **Repetitions per case** (`EXP/CLEAN/*_reward.json`):
   - BL 3, MB 3, EI_09 3; INT_01 4, INT_02 4.
   - ALPHA_01–07: 3, 4, 4, 5, 3, 4, 4.
   - EI_01–10: 6, 4, 3, 4, 3, 3, 4, 3, 3, 4.
   - BL_V020 2, MB_V020 2, EI_TR_V020 3.
   - BL_V050 3, MB_V050 2, EI_TR_V050 3, EI_01_V050 3, EI★_V050 4.
   - INF_01–10: 3 each. INF_11 and INF_12: 4 and 3, archived means only, RMS = 0.
   - **N_r = 3 for Figs. 2 and 14**, not 5.
2. **Reward used in Figs. 13–14 and in l. 861 and l. 910.**
   - Definition: R = 1 − J. J is the mean of [(z − z*)/R]² over the **repetition-averaged** trajectory samples with **2.20 ≤ x ≤ 3.70 m** (x/R 21.7–87.0), with N_R = 41–42 samples at the nominal condition. DT values come from factual replay with E12.
   - BL: R_∘ = 0.676, R_• = 0.544. MB: 0.968, 0.855. EI_09: 0.978, 0.952.
   - The stored per-repetition v1 means (`*_reward.json`) are BL −1.096 ± 0.124, MB −0.598 ± 0.096, EI_09 −0.173 ± 0.036 and EI_05 −0.191 ± 0.038.
3. **Generalization scores, both definitions** (S = 1 − J/J_BL):
   - The current Fig. 15 uses v1 averaged over repetitions:
     - (2.5, 0.045): MB 0.539, TR 0.679.
     - (1, 0.113): MB 0.680, TR 0.651, EI_01 0.365, EI★ 0.757.
     - Nominal: MB 0.455, EI★ 0.843.
   - With J370:
     - (2.5, 0.045): MB 0.622, TR 0.671.
     - (1, 0.113): MB 0.740, TR 0.772, EI_01 0.575, EI★ 0.827.
     - Nominal: MB 0.681, EI★ 0.894.
   - The text's 0.57 and 0.83 are J370 values; its "TR slightly worse at (1, 0.113)" holds only in v1.
4. **λ_min(F)**, from `pp_paper.py` and not normalized:
   - Designed curve: 0.030, 0.676, 0.779, 0.839, 0.894, 0.942, 1.000, 1.417, 1.530, 2.089, 2.509, 2.912, 3.242.
   - Repeated BL: 0.0298·N, i.e. 0.060 at N = 2 and 0.387 at N = 13.
   - INF_11 and INF_12 contribute 0.403 and 0.330.
5. **ρ_{A,p} for E00–E12:** 0.974, 0.783, 0.829, 0.848, 0.860, 0.857, 0.883, 0.860, 0.872, 0.847, 0.831, 0.822, 0.818.
6. **Coefficients.**
   - E06: A = 0.2176, p = 2.792.
   - E12: A = 0.1210, p = 1.980, with σ_A = 0.084 and σ_p = 1.09.
   - Cold start from (0, 0) on the full set: A = 0.1203, p = 1.970.
   - **The MB generator uses the manual (0.2304, 3.136).** Every RT flight's metadata say identification_iteration 006. Re-optimizing MB with either coefficient set gives the same shape (they differ by 0.04R RMS), about 10–15 % larger than the flown reference, so the DT cannot settle the provenance.
7. **a vectors** (units of R, box [−1, 1]³):
   - π_EI★ = EI_09: **(−0.664, +0.699, +0.200)**, 0.30 from the nearest face.
   - EI_05: (−0.644, +0.712, +0.176).
   - Full table in N11.
8. **Transfer rule.** a_j^tr = s_j a★_j, where s_j is the ratio of the local, basis-weighted RMS amplitudes of the new and nominal MB corrections:
   - s = (0.407, 0.527, 0.428) → a^tr = (−0.270, +0.368, +0.086) at (2.5, 0.045).
   - s = (1.845, 1.508, 1.604) → a^tr = (−1.225, +1.053, +0.321) at (1, 0.113), outside the nominal box.
   - EI★ at (1, 0.113): β = (−0.35, 0.20, 0.11), about 0.22 β_TR.
9. **Basis.**
   - Gaussian centers x/R = 34.8, 54.3, 69.6; σ = 10.9R, 8.7R, 10.9R.
   - Each is multiplied by a sin² envelope over 2.00–4.00 m and normalized to unit peak; effective peaks are at x/R = 40.4, 54.7, 66.4.
   - Sobol library: 2048 points (seed 17).
10. **MB optimizer.**
    - 81 nodes, 25 mm apart (1.09R), on 2.00–4.00 m.
    - Tracking window 2.20–4.00 m.
    - Weights 0.10, 2.0, 10⁵ applied to **mean** squares.
    - Adam: 150 iterations, learning rate 10⁻³.
    - |Δz| ≤ 3R; lowest-rotor clearance ≥ 0.5R while the CoM is above the obstacle.
11. **DT.**
    - m is measured.
    - T_max = 0.1148 N per motor is calibrated from hover (−4.3 % vs 0.12 N).
    - The battery correction is not used.
    - τ_rpm = 0.02 s, with a rate limit of 2·10⁵ rpm/s.
    - C_D = 0; RK4 at 2 ms.
    - d = 0.065 m is the adjacent-motor spacing.
12. **Setup.**
    - Hover at x = 0.20 m.
    - Speed ramp 0.20 → 1.10 m.
    - Logging is radio-streamed; rows are stored at about 10 Hz.
    - Horizontal motion is velocity-commanded.
    - v_h = 4.419 m/s; v/v_h = 0.0792, 0.0453, 0.1131 (and 0.091, 0.102 for INF_11/12).
