# In-depth review of `main.tex`

## Scope and overall assessment

This review focuses on mathematical consistency, reproducibility, strength of claims, and scientific wording. Line numbers refer to the current `main.tex` (997 lines at the time of review).

The paper has a clear and potentially strong contribution: it combines sequential experiment design, differentiable model identification, offline model-based reference shaping, and a local reward-transfer surrogate in a physical MAV campaign. The overall narrative—identify a compact ground-effect correction, exploit it for a model-based policy, and then learn the residual DT-to-physical performance discrepancy—is coherent and accessible.

The main weaknesses are not the high-level idea but the precision with which the implementation is specified and the confidence attached to some conclusions. In particular:

1. The nominal and transferred local-policy parameterizations are not yet mathematically consistent with one another.
2. The Hessian/Fisher quantities are carefully called “approximations” in some places, but later prose sometimes treats them as calibrated uncertainty or information.
3. The GP/EI construction omits essential implementation details and treats experimental rewards as effectively noise-free, despite documented run-to-run variability.
4. “Safe” is used more strongly than the evidence supports; the method performs virtual constraint screening, not a formal or experimentally guaranteed safety analysis.
5. Several results rely on qualitative wording such as “few,” “slightly,” “markedly,” and “stable” where counts, uncertainty, or numerical criteria should be reported.

I would classify the manuscript as technically promising but requiring a substantial consistency and reproducibility revision before fine copy-editing.

## Highest-priority issues

### 1. Reconcile the local-policy definition with the transfer rule

**Locations:** lines 732–740, 762–771, 942, and 955–962.

At the nominal condition, Eq. (the current `eq:rt-policy`) defines

\[
\Delta z_\pi(x)=\Delta z_{\mathrm{MB}}(x)+R\,\mathbf b^\mathsf{T}(x)\mathbf a.
\]

This is an additive correction with a fixed dimensional scale (R). However, the transfer discussion says that the same coefficients are applied “relative to the condition-specific model-based policy” and that the correction is automatically reduced when the local model-based deformation is small. That automatic scaling does not follow from the displayed equation. If (\mathbf b(x)) is unchanged, the same (\mathbf a) produces the same altitude offset (R\mathbf b^T\mathbf a), regardless of the size of (\Delta z_{\mathrm{MB}}).

There is a second dimensional inconsistency in line 740: (\mathbf a) is introduced as dimensionless with entries in ([-1,1]), yet the text says that “each coordinate [is] scaled by (0.30R).” It is unclear whether (0.30R) is the basis amplitude, the GP input normalization, or the physical perturbation corresponding to (a_j=1).

This must be resolved with one explicit definition used everywhere. For example, choose either:

- **Fixed additive bases:**
  \[
  \Delta z_\pi(x;\chi)=\Delta z_{\mathrm{MB}}(x;\chi)
  +0.30R\sum_{j=1}^3 a_j b_j(x),
  \]
  in which case transfer does **not** automatically shrink with the local MB action; or

- **Condition-scaled bases:**
  \[
  \Delta z_\pi(x;\chi)=\Delta z_{\mathrm{MB}}(x;\chi)
  +\sum_{j=1}^3 a_j b_j(x;\chi),
  \]
  with (b_j(x;\chi)) explicitly constructed from, or normalized by, the condition-specific (\Delta z_{\mathrm{MB}}(x;\chi)).

Define the Gaussian centers, widths, peak normalization, units, and transfer transformation. Without these definitions, the nominal search and the off-nominal generalization cannot be reproduced, and the claim about automatic scaling is unsupported by the current equations.

### 2. Rework the uncertainty and Fisher-information interpretation

**Locations:** lines 637–693 and 807–828.

The paper appropriately states that the inverse-Hessian matrix is “not a calibrated finite-sample confidence region” and that the Fisher matrix is a comparative proxy. This caution should govern all subsequent wording.

The current covariance-like construction is

\[
\Sigma_\theta \simeq J_p(\widehat\theta_p)H^{-1}
\]

after eigenvalue flooring. Because (J_p) is an average of episode-wise mean squared errors and (H) is the Hessian of that averaged loss, this is not the usual residual-variance-times-Gauss–Newton-inverse formula unless a specific scaling derivation is supplied. The factor depends on the loss convention, the number of effective residuals, degrees of freedom, and the unequal episode weights. Spatial residual correlation further invalidates an ordinary independent-noise covariance interpretation. The manuscript partly acknowledges this, but it should do one of the following:

- derive the scaling from a stated residual likelihood and effective sample count;
- use a Gauss–Newton matrix with a clearly defined residual covariance; or
- rename the quantity consistently as a **local curvature indicator** and avoid covariance/confidence terminology.

The same applies to (2\sigma_{f_{\mathrm{GE}}}/f_{\mathrm{GE}}). The most accurate label is “twice the propagated local relative standard-deviation indicator,” not “confidence.” In line 828, replace “improved confidence” with “reduced propagated local uncertainty indicator.” Its decrease at large clearance is partly structural because (f_{\mathrm{GE}}\to1) and its parameter derivatives vanish; it is not by itself evidence of informative data there.

For the Fisher proxy:

- Explain whether every past sensitivity is recomputed under the current parameter estimate and current scaling at each design step. Line 680 suggests that it is, but this should be stated directly next to the definition.
- Explain how the exact-looking value (\lambda_{\min}=1.000) was scaled. If the curve was normalized, give the normalization. If it is unnormalized, report sufficient precision and units/scale so that “1.000” does not look artificially anchored.
- Do not call replaying the same measured baseline record an independent repeated experiment. It is a counterfactual **repeated-design information proxy**. Reusing an identical record does not reproduce the noise realizations that actual repetitions would contain.
- The division by (K_n) intentionally removes the statistical information gain associated with more independent samples. That is defensible for equal episode weighting, but it is another reason to call the result a design metric rather than Fisher information without qualification.

### 3. Make the GP/EI procedure reproducible and statistically honest

**Locations:** lines 198–242, 728–760, 879–915, and 953–975.

The generic model includes an observation-noise term (\varepsilon\), but the specialized implementation treats the cleaned mean reward as deterministic and adds only (10^{-8}) numerical jitter. The paper also shows nonzero run-to-run dispersion. These positions are in tension.

At minimum, report:

- the number of physical repetitions used to compute every reward class: baseline, MB, interpolated, Sobol, EI, transferred, and condition-specific EI;
- the exact cleaning and spatial resampling procedure used before averaging;
- whether the affine coefficients are refitted after every observation;
- whether affine-coefficient uncertainty is included in (\sigma_\bullet) (it currently appears not to be);
- whether (\sigma_\bullet) is the latent-function standard deviation or the predictive standard deviation of a new noisy reward;
- Matérn kernel amplitude and length-scale parameterization, ARD versus isotropic choice, bounds, fitting objective, optimizer, initialization, and random seed;
- the operating-condition kernel and input scaling used for the generalized surrogate;
- how EI is optimized over the 2,000 candidates and whether the same fixed library is reused after each update.

If only mean rewards are modeled, a practical improvement is to estimate the variance of each mean from repetitions and use a heteroscedastic observation-noise term. If most search policies were flown once, state that clearly and soften the interpretation of the GP posterior. A nearly noise-free GP built from a very small physical dataset can be severely overconfident; numerical jitter is not a statistical noise model.

Equation `eq:rt-surrogate-mean` also sets (\sigma_\bullet=\sigma_\delta). This omits uncertainty in (\gamma_0,\gamma_1), any uncertainty in the DT reward, and—depending on the intended EI definition—the observation noise. Either include these terms or state that EI uses a plug-in latent-discrepancy approximation.

The condition-aware extension needs particular care. With only nominal-condition data and then one or two points at a new condition, the way information is shared across conditions is determined almost entirely by the condition-kernel length scales. Those length scales and their fitting/data basis must be reported before the claim that a “condition-aware GP discrepancy” redirected the search can be evaluated.

### 4. Replace unqualified “safe” language with the actual guarantee

**Locations:** abstract; lines 58, 181, 185–199, 238, 245, 358–363, 691, 704–730, 738, 890, 975, 982, and 986.

The DT screens candidate policies against predicted clearance and other constraints. Because the DT is explicitly known to have structural error—especially near the obstacle edges—this is not a formal guarantee that the physical trajectory is safe. A hard check on a model trajectory is still model-dependent.

Use phrases such as:

- “DT-screened policy,”
- “policy satisfying the adopted virtual constraints,”
- “constraint-aware candidate set,” or
- “reduced-risk experimental search.”

Reserve “safe” for a statement backed by a robust margin, uncertainty set, barrier/certificate, verified physical envelope, or a documented abort procedure. If the experiments used conservative physical margins, a safety pilot, geofencing, emergency stop, or automatic abort criteria, report them explicitly.

### 5. Strengthen experimental accounting and statistical support

**Locations:** lines 563–575, 730, 782, 809–824, 901–928, and 942–975.

The manuscript never gives one complete count of physical interactions. Add a campaign table with, for each block, the number of distinct policies, repetitions per policy, total flights, operating condition, and role in training or validation. This is essential because “limited number,” “few interactions,” and “data efficient” are central claims.

The best-policy comparison should include uncertainty in the tracking cost or reward, not only a trajectory RMS band. For example, report per-flight (J_{\mathrm{trk}}), mean ± standard deviation (or a bootstrap interval for the mean difference), and the number of repetitions. A representative video trajectory cannot itself support repeatability; line 928 should attribute repeatability to the repeated quantitative trajectories, with the video used only as a qualitative illustration.

At off-nominal conditions, “slightly better” and “slightly worse” are not meaningful without repetition uncertainty. If those policies were tested once, say “the observed reward was higher/lower in the single evaluation” and avoid a general performance claim. If repeated, report the dispersion.

## Detailed mathematical and technical comments

### Generic RT formulation

**Lines 75–115:** The physical and DT state equations are reasonable, but the notation should distinguish a state estimate from a true physical state. The sentence “The state is not assumed to be directly available as in a black-box framework” is conceptually unclear: a black-box model does not imply that the state is observed. Suggested wording: “The physical state is not assumed to be measured directly; the RT loop receives only the observation vector in Eq. …”

**Lines 117–143:** The physical objective is an expected reward, whereas the later DT policy optimization uses a deterministic reward from one rollout. State what the expectation is over (initial conditions, measurement noise, process disturbances, or repeated flights) and whether the implemented optimizer approximates it with a nominal rollout.

The episode record in lines 134–142 does not match the surrounding prose. It omits the applied input history, initial-state reconstruction, and operating-condition vector, even though those are said to be required for factual replay. Define a complete record, for example

\[
\mathcal E^{(n)}=\{\mathbf o_\bullet^{(n)},\mathbf u_\bullet^{(n)},
\theta_\pi^{(n)},\chi^{(n)},\mathbf d^{(n)},\widehat{\mathbf s}_0^{(n)},
\mathcal R_\bullet^{(n)}\}.
\]

**Lines 147–156:** (\pi_\bullet) denotes both the deployed policy on the left-hand side and the performance-policy family in the second branch. Use a neutral symbol such as (\pi^{(n)}_{\mathrm{dep}}) on the left.

**Lines 171–181 and 682–691:** The displayed argmax says the E-optimal policy is selected, but the prose then permits a novelty check to override it. If this occurred in the experiments, the actual selection rule differs from the equation. Define a combined score, a lexicographic rule, or a precise tolerance such as “among candidates within (q\%) of the maximum E-optimal score, select the most novel.” Also define the novelty metric and threshold.

**Lines 183 and 693:** The optimizer convergence tolerances are numerical and explicit, but the stopping rule for the entire information phase remains qualitative (“appreciably,” “meaningful”). Provide numerical stopping criteria or state that the phase length was fixed in advance at 12 designed policies and that the diagnostics were assessed post hoc. Avoid presenting a post hoc stopping argument as an online stopping rule.

**Lines 200–222:** The descriptor changes from general (\boldsymbol\xi=[\theta_\pi,\chi]) to local (\mathbf a), then later to ((\mathbf a,\chi)). Give one hierarchy of definitions: global policy descriptor, local coordinates around MB, and generalized condition-aware descriptor.

**Lines 224–234:** The EI formula is correct for maximization under a Gaussian latent predictive distribution. State that (\mathcal R_\bullet^+) is the best observed reward and clarify how EI is modified, if at all, for noisy rewards.

**Figure 1, lines 247–354:** The diagram is not fully consistent with the equations:

- Block 2 uses input (\mathbf z), whereas the equations use (\mathbf u); (z) is elsewhere the altitude.
- Block 5 shows only (\theta_p^{(m+1)}\to\theta_{\pi,\mathrm{MB}}) for the performance branch, but after MB construction the actual operation is local candidate evaluation plus reward-transfer prediction.
- The bypass arrow gives only ((\theta_\pi,\mathcal R_\bullet)), while the surrogate also requires (\mathcal R_\circ), local coordinates, and possibly (\chi).

Revise the diagram after fixing the notation.

### Physical and digital models

**Lines 372–374:** The laboratory coordinate (x) is later shifted and still called (x). Introduce a separate plotted coordinate, such as (\widetilde x=(x-x_0)/R), to avoid equations and basis centers depending on an ambiguous origin.

“The Lighthouse deck is detected by two Lighthouse infrared stations” reverses the sensing relation. A clearer sentence is: “Two Lighthouse base stations illuminate the flight volume, and the onboard Lighthouse deck estimates the vehicle position from their infrared sweeps.”

**Lines 425–427:** Say “estimated vehicle state” rather than “vehicle state.” Also specify the logging and resampling frequencies, time synchronization, filtering, interpolation onto spatial positions, and treatment of dropped Lighthouse measurements.

**Lines 434–468:** The rigid-body equations require an explicit frame/sign convention. With (\mathbf g=[0,0,-g]^T) and (\mathbf F_B=[0,0,T]^T), the body (+z) axis must point along thrust at identity attitude. State this explicitly. Define whether (\mathbf R=R_{IB}) maps body to inertial coordinates and give the scalar-first quaternion kinematic matrix, or at least its sign convention. Also state how unit quaternion normalization is maintained numerically.

The text calls the model high fidelity and lists battery, actuator, and controller dynamics, but the displayed equations show only a reduced rigid-body/thrust subset and omit aerodynamic drag or other forces. Say explicitly that the equations summarize the terms relevant to this paper and identify all additional terms retained from Richardson et al. Otherwise the displayed model appears less complete than the prose claims.

**Lines 470–500:** Define the rotor numbering, location vectors, positive body axes, and signs (s_i), ideally with a small top-view diagram. This is needed to verify the roll/pitch moment equations and the way unequal ground-effect corrections generate moments.

**Lines 503–505:** “Both physical and DT missions start with a fully charged battery” needs an experimental protocol: Was the battery replaced or recharged for every flight? What initial-voltage tolerance was accepted? Across a long campaign, battery condition can otherwise be confounded with policy order.

### Ground-effect correction

**Lines 529–542:** The Cheeseman–Bennett statement should be more precise. The classical relation commonly appears as a rational correction containing (1/[1-(R/4z)^2]), depending on the controlled quantity and assumptions. The additive law (1+(1/16)(R/z)^2) is its leading far-field expansion, not generally an exact “rearrangement.” State the exact classical relation being used, what is held constant (power, rotor speed, or out-of-ground-effect thrust), and that (A=1/16,p=2) is an asymptotic initialization if that is the intended derivation.

**Lines 538–551:** Define (z_i) geometrically. Is it the vertical distance from the rotor center, the lowest point on the tilted disk, or the distance measured normal to the surface? Likewise, (\chi_i(x)) cannot be reproduced from “fraction of disk overlap” alone. Give its formula or numerical construction, including the disk projection under vehicle attitude and the finite obstacle extent in both (x) and (y). If lateral overlap is ignored because (y=0), state the approximation.

The power law is singular at (z_i=0). State its enforced domain and what happens numerically outside it. The policy clearance constraint does not automatically guarantee that every transient rotor-center clearance remains within the fitted domain unless this is checked on the actual predicted trajectory.

**Line 544:** The claim that velocity dependence is “limited” should be stated narrowly for the tested range and quantity supported by the cited work. The manuscript itself later shows condition-dependent transfer, so avoid implying that velocity effects are negligible.

### Identification and experiment design

**Line 570:** Use (\boldsymbol\theta_p=[A,p]^\mathsf T) consistently.

**Lines 577–598:** Define the sign of (e_z). Because the same reference is used, comparing tracking errors is equivalent to comparing altitudes, but say so. Also specify (\Omega_R), spatial grid resolution, and interpolation scheme. Equal episode weighting is clear and defensible.

**Lines 614–635:** The Adam derivation occupies substantial space but several more consequential details are missing: numerical bounds on (A,p), their projection behavior, Adam (\beta_1,\beta_2,\epsilon), maximum steps, and whether gradients were checked against finite differences. Condense the textbook explanation and use the space for these reproducibility items.

**Lines 637–660:** In addition to the scaling issue discussed above, report the Hessian eigenvalues before flooring and show whether the floor is active. If it is active, the propagated indicator may be dominated by the arbitrary (10^{-6}) floor.

**Lines 662–680:** The local scaling (D_\theta) uses marginal standard deviations but leaves correlation in the parameter coordinates. If the aim is to measure perturbations in posterior-standardized directions, a full whitening factor (for example a square root of (\Sigma_\theta)) would be more natural. The present diagonal scaling is acceptable as a numerical normalization, but should not be described as fully standardized joint uncertainty.

**Lines 693 and 824–828:** Correlation alone is a poor stopping diagnostic: it may remain high while the uncertainty ellipse shrinks substantially, or fall while both parameters remain poorly determined. Prefer a task-relevant criterion such as maximum propagated uncertainty in (f_{\mathrm{GE}}) over the control envelope, predicted improvement in (\lambda_{\min}), or change in replay error on held-out repeated flights.

### Model-based policy and reward

**Lines 697–707:** This is offline finite-horizon reference optimization, not standard receding-horizon MPC. The clarification in line 707 is helpful, but the introduction’s emphasis on MPC can still mislead. Use “offline model-predictive reference synthesis” or “finite-horizon optimal reference shaping” consistently, and avoid implying that an optimizer runs onboard.

**Lines 704 and 718–726:** The regularization terms depend on grid resolution unless normalized. (\|\Delta z/R\|_2^2) grows with the number of control points, while an unscaled second difference changes with (\Delta x). Define these as spatial averages/integrals or include the (\Delta x) scaling. Give an explicit formula and normalization for (\Phi_{\mathrm{clr}}); otherwise it may have units inconsistent with (J_{\mathrm{trk}}). Explain all endpoint projections and list the actual actuator, rate, acceleration, and state bounds used.

**Lines 709–717:** Define (N_{\mathcal R}) and (\Omega_{\mathcal R}) numerically. The reward (\mathcal R=1-J\) is mathematically valid and bounded above by 1, but it is unbounded below. State this, or use a nonnegative monotone transformation if bounded rewards are important to the surrogate.

**Lines 762–768:** (\mathcal S=1-J_\pi/J_{\mathrm{BL}}) is a fractional improvement over the condition-specific baseline. It maps every baseline to zero, but it does not necessarily make different conditions statistically equivalent or remove all “baseline difficulty.” Revise line 953 to say that it enables comparison of **relative cost reduction**, not that it places all missions on a universally common performance scale.

### Results and claims

**Lines 782–784:** The causal explanation of the trailing-edge undershoot is plausible, but motor speed or thrust-command evidence should be plotted or cited if the text states that the command is still reduced at the edge. Otherwise write “consistent with the thrust command remaining reduced.”

**Lines 809–824:** The numerical ratios support the statement that the designed policy gives more than an order of magnitude larger proxy value than the repeated-design baseline. Keep the word “proxy” in the result sentence. Also report whether these trajectories were selected online from the criterion exactly as shown or with the novelty override.

**Lines 813, 828, and 850:** Replace “confidence” with “local propagated uncertainty indicator.” The method does not produce calibrated confidence intervals.

**Lines 837–841:** The baseline replay changes little between the broad-domain and final models. This is an important and honest observation, but it weakens the claim that the additional six near-wall flights were necessary for the demonstrated control policy. Consider adding an ablation: optimize the MB policy with the broad-domain model and compare its predicted/physical performance with the final-model MB policy. That would directly test the control value of the second identification stage.

**Lines 861–865:** The reward improvements are useful, but give the corresponding tracking costs and repeated-flight uncertainty. “Contains sufficient causal information” is stronger than the evidence warrants; “was sufficiently predictive to produce an improved physical policy” is more defensible.

**Lines 892 and 901:** Replace ASCII hyphens used as parenthetical dashes (“changes-such as … downstream-and”) with proper em dashes or commas.

**Line 910:** Replace “after only a few EI-guided evaluations” with the exact number. “Improvement enabled by the learned GP discrepancy” should be softened to “improvement identified by the discrepancy-guided search”; the experiment does not isolate the GP from all other search choices.

**Line 928:** A representative single run illustrates behavior but does not establish repeatability. Suggested wording: “The representative frames are consistent with the ordering obtained from the five-run mean trajectories; repeatability is assessed from the repeated trajectory data, not from this single realization.”

**Lines 964–975:** At the high-speed condition, call (\mathcal S_\bullet=0.57) “poor relative to the local incumbent,” not simply “poor,” because it still represents a 57% cost reduction relative to that condition’s baseline. Do not infer that the MB solution was “near a favorable local optimum” from one nearby EI outcome alone; say it is “consistent with” that interpretation.

## Scientific wording and accessibility

### Suggested title

The current title is understandable but slightly awkward. A clearer option is:

> **Reinforcement Twinning for Micro Aerial Vehicles Operating in Ground Effect**

If the finite obstacle is central to novelty, consider:

> **Reinforcement Twinning for Trajectory Control of a Micro Aerial Vehicle over a Finite Ground-Effect Obstacle**

### Suggested abstract revision

> This work demonstrates Reinforcement Twinning (RT) for a micro aerial vehicle crossing a finite obstacle in ground effect. The framework couples a Crazyflie 2.1+ with a physics-based digital twin whose low-order ground-effect correction is identified sequentially from flight data. During an information phase, the twin uses the remaining parameter sensitivity to design informative, constraint-screened altitude references for the physical vehicle. During a performance phase, offline model-based optimization produces an anticipatory reference correction, and a Gaussian-process reward-transfer model uses paired simulated and experimental rewards to refine that correction despite residual model discrepancy. The optimized policy is deployed as a lightweight spatial reference governor while the standard onboard feedback controller remains unchanged. In the tested clearance range, the designed experiments increase a local E-optimal information metric and reduce the propagated uncertainty of the identified ground-effect law. The model-based reference improves trajectory tracking, and subsequent discrepancy-guided evaluations yield a further reduction in tracking cost. Tests at two additional speed-clearance conditions show that direct policy transfer is condition dependent and that limited local refinement can recover improved performance at one off-nominal condition. These results demonstrate how an adaptive digital twin can combine targeted physical experiments, offline policy design, and local data-driven correction without unrestricted model-free exploration. 

This version avoids “safe” as an unqualified result, distinguishes the information metric from calibrated uncertainty, and says exactly what is deployed onboard.

### Rewrite the opening paragraph

Line 40 contains several grammatical errors (“interest and investments … hass,” “substituting or support,” “These includes,” “small onboard sensor,” “if retained necessary”). A concise replacement is:

> Interest and investment in unmanned aerial vehicles (UAVs) have grown substantially in recent years. A recent European Commission outlook estimates that the European commercial drone market could reach EUR 14.5 billion by 2030 and exceed EUR 50 billion by 2033 [citation]. This growth is supported by low operating costs, rapid deployment, and the ability to supplement or replace human operators in hazardous missions. Applications range from logistics and emergency response to infrastructure inspection. Micro aerial vehicles (MAVs) are especially attractive in confined or cluttered environments, where access is limited and human entry may be dangerous. Their small size and onboard sensors can provide an initial map of a restricted area and help operators plan subsequent intervention.

### Representative sentence-level edits

| Location | Current issue | Suggested revision |
|---|---|---|
| Line 32 | “couples a Crazyflie … as physical environment with its Digital Twin whose…” is awkward | “couples a Crazyflie 2.1+ physical platform with a digital twin whose ground-effect correction is identified from flight data” |
| Line 43 | “elementary interactions” is unnatural | “canonical rotor–surface interactions” |
| Line 49 | “computational burden related to its online computation” is redundant | “computational cost of online optimization” |
| Line 51 | “but still poorly experimentally validated” | “but experimental validation remains limited” |
| Line 56 | “remaining GP discrepancy” | “remaining discrepancy, modeled by a Gaussian process” |
| Line 72 | “the DT must improve the physical model” understates its policy-design role | “the DT supports both model refinement and policy design” |
| Line 125 | capitalization varies | Use “digital twin” in ordinary prose; retain “DT” after definition |
| Line 158 | “a subsequent separated performance phase” | “a subsequent, separate performance phase” |
| Line 370 | “transition between OGE and IGE” occurs twice in a crossing | “entry into and exit from in-ground-effect conditions” |
| Line 374 | “the deck is detected by two stations” | “the onboard deck receives signals from two Lighthouse base stations” |
| Line 529 | “as the vehicle closely crosses” | “as the vehicle passes close above” |
| Line 542 | “rearranged with the same unknowns” may be mathematically inaccurate | “whose leading far-field term gives (A=1/16) and (p=2)” if that is the intended derivation |
| Line 544 | “limited” can sound universal | “reported to be modest over a comparable low-speed range” |
| Line 702 | “preferred over the time representation” | “preferred to a time-based representation” |
| Line 707 | “At every optimizer step” is clear, but “MPC” is potentially misleading | Use “offline finite-horizon reference optimization” throughout |
| Line 837 | “supports the value” is promotional | “shows that system-specific identification materially changes the fitted static correction” |
| Line 865 | “sufficient causal information” is too strong | “sufficient predictive structure to improve the physical policy” |
| Line 901 | “teach the surrogate” is informal | “provide data with which the surrogate can distinguish” |
| Line 910 | “after only a few” is vague | State the exact number of EI evaluations |
| Line 953 | “removes baseline difficulty” is too strong | “expresses performance as fractional cost reduction relative to the condition-specific baseline” |
| Line 973 | “performs poorly” lacks comparator | “performs poorly relative to the local model-based incumbent” |
| Line 980 | “well constrained” overstates a proxy | “locally constrained according to the adopted curvature-based indicator” |

### Style conventions to apply globally

- Use sentence case for “digital twin,” “expected improvement,” and “Gaussian process” in prose unless they begin a sentence; keep the abbreviations DT, EI, and GP.
- Use “ground effect” as a noun and “ground-effect” as an adjective.
- Prefer “vehicle” or “MAV” over switching among “drone,” “quadcopter,” and “physical environment” when referring to the same object.
- Use “near-surface” rather than “near-wall” in a ground-effect paper unless an actual vertical wall is meant.
- Replace “with few interactions” and “after a few evaluations” with exact counts.
- Distinguish “reference,” “command,” “policy,” “vehicle trajectory,” and “measured response.” They are not interchangeable.
- Avoid causal verbs (“produces,” “enables,” “demonstrates”) when the evidence is correlational or based on one comparison; use “is consistent with,” “identifies,” or “is associated with” as appropriate.
- Split very long paragraphs, especially lines 54, 358–363, and 980–986. The scientific content is good but dense.

## Structural recommendations

1. Add a notation table for (n,m,k,N,K_n,t,\theta_p,\theta_\pi,\theta_\iota,\mathbf a,\chi,\xi,\mathcal R,\mathcal S), and the (\bullet/\circ) subscripts.
2. Add a campaign-accounting table with flight counts and repetitions.
3. Add an implementation table with optimizer parameters, parameter bounds, policy bases, constraint values, GP hyperparameters, preprocessing, and random seeds.
4. Separate “method definition” from “campaign decisions.” At present, some choices are introduced generically, repeated in the specialized method, and then explained again in the results.
5. Consider moving the standard Adam and EI derivations to an appendix or shortening them. Use the recovered space for details unique to this experiment.
6. Include one ablation that connects the information phase to control: compare MB policies computed from the initial, broad-domain, and final identified models. This would show whether the information metric and reduced local uncertainty translate into control benefit.
7. State all limitations before the conclusion: static GE law, spatially correlated residuals, plug-in uncertainty, noise-free reward surrogate, local search, no formal safety guarantee, and sparse off-nominal coverage.

## LaTeX and bibliography findings

The complete sequence `pdflatex → bibtex → pdflatex → pdflatex` succeeds, and all citations and cross-references resolve on the final pass. Two persistent overfull equations remain:

- line 651: approximately 52.4 pt overfull (`eq:parameter-covariance`);
- line 717: approximately 20.3 pt overfull (`eq:reward`).

Break the covariance expression into an `aligned` environment and put the reward definition on a separate line from the tracking cost. Several underfull boxes also remain, but they are less serious.

`references.bib` ends with a paragraph of manuscript prose after the final BibTeX entry (currently line 201). BibTeX silently ignores it, but it should be removed because it is not bibliography data and can confuse future maintenance.

The bibliography otherwise builds. Check the central dependence on the unpublished `Mendez2026` manuscript: if the present paper relies on definitions or algorithms not fully reproduced here, readers may not be able to verify them. The current manuscript should be self-contained for every method used in the experiments.

## Recommended revision order

1. Fix the policy-coordinate/scaling inconsistency and define the off-nominal transfer mathematically.
2. Decide whether the Hessian/Fisher objects are statistical estimates or design indicators; revise equations and claims consistently.
3. Fully specify the GP, observation noise, repetitions, and EI implementation.
4. Add campaign counts, statistical comparisons, and exact stopping/selection criteria.
5. Replace “safe” with model-screening language unless a genuine guarantee is added.
6. Repair the model/frame/overlap definitions and the Cheeseman–Bennett statement.
7. Apply the prose edits and streamline repeated explanations.
8. Fix the two overfull equations and remove the stray text from `references.bib`.

After these changes, the paper’s main message should be both stronger and more credible: the contribution is not that a low-order twin becomes exact or formally safe, but that a deliberately imperfect, experimentally updated twin can organize physical experimentation and produce a useful control policy, while a local data-driven layer corrects the remaining performance-ranking error.
