# Peer Reviewer 1: Methodology

**Seat:** Peer Reviewer 1, Methodology (system identification, optimal experiment design, Bayesian optimization with GP surrogates for experimental controller tuning)
**Manuscript:** "Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect" (A. Grava, M. A. Mendez), IEEE journal draft (`main_lf.tex`)
**Basis of review:** the manuscript text and the result figures supplied to the panel. I did not consult code. This report was written without seeing the other panel reports.
**Conventions:** Figures are numbered in order of appearance. Fig. 1 is the RT loop, Fig. 2 the setup, Fig. 3 the baseline, Fig. 4 the information policies, Fig. 5 sequential identification, Fig. 6 f_GE and its uncertainty, Fig. 7 the baseline replay, Fig. 8 π_MB, Fig. 9 the interpolation policies, Fig. 10 the Sobol library, Fig. 11 the surrogate after exploration, Fig. 12 the surrogate after EI, Fig. 13 BL/MB/EI★ trajectories, Fig. 14 video frames, Fig. 15 off-nominal trajectories, and Fig. 16 normalized scores. Values marked "read from Fig. X" were digitized from the supplied images (about ±0.01 in data units) and need confirmation by the authors.

---

## Summary

The manuscript reports an experimental Reinforcement Twinning campaign on a Crazyflie crossing a finite obstacle. A two-parameter static ground-effect law is identified by adjoint output-error fitting with sequential E-optimal experiment design. The frozen twin yields a regularized model-based reference governor, which is refined by Expected Improvement on an affine-plus-GP reward-transfer surrogate and tested at two off-nominal conditions. The staging is clear and the hardware work careful. However, the parameter-uncertainty scale, the information metric, and the treatment of experimental noise in the performance phase do not yet support the quantitative claims. Several definitions and plotted values are also inconsistent.

---

## Genuine strengths

1. **Identification is consistent with closed-loop operation.** The model parameters are fitted through a differentiable replica of the firmware cascade (PID states, mixer, actuator lag) under the recorded reference. This avoids the bias of open-loop regression on data collected under feedback, and the discrete-adjoint gradient is exact for the stated loss.
2. **The workflow can be traced.** The selector e_n, the separate indices n and m, the cumulative replay buffer, and the warm start with an Adam-moment reset are stated explicitly. So are the settings of the inner identification loop: learning rate, monitoring window, and three tolerances.
3. **The authors are candid about what their quantities are not.** They state that Σ_θ is not a calibrated confidence region, that the GP σ is not a measure of repeatability, that the static law cannot capture edge transients, and that generalization is a proof of concept.
4. **The policy class is sensible.** A spatial reference governor is robust to timing mismatch and leaves the onboard loop untouched. It also reduces the local search to three coefficients, a dimension a GP can handle on a small physical budget.
5. **The comparison of information content is good practice in principle.** The authors include a counterfactual (repeated baseline) and re-evaluate all episodes post hoc with a common final model, though see R1-5 and R1-6.
6. **Repeatability is shown at the trajectory level.** Key policies are flown five times and shown with ±RMS bands, and single-run video frames corroborate the ordering.
7. **A negative result is reported.** At one off-nominal condition the transferred correction underperforms π_MB, and the authors say so.

---

## Findings

### R1-1. The parameter-uncertainty indicator is mis-scaled; read at face value, it does not resolve the ground-effect augmentation

- **Severity:** Major
- **Location:** Sec. II-C, *Information phase*, Eq. (`eq:parameter-covariance`): "This matrix is used as a local curvature-based uncertainty approximation, not as a calibrated finite-sample confidence region." Also the Abstract and Fig. 6.
- **What is wrong:**
  (a) *Scale.* J_p (Eq. `eq:identification-loss`) is a per-sample average, and **H** is the Hessian of that average. Under the Gauss–Newton approximation, H ≈ (2/N) Σ_n K_n⁻¹ S_nᵀS_n. For independent residuals of variance σ_e² and equal K_n = K, the least-squares covariance is σ_e²(Σ_n S_nᵀS_n)⁻¹ = (2σ_e²/NK) H⁻¹. Eq. (`eq:parameter-covariance`) instead uses σ_e² H⁻¹, a variance NK/2 times larger. K_n is not reported. For K_n of 250–500 samples, the standard deviations are inflated by a factor of about 40–60. Because J_p and H are both averages, Σ_θ does not shrink as episodes accumulate. It changes only through the average curvature, and adding a weakly informative episode would *increase* it. The contraction from the broad-domain curve to the combined curve in Fig. 6(b) therefore reflects the mix of episodes, not accumulated evidence.
  (b) *Target quantity.* Fig. 6(b) reports 2σ_f/f_GE for the total factor. For the final model, read from Fig. 6(b), this is about 15 % at z/R = 1, so 2σ_f ≈ 0.17, while the augmentation is f_GE − 1 = A = 0.121. At z/R = 2 it is about 2.4 %, so 2σ_f ≈ 0.025, against an augmentation of 0.121·2^(−1.98) ≈ 0.031. Taken at face value, the ±2σ band of the augmentation includes zero at both clearances.
  (c) *Range.* Fig. 6 starts at z/R = 1, but the near-wall domain and the clearance constraint reach 0.5. The rotor clearances actually visited above the obstacle are not reported. In Fig. 4, for example, π_INF,9 flies at about 1.35–2.1 R over the obstacle while being commanded about 0.65–0.9 R (read from the figure). As a result, "the tested clearance range" is undefined.
- **Why it matters:** Three things rest on this matrix: the Abstract's claim that the workflow "constrains the dominant ground-effect response over the tested clearance range," the use of the uncertainty contraction as a stopping argument (Sec. III-B), and the D_θ scaling of the Fisher proxy (R1-6). Either the indicator is far too conservative, in which case its absolute values carry no meaning, or the augmentation is not resolved, in which case the claim fails. The reader cannot tell which.
- **Proposed fix:**
  1. Replace Eq. (`eq:parameter-covariance`) with an estimator whose scale can be defended and that respects residual correlation within an episode. One option is an episode-clustered sandwich covariance Σ_θ = H⁻¹(Σ_n g_n g_nᵀ)H⁻¹, where g_n is the gradient of episode n's contribution at θ̂_p, with a small-sample correction for 13 clusters. Cross-check it against a leave-one-episode-out jackknife (13 warm-started refits) and a profile-likelihood contour of J_p on an (A, p) grid.
  2. Report the uncertainty of the *augmentation* f_GE − 1, in absolute and relative terms, over 0.5 ≤ z/R ≤ 3, and extend Fig. 6 down to z/R = 0.5.
  3. Overlay on Fig. 6 a histogram of the rotor clearances actually visited above the obstacle, for the broad and near-wall episodes, weighted by the sensitivity of e_z to θ_p. Define "the tested clearance range" from this histogram.
  4. Revise the Abstract to match. Suggested wording: "…show that the identified correction reproduces the dominant baseline response for clearances between z/R = a and b, with an uncertainty in the thrust augmentation of c % at z/R = d."

### R1-2. The performance phase treats noisy rewards as exact, reports a winner's-curse estimate, and credits EI with gains that came mostly from the space-filling exploration

- **Severity:** Major
- **Location:** Sec. II-C, *Performance phase*: "The rewards are computed from the cleaned mean trajectories and are treated as deterministic campaign observations." Also Sec. III-D: "after only a few EI-guided evaluations."
- **What is wrong:**
  (a) Eq. (`eq:rt-surrogate`) includes ε ~ N(0, σ_ε²) for "experimental and reward-evaluation noise," but the implementation sets σ_ε ≈ 0 (jitter 10⁻⁸). The GP therefore interpolates noisy data, and the EI incumbent R_•⁺ is the maximum of noisy observations.
  (b) π_EI★ is the argmax of about 17 physical rewards: 2 interpolation, 7 Sobol, and about 8 EI policies, as counted in Fig. 12. Its reported value of 0.952 is the same measurement used to select it, so it is biased upward (the winner's curse). No independent confirmation flights are reported.
  (c) *Attribution.* Fig. 11 shows that one Sobol policy π_a,i had already reached R_• ≈ 0.93 (R_∘ ≈ 0.954) before any EI step (read from the figure). The EI evaluations therefore raised the best observed reward from about 0.93 to 0.952, a gain of about 0.02. The 0.855 → 0.952 gain quoted in Sec. III-D is the joint result of the Sobol exploration and EI.
  (d) *Noise scale.* Suppose the run-to-run deviation is about 0.05 R and coherent along x (the BL band in Fig. 3), and the tracking RMS for π_EI★ is about 0.22 R (R_• = 0.952). The per-run reward SD could then reach 2 × 0.22 × 0.05 ≈ 0.02. The 0.02 difference between the best Sobol policy and the best EI policy is therefore not clearly resolved.
  (e) Eq. (`eq:rt-physical-objective`) defines the objective as E[R_•], but the reward is computed on the mean trajectory. By Jensen's inequality, R(z̄) ≥ the mean of the per-run rewards, with a difference equal to the spatial mean of RMS²(x)/R². The gap is small for π_BL but varies by policy.
  (f) The number of EI evaluations is never stated.
- **Why it matters:** The headline result (R_• from 0.855 to 0.952) and the claimed effectiveness of EI rest on single values chosen by selection, with no noise model and no confirmation. Data efficiency cannot be judged without the number of iterations.
- **Proposed fix:**
  1. Compute the reward *per run*, and for every policy report n_runs, the mean, and the SD (see the table in R1-11).
  2. Refit the surrogate with fixed heteroscedastic noise σ_i² = s_i²/n_i (or an ML-II homoscedastic σ_ε²). Use either noisy EI or EI with a posterior-mean incumbent, μ⁺ = max_i μ_•(a_i), and show whether the EI sequence would have changed.
  3. Fly a confirmation block: at least five fresh, interleaved (A–B–A–B) flights each of π_MB, π_EI★, and the best Sobol policy, under the same battery protocol. Report the differences in mean reward with 95 % confidence intervals (Welch t-test or bootstrap).
  4. State the number and order of the EI evaluations, and plot the best-so-far reward against evaluation index with the Sobol and EI phases marked.
  5. Reword Sec. III-D, for example: "The space-filling exploration raised the best observed physical reward from 0.855 (π_MB) to about 0.93, and N subsequent EI evaluations raised it to 0.952 (π_EI★). Confirmation flights give R_• = x ± y for π_EI★ versus u ± v for π_MB."

### R1-3. The normalized scores in Fig. 16 cannot be reproduced from the reported rewards, and the text contradicts the figure

- **Severity:** Major
- **Location:** Sec. III-E, Eq. (`eq:normalized-score`) and Fig. 16: "the second evaluation reaches a new condition-specific best of approximately S_• = 0.83, marked by the purple star"
- **What is wrong:**
  (a) Apply Eq. (`eq:normalized-score`) to the nominal rewards of Secs. III-C/D, which are R_• = 0.545, 0.855, 0.952 and R_∘ = 0.676, 0.968, 0.978 for π_BL, π_MB, π_EI★. This gives S_∘ ≈ 0.90 and 0.93, and S_• ≈ 0.68 and 0.89, for π_MB and π_EI★. In Fig. 16 the black (nominal) square and star sit at S_∘ ≈ 0.91 and 0.93, which agrees. Their S_• values, however, are about 0.45 and 0.84, which does not. The two interpolation policies show the same pattern: the expected S_• is about 0.40 and 0.53, but the plotted values are about 0.31 and 0.35. No single baseline cost reconciles these values. (All Fig. 16 values are read from the figure.)
  (b) The text places the two EI evaluations at (1, 0.113) at S_• ≈ 0.57 ("small purple marker") and 0.83 ("purple star"). The purple markers in Fig. 16 are at about 0.36 and 0.76, while *black* markers sit at about 0.57 and 0.84.
  (c) At (2.5, 0.045), Sec. III-E describes the transferred policy's gain over π_MB as "further, albeit modest" and "slightly." In Fig. 16, however, the orange diamond is at S_• ≈ 0.68 and the orange square at about 0.54, a gain of roughly 0.14. The DT ordering is also reversed there (S_∘ ≈ 0.77 versus 0.98), and the text does not discuss this.
  (d) S is a ratio with a noisy denominator J_BL, and "exceeds the corresponding model-based policy" rests on the better of two evaluations.
- **Why it matters:** The generalization conclusion is that transfer helps at one condition, hurts at the other, and two EI steps recover. That conclusion depends on orderings that differ by 0.03–0.15, and the plotted values cannot be reconciled with either the reported rewards or the text.
- **Proposed fix:**
  1. Add a table giving R_∘, R_•, S_∘, and S_• for every policy at all three conditions, with per-run SD and n. Regenerate Fig. 16 from this table, and correct the values and color references in the text.
  2. Propagate the uncertainty of J_BL into S, by the delta method or a per-run bootstrap.
  3. Report the GP lengthscales in the condition dimensions (z*/R, v_x*/v_h), and explain how they were set with only three conditions.
  4. Reword, for example: "One of two EI evaluations at (1, 0.113) exceeded π_MB by ΔS_• = x ± y (n runs each)."

### R1-4. The reward-transfer surrogate is fitted in two stages, underreports its uncertainty, and is never shown to beat a plain GP

- **Severity:** Major
- **Location:** Sec. II-C, *Performance phase*: "The affine component of the reward-transfer surrogate is fitted by ordinary least squares to the paired DT and physical rewards." Also Eqs. (`eq:rt-surrogate`) and (`eq:rt-surrogate-mean`).
- **What is wrong:**
  (a) *Two-stage fit.* (γ₀, γ₁) are fitted by OLS, and a zero-mean GP is then fitted to the residuals. σ_• = σ_δ therefore omits the uncertainty of (γ₀, γ₁). That fit is dominated by the high-leverage π_BL and π_λ points, which lie far from the search region.
  (b) *Unreported quantities.* The paper does not report γ₀ and γ₁ with their standard errors, the kernel lengthscales (fixed at "0.30R" or learned?), the final signal variance, or how the hyperparameters were estimated. Read from Fig. 12, the affine line implies γ₁ ≈ 1.2 and γ₀ ≈ −0.26.
  (c) *Added value of the DT term.* Among the 13 tested policies with R_∘ ≥ 0.94 (read from Fig. 12), the rank correlation between R_∘ and R_• is weak (Spearman ≈ 0.2). In the search region, the surrogate therefore behaves much like a GP on **a** with an offset, which is close to model-free local Bayesian optimization started at π_MB.
  (d) The Abstract, Sec. II-A, and Sec. IV claim data efficiency relative to model-free search, but no comparison is made.
- **Why it matters:** The surrogate is the paper's methodological contribution in the performance phase. Without an ablation, its effect cannot be separated from that of the π_MB initialization combined with a standard GP.
- **Proposed fix:**
  1. Fit a single-stage GP with an explicit linear basis h(ξ) = [1, R_∘(ξ)] and a Gaussian prior on (γ₀, γ₁) (Rasmussen and Williams 2006, Sec. 2.7), so that the predictive variance includes the affine uncertainty. Report all hyperparameters at each EI step.
  2. Run leave-one-out cross-validation over all performance-phase policies for three predictors: affine only, a GP on **a** with constant mean, and the full reward-transfer surrogate. Report the RMSE, the mean standardized log loss, Kendall's τ, and the distribution of standardized residuals.
  3. Either soften the efficiency wording (for example, "required N physical evaluations beyond π_MB" instead of "data-efficient"), or add an in-silico benchmark. In the benchmark, treat a perturbed twin as the "truth," for example the final DT with a first-order lag on the ground-effect force to mimic edge transients. Compare EI with the reward-transfer surrogate against EI with a plain GP, both starting from π_MB, over at least 20 seeds and equal budgets, and report median and interquartile best-so-far curves.

### R1-5. The E-optimal design was not actually optimized over the broad domain, and the comparison against repeated baselines is too easy to win

- **Severity:** Major
- **Location:** Sec. II-C, *Information phase*: "The admissible design domain is therefore restricted to 0.5<z/R<1.5 for the remaining six policies, defining the near-wall domain." Also Fig. 5(b) and Eq. (`eq:e-optimal-design`).
- **What is wrong:**
  (a) The near-wall domain (0.5 < z/R < 1.5) is a *subset* of the broad domain (0.5 < z/R < 6). If Eq. (`eq:e-optimal-design`) had been maximized over the broad domain, near-wall references would have been admissible at steps 3–7. Yet the gain in λ_min per episode was about 0.05 at steps 3–7 and about 0.2–0.6 after the restriction (Fig. 5b). One of three things must have happened: the candidate generator or optimizer did not find the maximizer; the novelty override was active; or the in-campaign DT (A = 0.218, p = 2.79) predicted much lower near-wall sensitivity than the final DT used for Fig. 5(b). The physical explanation offered ("at larger clearances, f_GE approaches unity…") explains why high-clearance candidates are uninformative. It does not explain why they were chosen.
  (b) Design details are missing: the number of candidates per step, how they were generated (random, Sobol, or gradient ascent), the number of nodes, the rate and acceleration limits, and whether the novelty check was used, and at which episodes.
  (c) In Fig. 4, the π_INF,9 reference dips to about 0.35 R near x/R ≈ 18 (read from the figure), below the stated lower bound of 0.5. The authors should state whether the bounds apply only above the obstacle.
  (d) The repeated-baseline counterfactual cannot add a new direction by construction. The ">10×" comparison therefore does not isolate the value of optimization over generic variation of the reference.
- **Why it matters:** The contribution of the information phase is that designed experiments outperform the alternatives. That requires a fair comparator and evidence that the criterion was actually maximized.
- **Proposed fix:**
  1. For every step, tabulate the number of candidates, the λ_min gain predicted for the selected policy with the in-campaign DT, the gain realized post hoc with the final DT, and whether novelty overrode E-optimality.
  2. Using the in-campaign θ̂_p at steps 3–7, compute retrospectively the predicted gain of the best near-wall candidate.
  3. Add an in-silico comparator, which needs no flights. Draw at least 100 random admissible sequences from the same candidate generator, under two schedules (broad then near-wall, and near-wall only). Compute λ_min(F_1:N) for each with the final DT and the same scaling, and report the percentile of the designed sequence.
  4. Make the manual step explicit, for example: "After episode 7, we manually restricted the reference domain to 0.5 < z/R < 1.5 because …"

### R1-6. The Fisher-information proxy is defined inconsistently and its scale is partly circular

- **Severity:** Moderate
- **Location:** Eq. (`eq:cumulative-fisher`) versus Eq. (`eq:rt-fisher-update`): "where K_n prevents a longer episode from appearing more informative solely because it contains more samples."
- **What is wrong:**
  (a) Two different objects are both called the Fisher information. Eq. (`eq:rt-fisher-update`) is F_n + SᵀΣ_ν⁻¹S, unscaled and without a 1/K_n factor. Eq. (`eq:cumulative-fisher`) is scaled by D_θ and divided by K_n σ_e².
  (b) Under the stated independent, homoscedastic residual approximation, information adds across samples, so dividing by K_n is inconsistent with that approximation. If the intent is to discount autocorrelated residuals, the right quantity is an effective sample size K_eff,n.
  (c) σ_e² cancels. D_θ² ∝ σ_e² (Eq. `eq:parameter-covariance`) and F ∝ 1/σ_e², so the "common normalized residual variance" has no effect.
  (d) *Self-normalization.* With D_θ taken from Σ_θ of the same data, and with a Gauss–Newton H, D_θ F_1:N D_θ = (N/2) P⁻¹, where P is the parameter correlation matrix. At the final step, therefore, λ_min = N/[2(1 + |ρ|)]. For N = 13 and ρ = 0.818 this gives about 3.58, close to the reported 3.242; the difference is plausibly due to the full Hessian and the eigenvalue floor. The endpoint of the designed curve in Fig. 5(b) is thus largely fixed by the episode count and the final correlation, rather than being an independent measure.
  (e) The value of exactly 1.000 after the sixth policy suggests a normalization that is not stated.
- **Why it matters:** Fig. 5(b) is the main quantitative evidence for the information phase.
- **Proposed fix:** Define a single information matrix, F_1:N = Σ_n (K_eff,n/K_n) S_nᵀS_n/σ_ν². Estimate σ_ν² from the five repeated baseline flights and K_eff,n from the residual autocorrelation. For post hoc comparisons, scale with fixed a priori parameter scales D₀ = diag(1/16, 2), the Cheeseman–Bennett values, instead of the data-dependent D_θ. Also report the D-optimal criterion log det F, which is invariant to rescaling each parameter. State any normalization explicitly.

### R1-7. π_MB is not the maximizer of the DT reward, so the claim that "the DT alone regards the two policies as nearly equivalent" misattributes the gain

- **Severity:** Moderate
- **Location:** Eq. (`eq:rt-mb-optimum`) versus Eq. (`eq:mb-objective`). Sec. III-D: "the DT alone regards the two policies as nearly equivalent, while the physical observations reveal a substantial performance gain."
- **What is wrong:**
  (a) Eq. (`eq:rt-mb-optimum`) defines θ_π,MB as the argmax of R_∘ over the safe set, but Eq. (`eq:mb-objective`) adds amplitude (0.10) and curvature (2.0) penalties. π_MB therefore does not maximize the DT reward: some tested Sobol and EI policies reach R_∘ ≈ 0.983–0.988 (Figs. 11–12), versus 0.968 for π_MB.
  (b) The DT ranks π_EI★ above π_MB (0.978 versus 0.968). The reference of π_EI★ also has a larger amplitude than that of π_MB (read from Fig. 13): it peaks near 3.1 R rather than 2.5 R at x/R ≈ 62, and dips to about 0.45 R rather than 0.65 R over the obstacle. Part of the physical gain may therefore come from relaxing the regularization rather than from learning the discrepancy.
  (c) Conversely, the paper omits its strongest evidence for the GP's role. The tested policies the DT ranks highest (R_∘ ≈ 0.983–0.988) achieved only R_• ≈ 0.886–0.920, below π_EI★.
- **Why it matters:** The claim "the improvement enabled by the learned GP discrepancy" needs a comparison against DT-only selection.
- **Proposed fix:**
  1. Rewrite Eq. (`eq:rt-mb-optimum`) as θ_π,MB = argmin over Θ_π,safe of J_MB(θ_π; θ̂_p), and state that R_∘(π_MB) is not the maximum.
  2. Report the policy a DT-greedy search would choose from the same 2000-candidate safe library (the argmax of R_∘), and its R_• if flown, or at least the measured R_• of the tested policies with the highest R_∘. Also report the penalty terms of π_MB and π_EI★.
  3. Replace the sentence with, for example: "The DT ranks π_EI★ only marginally above π_MB (0.978 versus 0.968) and below several tested policies (R_∘ up to 0.988) whose physical rewards were lower (R_• ≤ 0.92); the physical rewards, through the GP discrepancy, reorder these candidates."

### R1-8. The identifiability argument and stopping rule depend on the parameterization, the law is likely misspecified, and A and p are confounded with nominal-model error

- **Severity:** Moderate
- **Location:** Sec. III-B: "Additional data can shrink the set of plausible coefficient pairs without removing this intrinsic elongated direction completely." Also Sec. II-B (nominal DT) and Sec. II-C (stopping rule).
- **What is wrong:**
  (a) For f_GE − 1 = A(R/z)^p, keeping f fixed at clearance z requires dA/A = ln(z/R) dp. The A–p correlation is therefore set by where the data lie relative to the anchor z = R. Reparameterizing as f_GE − 1 = A_c (z_c/z)^p, with z_c the sensitivity-weighted mean clearance of the data, largely removes the correlation without changing the fit. The elongation is not intrinsic. ρ (0.974 → 0.883 → 0.818) is not an identifiability measure that is invariant to parameterization, so it should not be used to decide when to stop.
  (b) Adding the near-wall data moved the estimates from (0.218, 2.79) to (0.121, 1.98). The statement that they "stabilize from approximately cumulative episode 11 onward" rests on three points. A shift of this size is what one would expect if the static power law fits different clearance ranges with different effective parameters, which the unmodeled edge transients make likely.
  (c) The outer stopping rule has no thresholds; it relies on terms such as "appreciably" and "meaningful."
  (d) The only replay shown (Fig. 7) is the baseline flight, which is part of the training set. No held-out validation is presented.
  (e) *Confounding.* The nominal parameters are "neither reidentified nor independently revalidated," so any bias outside ground effect (in k_T, the mass with deck and battery, estimator delay, or voltage sag) is absorbed into A and p. The paper also says that both missions "start with a fully charged battery and last only a few seconds." In fact, a 10 s hover followed by about 4.2 m at no more than 0.35 m/s takes at least 20 s, and V_b is logged but not shown.
- **Why it matters:** The coefficients are given a physical interpretation ("the identified amplitude is almost twice the classical value"). That interpretation requires A and p to capture ground effect rather than bias in the nominal model.
- **Proposed fix:**
  1. Reparameterize, or report ρ in both parameterizations, and remove ρ from the stopping rule.
  2. Fit the broad-only and near-wall-only subsets separately and overlay their uncertainty regions (from R1-1). If they are inconsistent, state that (A, p) are effective, range-weighted parameters.
  3. Show residuals by streamwise segment: pre-obstacle, leading edge, plateau, trailing edge, and recovery.
  4. Use the roughly 20 performance-phase flights, none of which were used for identification, as held-out validation. Report the replay error of the Cheeseman–Bennett, broad-only, and final models on them.
  5. Validate the nominal DT out of ground effect, using the residual on the pre-obstacle segment (0 ≤ x/R ≤ 20) and, ideally, one flight without the obstacle. Alternatively, add a free thrust-scale factor outside ground effect and show that A and p are robust to it. Plot V_b over the region of interest.
  6. Replace the qualitative stopping rule with one tied to the control goal, for example: "We stop when the change in R_∘(π_MB), recomputed with the latest θ̂_p, is below the run-to-run SD of R_• for two consecutive episodes."

### R1-9. The policy parameterization and the GP inputs are not defined consistently

- **Severity:** Moderate
- **Location:** Sec. II-C, *Performance phase*, Eq. (`eq:rt-policy`): "a correction learned where the model-based action is large is reduced automatically when the local MB solution requires little intervention"
- **What is wrong:**
  (a) As written, Eq. (`eq:rt-policy`) is additive and does not depend on the condition: Δz_π = Δz_MB + R bᵀa. A transferred **a** therefore adds the *same* absolute offset at every condition, which is exactly what the text says does not happen ("rather than being transferred as a fixed altitude offset"). Fig. 15 shows that π_EI^tr − π_MB differs between conditions: near x/R ≈ 30 it is about −0.1 R at (2.5, 0.045) but about −0.4 to −0.5 R at (1, 0.113) (read from the figure). Unless clipping by the bounds explains the difference, the implemented parameterization is therefore not Eq. (`eq:rt-policy`).
  (b) **b**(x) is not defined: the Gaussian widths and normalization are missing, and "centered on the model-based reference" is ambiguous.
  (c) The GP input is **a**, but π_BL and π_λ have no **a**-coordinates. If they are assigned **a** = 0, they coincide with π_MB but carry different discrepancies, which a nearly interpolating GP (jitter 10⁻⁸) cannot fit. If they are excluded from the GP, the paper should say so.
  (d) "Each coordinate scaled by 0.30R" is not meaningful, because **a** is dimensionless (R appears explicitly in Eq. `eq:rt-policy`).
  (e) The selection of 7 of the 2000 Sobol candidates is described only qualitatively.
  (f) The paper does not say whether EI is maximized over the 2000-point library, which seems necessary because R_∘ must be evaluated, or continuously.
- **Why it matters:** A reader cannot reimplement the search, and the transfer claim in Sec. III-E rests on a property the stated equation does not have.
- **Proposed fix:** Write the implemented form explicitly. If it is multiplicative: Δz_π(x) = Δz_MB(x)[1 + bᵀ(x)a]. If a scale depends on the condition: Δz_π(x) = Δz_MB(x) + s(χ) R bᵀ(x)a, with s defined. Give b_j(x) = exp[−(x − c_j)²/(2w²)] with numerical c_j and w. List the GP training inputs, and give the lengthscale in units of **a**, stating whether it is fixed or learned. State the subset-selection rule, for example greedy maximin distance in **a** among safe candidates, stratified by R_∘ tercile, and state the domain over which EI is maximized.

### R1-10. Safety screening uses a twin known to be optimistic, with no margin for model error

- **Severity:** Moderate
- **Location:** Sec. II-C, *Model-based policy*: "while the predicted lowest rotor must retain a clearance of at least 0.5R from the local surface."
- **What is wrong:** Admissibility (Θ_ι,safe, Θ_π,safe, 𝒜_safe) is checked only against the nominal DT at θ̂_p, with no margin for model error or run-to-run dispersion. The DT is demonstrably optimistic where clearance is smallest. For π_MB it predicts that the trailing-edge undershoot will be almost suppressed, whereas the measured minimum is about 0.55 R above obstacle level (Figs. 8 and 13). At (1, 0.113), the references descend to about −0.5 R to −0.85 R, below the top of the obstacle (Fig. 15b). The margin to contact then depends entirely on the ground-effect lift predicted by the DT. The obstacle height, and hence the clearance to the floor downstream, is not given.
- **Why it matters:** The paper repeatedly says policies are "safe," "screened," and kept within a "safety envelope." As the method stands, these words mean only "admissible under the nominal model."
- **Proposed fix:**
  1. For each flown policy, report the DT-predicted and measured minimum clearance of the lowest rotor above the obstacle, and the minimum height above the floor downstream.
  2. Calibrate an empirical margin, for example the largest observed under-prediction plus three times the run-to-run RMS. Alternatively, screen robustly over an ensemble of (A, p) values, such as the jackknife ensemble from R1-1.
  3. State the obstacle height.
  4. Where no margin is applied, replace "safe" with "admissible under the nominal DT screen."

### R1-11. The campaign is not reported in enough detail to be reproduced or to check the data-efficiency claim

- **Severity:** Moderate
- **Location:** Sec. III-D: "Whereas the curves in Fig. 13 are obtained by averaging five repetitions of each case." Also Sec. II-B: "the adjoint optimization minimizes the normalized vertical-position discrepancy over the obstacle region."
- **What is wrong:**
  (a) Repetitions are stated only for π_BL (five) and for π_BL, π_MB, and π_EI★ in Fig. 13. They are not stated for π_INF, π_λ, π_a, π_EI,i, or the off-nominal policies. The total number of flights, and hence the "limited number of physical interactions," is not quantified.
  (b) "Cleaned" is not defined: the paper does not say what filtering, rejection of outliers or tracking losses, or alignment it involves.
  (c) The paper does not say how runs are aligned and resampled in x (grid spacing, interpolation), or whether identification uses individual runs or their mean, which changes K_n and the noise level.
  (d) The identification window is inconsistent. Sec. II-B says "over the obstacle region," while Sec. II-C refers to K_n positions per episode. Ω_ℛ and N_ℛ in Eq. (`eq:reward`) are not defined explicitly.
  (e) Several settings are missing: the logging rate; the Lighthouse estimator; the bounds Θ in Π_Θ; the MB optimizer settings (learning rate, iterations, initialization, endpoint projection); the obstacle height and material; the battery protocol between flights; and the ambient conditions.
- **Why it matters:** These details are needed to reproduce the campaign and to judge both the efficiency claim and the noise analyses in R1-2 and R1-3.
- **Proposed fix:**
  1. Add a campaign table listing, for each policy: phase, condition, flights flown, flights discarded (with reason), K_n, R_∘, R_• (mean ± SD), and S_• where relevant.
  2. Add a "Data processing" paragraph that defines cleaning, alignment, the identification window, Ω_ℛ, and the sampling grid.
  3. Add an appendix table of all numerical settings.
  4. State the total number of flights in the Abstract or the Conclusions.

### R1-12. Notation clashes and inconsistencies between equations

- **Severity:** Minor
- **Location:** Sec. II-A, Eq. (`eq:rt-expected-improvement`): "Let ℛ_•⁺ denote the best physical reward and ξ≥0 an optional exploration margin." This and the other issues listed below.
- **What is wrong:**
  (a) **ξ** denotes both the descriptor (bold) and the EI margin (italic).
  (b) **χ** denotes both the operating-condition vector (Eq. `eq:rt-surrogate`) and the rotor-disk overlap fraction χ_i(x) (Eq. `eq:corrected-thrust`).
  (c) π_• denotes both the deployed policy π_•^(n) and the performance-oriented family in Eq. (`eq:rt-policy-schedule`).
  (d) Different symbols are used for the same object: ℒ_p and J_p; Θ_ι,safe and Π_safe; π_ι and π_INF; F_n and F_1:N; Σ_ν and σ_e²; Θ and Θ_p.
  (e) The same symbol is reused for different objects: m (mass and model-update index); ε (Adam constant and reward noise); Φ (normal CDF and clearance penalty); λ (eigenvalues and interpolation fraction); D (D_θ and the operator D²); S (sensitivity and normalized score); d (motor distance and disturbance vector).
  (f) Fig. 1 uses "input z" (undefined; **d** is probably meant), 𝒥_info (never defined in the text), and ℛ̂_•(ℛ_•, ℛ_∘, θ_π) (not used in the text).
  (g) The legend of Figs. 11–12 uses π_k,i where the text uses π_λ,i; Fig. 16 uses π_i, which is undefined; and "S_e = 0" has an undefined subscript.
  (h) Eqs. (`eq:reward-transfer`) and (`eq:ei`) restate Eqs. (`eq:rt-surrogate`) and (`eq:rt-expected-improvement`) with different arguments.
  (i) In Eq. (`eq:episode-error-vectors`), the label inside `align` attaches only to the second line.
- **Why it matters:** The clashes in (a)–(c) fall inside the equations that define the method, so they can mislead readers.
- **Proposed fix:** Add a nomenclature table. Rename the EI margin ζ, the overlap fraction κ_i(x), and the deployed policy π^(n). Use one symbol for each object throughout. Keep a single version of the surrogate and EI equations, and refer back to it with the nominal-condition specialization (ξ = **a**). Align the figure legends with the text.

---

## Recommendation

**Major revision.** The platform, the closed-loop differentiable twin, and the staged RT workflow are valuable, and the authors are commendably candid about the limits of their uncertainty quantities. As submitted, however, the quantitative claims are not yet supported by the methodology. The parameter-uncertainty indicator has an arbitrary scale and, read at face value, does not resolve the augmentation (R1-1). The headline performance gain is a single selected value with no noise model or confirmation, and most of it predates EI (R1-2). The normalized scores used for generalization contradict both the reported rewards and the text (R1-3). The contribution of the reward-transfer surrogate is not separated from that of the π_MB initialization combined with a plain GP (R1-4). The E-optimal design was not demonstrably optimized, and its comparator is weak (R1-5). Resolving R1-1 to R1-5 is necessary for acceptance; R1-6 to R1-11 are needed for rigor and reproducibility. Most of the requested analyses use existing data: per-run rewards, a clustered covariance or jackknife, LOO cross-validation, in-silico design comparators, held-out replays, and a corrected Fig. 16. New flights are needed only for a short confirmation block, possibly one DT-greedy policy, and one validation flight without ground effect.
