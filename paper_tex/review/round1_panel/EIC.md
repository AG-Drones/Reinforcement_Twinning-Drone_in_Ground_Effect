# Journal-Fit Review (EIC seat): "Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect"

**Seat:** Journal-Fit Reviewer, acting as associate editor for an IEEE Transactions-level control/robotics venue (candidates: IEEE T-CST, T-RO, RA-L, T-Mech).
**Remit:** fit, originality and significance relative to the claims; framing; title, abstract and keywords; clarity of contribution; length and organization. Statistics and aerodynamics are left to the other seats.

---

## Summary (max 100 words)

The manuscript reports a hardware demonstration of Reinforcement Twinning (RT) on a Crazyflie 2.1+ crossing a finite obstacle in ground effect. A differentiable twin of the vehicle and its stock PID controller designs twelve E-optimal identification flights for a two-parameter ground-effect law. The twin then synthesizes offline a position-scheduled altitude reference that is added to the PID setpoint. An affine-plus-GP reward-transfer surrogate and Expected Improvement refine that reference using about fifteen further policies. Tracking cost falls from 0.46 (PID) to 0.15 (model-based) and then to 0.05 (refined). Transfer to two off-nominal conditions is explored as a proof of concept.

---

## Genuine strengths

1. **Complete loop on real hardware.** Identification, experiment design, model-based synthesis and data-driven refinement are all closed on a physical vehicle, not only in simulation. Few sim-to-real papers close the whole cycle on hardware.
2. **Production controller retained.** The correction is added as a setpoint modification above the unmodified Bitcraze cascaded PID. This add-on architecture is attractive for control-systems technology and lowers the barrier to adoption.
3. **Clear, repeatable testbed.** The baseline excursions (overshoot to about z/R = 2.5 over the obstacle and undershoot to about 0.5 after the trailing edge) are much larger than the run-to-run spread. The test case is therefore discriminating rather than marginal.
4. **Clear evidence that the twin cannot rank policies on its own.** Figs. 11–12 show a DT reward gain of about 0.01 against a physical gain of about 0.10 between the model-based and refined policies. This is a crisp, instructive demonstration of why a discrepancy model is needed.
5. **Sensible engineering choices.** The DT is differentiable and includes the firmware controller logic. The reference is indexed by position to avoid timing desynchronization. The policy space is deliberately small (three coefficients).
6. **Candid about limitations in several places.** The authors state that the static two-parameter law is a limitation, that the GP σ is an interpolation uncertainty and not a repeatability measure, that A and p remain correlated, and that the off-nominal study is proof-of-concept only.
7. **Illustrative material.** Fig. 1 and the video-frame comparison (Fig. 14) communicate the method and the result well to a broad readership.

---

## Findings

### EIC-1: Length and organization exceed every candidate venue and contain extensive duplication
- **Severity:** Critical (for T-CST and RA-L); Major (for T-RO).
- **Location:** Sec. II-A, "The actions carried out in each block can be summarized as follows:"
- **What is wrong:** The manuscript runs to 20 two-column pages, with 16 figures and about 46 numbered equations. The method section alone fills about 8 pages (pp. 2–10). The RT loop is described three times:
  - the generic paragraphs of Sec. II-A;
  - the six-item block list after Fig. 1, which repeats those paragraphs and the Fig. 1 caption;
  - the instantiation in Sec. II-C.

  Several equations appear twice: Fisher/E-optimal as Eqs. (9)–(10) and again as (35)–(36); the surrogate as Eq. (11) and again as (41); EI as Eqs. (13)–(14) and again as (42)–(44). Textbook material is typeset in full: rigid-body and quaternion Eqs. (15)–(19), inherited unchanged from [20], and the Adam moment and update Eqs. (28)–(30).

  Sec. II-C is titled "Test Campaign Overview" but holds the core algorithms under `\paragraph*` headings. Its labels (e.g., `sec:information-phase`) are attached to paragraphs rather than subsections. The Results subsections also re-describe the parameterization (opening paragraphs of III-B and III-C) and end with summary paragraphs that restate conclusions.
- **Why it matters:**
  - **T-CST:** regular papers are capped at 16 pages, and longer manuscripts are returned without review.
  - **RA-L:** capped at 8 pages, with charges for pages 7–8.
  - **T-RO:** 20 pages is the absolute maximum, and pages 13–20 carry overlength charges.

  In its current form, the paper cannot be submitted to T-CST or RA-L. Even at T-RO, the duplication hides the contribution.
- **Proposed fix:** Target ≤ 14 pages for T-CST, which leaves room for revision requests and also limits T-RO overlength charges. Concrete cuts:
  1. Delete the six-item block list in Sec. II-A. Fig. 1 and its caption already carry this content. Keep Eqs. (1)–(8) in compressed form.
  2. Keep each of the Fisher/E-optimal criterion, the reward-transfer surrogate and EI in one place only. Use the instantiated versions and refer back to them from the generic section.
  3. Replace Eqs. (15)–(19) with one sentence and a citation to [20]. Keep Table I.
  4. Replace Eqs. (28)–(30) with "Adam [Kingma & Ba, 2015] with learning rate 5×10⁻³…". Keep the tolerances.
  5. Merge Fig. 3 into Fig. 13, which already shows the baseline. Merge Fig. 9 with Fig. 10, Fig. 11 with Fig. 12 (same axes; mark the EI points), and Fig. 7 into a panel of Fig. 6.
  6. Remove the summary paragraphs at the ends of III-B, III-C and III-E, and cut the Conclusions to two paragraphs.

  Restructure as:
  - I Introduction (with a contributions list)
  - II Related Work
  - III Problem Setup and Digital Twin (platform, ground-effect model, mission, reward, assumptions)
  - IV RT for Ground-Effect Compensation (A: information phase; B: model-based reference shaping; C: reward-transfer refinement)
  - V Experimental Results (with a summary table; see EIC-4)
  - VI Discussion and Limitations
  - VII Conclusion

### EIC-2: The contribution and its novelty relative to the authors' prior RT papers are not stated; the key method reference is unpublished
- **Severity:** Major.
- **Location:** Sec. I, "This paper presents an experimental demonstration of the present RT formulation on a physical MAV."
- **What is wrong:** There is no explicit contributions statement. The reader cannot tell which elements are new and which are inherited. Candidates include:
  - the two-domain sequential E-optimal design;
  - the position-scheduled reference parameterization;
  - the affine-plus-GP reward transfer;
  - the normalized cross-condition surrogate, Eqs. (45)–(46).

  The Introduction attributes the "twin-calibrated Bayesian policy search," including the affine-plus-GP transfer, to [9]. That reference is listed as "manuscript submitted to Proceedings of the Royal Society A," so reviewers cannot see it. The individual building blocks are standard: adjoint/AD identification, E-optimal design, offline trajectory optimization, Kennedy–O'Hagan-type discrepancy and EI. The originality therefore rests on the experimental integration, which the paper should say plainly.
- **Why it matters:** Editors triage on the originality delta. An unpublished methodological parent paper also raises a salami-slicing question that the authors should preempt.
- **Proposed fix:**
  - Post [9] on arXiv, or upload it as confidential "material for review only."
  - Add one sentence that states what is taken from [8]–[10] and what is new here.
  - Add a contributions paragraph at the end of Sec. I, for example:

  > "The contributions of this paper are threefold. First, we report, to the best of our knowledge, the first hardware demonstration of Bayesian Reinforcement Twinning on a multirotor, in which a differentiable digital twin of a Crazyflie 2.1+ and its onboard controller is used both to design identification experiments and to synthesize control references. Second, we show that sequential E-optimal design over two nested clearance domains identifies a two-parameter ground-effect law from twelve flights, and that the identified twin yields a position-scheduled reference correction that reduces the tracking cost of the stock PID controller from 0.46 to 0.15 without modifying the onboard controller. Third, we show that an affine-plus-Gaussian-process reward-transfer surrogate, trained on [N] additional flights, finds a further reduction to 0.05 that the twin alone does not predict, and we examine the transfer of this correction to two off-nominal operating conditions."

  Before using "first," check the claim against [10] and against flapping-wing hardware work.

### EIC-3: The significance claims are comparative but no comparator and no experimental or computational budget is reported
- **Severity:** Major.
- **Location:** Abstract, "improves trajectory tracking with a limited number of physical interactions"
- **What is wrong:** The only comparator is the stock PID controller. Yet the abstract and Conclusions claim data efficiency and success "without exhaustive model-free exploration" and "without requiring unconstrained model-free exploration," both of which are comparative claims.

  The total number of flights is never stated. The text says only "after only a few EI-guided evaluations." From the figures, the nominal campaign appears to include:
  - 12 information-oriented policies;
  - the baseline and model-based policies;
  - 2 interpolation policies;
  - 7 Sobol policies (Fig. 11);
  - about 7–8 EI policies (Fig. 12).

  If each policy was flown five times, as stated for Fig. 13, this amounts to roughly 150 flights. The paper also lacks three ablations:
  - The value of the information phase for control is never shown. No model-based policy designed with the Cheeseman–Bennett-initialized twin is flown.
  - The value of the DT prior in the refinement is never isolated. There is no GP-BO run on the same three coefficients without the affine DT mean.
  - The information-design counterfactual is a repeated baseline, which is the weakest possible alternative.

  The claim of a "lightweight lookup table" is not backed by implementation details. The paper does not say whether the table runs in firmware or is streamed from a ground station, how large it is, or how long identification, model-based optimization and screening of the 2000 Sobol candidates take.
- **Why it matters:** T-CST and T-RO reviewers will ask why RT is preferable to simpler practice, in particular iterative learning control from the baseline (see EIC-5), plain Bayesian optimization on hardware, or a nominal-model feedforward. Without this evidence, the paper reads as a demonstration rather than an advance.
- **Proposed fix:**
  1. Add a flight-budget table per phase: policies × repetitions, battery packs, wall-clock time. Add a computation table: CPU/GPU and run time for identification, model-based optimization and candidate screening. Describe where the reference table runs.
  2. Add at least two comparators flown on hardware, or, if flights are impossible, evaluated on a "truth" simulator with a transient ground-effect term:
     - (a) a model-based policy from the Cheeseman–Bennett twin, which isolates the value of identification;
     - (b) GP-EI over **a** with a constant prior mean and the same flight budget, which isolates the value of the DT prior.

     Iterative learning control from the baseline is the natural third comparator.
  3. If no comparator is added, soften the abstract wording, for example: "...improves tracking relative to the stock PID controller using [N] flights; a comparison with model-free search was not performed."
  4. Provide the flight video as a multimedia attachment and add a data and code availability statement.

### EIC-4: No consolidated results table, and the headline generalization numbers in the text disagree with Fig. 16
- **Severity:** Major.
- **Location:** Sec. III-E, "the second evaluation reaches a new condition-specific best of approximately S•=0.83, marked by the purple star"
- **What is wrong:** Results are scattered across prose and scatter plots, and several numbers cannot be reconciled. Fig. 16 values below were measured from the submitted PNG and are accurate to about ±0.01.
  1. **Off-nominal EI flights at (1, 0.113).** The text gives S• ≈ 0.57 for the first EI flight (small purple marker) and S• ≈ 0.83 for the second (purple star). Fig. 16 shows ≈ 0.36 and ≈ 0.76.
  2. **Nominal points in Fig. 16.** The nominal π_MB and π_EI* plot at S• ≈ 0.45 and ≈ 0.84. Applying Eq. (45) to the rewards in Secs. III-C/D (R_BL ≈ 0.54, R_MB ≈ 0.855, R_EI* ≈ 0.952) gives ≈ 0.68 and ≈ 0.90. The DT-axis values do match (≈ 0.91 and ≈ 0.93). The physical normalization baseline in Fig. 16 therefore appears to differ from the one reported in the text.
  3. **Legend labels.** The interpolation policies are labeled π_k (Fig. 11), π_{k,i} (Fig. 12) and π_i (Fig. 16), but π_{λ,i} in the text.
  4. **Missing count.** The number of EI flights is never stated.
  5. **Artifact.** A stray glyph sits next to the black star in Fig. 16.
- **Why it matters:** The generalization result appears in the abstract and the Conclusions. An editor who spots text–figure mismatches on headline numbers will doubt the rest of the reporting.
- **Proposed fix:**
  - Add one table listing every physically flown policy with: operating condition, phase, ID, number of repetitions, R∘, R•, S∘, S•, and minimum measured clearance.
  - Regenerate Figs. 11, 12 and 16 from the same data file.
  - State in the Fig. 16 caption which baseline normalizes the nominal points.
  - Quote the numbers in the text from the table.

### EIC-5: Positioning against neighboring literature is thin (24 references) and omits the closest alternatives
- **Severity:** Major.
- **Location:** Sec. I, "This principle has been explored for wind-turbine control, gust rejection on a flapping-wing vehicle, cryogenic thermal management, and flapping-wing flight"
- **What is wrong:** This sentence attributes four application domains to only two citations, [8] and [10]. More broadly, there is no Related Work section, and several strands that reviewers at the candidate venues will expect are absent:
  - **(a) Iterative learning control (ILC).** A repeated mission with a position-indexed feedforward correction refined from trial data is the ILC setting. Examples: Bristow, Tharayil & Alleyne, IEEE CSM 2006; Schoellig, Mueller & D'Andrea, Auton. Robots 2012 (quadrocopter ILC).
  - **(b) Learning-based compensation of ground effect and aerodynamics on multirotors.** Shi et al., "Neural Lander," ICRA 2019; O'Connell et al., "Neural-Fly," Sci. Robot. 2022; model- and observer-based ground-effect compensation, e.g., Sanchez-Cuevas et al., 2017; He et al., J. Dyn. Syst. Meas. Control 2019.
  - **(c) Policy search combining simulator and hardware.** Cutler, Walsh & How, IEEE T-RO 2015; Marco et al., "Virtual vs. real," ICRA 2017; Berkenkamp et al., safe BO for quadrotors, ICRA 2016.
  - **(d) Learning-based and data-driven MPC.** Hewing et al., Annu. Rev. Control Robot. Auton. Syst. 2020; Torrente et al., RA-L 2021. The current MPC citation [7] is a manufacturing-oriented review.
  - **(e) Optimal input and experiment design for identification.** E.g., Mehra, IEEE TAC 1974; Pronzato, Automatica 2008.
  - **(f) Reference and command governors.** Garone, Di Cairano & Kolmanovsky, Automatica 2017.
  - **(g) Tools used but not cited.** Adam (Kingma & Ba), JAX, Sobol sequences.
- **Why it matters:** Strands (a)–(c) are the obvious alternative solutions to the same problem. Reviewers from the ILC and sim-to-real BO communities will treat their absence as overclaiming novelty.
- **Proposed fix:**
  - Add a compact Related Work section (about 0.6 page) built around strands (a)–(e). The authors should verify each suggested reference.
  - Reword the flagged sentence so that each application has its own citation, and replace "poorly experimentally validated" with "validated experimentally only in [x]".
  - Add an explicit ILC distinction, for example:

  > "Unlike iterative learning control, which updates a feedforward signal from the previous trial's tracking error through a fixed learning operator, RT selects each trial using a physics-based twin and a reward-transfer surrogate, so the same flights serve model identification, constraint screening in the twin, and transfer to new operating conditions."

### EIC-6: Control terminology does not match the conventions of the target community
- **Severity:** Major.
- **Location:** Sec. II-C, "In this work, model predictive control refers to this model-predictive reference synthesis; a receding-horizon optimizer is not run onboard."
- **What is wrong:** Several labels have established and different meanings in the control and robotics literature:
  1. **"Model predictive control" and the keyword "predictive control."** Both label a single offline, open-loop trajectory optimization.
  2. **"Reference governor."** This labels a precomputed lookup table. In the control literature, a reference governor is an online add-on that modifies the reference to enforce constraints (Garone et al., 2017).
  3. **"Policy."** This labels a position-scheduled feedforward with no state feedback beyond x. That use is acceptable in RL, but it should be stated explicitly.
  4. **"Generalization Across Operating Conditions."** This heading covers two conditions, one of which does not improve.
- **Why it matters:** T-CST and T-RO reviewers will read these terms literally and will object, or will judge the contribution to be overstated. The disclaimer sentence quoted above signals that the authors already know about the mismatch.
- **Proposed fix:**
  - Replace "MPC" with "offline model-based reference shaping" and "reference governor" with "position-scheduled feedforward reference."
  - Remove "predictive control" from the keywords.
  - Rename III-E to "Transfer to Two Off-Nominal Operating Conditions."
  - Proposed wording for Sec. II-C:

  > "The model-based policy is obtained offline by optimizing the complete closed-loop mission in the DT. No optimization is performed during flight; the result is executed as a position-scheduled altitude reference added to the setpoint of the stock PID controller."

### EIC-7: "Safe" is used as a guarantee, but safety rests only on screening in a twin that the paper shows to be optimistic
- **Severity:** Major.
- **Location:** Sec. I, "The model supplies the initial direction and the safety envelope; physical data correct its ranking where this is needed."
- **What is wrong:**
  - "Safe" or "safety" appears more than 30 times. The only mechanism is admissibility checking in the DT.
  - Yet the paper states that the DT "overestimates its effectiveness in the transient regions" (Sec. III-C) and "remains optimistic" (Sec. III-D).
  - In Fig. 15(b), the references at (1, 0.113) for π_MB, π_EI^tr and π_EI* go to z/R ≈ −0.5 to −0.8 over the obstacle. These setpoints lie inside the obstacle, and the vehicle relies on closed-loop lag and ground effect to stay above it.
  - The paper reports no measured minimum clearance per flight and no physical safeguards (abort logic, minimum-clearance monitor, protective netting).
  - The obstacle height, and therefore the clearance to the floor off the obstacle, is not reported.
- **Why it matters:** Robotics and control readers interpret "safe" as a guarantee. A reviewer who notices setpoints commanded below the surface will question the framing of the whole performance phase.
- **Proposed fix:**
  - Where no guarantee exists, replace "safe" with "DT-screened" or "admissible in the DT."
  - Report the obstacle height and the minimum measured clearance for every flight (center of mass and estimated lowest rotor) in the table proposed in EIC-4.
  - Describe the physical safeguards and justify the sub-surface setpoints.
  - Add to Discussion and Limitations:

  > "Admissibility is verified only in the DT. Because the identified DT underpredicts the trailing-edge undershoot, DT screening does not guarantee constraint satisfaction on the vehicle; in the present campaign, the smallest measured center-of-mass clearance above the obstacle was z/R = [value]."

### EIC-8: The Introduction motivates a broader problem than the experiments address, and the assumptions are not stated
- **Severity:** Major.
- **Location:** Sec. I, "A vehicle passing through a narrow tunnel may experience floor, ceiling, and lateral-wall interactions at the same time"
- **What is wrong:** About 1.5 columns of the Introduction cover market size, GNSS-denied inspection, tunnels, and wall and ceiling effects.

  The experiments instead involve:
  - one known rectangular obstacle;
  - planar flight at y = 0 at constant speed;
  - external Lighthouse positioning;
  - repeated identical missions.

  The learned correction is indexed by x and therefore requires the obstacle's position and geometry to be known in advance. It does not react to unknown or unmapped surfaces. The motivating applications (unknown cluttered spaces, degraded sensing) are therefore not addressed.
- **Why it matters:** Editors judge significance against the stated motivation, and the present framing invites an "applicability not demonstrated" verdict.
- **Proposed fix:**
  - Cut the Introduction by about half. Drop the market figures, and reduce the wall and ceiling paragraph to one sentence.
  - Motivate the work with missions that are repeated and mapped.
  - Add a "Problem Statement and Assumptions" paragraph, for example:

  > "We consider a repeated mission over a surface whose geometry and position are known, flown with external positioning. This setting isolates the ground-effect transient from perception and planning, and corresponds to inspection routes, warehouse aisles, or docking approaches that are flown repeatedly. Extending the approach to unmapped surfaces would require the reference correction to be conditioned on sensed geometry, which is beyond the scope of this paper."

### EIC-9: The title, abstract and keywords do not convey the problem, the result or the scope
- **Severity:** Major.
- **Location:** Abstract, "Experiments over a finite obstacle show that the proposed workflow constrains the dominant ground-effect response over the tested clearance range"
- **What is wrong:**
  - **Title.** It leads with the method name. "Applied to" signals an application note. "Vehicles" is plural although one vehicle is tested. "In Ground Effect" omits the actual task, which is altitude tracking across the entry to and exit from a finite obstacle.
  - **Abstract.** It describes the procedure but gives no numbers: no tracking-cost reduction, no identified parameters, no flight count, no comparator. The phrase "constrains the dominant ground-effect response" is vague.
  - **Keywords.** "Reinforcement Twinning" is not a standard index term, and "predictive control" is misleading (see EIC-6). Standard terms that are relevant here are missing.
- **Why it matters:** Desk decisions and reviewer invitations are based on the title and abstract, and these do not convey the result.
- **Proposed fix:**
  - **Title options:**
    - (a) "Reinforcement Twinning for Ground-Effect Compensation of a Nano Quadrotor Crossing a Finite Obstacle"
    - (b) "Digital-Twin-Guided Experiment Design and Bayesian Reference Refinement for Ground-Effect Compensation on a Nano Quadrotor"
  - **Proposed abstract (about 200 words; bracketed counts to be filled in):**

  > "Multirotors flying close to surfaces experience ground-effect thrust changes that a standard cascaded PID controller corrects only after a tracking error has developed. We study this problem experimentally with a Crazyflie 2.1+ nano quadrotor that crosses a finite obstacle at constant speed and at a nominal clearance of 1.5 rotor radii. We address it with Reinforcement Twinning (RT), in which a differentiable digital twin (DT) of the vehicle and its onboard controller is updated from flight data and used to design the next flight. In an information phase, twelve flights selected by E-optimal design identify a two-parameter ground-effect law whose amplitude is about twice the Cheeseman–Bennett value. The identified DT then synthesizes, offline, a position-scheduled altitude reference that is added to the setpoint of the unmodified PID controller, reducing the mean squared normalized altitude error over the obstacle region from 0.46 to 0.15. A surrogate that combines an affine DT-to-flight reward map with a Gaussian-process discrepancy then guides [N] further flights by Expected Improvement and reduces the error to 0.05, an improvement that the DT alone does not predict. At two off-nominal operating conditions, direct transfer of the learned correction helps at one condition but not at the other, and two additional guided flights recover an improvement."
  - **Keywords:** Aerial systems: mechanics and control; ground effect; digital twin; optimal experiment design; Bayesian optimization; Gaussian processes; sim-to-real transfer; feedforward reference shaping.

### EIC-10: Notation is overloaded and the language needs professional editing
- **Severity:** Minor.
- **Location:** Sec. II-A, "Let R•+ denote the best physical reward and ξ≥0 an optional exploration margin."
- **What is wrong:**
  - **Overloaded symbols:**
    - ξ is both the EI exploration margin and, in bold, the surrogate descriptor.
    - χ is both the operating-condition vector and the rotor-overlap fraction χ_i(x).
    - m is the mass, the model-update index and the Adam first moment.
    - π• is both "the deployed policy" and "the performance-oriented family."
    - R denotes the rotor radius and the rotation matrix, while the script ℛ denotes reward.
    - S is the sensitivity and the script 𝒮 is the normalized score.
    - d is both the disturbance and the motor distance.
  - **Fig. 1 notation.** Fig. 1 uses an input **z** (the text uses **u**) and the undefined symbols J_info and R̂•.
  - **Language errors:** "hass grown"; "These includes"; "substituting or support"; "if retained necessary"; "sub-centimetre" (British spelling); "changes-such as" (a hyphen used for an em dash); "but still poorly experimentally validated."
- **Why it matters:** Readers outside RT must track about 60 symbols across 46 equations. The overloads and errors slow review and suggest the draft is not yet final.
- **Proposed fix:**
  - Add a nomenclature table.
  - Rename the exploration margin (e.g., κ, or drop it, since ξ = 0 is used) and the overlap fraction (e.g., w_i(x)).
  - Align the Fig. 1 symbols with the text.
  - Copyedit into American English. Example for the first sentence of Sec. I: "Interest and investment in unmanned aerial vehicles (UAVs) have grown significantly in recent years."

---

## Recommendation and best venue

**Recommendation: Major revision. The paper is not submittable in its present form to the best-fitting venue.**

**Best venue: IEEE Transactions on Control Systems Technology, as a regular paper.** The contribution is a control-technology workflow validated on hardware. It combines identification, experiment design, model-based feedforward synthesis and data-driven sim-to-real correction around an unmodified production controller, which is the profile T-CST publishes. T-CST also accepts single-platform experimental studies when they include credible comparators and implementation detail. However, the 16-page T-CST cap means the current 20-page manuscript would be returned without review. Before submission, the authors should:
- condense it to ≤ 14 pages (EIC-1);
- state the contributions and their novelty relative to [9] (EIC-2);
- add at least the Cheeseman–Bennett-twin and DT-prior-free comparators, plus the flight and computation budget (EIC-3);
- reconcile the reported numbers in a single results table (EIC-4);
- fix the MPC and reference-governor terminology and the safety wording (EIC-6, EIC-7).

**Other venues:**
- **RA-L** is a viable fallback for a faster path. It requires a focused 8-page letter on the nominal-condition loop, with the generalization study dropped and the method compressed to about two pages; reviewers will still ask for comparators.
- **T-RO** is plausible only if the scope is broadened, for example to several surfaces (floor and ceiling), three-dimensional maneuvers or unmapped obstacles. T-RO expects broader robotics significance than a single-obstacle, single-axis correction, and 20 pages is its absolute maximum, with overlength charges from page 13.
- **T-Mech** is the weakest fit, because there is no mechatronic design or integration contribution: hardware and firmware are stock.

*Venue limits consulted:* [IEEE CSS – T-CST page](https://www.ieeecss.org/node/161) (regular papers ≤ 16 pages; overlength manuscripts returned without review); [IEEE RAS overlength policy](https://www.ieee-ras.org/about-ras/latest-news/new-ras-page-overlength-policy-announced) (T-RO ≤ 20 pages with charges for pp. 13–20; RA-L ≤ 8 pages with charges for pp. 7–8). The T-Mech limit could not be confirmed online, so the authors should check its current Information for Authors.
