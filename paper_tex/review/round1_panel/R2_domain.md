# Peer Reviewer 2 (Domain): referee report

**Manuscript:** "Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect" (A. Grava, M. A. Mendez), IEEE-format draft, round 1 (`main_lf.tex` and the result figures).

**Seat identity.** Peer Reviewer 2, Domain. I work on multirotor aerodynamics near surfaces (ground, partial, edge and ceiling effects, low-advance-ratio forward flight) and on quadrotor modeling and control (Crazyflie firmware, cascaded PID, feedforward and reference shaping, in-flight identification). In this report I assess:
- whether the ground-effect (GE) model and its assumptions are physically sound;
- whether the figures support the physical interpretations in the Results;
- how well the paper covers the literature on GE modeling and identification;
- what the paper contributes to the field of MAV flight near surfaces.

I did not inspect code, and I did not read the other panel reports.

---

## Summary (100 words or fewer)

The authors apply Reinforcement Twinning to a Crazyflie 2.1+ crossing a finite obstacle at constant speed. The digital twin is a differentiable closed-loop model: the Richardson–Pretorius model plus a per-rotor power-law GE factor weighted by disk overlap. It is identified in flight from twelve E-optimal reference trajectories, giving A = 0.121 and p = 1.98. The twin then synthesizes, offline, a spatial altitude-reference correction for the stock PID controller. An affine-plus-GP reward-transfer surrogate with Expected Improvement refines this correction. The physical reward rises from 0.54 (baseline) to 0.85 (model-based) and 0.95 (EI). Two off-nominal conditions test transfer.

---

## Genuine strengths

1. **A relevant and under-studied configuration, tested in flight.** Most GE data come from load cells hovering over an infinite plane. Here a free-flying vehicle crosses a *finite* obstacle, with entry, residence and exit in one mission, and each policy is repeated five times with run-to-run RMS bands. Experimental data of this kind are scarce at Crazyflie scale.
2. **A sensible low-order physical structure.** The GE factor is applied per rotor and evaluated at the tilt-aware clearance of each rotor. This produces the pitching moments of asymmetric entry and exit, stays differentiable, and keeps the number of unknowns small enough to identify from flight data.
3. **A closed-loop twin that includes the onboard controller.** The cascaded PID is reproduced from the firmware, and episodes are replayed factually with spatial alignment. Errors are therefore compared through the same feedback loop that shaped them, which is the right approach when the stock controller is kept.
4. **A physically sensible policy representation.** The reference correction is indexed in space rather than time. This matches a disturbance that is locked to a location and removes sensitivity to timing differences between the twin and the experiment. The deployed artifact is only a lookup table, so it is easy to run onboard.
5. **A physically plausible identified result.** The amplitude comes out about twice the Cheeseman–Bennett (CB) value with an exponent close to 2. This agrees qualitatively with the known multirotor fountain-flow enhancement reported for the Crazyflie by Carter et al. [3]. Once it is shown quantitatively (R2-1), this is independent support for the in-flight identification.
6. **Candid reporting.** The authors report a negative transfer result at (1, 0.113), a remaining post-edge undershoot under π_MB, and uncertainty measures that they explicitly do not treat as confidence intervals. The Conclusions state the limitations clearly.

---

## Findings

### R2-1: The identified GE law is not benchmarked against existing Crazyflie data, and the "twice the classical value" result is expected multirotor physics
- **Severity:** Major
- **Location:** §III-B (Information Phase): "the exponent returns close to two, but the identified amplitude is almost twice the classical value."
- **What is wrong.** The identified f_GE is compared only with the single-rotor CB law. Two Crazyflie-specific data sets already in the reference list would allow a quantitative comparison, but neither is used.
  - **Carter et al. [3]** (Crazyflie 2.0, R = 23 mm, load cell): lift rose by up to about 20% near the ground, "more than twice what classic theory predicts". The data were fitted well (R² ≈ 0.96 for 1 < z/R < 3) by the multirotor model of Sanchez-Cuevas et al. with fountain coefficient K_b ≈ 2.
  - **Kan et al. [6]:** two GE models fitted on a larger quadrotor and validated on a Crazyflie 2.0 (0–2.1 m/s, 0.035–0.115 m). Taken at face value, their low-speed Model 1, T_IGE/T_h = (1 − 3R/25z)/(1 + (3/50)(V/v_h)³), gives an equivalent augmentation T_h/T_IGE ≈ 1.09 at z/R = 1.5 and V/v_h = 0.079. The identified law gives 1.054 at the same point. Model 1 also decays roughly as (R/z)¹, not (R/z)².
- **Why it matters.**
  - An amplitude near twice CB is what multirotor GE physics predicts (fountain flow between rotors and onto the body, Sanchez-Cuevas et al., 2017). It confirms known physics rather than adding a new finding.
  - The roughly 1.6-fold difference from Kan et al. in the augmentation at z/R = 1.5, and the different decay rate, need an explanation. Candidates include the clearance reference (R2-2), constant-power versus constant-speed definitions (R2-12), edge effects (R2-3), and bias from identifying in closed loop (R2-5).
  - Without this comparison, readers cannot tell whether the closed-loop identification recovers the aerodynamics or only an effective fitting factor of the closed loop.
- **Proposed fix.**
  1. In Fig. 6(a), overlay four curves, all expressed with the same clearance reference (rotor plane above the surface):
     - the exact CB law;
     - the multirotor law of Sanchez-Cuevas et al. with K_b taken from Carter et al.;
     - Carter's Crazyflie lift data;
     - Kan's Models 1 and 2 evaluated at the tested V/v_h.
  2. Discuss where these agree and disagree, and why.
  3. If the agreement holds, state it as validation of the in-flight identification.
  4. References:
     - P. J. Sanchez-Cuevas, G. Heredia, A. Ollero, "Characterization of the aerodynamic ground effect and its influence in multirotor control," *Int. J. Aerospace Eng.*, 2017, Art. 1823056, doi:10.1155/2017/1823056.
     - S. A. Conyers, M. J. Rutherford, K. P. Valavanis, "An empirical evaluation of ground effect for small-scale rotorcraft," *ICRA* 2018, doi:10.1109/ICRA.2018.8461035.
     - D. Del Cont Bernard, F. Riccardi, M. Giurato, M. Lovera, "A dynamic analysis of ground effect for a quadrotor platform," *IFAC-PapersOnLine* 50(1):10311–10316, 2017, doi:10.1016/j.ifacol.2017.08.1500.

### R2-2: The clearance reference, its measurement, and the floor are undefined
- **Severity:** Major
- **Location:** §II-B (Experimental setup): "Positive z therefore measures the vertical distance of the vehicle from this surface"
- **What is wrong.**
  1. The manuscript does not say which point z refers to: the Lighthouse-deck estimate, the body origin, or the rotor plane. It also does not say how the rotor clearances z_i in Eqs. (20)–(22) are built from it. On this airframe, the vertical offsets between the Lighthouse deck, the rotor plane, and the lowest point of the airframe are a sizable fraction of R = 23 mm.
  2. The manuscript does not describe how the height of the obstacle top was located in the Lighthouse frame. The Lighthouse absolute accuracy the authors quote (0.5–1 cm) corresponds to 0.22–0.43R.
  3. The obstacle height above the floor is not reported. Outside the footprint χ_i = 0, so GE from the floor is ignored, yet trajectories descend to z/R ≈ −1.3 downstream (Fig. 4, EXP_INF,9).
  4. The two Lighthouse fields of view overlap only above the obstacle. The region past the trailing edge, where the largest mismatch between twin and experiment occurs, may therefore be seen by only one station.
- **Why it matters.**
  - Because f_GE − 1 ∝ z^(−p), an offset of only 0.2R (4.6 mm) changes the predicted augmentation at z/R = 1 by about 30%, and that error maps directly into A and p.
  - An unknown origin offset trades off against the exponent, so it also contributes to the A–p correlation ridge.
  - The offset determines whether the 0.5R lowest-rotor constraint (11.5 mm) is physically meaningful given the motor mounts.
  - Every comparison with the literature (R2-1) depends on the same definition.
- **Proposed fix.**
  1. Report the geometry: the offset of the rotor plane from the estimated position, the lowest point of the airframe, the obstacle height, and the floor and obstacle materials.
  2. Calibrate the heights of the obstacle top and of the floor in the Lighthouse frame, for example by resting the vehicle on each surface and logging z.
  3. Either model the floor as a second GE surface or show that its contribution is negligible in every flight.
  4. Show how sensitive (A, p) are to origin offsets of ±0.1–0.2R. Alternatively, identify a nuisance offset z₀ in f = 1 + A[R/(z + z₀)]^p.
  5. Report how many base stations are visible along x. Cross-check the altitude after the trailing edge with an independent measurement, such as a downward time-of-flight range sensor (if compatible with the deck stack) or integrated IMU vertical acceleration.

### R2-3: The edge model (linear disk-overlap weighting) is assumed, not validated, in exactly the regions that matter
- **Severity:** Major
- **Location:** §II-B (Ground-effect correction): "It is therefore weighted by χi(x)∈[0,1], defined as the fraction of rotor disk i that overlaps the obstacle."
- **What is wrong.**
  - The isolated-rotor factor is scaled linearly with the geometric disk overlap. No physical argument or data support this rule at the leading and trailing edges, which dominate both the twin's error and the control gains.
  - The literature shows that partial GE is not proportional to geometric overlap:
    - Sanchez-Cuevas et al. (2017) characterized partial GE, where only some rotors are in GE.
    - He (2020 dissertation, Univ. of Utah) characterized partial GE empirically and built it into an IGE model; the related journal model is He et al. (2019).
    - Herz et al. (2026) found that partial GE "did not resemble full GE until most of the vehicle passed over the boundary", that the airframe drove its development, and that rotor performance degraded near the edge of the boundary.
  - The identified A is in effect a whole-vehicle factor (fountain flow between rotors and onto the body). A per-rotor overlap rule redistributes it incorrectly when only the front pair or only the rear pair is over the obstacle.
  - Fig. 7 is consistent with this:
    - The final twin underpredicts the leading-edge peak (about 2.25R against 2.55R measured).
    - Its descent after the trailing edge lags the experiment by about 5–7R and reaches a shallower minimum (about 0.6R against 0.42R).
- **Why it matters.** Figs. 8 and 13 show that most of the policy improvement occurs at the trailing edge, which is precisely where this weighting rule is least supported.
- **Proposed fix.**
  1. Cite and discuss the works above.
  2. Test at least one alternative edge law that adds one identified parameter, for example a smoothed step in x with identified width and offset, or an overlap computed for the whole vehicle for the fountain contribution. Compare the replay errors with those of the current rule.
  3. Use the logged asymmetry in pitch rate and motor commands at the edges as an extra observation of the front–rear thrust imbalance.
  4. As a minimum, state that the GP discrepancy is absorbing an edge effect, and show where in x it acts.
  5. References:
     - X. He, G. Kou, M. Calaf, K. K. Leang, *J. Dyn. Syst. Meas. Control* 141(7), 2019, doi:10.1115/1.4043221.
     - S. Herz, J. Taylor, L. Clar, M. McCrink, "Effects of partial boundaries and variable wind conditions on a free-flying multirotor platform," VFS Forum 82, 2026, doi:10.4050/F-0082-2026-0091.

### R2-4: Attributing the trailing-edge discrepancy to "transient" GE is unsupported; the logged data can test it directly
- **Severity:** Major
- **Location:** §III-C (Model-Based Policy): "overestimates its effectiveness in the transient regions where the static GE model is least representative"
- **What is wrong.**
  - The manuscript repeatedly attributes the residual to "transient development and decay" of the interaction between rotor and surface, but never shows evidence for it.
  - A time-scale estimate suggests the rotor–wake interaction is quasi-steady here:
    - the wake reaches the surface in about z/v_h ≈ 8 ms at z = 1.5R;
    - at 0.35 m/s, a rotor disk crosses an edge in about 0.13 s, and the whole footprint (about 4.8R) in about 0.32 s.
  - Several other explanations remain open:
    - The static augmentation may be underpredicted (the twin already underpredicts the overshoot), which leaves a larger integral state at the edge.
    - Edge flow (R2-3).
    - Positioning (R2-2).
    - Attitude coupling from front–rear thrust asymmetry.
  - The off-nominal data hint at a deficit specific to the edge:
    - The post-edge undershoot of the baseline is about 1.1R at both (1.5, 0.079) and (2.5, 0.045). Yet Eq. (21) gives about 3.1% and 1.8% augmentation at the clearances actually flown over the obstacle in those two cases.
    - At (2.5, 0.045) the twin predicts S∘ ≈ 0.98 for π_MB, whereas the experiment gives S• ≈ 0.54 (Fig. 16).
    - The residence time over the obstacle differs (2.3 s against 4.1 s), which confounds the comparison. That is one more reason to test the hypothesis directly.
- **Why it matters.**
  - The physical interpretation, and the argument for adding a GP rather than improving the model, both rest on this attribution.
  - Testing it is also where the paper could add genuine aerodynamic insight.
- **Proposed fix.**
  1. Reconstruct an experimental thrust ratio along each flight from the logged IMU acceleration, attitude, motor PWM and battery voltage:

     f_exp(x) = m(a_z + g) / [cos φ cos θ · Σ_i T_i,OGE(PWM_i, V_b)]

     This is the residual-force approach used by Shi et al. (2019) and Bauersfeld et al. (2021).
  2. Plot f_exp against rotor clearance and against x, separately for entry and exit, and compare it with the twin.
  3. Interpret the outcome:
     - hysteresis between entry and exit, or a dip below 1 after the trailing edge, would demonstrate a non-static or edge effect;
     - the absence of either would point to closed-loop or modeling causes instead.
  4. Show twin replays of the two off-nominal baseline flights.
  5. Fly the nominal mission with the obstacle removed, as a control experiment.
  6. Replace "transient" with whichever mechanism these data support.
  7. References:
     - G. Shi et al., "Neural Lander: Stable drone landing control using learned dynamics," *ICRA* 2019 (arXiv:1811.08027).
     - L. Bauersfeld et al., "NeuroBEM: Hybrid aerodynamic quadrotor model," *RSS* 2021.

### R2-5: The nominal twin is not validated out of ground effect, so any mismatch there is absorbed into (A, p)
- **Severity:** Major
- **Location:** §II-B (Digital Twin): "they are neither reidentified nor independently revalidated in the present campaign"
- **What is wrong.**
  - A and p are the only free parameters. The loss uses only the closed-loop z error, and only over the obstacle region.
  - Any mismatch that exists out of ground effect will therefore be absorbed into (A, p). Candidate sources:
    - the PWM-to-thrust map and k_T;
    - the motor lag;
    - the battery terminal voltage: the twin sets V_b from state of charge, while the logged voltage drops under load;
    - firmware version and gains;
    - the onboard estimator and Lighthouse latency. Is the onboard EKF modeled, or does the twin's PID act on true states?
  - Identifying a system in closed loop is known to give biased estimates when the controller or noise model is mis-specified (Forssell & Ljung, 1999).
  - A mission lasts about 20–25 s (10 s of hover plus the translation), not "a few seconds".
- **Why it matters.** The aerodynamic interpretation of (A, p), and their transfer to other conditions, both depend on this.
- **Proposed fix.**
  1. Report replay residuals in the out-of-ground-effect segments (x/R < 20) and for the no-obstacle flight (R2-4).
  2. Use the logged battery voltage as an exogenous input during replay.
  3. State whether the estimator is modeled, and quantify its latency.
  4. Report the firmware version and the PID gains.
  5. Optionally, identify a nuisance thrust-scale factor jointly with (A, p) to show that the two do not alias.
  6. References:
     - U. Forssell, L. Ljung, "Closed-loop identification revisited," *Automatica* 35(7):1215–1241, 1999.
     - R. V. Jategaonkar, *Flight Vehicle System Identification: A Time-Domain Methodology*, 2nd ed., AIAA, 2015 (output-error method).

### R2-6: Identifiability and uncertainty claims are stronger than the analysis supports
- **Severity:** Major
- **Location:** §IV (Conclusions): "the resulting ground-effect function was well constrained over the control-relevant clearance range"
- **What is wrong.**
  - **(a) The augmentation is only constrained above about z/R = 1.5–2.**
    - In Fig. 6(b), the final 2σ_f/f is about 15% at z/R = 1. That gives 2σ_f ≈ 0.17, which is larger than the augmentation itself (f − 1 ≈ 0.12). Normalizing by the total factor hides this.
    - Fig. 6 omits 0.5 ≤ z/R < 1 entirely, although this range lies in the design domain and the policies command it (R2-7).
    - Even in the near-wall flights, the measured clearances over the obstacle stay above about 1.3R except briefly at the leading edge (Fig. 4, EXP_INF,9). Bounds on the reference do not bound the trajectory.
  - **(b) The covariance in Eq. (32) has no absolute meaning.** Σ_θ ≈ J_p H⁻¹ is built from a loss and a curvature that are both averaged per sample. It therefore lacks the effective sample size and ignores residual correlation. It is neither a confidence region nor a conservative bound, so the 2σ magnitudes cannot be read at face value.
  - **(c) The endpoint of the designed curve in Fig. 5(b) largely restates N and ρ.**
    - The final comparison scales by D_θ built from the final Σ_θ. Suppose S̄ and J_p use the same residual normalization. Then the Gauss–Newton approximation gives F_1:N ≈ (N/2)C⁻¹, where C is the A–p correlation matrix.
    - Hence λ_min ≈ N/[2(1 + |ρ|)], which is about 3.6 for N = 13 and ρ = 0.818. The reported value is 3.242.
  - **(d) The design criterion is scale-dependent.** The E-criterion depends on parameter scaling, and here it is scaled by the current uncertainty estimate. D-optimality is invariant to such scaling.
- **Why it matters.** The stopping rule, the "well constrained" claim, and the safety screening (R2-7) all rest on these quantities.
- **Proposed fix.**
  1. Reparameterize the law as f = 1 + α(z_ref/z)^p, where α = f_GE(z_ref) − 1 is the augmentation at a clearance near the data centroid (z_ref = 1.5R or 2R). This removes most of the ridge.
  2. Report α and p with intervals obtained from leave-one-episode-out or episode-bootstrap refits, which are cheap with the differentiable twin, and/or from profile likelihood (A. Raue et al., *Bioinformatics* 25(15):1923–1929, 2009).
  3. Plot the uncertainty of f − 1 (not of f) down to z/R = 0.5.
  4. Add a histogram of the χ-weighted rotor clearances actually visited in each stage.
  5. Correct the Fisher proxy for colored residuals. The correction of Cramér–Rao bounds in E. A. Morelli & V. Klein, *Aircraft System Identification: Theory and Practice*, 2nd ed., Sunflyte, 2016, is one way to do this.
  6. Compare the E-optimal design with a D-optimal one.
  7. Complement the repeated-baseline counterfactual with a standard excitation set: random or Sobol references within the same bounds.
  8. Further references:
     - G. Franceschini & S. Macchietto, "Model-based design of experiments for parameter precision: State of the art," *Chem. Eng. Sci.* 63(19):4846–4872, 2008.
     - É. Walter & L. Pronzato, *Identification of Parametric Models from Experimental Data*, Springer, 1997.

### R2-7: The virtual safety screening relies on the least-constrained part of the model; some references command clearances inside the obstacle
- **Severity:** Major
- **Location:** §II-C (Model-based policy): "The reported policy is optimized with the single final identified DT; no model-uncertainty ensemble is used."
- **What is wrong.**
  - Several deployed references command clearances where the model is least constrained:
    - π_EI* holds the reference at about 0.45–0.55R over x/R ≈ 27–42 (Fig. 13).
    - At (1, 0.113), the π_MB, π_EI^tr and π_EI* references reach about −0.5R to −0.85R, i.e. *below the obstacle top* (Fig. 15b).
    - A supplied figure that is not in the manuscript (information datasets, panel d) also shows a reference below z = 0 over the obstacle. This contradicts the stated bound 0.5 < z/R.
  - These references are safe only because the predicted GE "cushion" holds the vehicle up. The clearance check uses the point estimate of the model.
  - At z/R = 0.5 the identified law extrapolates to f ≈ 1.48 (the exact CB value is 1.33), with no data in that range to support it.
- **Why it matters.**
  - The paper presents virtual safety screening as a central advantage of RT, yet the safety margin rests on the least certain part of the model.
  - The physically interesting behavior, a policy that exploits the GE cushion, is not discussed.
- **Proposed fix.**
  1. Add a reference floor that does not depend on the model (z_ref ≥ z_min above the surface), or justify why references below the surface are acceptable.
  2. Screen candidates against an ensemble of (A, p) from R2-6, or against a lower confidence bound on f − 1 combined with the worst-case edge law from R2-3.
  3. Report the measured minimum rotor clearance for every flight.
  4. Describe the onboard abort logic.
  5. Discuss the cushion mechanism explicitly.
  6. Position the work against safe Bayesian optimization on quadrotors: F. Berkenkamp, A. P. Schoellig, A. Krause, "Safe controller optimization for quadrotors with Gaussian processes," *ICRA* 2016.

### R2-8: The work is not positioned against established ways to compensate GE and repeatable disturbances, and the only comparator is the stock PID
- **Severity:** Major
- **Location:** §I: "However, they are intrinsically reactive: an unmodeled disturbance must first produce an error before feedback counters it."
- **What is wrong.**
  - The disturbance is fixed in space and the mission is repeated. This is the canonical setting for iterative learning control (ILC): Schoellig et al. (2012) learned feedforward corrections for quadrocopter tracking within a few trials, using a nominal model.
  - Compensation specific to GE also exists:
    - model-inversion feedforward (Sanchez-Cuevas et al., 2017);
    - a nonlinear disturbance observer (He et al., 2019);
    - a learned GE residual combined with stable nonlinear control (Shi et al., 2019).
  - So does residual-model learning for MPC (Torrente et al., 2021; Bauersfeld et al., 2021), and Bayesian optimization that trades simulations against physical experiments (Marco et al., 2017).
  - None of these is cited or compared. The only baseline is the stock PID, whose gains are not reported.
  - "Reference governor" has a specific meaning in constrained control (Garone et al., 2017). The deployed policy is in fact an offline spatial feedforward reference.
- **Why it matters.**
  - The contribution to the field cannot be assessed.
  - Part of the improvement from 0.54 to 0.95 might be obtainable by simpler, established means.
- **Proposed fix.**
  1. Add a related-work paragraph covering these approaches.
  2. Include at least one non-RT comparator with the same flight budget. Either option below would do:
     - onboard thrust feedforward that divides each rotor command by the identified factor [1 + χ_i(f_GE − 1)]. This takes a few lines of firmware and also directly validates the identified law.
     - if firmware changes are excluded by design: 3–5 ILC iterations on the same spatial reference parameterization, which is the like-for-like comparator.
  3. Report the default PID gains and comment on whether retuning them would help.
  4. Use "spatial feedforward reference shaping" in place of "reference governor", or justify the current term.
  5. References:
     - A. P. Schoellig, F. L. Mueller, R. D'Andrea, *Auton. Robots* 33:103–127, 2012.
     - D. A. Bristow, M. Tharayil, A. G. Alleyne, *IEEE Control Syst. Mag.* 26(3):96–114, 2006.
     - E. Garone, S. Di Cairano, I. Kolmanovsky, *Automatica* 75:306–328, 2017.
     - G. Torrente et al., *IEEE RA-L* 6(2):3769–3776, 2021.
     - A. Marco et al., "Virtual vs. real: Trading off simulations and physical experiments in reinforcement learning with Bayesian optimization," *ICRA* 2017.

### R2-9: Literature coverage of GE modeling and, above all, of identification is thin
- **Severity:** Major
- **Location:** §I: "At MAV scale, however, four nearby rotors interact with one another and with the central body"
- **What is wrong.**
  - The GE literature is covered by six references: the review, Carter, Franzetti, Cai, Kan and CB.
  - The identification literature is not covered at all. No reference supports the methods used in §II-C: output-error/adjoint identification, closed-loop identification, model-based experiment design, E-optimality, identifiability, or uncertainty quantification.
- **Why it matters.** The authors themselves flag this as a weak point, and reviewers will check it. The missing works also bear on the novelty claims.
- **Proposed fix.** Add a short "Related work" subsection and cite the identification works at Eqs. (26)–(36). Group the additions as follows:
  - **(a) Multirotor GE models and data:** Sanchez-Cuevas et al. 2017; Conyers et al. 2018; Del Cont Bernard et al. 2017; He et al. 2019 and He 2020 (dissertation); Herz et al. 2026. Also use Kan 2019 and Carter 2021 quantitatively (R2-1).
  - **(b) Learning or compensating GE in flight:** Shi et al. 2019; Bauersfeld et al. 2021; Torrente et al. 2021.
  - **(c) Identification:**
    - L. Ljung, *System Identification: Theory for the User*, 2nd ed., Prentice Hall, 1999;
    - Forssell & Ljung 1999; Jategaonkar 2015; Morelli & Klein 2016; Walter & Pronzato 1997; Franceschini & Macchietto 2008; Raue et al. 2009.
  - **(d) Feedforward and learning control:** Schoellig et al. 2012; Bristow et al. 2006; Garone et al. 2017; Berkenkamp et al. 2016; Marco et al. 2017.

### R2-10: Velocity is aerodynamically secondary at these advance ratios; the explanation of the failed transfer is speculative
- **Severity:** Minor
- **Location:** §III-E: "whereas the relative importance of the unmodeled transients changes with velocity, clearance, and the magnitude of the model-based action"
- **What is wrong.**
  - Aerodynamically, the tested crossings are quasi-hover:
    - all tested v_x/v_h values (0.045–0.113) lie in the range where Kan et al. found the thrust "practically constant" (V/v_h ≤ 0.7);
    - the CB forward-flight factor 1/[1 + (V/v_i)²], from the CB report already cited, changes the augmentation by less than 1.3%;
    - wake skew moves the impingement point by only about z·V/v_h ≈ 0.1R.
  - Velocity therefore acts mainly through the residence time over the obstacle (about 4.1 s, 2.3 s and 1.6 s for the three conditions) relative to the closed-loop time constants.
  - At (1, 0.113), the policies also operate where f_GE is least constrained (R2-6). This is a competing explanation for the failed transfer.
- **Why it matters.** The generalization discussion and the "forward flight" framing in the Introduction attribute effects to aerodynamics that the regime does not support.
- **Proposed fix.**
  1. State the quasi-hover regime explicitly, with these numbers.
  2. Discuss generalization in terms of residence time and closed-loop bandwidth.
  3. Add the uncertainty below z/R = 1 as a competing explanation for the failed transfer.
  4. Moderate the claims about forward flight in the Introduction.

### R2-11: The physical interpretation of π_EI* versus π_MB overreaches the figure
- **Severity:** Minor
- **Location:** §III-D (Performance Phase): "The command then rises earlier and more rapidly near the trailing edge."
- **What is wrong.**
  - In Fig. 13, both references cross z/R = 1.5 near x/R ≈ 52 and peak near x/R ≈ 62–63. π_EI* differs mainly in two ways:
    - a lower plateau over x/R ≈ 27–42;
    - a larger peak (about 3.1R against 2.5R).

    It therefore rises more steeply and higher, but not clearly earlier.
  - The claim that the vehicle "reaches a somewhat larger clearance before leaving the obstacle" is not visible: EXP_EI* and EXP_MB are close at x/R ≈ 55–57.
  - The decisive difference is the minimum after the trailing edge (about 1.1R against 0.55R).
  - Fig. 11 shows one Sobol policy already at R• ≈ 0.93 before EI. The final EI increment, to 0.952, should be compared with the run-to-run spread of the reward.
- **Why it matters.** The stated mechanism of the improvement should be what the data show.
- **Proposed fix.**
  1. Add a small table with the following quantities, each with its RMS over the five runs:
     - z at the trailing edge;
     - minimum clearance after the trailing edge;
     - peak reference amplitude and its location;
     - x where the reference crosses zero.
  2. Report the dispersion of the reward across repeated runs.
  3. Revise the wording accordingly.

### R2-12: Cheeseman–Bennett is misdescribed (expansion versus "rearrangement", constant power versus constant rotor speed)
- **Severity:** Minor
- **Location:** §II-B (Ground-effect correction): "The original Cheeseman and Bennett formulation rearranged with the same unknowns would have retained A=1/16 and p=2."
- **What is wrong.**
  - CB give T_IGE/T_OGE = 1/[1 − (R/4z)²] at constant power, from an image source combined with momentum theory.
  - 1 + (1/16)(R/z)² is the *first-order expansion* of that relation, not a rearrangement. The two differ appreciably near the wall: 1.25 against 1.33 at z/R = 0.5.
  - The dashed "Cheeseman–Bennett" curve in Fig. 6 is the expansion.
  - The twin applies the factor at constant rotor speed. For a fixed-pitch propeller, that ratio differs from the constant-power ratio, so "twice the classical value" mixes two definitions.
  - The Introduction labels CB a "momentum-theory relation".
- **Why it matters.** Precise definitions are needed for the literature comparisons in R2-1 and for the interpretation of A.
- **Proposed fix.**
  1. Rephrase as "first-order expansion of the CB constant-power relation".
  2. Plot or label the exact CB curve in Fig. 6.
  3. Add one sentence on constant power versus constant rotor speed.
  4. Mention the CB forward-flight factor in support of the static assumption (R2-10).

---

## Recommendation

**Major revision.** From the domain perspective, the paper has real experimental value: a free-flying Crazyflie crossing a finite obstacle, repeated runs, and a closed-loop differentiable twin that includes the stock controller. The workflow is coherent.

However, the physical claims about ground effect are not yet adequately grounded. The authors should:
1. define the clearance reference, its calibration, and the role of the floor (R2-2);
2. validate the identified law quantitatively against the Crazyflie data of Carter et al. and Kan et al., and against the multirotor model of Sanchez-Cuevas et al. (R2-1);
3. replace the untested "transient" explanation with direct force evidence at the edges, reconstructed from the IMU and PWM logs they already have (R2-3, R2-4);
4. make the safety screening aware of model uncertainty, given that several references command clearances where the model is unconstrained or lie inside the obstacle (R2-6, R2-7);
5. position the method against ILC, model-inversion or disturbance-observer compensation, and learned residual dynamics, with at least one comparator (R2-8);
6. substantially strengthen the identification literature and the uncertainty analysis (R2-6, R2-9).

Most of these can be addressed with data already logged. Only the no-obstacle control flight and one comparator require modest new experiments. With these additions, the paper would make a credible contribution: in-flight identification of finite-obstacle GE, combined with data-efficient feedforward correction for nano-quadrotors.
