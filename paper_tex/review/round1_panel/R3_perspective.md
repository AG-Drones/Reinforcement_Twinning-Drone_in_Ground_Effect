# Peer Reviewer 3: Perspective

**Manuscript:** "Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect" (A. Grava, M. A. Mendez), IEEE journal draft, round 1 (`main_lf.tex`).

**Seat identity.** I am a researcher in learning-based control and sim-to-real transfer: model-based RL, Bayesian optimization (BO) in the loop, multi-fidelity surrogates, digital twins, and iterative learning control. I review from a cross-disciplinary angle. I ask which alternatives a reader would consider and whether the data-efficiency and risk-reduction claims are shown against a fair baseline. I also look at the practical cost in flights and compute, at what generalizes beyond this testbed, and at whether the framing ("Reinforcement Twinning", "active digital twin") is clear to an outsider. I read the full LaTeX source and the rendered result figures. I did not look at code or at other panel reports. Values marked "by my reading of Fig. X" were measured from the plotted markers and should be checked against the authors' data.

---

## Summary (≤100 words)

The paper demonstrates a Reinforcement Twinning (RT) workflow on a Crazyflie 2.1+ crossing a finite obstacle in ground effect. Twelve E-optimally designed flights identify a two-parameter static ground-effect law inside a differentiable closed-loop digital twin (DT). The frozen DT then yields an offline-optimized, position-indexed altitude-reference correction above the stock PID. Finally, a reward-transfer surrogate (an affine DT-to-physical map plus a GP discrepancy) drives Expected Improvement over three basis amplitudes. Tracking reward rises from 0.54 (PID) to 0.85 (model-based) and 0.95 (best EI). Two off-nominal conditions probe transfer, with two extra EI flights at one of them.

---

## Genuine strengths

1. **Real hardware, well-chosen testbed.** A finite obstacle produces the onset and removal of ground effect in one mission, including leading- and trailing-edge transients. The baseline excursion (about +1R over the obstacle, about −1R after it) is large and repeatable relative to the five-run RMS band (Fig. 3), so the test is meaningful.
2. **A deployable architecture.** All prediction and optimization happen offline. Onboard, only a lookup-table reference correction runs, and the stock cascaded PID firmware is unchanged. For small platforms with limited compute this is a practical, low-barrier pattern, and it deserves to be emphasized.
3. **Technically sound gray-box identification.** The closed-loop DT reproduces the firmware PID, and adjoint (reverse-mode) identification runs through the whole closed loop. The authors are careful to call the curvature-based covariance a local indicator rather than a confidence region.
4. **Adaptive experiment design that is visible in the data.** Switching from the broad to the near-wall domain produces a clear change in slope of λ_min(F) (Fig. 5b), which is an instructive example of adapting the design space during sequential design.
5. **Honest reporting.** The authors state that the DT is optimistic at the trailing edge (Fig. 8), report that the transferred correction underperforms at (1, 0.113), call the generalization a proof of concept, and separate GP posterior uncertainty from run-to-run repeatability.
6. **An interpretable transfer surrogate.** The affine-plus-GP form corrects the DT's *ranking* of policies without enlarging the physics model. It is easy to explain to practitioners and sensible when the model structure is deliberately limited.
7. **Clear figures.** In particular, the video-frame comparison (Fig. 14) shows the result to non-specialists at a glance.

---

## Findings

### R3-1: No fair baseline supports the data-efficiency claim of the performance phase

- **Severity:** Major
- **Location:** Sec. II-A, "Performance phase": "Exploring the full policy space with a purely model-free strategy would require substantially more physical tests". See also Sec. III-D: "The marked difference between these two increments is the improvement enabled by the learned GP discrepancy".
- **What is wrong.** The paper asserts that the reward-transfer surrogate is more data-efficient than model-free search, but never tests this. The fair alternative is not a global model-free search over the full policy space. It is one of two things. The first is the *same local search* in the same three-dimensional coefficient space **a** around π_MB, with the DT term removed: standard GP-EI on the physical reward R•, starting from the same Sobol design. The second is an iterative learning control (ILC) update of the reference, the textbook approach for repeated tracking tasks, which has been shown on quadrotors to converge within a handful of trials. Figs. 11–12 suggest that, inside the search region, the DT reward carries little ranking information:
  - The seven Sobol policies span R• ≈ 0.77–0.93, while their R∘ values lie between about 0.89 and 0.99.
  - By my reading of Fig. 12, among the roughly 16 policies with R∘ > 0.93, the Spearman rank correlation between R∘ and R• is only about 0.3.
  - A *space-filling* Sobol policy had already reached R• ≈ 0.93 (at R∘ ≈ 0.954) before any EI step. With J = 1 − R, the tracking cost falls from 0.145 (π_MB) to 0.048 (π_EI*), and the best Sobol policy is already at about 0.067. That is about 80% of the reduction before EI was used.
- **Why it matters.** The main methodological claim of the performance phase is that a DT-informed surrogate improves the physical policy with fewer flights than the alternatives. Without an ablation, a reader in learning-based control cannot tell whether the affine-plus-GP structure helps, is neutral, or whether the gain comes from the compact three-dimensional parameterization around π_MB, which any BO or ILC scheme would also exploit. As written, the gain is overattributed to the GP discrepancy.
- **Proposed fix.**
  - (a) *Retrospective ablation, no new flights.* Using the collected data in its acquisition order, refit (i) a GP-only surrogate on R• with no affine DT term and (ii) an affine-only surrogate with no GP. Report the leave-one-out prediction error of each, and where each surrogate's EI would have proposed the next policy.
  - (b) *Simulation benchmark.* Build a "pseudo-physical" DT variant that adds a transient ground-effect term (for example, a first-order lag on χ_i, or a velocity-dependent amplitude) and use it as the stand-in plant. On it, compare RT reward-transfer EI, plain GP-EI on **a**, random search, and a model-based ILC on the reference that uses the DT sensitivity as the learning gain. Run at least 20 seeds and plot best-so-far reward against the number of "flights".
  - (c) If feasible, add one hardware ILC run of 5–8 iterations starting from π_MB.
  - (d) Reword Sec. III-D to match the evidence. For example: "Most of this gain was already captured by the best space-filling policy; Expected Improvement then added a further, smaller improvement."

### R3-2: π_MB is a regularized DT optimum, which confounds the gain attributed to model discrepancy

- **Severity:** Major
- **Location:** Sec. III-D: "Relative to π_MB, its DT reward increases only from approximately 0.968 to 0.978".
- **What is wrong.** π_MB minimizes J_MB in Eq. (39), which adds an amplitude penalty (0.10‖Δz/R‖²) and a curvature penalty (2.0‖D²Δz/R‖²) to the tracking cost. It does not maximize R∘. Several tested policies therefore have a *higher DT reward* than π_MB (R∘ ≈ 0.98–0.99 in Figs. 11–12), and they also do better physically (R• ≈ 0.89–0.92, against 0.855 for π_MB). π_EI* also commands larger amplitudes than π_MB: by my reading of Fig. 13, its reference goes down to about 0.45R over the obstacle and up to about 3.1R at the trailing edge. A sizable share of the MB-to-EI* gain could therefore be available simply by relaxing the penalties in the DT, with no flights at all; by my reading of Fig. 12, the high-R∘ candidates account for roughly one third to two thirds of the cost reduction. The weights 0.10 and 2.0 are not justified anywhere.
- **Why it matters.** The claim that physical rewards "allow RT to improve upon that policy" because of model discrepancy is only meaningful against the *best DT-only* policy, not a regularized one. For practitioners, retuning the regularization offline is far cheaper than about 16 additional flights.
- **Proposed fix.**
  - Compute the DT-reward-optimal policy in the same screened set, with the penalties reduced to the minimum needed for smoothness, and report its R∘ and predicted minimum clearance. Ideally, fly it once with five repetitions.
  - Split the MB-to-EI* improvement into (i) the part obtained by relaxing regularization in the DT alone and (ii) the part due to the learned discrepancy.
  - Justify the weights, for example with a DT Pareto curve of J_trk against ‖Δz/R‖.
  - If the DT-optimal policy cannot be flown, add a sentence such as: "The reported gain is measured relative to a regularized model-based policy; part of it may be attainable by reducing the regularization in the DT."

### R3-3: The control value of the 12-flight information phase is not shown, and its counterfactual is weak

- **Severity:** Major
- **Location:** Sec. III-B: "The latter repeats the same measured baseline episode at 0.35 m/s, including its sampling and residual level".
- **What is wrong.** The repeated-baseline counterfactual reuses one constant-altitude record N times, so its information proxy is just N·F_BL. This shows that one trajectory is poorly informative. It does not show that E-optimal design beats a sensible campaign that was not optimized. A flight-test engineer would compare against constant-altitude crossings at several clearances (the classical way to map f_GE(z/R)) or against random smooth references in the same domain. The paper also never shows the downstream effect of identification:
  - Fig. 7 shows that the broad-domain model and the final model replay the baseline almost identically.
  - No π_MB is reported for the Cheeseman–Bennett model (zero identification flights) or the broad-domain model (six flights).
- **Why it matters.** For a sim-to-real reader, the key question is whether the identification flights pay off for control. Would a π_MB designed with Cheeseman–Bennett, followed by the same reward-transfer EI, reach the same final performance with 12 fewer flights? The data-efficiency claim for RT *as a whole* depends on the answer.
- **Proposed fix.**
  - (a) *No new flights needed.* Compute λ_min(F) with the final DT and scaling, as is already done for the post-campaign comparison, for non-optimized designs of the same size. Examples are constant-altitude crossings at z/R ∈ {0.75, 1, 1.5, 2, 3, 4} and N random smooth references in each domain; report the median and spread over random draws.
  - (b) Compute π_MB with the Cheeseman–Bennett, broad-domain, and final parameters. Evaluate all three in the final DT and report R∘ and the predicted minimum clearance.
  - (c) If possible, fly π_MB designed with Cheeseman–Bennett (five repetitions) as the "no information phase" reference point.
  - (d) State explicitly what the information phase cost in flights and what it bought in control performance.

### R3-4: Rewards are treated as deterministic, so the EI improvement has no uncertainty and is exposed to selection bias

- **Severity:** Major
- **Location:** Sec. II-C, "Performance phase": "The rewards are computed from the cleaned mean trajectories and are treated as deterministic campaign observations".
- **What is wrong.**
  - The GP uses only a 10⁻⁸ jitter, so ε in Eqs. (11) and (41) is effectively zero.
  - The incumbent R•⁺ is the maximum of about 17 noisy evaluations.
  - No reward-level repeatability is reported.
  - π_EI* appears to be scored on the same flights that selected it.
  - The gap between the best Sobol policy and π_EI* is about 0.02 in reward. With R = 1 − J, this is an RMS tracking error of about 0.26R versus 0.22R, or roughly 6.0 mm versus 5.0 mm. A difference of about 1 mm is comparable to the Lighthouse jitter (0.5–1 mm) and to the RMS bands in Figs. 3, 8 and 13.
  - The five repetitions per policy that would quantify this already exist.
- **Why it matters.** EI on a noiseless GP will chase noise, and a best-of-N incumbent is biased upward (the winner's curse). Readers cannot tell whether π_EI* really beats the best Sobol policy, or whether EI points that "remain below the incumbent" were exploratory or simply noisy.
- **Proposed fix.**
  - (i) Tabulate per-repetition rewards for every physical policy (mean ± SD, n).
  - (ii) Estimate σ_ε from the repetitions and use it in the GP, as heteroscedastic noise with variance σ²/n_rep per point.
  - (iii) After selection, fly fresh confirmation repetitions of π_EI*, π_MB, and the best Sobol policy, and report their differences with confidence intervals.
  - (iv) Add error bars to Figs. 11, 12 and 16.
  - (v) Reword "a substantial performance gain" if the confirmation flights do not support it.

### R3-5: Physical and computational cost is not reported, so "a limited number of physical interactions" cannot be checked

- **Severity:** Major
- **Location:** Abstract: "improves trajectory tracking with a limited number of physical interactions".
- **What is wrong.** The paper never totals its flights. The number of distinct policies can be partly reconstructed:
  - 5 baseline repetitions
  - 12 information policies
  - π_MB
  - 2 interpolation policies
  - 7 Sobol policies
  - "a few" EI policies (about 8–9 red markers in Fig. 12)
  - at the off-nominal conditions, 2 × (baseline, MB, transferred) plus 2 EI policies

  However, repetitions are stated only for the baseline, π_MB and π_EI* ("averaging five repetitions"), so the total could be anywhere from about 45 to more than 150 flights. Also missing: aborted or discarded runs, battery swaps, campaign duration, and the wall-clock time and hardware for each adjoint identification, the MB optimization, the 2000-candidate DT screening, and the EI acquisition. Meanwhile, the abstract describes the MB step as "computationally efficient".
- **Why it matters.** Data efficiency is the main argument against model-free RL and plain BO, so it must be quantified in flights and hours. Compute time decides whether the between-flight loop is practical in the field (minutes or hours per iteration).
- **Proposed fix.**
  - Add a campaign-budget table with these columns: phase | distinct policies | repetitions per policy | total flights | airborne time | discarded runs (reason) | compute per iteration (hardware, wall-clock).
  - Replace "after only a few EI-guided evaluations" with the exact count.
  - Report how many DT candidates the safety screen rejected in each phase.

### R3-6: The safety and risk-reduction claims rely on a DT shown to be non-conservative where it matters, and some commanded references enter the obstacle

- **Severity:** Major
- **Location:** Sec. II-A, "Summary of the Reinforcement Twinning loop": "the physical environment is exposed only to a policy that has first been generated and screened in the DT".
- **What is wrong.**
  - (i) The DT is optimistic at the trailing edge, the most safety-critical region (Sec. III-C: "the DT predicts that the reference increase should almost suppress the downstream undershoot"). A screen with a known non-conservative bias and no margin for model error is not a safety guarantee.
  - (ii) Deployed *references* fall below the stated clearance and, at (1, 0.113), inside the obstacle. By my reading, Fig. 13 shows π_EI* at about 0.45R. Fig. 15(b) shows π_MB and π_EI* at about −0.5R, and π_EI^tr at about −0.85R, over x/R ≈ 22–45. The vehicle stays clear only because the *predicted* ground-effect support and PID lag hold it up, which is exactly the uncertain physics. If that support is lost (lateral drift off the obstacle, battery sag, a weakening motor), the PID drives the vehicle toward the surface.
  - (iii) Lighthouse absolute accuracy (0.5–1 cm) is comparable to the 0.5R = 11.5 mm margin. Neither the obstacle height nor the way the z = 0 datum was registered is reported, so floor clearance after the trailing edge cannot be judged; EXP_INF,9 reaches z/R ≈ −1.3 there (Fig. 4).
  - (iv) No experiment supports the statement that model-free search "could expose the physical environment to unsafe policies".
- **Why it matters.** For readers from safe learning (SafeOpt, safe BO, learning-based MPC), "safe" implies a stated, usually probabilistic, guarantee. The actual contribution, that DT screening reduces risk, is valuable when stated precisely, but the current wording overclaims and invites rejection. A datum error also biases the identified (A, p), because f_GE depends on R/z: at z = 0.5R, a 5 mm datum shift changes R/z from 2.0 to about 1.4.
- **Proposed fix.**
  - (a) Replace "safe" with "DT-screened" (or "screened against the DT clearance constraint"), or define safety formally.
  - (b) For every flight, report the measured minimum clearance of the lowest rotor next to the DT-predicted value. Use the worst observed DT-minus-measured error as an explicit margin in the screen.
  - (c) Constrain the commanded reference itself (for example, z_π ≥ 0.5R above the local surface), or justify set points inside the obstacle with a failure-mode analysis of what happens if ground-effect support disappears.
  - (d) Model the clearance outcome with its own GP discrepancy and use a constrained acquisition, such as EI multiplied by the probability of feasibility, or SafeOpt-style screening (Sui et al. 2015; Berkenkamp et al. 2016).
  - (e) Report the obstacle height, how the z = 0 datum was registered in the Lighthouse frame, and its uncertainty, and discuss how that uncertainty affects the identified A and p.

### R3-7: The paper is not positioned against its closest alternatives

- **Severity:** Major
- **Location:** Sec. I: "This also distinguishes RT from dual control."
- **What is wrong.** RT is positioned only against dual control and MPC in general. The closest prior work for each component is not discussed (all references below verified to exist):
  - *Multi-fidelity and sim-to-real BO*, where one GP links simulated and physical performance:
    - A. Marco, F. Berkenkamp, P. Hennig, A. P. Schoellig, A. Krause, S. Schaal, S. Trimpe, "Virtual vs. real: Trading off simulations and physical experiments in reinforcement learning with Bayesian optimization," *ICRA* 2017.
    - M. Cutler, J. P. How, "Efficient reinforcement learning for robots using informative simulated priors," *ICRA* 2015.
    - A. Rai, R. Antonova, F. Meier, C. G. Atkeson, "Using simulation to improve sample-efficiency of Bayesian optimization for bipedal robots," *JMLR* 20, 2019.

    The reward-transfer surrogate (Eq. 11) is in fact the autoregressive co-kriging of M. C. Kennedy, A. O'Hagan, "Predicting the output from a complex computer code when fast approximations are available," *Biometrika* 87(1), 2000. The already-cited 2001 calibration paper is closely related.
  - *Policy search with an inaccurate model plus real rollouts:* P. Abbeel, M. Quigley, A. Y. Ng, "Using inaccurate models in reinforcement learning," *ICML* 2006.
  - *Iterative learning control for quadrotor tracking:*
    - A. P. Schoellig, F. L. Mueller, R. D'Andrea, "Optimization-based iterative learning for precise quadrocopter trajectory tracking," *Autonomous Robots* 33, 2012.
    - D. A. Bristow, M. Tharayil, A. G. Alleyne, "A survey of iterative learning control," *IEEE Control Systems Magazine* 26(3), 2006.
  - *Learned ground-effect compensation on multirotors:* G. Shi et al., "Neural Lander: Stable drone landing control using learned dynamics," *ICRA* 2019.
  - *Safe BO and controller tuning on quadrotors:*
    - F. Berkenkamp, A. P. Schoellig, A. Krause, "Safe controller optimization for quadrotors with Gaussian processes," *ICRA* 2016.
    - Y. Sui, A. Gotovos, J. Burdick, A. Krause, "Safe exploration for optimization with Gaussian processes," *ICML* 2015.
  - *Learning-based MPC:* L. Hewing, K. P. Wabersich, M. Menner, M. N. Zeilinger, "Learning-based model predictive control: Toward safe learning in control," *Annu. Rev. Control Robot. Auton. Syst.* 3, 2020.
- **Why it matters.** Without this positioning, readers from learning-based control may see RT as a relabeling of established tools, and the real novelty goes unstated. As I read it, the novelty is combining E-optimal identification inside a differentiable closed-loop twin with a search anchored at the twin's optimum, and demonstrating it on hardware. The sentence "still poorly experimentally validated" also leaves unclear whether this is the *first* hardware RT demonstration.
- **Proposed fix.**
  - Add a related-work paragraph, or a compact table with these columns: method | what is learned | data used per flight | model required | safety mechanism | hardware demonstration.
  - State precisely what is new relative to Marco et al. 2017, which already combines simulated and physical evaluations in one GP and chooses which to query, and relative to Neural Lander, which learns ground-effect residual dynamics.
  - Suggested wording: "The reward-transfer surrogate is closely related to multi-fidelity Bayesian optimization with a simulator as the low-fidelity source [Marco 2017; Cutler & How 2015]. RT differs in that the low-fidelity source is itself identified from designed experiments, and the search is anchored at the twin's model-based optimum."
  - State explicitly whether this is the first hardware demonstration of RT.

### R3-8: The framing and terminology are hard for outsiders to follow, and partly nonstandard

- **Severity:** Moderate
- **Location:** Sec. II-C, "Model-based policy": "model predictive control refers to this model-predictive reference synthesis; a receding-horizon optimizer is not run onboard".
- **What is wrong.**
  - (i) "Reinforcement" suggests RL, yet no value function, no policy gradient on physical data, and no MDP exploration are used. The implemented pipeline is sequential optimal experiment design, gray-box adjoint identification, offline reference optimization, and twin-anchored BO.
  - (ii) Standard terms are redefined:
    - "Model predictive control" is used for offline open-loop reference optimization.
    - "Reference governor" normally means an online, constraint-enforcing modification of references (E. Garone, S. Di Cairano, I. Kolmanovsky, *Automatica* 75, 2017), not a fixed lookup table.
    - "Predictive control" appears as a keyword.
  - (iii) The introduction spends a paragraph on earlier RT features that are not used here (a model-free branch, a referee, policy cloning). "Bayesian RT" appears without definition.
  - (iv) "Active DT", "steering representation" and "acting model" are never translated into operational terms.
  - (v) Notation drifts: the interpolation policies are π_{λ,i} in the text and Fig. 9 but π_k / π_{k,i} in the legends of Figs. 11–12.
- **Why it matters.** IEEE readers in control and robotics will judge the work against the benchmark the words suggest. An MPC reader expects a receding horizon; a reference-governor reader expects constraint guarantees. Mislabeling triggers avoidable objections.
- **Proposed fix.**
  - Add a short mapping box at the end of Sec. I or the start of Sec. II with three columns: RT element → standard term → implementation here. For example:
    - information phase → sequential E-optimal experiment design with gray-box identification;
    - model-based policy → offline, gradient-based optimization of a feedforward altitude-reference profile through the closed-loop DT;
    - performance phase → Bayesian optimization with a twin-informed affine prior mean and a GP discrepancy.
  - Replace "model predictive control" and "model-predictive reference synthesis" with "offline model-based reference optimization".
  - Replace "reference governor" with "feedforward reference shaping (position-indexed lookup table)".
  - Remove or qualify the keyword "predictive control".
  - Shorten the paragraph on earlier RT to two sentences, and either define "Bayesian RT" or drop the term.
  - Use one notation for the interpolation policies throughout.

### R3-9: The scope of generalization is unclear, and the off-nominal scores in the text do not match Fig. 16

- **Severity:** Moderate
- **Location:** Abstract: "A proof-of-concept extension to different operating conditions further illustrates how the same workflow can adapt a transferred correction".
- **What is wrong.**
  - (i) The deployed policy is a position-indexed table for one obstacle (0.81 m long), one speed, and one clearance. It needs accurate global position relative to a known obstacle geometry, plus many repeated crossings. The introduction motivates GNSS-denied inspection of *unknown* confined spaces, where none of these is available, and this gap is not discussed.
  - (ii) The paper does not say *what* transfers: the identified f_GE (plausibly reusable across geometries), the MB design procedure (reusable whenever the geometry is known), or the GP correction (shown not to transfer reliably).
  - (iii) The transfer rule is inconsistent. Eq. (40) *adds* R·b(x)ᵀa to Δz_MB, a correction with fixed absolute amplitude. Yet Sec. II-C states that the correction is "reduced automatically when the local MB solution requires little intervention".
  - (iv) The text and figure disagree. Sec. III-E gives S• ≈ 0.57 for the first EI flight at (1, 0.113) and ≈ 0.83 for the second. In Fig. 16, by my reading, the small purple marker is near 0.37 and the purple star near 0.76; the value 0.83 matches the *black* nominal star instead.
  - (v) Only one off-nominal condition received EI, with two flights, and the first of those fell well below π_MB. This shows the exploration risk at new conditions.
- **Why it matters.** Generalization is what readers outside this testbed care about most. The honest message, that the identified physics transfers while the reward-level correction is local, is worth stating clearly, and it supports RT's design logic.
- **Proposed fix.**
  - Add a "What transfers" paragraph that separates three things: (1) the identified ground-effect law, reusable for other geometries at similar speeds and clearances; (2) the MB design, recomputed offline for each known mission; (3) the GP correction, which is local to the operating condition.
  - Make Eq. (40) and the text agree. If scaling is intended, write it explicitly, for example as a basis whose amplitude is modulated by |Δz_MB(x)|.
  - Correct either the S• values or the figure.
  - A cheap and compelling test of point (1): with the frozen DT, design π_MB for a different obstacle length and fly it five times.
  - In the DT, add a sensitivity study to streamwise registration error (shift the Δz table by ±1–2R) to show what localization accuracy the method needs in the field.
  - Qualify the abstract: "...illustrates, at one off-nominal condition and with two additional flights, how..."

### R3-10: The performance phase discards trajectory information, and the choice and scalability of the basis are not discussed

- **Severity:** Minor
- **Location:** Sec. III-D: "a high-dimensional correction could describe more complex shapes, but would require substantially more physical tests".
- **What is wrong.**
  - Each performance flight records a full trajectory of K_n samples, but the surrogate keeps one scalar per flight.
  - Those trajectories are never fed back to identification, because θ_p stays frozen.
  - The three Gaussian bases (centers at x/R ≈ 35, 54, 70) appear to have been placed by hand after inspecting the π_MB flight, and their widths are not reported.
  - BO on a scalar reward scales poorly beyond roughly 5–10 dimensions. As presented, the approach does not extend to richer policies or multi-obstacle missions unless a human chooses a low-dimensional basis.
- **Why it matters.** For generality, readers need to know whether the hand-designed three-dimensional basis is essential, and whether a trajectory-level correction (for example, an ILC-type reference update or residual-dynamics learning) would use the same flights more efficiently.
- **Proposed fix.**
  - (i) Report the basis widths and the rule used to place the centers (for example, at extrema of the DT-versus-experiment replay error of π_MB), and present the basis as a design choice.
  - (ii) After the campaign, re-identify (A, p) with the roughly 20 performance flights included; this needs no new flights. Report the parameter shift and the replay error. This directly tests whether the remaining discrepancy is structural.
  - (iii) In the outlook, discuss trajectory-level alternatives (a GP on the spatial error profile, or an ILC update using the DT's lifted sensitivity) and how RT could interleave them.
  - (iv) In the simulation benchmark of R3-1, report sensitivity to the number of basis functions, for example 3 versus 6.

---

## Recommendation

**Major revision.** This is a careful and well-instrumented hardware study with a deployable architecture and unusually candid reporting of model limitations, and it would interest the learning-for-control community. Its central claims, however, are not yet supported against the alternatives a reader would consider: data efficiency (R3-1, R3-3, R3-5), improvement attributable to the learned discrepancy (R3-2, R3-4), and risk reduction (R3-6). The performance gain is shown only relative to a *regularized* model-based policy, with deterministic rewards, no confirmation flights, and no ablation against plain BO or ILC. The information phase is compared only with a trivially weak counterfactual. Most of the requested evidence needs no new flights: retrospective surrogate ablations, DT-only re-optimization with relaxed regularization, Fisher comparisons against non-optimized designs, a simulation benchmark with a pseudo-physical twin, and post-hoc re-identification. The remaining requests are a small number of confirmation flights. If the authors add this evidence, position RT against multi-fidelity BO, ILC and learned ground-effect compensation (R3-7), restate "safe" precisely, and align the terminology with standard usage (R3-8), the paper would make a solid and credible contribution.
