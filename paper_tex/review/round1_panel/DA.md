# Devil's Advocate Report

**Manuscript:** "Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect" (Grava and Mendez), file `main_lf.tex`, Round 1
**Seat:** Devil's Advocate (5-seat simulated panel). Written without reading the other seats' reports.
**Basis:** the full LaTeX source and the rendered result figures.

**Figure numbers** follow the compiled order: Fig. 4 informative trajectories, Fig. 5 sequential identification and λ_min, Fig. 6 identified f_GE and uncertainty, Fig. 7 baseline replay, Fig. 8 model-based policy, Fig. 11 surrogate after local exploration, Fig. 12 surrogate after EI, Fig. 13 BL/MB/EI* trajectories, Fig. 15 off-nominal trajectories, Fig. 16 normalized scores.

**Values marked "(read)"** were measured from the pixel positions of the plotted markers and curves. They are accurate to roughly ±0.01 in reward or score units. The authors should check them against their own data.

---

## 1. Strongest counter-argument

The paper's causal story has four steps:

1. Fisher-optimal flights identify a ground-effect law good enough for control.
2. That law yields a safe, effective model-based reference.
3. Reward transfer with Expected Improvement finds a better physical policy data-efficiently.
4. The workflow adapts across operating conditions.

Each step has a simpler explanation the evidence does not exclude.

**Step 1.** The evidence is a Fisher proxy computed with the final DT and compared with a duplicated baseline record, the weakest possible alternative. Fig. 7 shows the near-wall flights barely changed the replay, and no π_MB built from the Cheeseman–Bennett or broad-only DT was flown.

**Step 2.** "Safe" means screened by a DT known to mispredict the obstacle edges, while deployed references go down to about 0.5R and, off-nominal, below the obstacle surface.

**Step 3.** Where the search ran, the DT reward is nearly flat and almost uncorrelated with the physical reward (Spearman ≈ 0.24, read from Figs. 11–12), so the surrogate acts as a three-parameter GP on physical rewards. One hand-selected Sobol perturbation found most of the gain (0.855 → ≈0.93) before EI; EI added about 0.02, without replicate uncertainty, a re-flight of π_MB, or a drift control. The regularization penalties may simply have left π_MB under-actuated.

**Step 4.** Two EI flights at one condition, with text and figure values that disagree, cannot separate EI from a lucky perturbation.

Without ablations and replicate statistics, the data show that a feedforward reference correction helps, not that Reinforcement Twinning made it effective or data-efficient.

---

## 2. Issues

### DA-1. The nominal gain over π_MB is not shown to come from reward transfer or EI
- **Severity:** CRITICAL
- **Location:** Sec. III-D (Performance Phase): "The marked difference between these two increments is the improvement enabled by the learned GP discrepancy"
- **Challenge:**
  - **(a) Most of the gain came before EI.** In Fig. 11, before any EI step, one Sobol policy π_a,i already reached R_• ≈ 0.93 (read), compared with 0.855 for π_MB. π_EI* reached ≈0.95. So about 0.08 of the ≈0.10 improvement credited to the search came from one of seven quasi-random perturbations. The rule used to pick those seven is not fully specified: the text says the subset "deliberately includes both apparently unfavorable changes" and corrections that extend π_MB. EI then needed about six or seven more flights to add ≈0.02. Only one of those flights beat the pre-EI incumbent.
  - **(b) Random perturbations mostly beat π_MB.** Five of the seven Sobol policies plot above π_MB in Fig. 11. If π_MB were the well-informed reference the authors describe, this would be surprising. It is what one would expect if:
    - the single reward measurement of π_MB is low;
    - conditions drifted between the π_MB flights and the later flights; or
    - π_MB is under-actuated (see DA-2).
  - **(c) Measurement noise is not reported, and the winner is biased upward.** Rewards are treated as deterministic, with only a diagonal jitter of 10⁻⁸. They are computed from "cleaned" mean trajectories, but the cleaning rule and the number of runs per policy are not stated, and no per-run reward spread is reported. π_EI* is the maximum of about 14 local evaluations, so its reported reward is the selection statistic itself and is biased upward (winner's curse). No confirmation flights were made after the selection.
  - **(d) Possible drift is not controlled.** The flight order and dates are not reported, and π_BL and π_MB were not re-flown at the end. A slow drift over the campaign (propeller wear, Lighthouse recalibration, room airflow, battery batch, obstacle placement) would systematically favor policies flown later.
- **What would answer it:**
  1. Add a table listing every nominal-condition policy with: flight order and date, number of runs, runs excluded and why, per-run R_• (mean ± SD), and R_∘.
  2. Run post-selection confirmation flights: re-fly π_BL, π_MB, the best Sobol policy and π_EI* in a randomized, interleaved order, with at least five runs each. Report the pairwise differences with confidence intervals.
  3. State the rule used to select the seven Sobol policies.
  4. Rephrase the claim, for example: "Local exploration and EI together raised the physical reward from 0.855 to 0.952. Most of this gain was already obtained by the space-filling exploration, and EI added about 0.02, which is [within / outside] the run-to-run spread."

### DA-2. Alternative explanation: reward compression and MB regularization, not discrepancy learning
- **Severity:** MAJOR
- **Location:** Sec. III-D: "the DT alone regards the two policies as nearly equivalent, while the physical observations reveal a substantial performance gain"
- **Challenge:**
  - **(a) "Nearly equivalent" is an artifact of the reward scale.** Because R = 1 − J saturates near 1, small reward differences can hide large cost differences. From π_MB to π_EI*, the DT predicts that the tracking cost falls from J_∘ ≈ 0.032 to ≈ 0.022, a 31% reduction. The physical cost falls from 0.145 to 0.049, a 66% reduction. The DT got the direction right and predicted about half of the relative gain.
  - **(b) π_MB is not the DT-optimal tracking policy.** Its objective (Eq. (mb-objective)) adds an amplitude penalty (weight 0.10) and a curvature penalty (weight 2.0) that the reward does not contain. Sobol candidates in the same neighborhood reach R_∘ ≈ 0.985–0.988, above π_MB's 0.968 (Fig. 11). π_EI* is essentially a larger-amplitude π_MB (Fig. 13, read):
    - over the obstacle, its reference goes down to ≈0.5R, against ≈0.65R for π_MB;
    - at the trailing edge, it peaks at ≈3.1R, against ≈2.5R.

    A simpler explanation is therefore that the penalties shrank π_MB, and the physical data rewarded undoing that shrinkage. No GP discrepancy is needed for this. The statement that a "residual mismatch ... prevents the best DT policy from coinciding with the best physical policy" (Sec. III-C) conflates the regularized π_MB with the DT's best tracking policy.
  - **(c) Locally, the DT reward does not rank the policies.** Within the cluster where the search actually ran (R_∘ ≥ 0.93, n ≈ 12), DT and physical rewards are essentially uncorrelated: Spearman ≈ 0.24, read from Figs. 11–12. The "global affine relation" is fixed by π_BL and the two λ-policies, which are high-leverage points. The twelve information flights also have paired DT and physical rewards, but they are excluded from the fit. In practice, the surrogate is a 3-D GP on physical reward with an offset.
- **What would answer it:**
  1. Report J_∘ and J_• (or log J) alongside R.
  2. Fly two ablations physically:
     - extrapolations of π_MB with λ > 1 (for example λ = 1.25 and 1.5);
     - π_MB re-optimized with reduced amplitude and curvature weights.
  3. Report R_∘ for the unpenalized DT-optimal tracking policy.
  4. Show the information-phase reward pairs in the transfer plot, or justify leaving them out.
  5. Report γ₀ and γ₁ with standard errors, and how they change when π_BL is left out.
  6. Replace "regards the two policies as nearly equivalent" with "predicts a smaller relative cost reduction (31%) than observed (66%)".

### DA-3. The information phase is not shown to matter for control
- **Severity:** MAJOR
- **Location:** Sec. III-C: "Their consistent ordering supports the conclusion that the identified DT contains sufficient causal information to design a policy"
- **Challenge:**
  - **The test is too weak.** An ordering of two points (π_BL below π_MB) says little. Fig. 7 shows that even the Cheeseman–Bennett DT predicts the qualitative rise over the obstacle and the descent after it. A π_MB designed with that DT would therefore plausibly also beat π_BL.
  - **The near-wall stage barely changed the prediction.** Fig. 7 shows that the broad-only and final DTs give nearly identical baseline replays, even though A changed by about 45% between them.
  - **No π_MB from the classical or broad-only DT was computed or flown.** Without that comparison, the 0.54 → 0.85 improvement cannot be credited to the 12 information flights or to the near-wall stage. The authors also argue that the performance phase corrects residual model error anyway. A workflow of "Cheeseman–Bennett DT → π_MB → local BO" might therefore reach a similar final policy with twelve fewer flights.
- **What would answer it:**
  1. Compute π_MB from the Cheeseman–Bennett DT and from the broad-only DT, fly both (at least five runs each), and report R_•.
  2. At minimum, evaluate all three model-based policies in the final DT and discuss the differences.
  3. Replace "contains sufficient causal information to design a policy" with "is sufficient to rank π_MB above π_BL".

### DA-4. The Fisher evidence for designed experiments is self-referential, and the comparator is a straw man
- **Severity:** MAJOR
- **Location:** Sec. IV (Conclusions): "the cumulative smallest Fisher eigenvalue grew much faster than for repeated baseline experiments"
- **Challenge:**
  - **(a) The model under test grades itself.** Both curves in Fig. 5(b) are evaluated with the final DT, whose parameters were fitted to the designed flights, and with scaling taken from the final Σ_θ. E-optimal designs maximize λ_min by construction. Showing that they reach a higher λ_min than an alternative tests the optimizer, not how well the parameters were identified.
  - **(b) The comparator is the weakest possible one.** The counterfactual is the same baseline record duplicated N times, so F = N·F₁ and λ_min grows exactly linearly, by ≈0.030 per copy. No sequence could be less informative. Any second trajectory at a different clearance breaks the A–p degeneracy. That alone explains most of the jump at episode 2 (0.06 → 0.68).
  - **(c) The restored information gain came from a manual decision.** The near-wall domain (0.5 < z/R < 1.5) is a subset of the broad domain (0.5 < z/R < 6). Near-wall flights add about 0.37 to λ_min each, against about 0.06 for the last broad-domain flights. If so, an E-optimal search over the broad domain should already have chosen near-wall references. That it did not means the optimizer, the candidate generator, or the design-time model failed to find the informative region. The restored slope therefore came from a manual restriction of the domain, not from the criterion. The Conclusions nevertheless credit the design: "restricting the design ... restored information gain".
- **What would answer it:**
  1. Fly or replay fair comparators of equal size:
     - non-optimized references in the same domain (Sobol or random);
     - a simple constant-clearance sweep (for example z/R = 0.5, 0.75, 1, 1.5, 2, 3).
  2. Use an outcome that does not depend on the model under test. For example, report the leave-one-flight-out prediction error of DTs identified from the designed set and from the non-designed set.
  3. Report the λ_min gains predicted at design time next to the post-hoc values, and explain why near-wall candidates were not selected within the broad domain.
  4. Describe the domain restriction as an operator intervention.

### DA-5. Parameter "stabilization" may be dilution; drift suggests misspecification; identification stopped while information was rising fastest
- **Severity:** MAJOR
- **Location:** Sec. III-B (Information Phase): "stabilize from approximately cumulative episode 11 onward"
- **Challenge:**
  - **(a) Stability may just be dilution.** J_p weights each episode by 1/N. A new flight's influence on the minimizer therefore shrinks roughly as 1/N, whether or not the parameters are identifiable. Stability over three points (episodes 11–13) is weak evidence.
  - **(b) The parameter drift points to a misspecified model.** When the near-wall data were added, A moved from 0.218 to 0.121 and p from 2.79 to 1.98. The parameters of a correct model should not shift by about 45% because the mix of data changes. This pattern is typical of a misspecified law that fits whichever clearance band dominates the loss. A and p are therefore effective coefficients tied to the data mix. They do not support physical readings such as "the exponent returns close to two, but the identified amplitude is almost twice the classical value", particularly with ρ_A,p = 0.818.
  - **(c) Identification stopped while information was still rising fastest.** At episode 13, Fig. 5(b) shows λ_min growing at its steepest rate, about 0.35–0.4 per flight. The criterion in Sec. II-A ("further experiments yield only marginal changes") is therefore not met by the paper's own information metric.
  - **(d) Floor proximity is an unmodeled candidate.** Beyond the transients the paper names, the floor downstream of the trailing edge could matter:
    - the obstacle height is not reported;
    - χ_i = 0 outside the obstacle footprint, so the DT contains no floor effect;
    - EXP_INF,9 descends to z/R ≈ −1.3 (Fig. 4, read), i.e., 1.3R below the obstacle top.

    Part of the "trailing-edge transient" discrepancy may come from the floor.
- **What would answer it:**
  1. Report estimates from broad-only, near-wall-only and leave-one-flight-out fits, and the held-out prediction error.
  2. Define a numeric stopping rule in advance.
  3. Report the obstacle height and the minimum height above the floor in each flight.
  4. Tone down the physical interpretation of A and p.

### DA-6. "Well constrained" is contradicted by the paper's own uncertainty indicator when applied to the augmentation
- **Severity:** MAJOR. The sentence as written would not survive a careful referee, but it can be fixed by rewording.
- **Location:** Sec. IV: "the resulting ground-effect function was well constrained over the control-relevant clearance range"
- **Challenge:**
  - **The band is as large as the effect.** Fig. 6(b) gives 2σ_f/f ≈ 15% at z/R = 1 and ≈ 4% at z/R = 1.5 (read). At those clearances the augmentation f − 1 is ≈ 0.12 and ≈ 0.055. The 2σ band on the augmentation, which is the only part RT learns, is therefore about 135% and 80% of its value. At z/R = 1, the augmentation cannot be distinguished from zero at the 2σ level. The paper itself notes that the indicator refers to the total factor (Sec. III-B).
  - **The covariance is not calibrated.** Σ_θ = J_p·H⁻¹ is not a calibrated covariance. For this loss, the Gauss–Newton covariance with independent residuals would be about 2J_p·H⁻¹/(N·K̄); serial correlation would then inflate it by an unknown factor. Moreover, J_p is dominated by structural misfit, so the indicator measures the curvature of a misfit rather than parameter uncertainty.
  - **The plotted range is too narrow.** Fig. 6 starts at z/R = 1, while the information references go down to 0.5R and π_EI* commands about 0.5R.
- **What would answer it:**
  1. Report the augmentation and an interval for it at z/R = 0.5, 1 and 1.5, for example from a block bootstrap over flights or a profile likelihood.
  2. Extend Fig. 6 down to z/R = 0.5.
  3. Replace "well constrained" with a quantitative statement, for example "the augmentation at the nominal clearance is identified as 0.055 ± X".
  4. Revise the abstract's "constrains the dominant ground-effect response" in the same way.

### DA-7. "Safe" is certified only by a DT that is known to be wrong at the edges
- **Severity:** MAJOR
- **Location:** Abstract: "model-based optimization first provides a safe and computationally efficient policy"
- **Challenge:**
  - **The screening relies on one DT that is known to err at the edges.** Safety is checked with the single final DT, and the paper states that "no model-uncertainty ensemble is used". Sec. III-C shows that this DT predicted almost no trailing-edge undershoot for π_MB. In the experiment, π_MB reached a minimum of about 0.55R, comparable to π_BL.
  - **The deployed references depend on the predicted cushion.** They count on the predicted ground-effect lift and PID lag to keep the vehicle clear:
    - π_EI* commands about 0.5R above the obstacle surface (Fig. 13).
    - At (1, 0.113), the MB, transferred and EI references go below the obstacle surface, to about −0.5R and −0.9R (Fig. 15(b), read).

    If ground effect were weaker than identified (the augmentation is uncertain, see DA-6), or the vehicle's timing slower, the commanded set point would lie inside the obstacle.
  - **No physical safety statistic is reported.** The paper gives no minimum measured rotor clearance per flight, and no count of aborted flights or contacts.
- **What would answer it:**
  1. Replace "safe" with "screened in the DT against a 0.5R predicted rotor clearance".
  2. Report the measured minimum clearance for every flight, and any aborts or contacts.
  3. Screen robustly over parameter samples drawn from Σ_θ, or over both the broad-only and final DTs.
  4. State explicitly that some references penetrate the obstacle, and justify this, or add a floor constraint on the reference.

### DA-8. The data-efficiency claims are not benchmarked
- **Severity:** MAJOR
- **Location:** Sec. II-A (Performance phase): "Exploring the full policy space with a purely model-free strategy would require substantially more physical tests". The abstract makes related claims: "data-efficient policy refinement" and "a limited number of physical interactions".
- **Challenge:**
  - **The flight budget is never totaled.** At the nominal condition alone, the campaign used about 30 policies: π_BL, 12 information policies, π_MB, 2 λ-policies, 7 Sobol policies and about 7 EI policies. If each was flown five times, as Figs. 3 and 13 suggest, that is about 150 flights before the off-nominal tests.
  - **No comparator is run.** The advantage over model-free search is asserted, not measured. Three comparators are natural:
    - **(i)** The same GP-EI on **a** with γ₁ = 0 (no DT term), started from π_MB. This isolates the contribution of reward transfer and can be partly assessed offline by refitting the logged data.
    - **(ii)** GP-BO in the same 3-D basis, started from π_BL.
    - **(iii)** Iterative learning control. ILC is the standard way to refine a feedforward over repeated trajectories and is a natural competitor for a fixed-obstacle, repeated-crossing task. Neither ILC nor any comparator of this kind is discussed.
- **What would answer it:**
  1. Report the total number of flights and repetitions per stage, including discarded runs.
  2. Provide at least comparator (i), even offline: show which candidates EI would have chosen with γ₁ = 0 and how it would have ranked the flown policies.
  3. Ideally, add a physical ILC or BO baseline with an equal flight budget.
  4. Otherwise, replace "data-efficient" with a factual count, for example "with N flights in total".

### DA-9. The off-nominal evidence has inconsistent numbers and is too thin to support "adapt"
- **Severity:** MAJOR
- **Location:** Sec. III-E (Generalization): "Once this observation updates the condition-aware GP discrepancy, the second evaluation reaches a new condition-specific best"
- **Challenge:**
  - **(a) The text and Fig. 16 disagree.** For the two EI flights at (1, 0.113), the text reports S_• ≈ 0.57 and ≈ 0.83. The plotted markers sit at ≈ 0.37 and ≈ 0.76 (read).
  - **(b) Fig. 12 and Fig. 16 disagree at the nominal condition.** Applying Eq. (normalized-score) to Fig. 12 (R_•: π_BL ≈ 0.544, π_MB ≈ 0.855, π_EI* ≈ 0.951) gives S_• ≈ 0.68 for π_MB and ≈ 0.89 for π_EI*. Fig. 16 plots ≈ 0.46 and ≈ 0.85. No single baseline cost reconciles the two: the points imply J_BL ≈ 0.27 and ≈ 0.32 respectively. The DT coordinates do agree (≈ 0.90 and ≈ 0.93).
  - **(c) The DT ranking is inverted at (2.5, 0.045).** There, the DT scores π_MB well above the transferred policy (S_∘ ≈ 0.98 against ≈ 0.77), while the physical order is reversed (S_• ≈ 0.54 against ≈ 0.68). This contradicts "the DT reward supplies the global performance trend" at the very condition where transfer is said to have worked.
  - **(d) Too few flights to support "adapt".**
    - At one condition, EI produced one failure and then one success. That cannot be distinguished from a random local perturbation; at the nominal condition, five of seven random perturbations improved on π_MB (DA-1).
    - The kernel length scales for (z*/R, v_x*/v_h) are not given, so "condition-aware" is not specified.
    - Direct transfer was better at one condition and worse at the other, so "Transfer therefore provides an informed initialization" is not supported either.
- **What would answer it:**
  1. Reconcile the numbers, and state which runs and which processing feed Fig. 16.
  2. Give the condition-kernel hyperparameters and the number of off-nominal points in the GP.
  3. Report the replicate spread at the off-nominal conditions.
  4. Rephrase the abstract, for example: "At one off-nominal condition, one of two additional EI flights exceeded the local model-based policy."

### DA-10. "So what?": the reward and the policy class do not match the stated motivation
- **Severity:** MINOR. The tracking claims survive; the issue is how relevant they are to the application.
- **Location:** Sec. I (Introduction): "Predicting and compensating the interaction before the tracking error develops is therefore a safety requirement."
- **Challenge:** The Introduction motivates the work with safety margins in cluttered, GNSS-denied flight. Three things do not match that motivation:
  - **(a) The reward does not target the hazardous excursion.** The reward is a symmetric mean-squared error over the whole window. It penalizes the upward overshoot above the obstacle, which increases clearance there, as much as the downward excursion. The improvement of π_MB came "mainly from reducing the excursion over the obstacle", while its trailing-edge minimum stayed "comparable to that obtained under π_BL". The first, and largest, improvement therefore did not address the potentially hazardous excursion.
  - **(b) The policy is mission-specific.** It is a lookup table indexed by the x position measured by the Lighthouse system, built for one obstacle of known location and length, crossed at a known speed. It does not carry over to an unmapped geometry.
  - **(c) A simpler use of the identified law is not compared.** The thrust command could be compensated onboard as T_cmd/f_GE(z_i) using a height sensor. That would be mission-independent, and it is neither compared nor discussed.
- **What would answer it:**
  1. Report the minimum clearance and the peak downward deviation alongside R.
  2. Discuss, or test, an onboard inverse-f_GE feedforward.
  3. State what prior knowledge the method needs in the motivating scenario (obstacle map, absolute positioning).
  4. Either soften the safety framing in the Introduction or add a paragraph on how the benchmark relates to cluttered missions.

---

## 3. Observations that are not defects

- **Candid limitations.** The Conclusions explicitly limit the claims to the tested envelope. They acknowledge the static two-parameter law and the z/R ≥ 0.5 bound. They state that the off-nominal results do not establish a surrogate converged over the velocity–clearance domain. The manuscript avoids priority ("first") claims.
- **Honest reporting of a negative result.** The paper reports that direct transfer underperformed π_MB at (1, 0.113) instead of omitting it, which strengthens its credibility.
- **Uncertainty caveats.** The paper correctly states that the GP posterior standard deviation is interpolation uncertainty, not repeatability, and that the f_GE indicator is not a 95% interval. DA-1 and DA-6 ask the authors to act on these caveats, not to add them.
- **The baseline phenomenon is solid.** Under π_BL, the overshoot over the obstacle and the undershoot after it are much larger than the run-to-run band (Fig. 3). The physical problem is therefore real and repeatable.
- **The π_BL → π_MB improvement is large and visible.** It goes from 0.54 to 0.85 in reward, and the mean trajectories show it. That result does not depend on most of the objections above; only the ablation in DA-3 bears on it.
- **Practical engineering choices.**
  - Keeping the stock PID and deploying a spatially indexed reference is sound and makes the policy robust to timing differences between the DT and the flights.
  - Embedding the firmware controller logic in a differentiable closed-loop DT is a useful asset.
  - The "MPC" terminology is clarified explicitly as offline reference synthesis.
- **The identified exponent is plausible.** A final p ≈ 2 with a larger amplitude is physically reasonable for a multirotor and is consistent with the literature, which reports stronger ground effect than the single-rotor estimate. DA-5 concerns how firmly this can be interpreted, not whether it is plausible.
- **The sequential schedule is acknowledged as a simplification.** The paper presents the separation into an information phase and a performance phase as a simplification of the general interleaved RT loop. It is not a flaw as long as it is not sold as a demonstration of the general schedule.
