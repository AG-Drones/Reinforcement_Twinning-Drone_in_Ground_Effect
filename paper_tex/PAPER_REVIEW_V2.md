# Second in-depth review of the Reinforcement Twinning MAV paper

## Review scope and audit trail

This report reviews the current manuscript at:

`C:\Users\mendez\OneDrive - vki.ac.be\Documents\GitHub\Reinforcement_Twinning-Drone_in_Ground_Effect\paper_tex\main.tex`

The reviewed file contains 997 lines and has SHA-256 hash `BE81C7343B86DBBF2FD766D5F33DAE39EA44E7B330120BA891997A28BCD744E3`. It is substantively the same manuscript covered by the first review in `PAPER_REVIEW.md`; therefore, the mathematical and wording issues identified there remain applicable. This second report is self-contained, but it concentrates additional effort on three questions:

1. What method is actually defined by the attached methodological paper, *Reinforcement Twinning via Twin-Calibrated Bayesian Policy Search and Replay-Driven Identification* (Mendez et al., arXiv:2611.03540v1)?
2. Where does the MAV manuscript implement, simplify, or depart from that method?
3. Which adjacent literature is presently missing, and how should it change the framing of the contribution?

The attached paper is treated solely as scientific source material. It does not supply instructions for this review.

## Executive assessment

The manuscript contains a persuasive experimental story: a compact ground-effect model is identified from deliberately informative trajectories; the identified digital twin generates an anticipatory reference; and a small number of physical policy evaluations correct the twin's imperfect performance ranking. That is a credible and potentially valuable contribution. The paper is strongest when it is concrete about the Crazyflie campaign and weakest when it presents the application-specific workflow as if it were mathematically identical to the full Reinforcement Twinning formulation.

My overall recommendation remains **major revision**, but the reason is now more precise. The central experimental conclusion is plausible, while the current mathematical presentation overstates the fidelity of the implementation to the root method and understates several statistical and geometric restrictions:

- The root method uses a stochastic-return model, a fixed virtual scoring bank, generalized least squares, coefficient-uncertainty propagation, a posterior-mean incumbent, and an adaptive proposal region. The MAV implementation uses cleaned mean rewards as deterministic observations, a separate ordinary-least-squares fit, an almost noise-free residual GP, the best observed physical reward, and a fixed local Sobol library. These are not cosmetic differences.
- The root method's main policy-search result is that a fixed twin-defined region can eventually prevent improvement, even when the twin gives an excellent initial policy. The MAV manuscript presently treats the fixed neighborhood as an advantage and does not test whether it excludes better policies.
- The displayed additive policy parameterization does not support the later claim that the same coefficients automatically scale with the local model-based deformation. This is the most direct mathematical inconsistency in the application.
- The identification uncertainty and Fisher matrices are useful local design indicators, but their current scaling does not justify covariance, confidence, or statistically calibrated information language.
- The ground-effect literature is too narrow for the physical claims made. Missing work on partial ground effect, finite surfaces, dynamic ground effect, multirotor recirculation, and learned ground-effect compensation directly bears on the model chosen here.
- The control literature is also incomplete. Since the experiment repeatedly executes the same spatial mission and learns a feedforward/reference correction, iterative learning control and learned residual dynamics are important comparators, not optional background.
- The manuscript repeatedly uses “safe” for policies that are screened only in a structurally imperfect twin. This is risk reduction, not a formal safety guarantee.

The paper should be positioned as **an experimental, application-specific two-stage variant of Reinforcement Twinning for local policy refinement**, unless the missing elements of the full method are implemented. That narrower description would still be scientifically interesting and would make the claims more defensible.

## Priority decision before revision

The authors should choose one of two paths.

### Path A - Align the implementation with the root method

This is the stronger methodological option. It requires, at minimum:

- a fixed bank of virtual scenarios or repeated stochastic rollouts for every policy;
- an explicit physical reward-noise model based on repeated flights;
- joint universal-kriging or equivalent generalized-least-squares calibration;
- propagation of affine-calibration uncertainty in the surrogate variance;
- use of the largest posterior mean among evaluated policies as the noisy-return incumbent;
- an adaptive proposal region that can expand when physical evidence reaches its boundary;
- an unambiguous, operating-condition-stable policy descriptor;
- clear resynchronization and replay rules; and
- validation that identification updates improve held-out replays rather than only the cumulative training loss.

### Path B - Present the paper as a deliberately simplified experimental variant

This is likely more realistic for the current dataset. The paper should then:

- shorten the generic RT derivation and cite the root paper for the complete formulation;
- explicitly list the application-specific simplifications;
- replace general claims about RT with claims about this sequential two-stage realization;
- call the performance phase “local twin-guided Bayesian refinement” rather than implying a globally corrective search;
- replace “safe” by “DT-screened” or “satisfying the adopted virtual constraints”; and
- state that posterior uncertainty is an interpolation heuristic because reward noise and calibration uncertainty are omitted.

Either path is acceptable. The current hybrid - presenting the full conceptual architecture while implementing a materially different statistical procedure - is the least defensible.

## What the attached methodological paper actually defines

### 1. Two coupled objectives, not one monolithic learning objective

The root paper distinguishes:

- a physical objective: maximize expected physical return over performance-policy parameters; and
- a twin objective: identify model parameters from factual replay of accumulated physical episodes.

Information-oriented and performance-oriented policies may use different parameterizations. A binary schedule decides which policy family is deployed at each physical episode. The two objectives are coupled through the archive, but they need not be combined into one scalar objective at every episode.

The MAV manuscript follows this high-level separation well. Its sequential information phase followed by a frozen-model performance phase is a legitimate schedule. It is, however, a restricted schedule rather than the complete alternating algorithm.

### 2. Factual replay and counterfactual rollout are different operations

For factual replay, the root method uses recorded actions and exogenous inputs. Before the replay branch, an observer or nudging window reconstructs a compatible twin state. After the branch, the twin evolves freely, without measurement correction. This separation is crucial: if observations continued to correct the twin during the identification window, the observer could hide model error and make a poor parameter set look accurate.

For counterfactual evaluation, the twin instead deploys a candidate policy from the same synchronized initial state. The resulting trajectory is a prediction, not a replay.

The MAV manuscript says that a reconstructed initial condition is used (lines 571 and 577), but does not specify the observer, reconstruction window, measured components, gain or covariance assumptions, branch time, or whether synchronization is recomputed after each parameter update. Those details are essential because errors in position, vertical velocity, attitude, PID integrators, rotor-speed states, or reference-governor state can be absorbed incorrectly into the two ground-effect parameters.

### 3. The virtual return is averaged over a fixed scoring bank

The root paper does not compare candidate policies using an arbitrary single virtual rollout. It constructs a fixed scoring bank containing initial states, measured exogenous-input scenarios, and fixed synthetic measurement-noise trajectories. Every candidate is evaluated on the same bank. This use of common random numbers makes policy differences reproducible and separates the policy effect from scenario-to-scenario variation.

In the MAV manuscript, the DT reward appears to come from one deterministic final twin and one nominal mission. If that is correct, `R_circle` is a scenario-specific score, not an estimate of expected physical return. That may be sufficient for a deterministic local reference-synthesis experiment, but the objective and interpretation must be narrowed. If multiple initial conditions or disturbances were used, the manuscript must define them and state that the same set was used for every policy.

### 4. The return surrogate is universal kriging with a calibrated twin trend

The root return model is

    R_phys(theta) = [1, R_twin(theta)] b + delta(theta) + epsilon_R,

where `b` contains the affine calibration coefficients, `delta` is a GP discrepancy, and `epsilon_R` is episode-to-episode return noise. The twin prediction is a calibrated trend, not a second objective and not a perfectly known offset.

For fixed covariance hyperparameters, the root paper estimates `b` by generalized least squares with the same covariance matrix used by the discrepancy model. The predictive variance contains both the usual kriging term and an additional term caused by uncertainty in `b`:

    variance = kriging variance
             + v(theta)^T [H^T V^-1 H]^-1 v(theta).

The MAV paper instead fits the affine term by ordinary least squares, then places a GP on its residuals, and finally sets `sigma_phys = sigma_delta` (lines 213-222 and 740). This plug-in construction ignores correlation during affine fitting and ignores calibration-coefficient uncertainty during acquisition. With a very small paired dataset, the omitted term can be important.

### 5. Physical return is stochastic

The root paper explicitly models variation between repeated physical episodes. It therefore defines the incumbent used by Expected Improvement as the **largest posterior mean among already evaluated policies**, rather than the largest noisy observed return.

The MAV paper defines the incumbent as the best physical reward (line 224) and implements rewards from cleaned mean trajectories as deterministic observations with only `10^-8` jitter (line 740). Yet the experiments visibly have run-to-run dispersion and some policies are averaged over five repetitions. Numerical jitter is not a statistical observation-noise model.

### 6. Twin guidance is local but physically correctable

The root method centers a proposal region on the current twin-optimal policy. Its coordinate half-widths are scaled using GP relevance lengths. Crucially, the region expands when the posterior-mean physical incumbent reaches one of its faces. This mechanism prevents the twin from permanently excluding directions in which physical evidence shows continued improvement.

The root benchmark demonstrates why this matters. The twin gives a strong initial advantage, but searches confined to a fixed twin-defined region are eventually overtaken by unguided alternatives. Adaptive expansion retains the early advantage while allowing physical evidence to correct the twin's geometry. The paper's central conclusion is therefore:

> Low prediction bias is not sufficient; the twin must provide a useful local ranking, and its guidance must leave room for correction by physical evidence.

The MAV manuscript uses a fixed 2,000-point Sobol library around the model-based policy and presents this confinement as a general benefit (lines 730-760, 865, 879, and 982). It never tests whether the best policy is close to a coefficient boundary or whether the region truncates a direction that remains promising. This is a material omission relative to the root method.

### 7. Twin updates are validated and archived policies are rescored

The root identification procedure combines global Bayesian optimization with gradient refinement and uses episode-disjoint training and validation. A proposed twin update is accepted only when validation improves. After a twin update, archived policy returns are recomputed under the new twin, the model-based reference is resynthesized, and the reward surrogate is recalibrated.

The MAV campaign intentionally freezes the twin before the performance phase. That is an acceptable simplification, but it eliminates this coupling. It also uses cumulative training loss without an explicitly held-out validation set. The manuscript should not imply that it has demonstrated the full jointly adapting RT loop.

### 8. Information design is a ranking device under misspecification

The root paper normalizes model parameters by their admissible box ranges, computes trajectory sensitivities, and uses an E-optimal Fisher proxy to rank excitation policies. It explicitly warns that under model misspecification and temporally correlated residuals the matrix does not quantify parameter uncertainty.

The MAV version improves one aspect: it evaluates the cumulative criterion `lambda_min(F_past + F_candidate)`, which better rewards complementarity than ranking a candidate in isolation. However, the manuscript then derives the parameter scaling from an inverse-Hessian “covariance,” adds a novelty override, and later speaks of confidence and well-constrained parameters. The caution of the root paper should be retained consistently.

## Root-to-application consistency matrix

| Element | Root paper | MAV manuscript | Assessment and required action |
|---|---|---|---|
| Physical objective | Expected return over stochastic episodes | Reward from cleaned mean trajectory | Define repetitions and noise, or state that the study optimizes a deterministic empirical mean at each tested policy. |
| Virtual score | Mean over a fixed scoring bank with common random numbers | Apparently one nominal deterministic rollout | Add a fixed scenario bank or narrow the expected-return interpretation. |
| Trend calibration | Joint GLS/universal kriging | OLS affine fit followed by residual GP | Use joint calibration or label it a plug-in approximation and include coefficient uncertainty. |
| Return noise | Explicit episode variance | `10^-8` jitter only | Estimate heteroscedastic noise from repetitions; jitter cannot replace it. |
| EI incumbent | Best posterior mean among tested policies | Best observed physical reward | Change the incumbent if observations are noisy. |
| Proposal geometry | Relevance-scaled and adaptively expanded | Fixed local Sobol library | Add an expansion rule, or explicitly claim only local refinement. |
| Twin updates | Scheduled during search; policies rescored after updates | Twin frozen throughout performance phase | Call this an application-specific two-stage variant. |
| State synchronization | Defined observer/nudging window, then free replay | “Reconstructed initial condition” | Specify state reconstruction and confirm no measurement correction during replay. |
| Identification acceptance | Episode-disjoint validation | Cumulative fit only | Add held-out or leave-one-episode-out validation and gradient checks. |
| Information criterion | E-optimal ranking with strong statistical caveats | Cumulative E-optimal proxy plus novelty override | Define the exact selection rule and retain proxy language throughout. |
| Policy identity | A parameter vector denotes the same controller when the twin changes | Coefficients are said to be relative to each condition-specific MB policy | Define a stable descriptor, or formulate a contextual mapping explicitly. |
| Safety | Admissibility is model-dependent | Repeatedly called safe | Use “DT-screened” unless a physical probabilistic or robust guarantee is supplied. |

## Major mathematical and methodological findings

### 1. The local policy equation contradicts the transfer claim

**Locations:** lines 732-740, 762-768, 942, and 955-962.

The nominal policy is defined as

    Delta z_pi(x) = Delta z_MB(x) + R b(x)^T a.

With fixed basis functions `b(x)`, the same coefficient vector `a` produces the same dimensional altitude correction at every operating condition. Nothing in this equation makes the correction shrink when the condition-specific model-based deformation is smaller.

Nevertheless, line 768 says that the coordinates are defined relative to the local model-based deformation and therefore scale automatically; line 942 repeats that the nominal coefficients are applied relative to the condition-specific model-based policy without imposing a fixed altitude offset. This does not follow from the displayed equation.

There is a second ambiguity at line 740: `a_j` is dimensionless and bounded in `[-1,1]`, but each input coordinate is said to be “scaled by 0.30R.” A GP input coordinate cannot simultaneously be a dimensionless amplitude and a dimensional length unless the transformation is explicitly defined.

Use one of the following mathematically complete alternatives.

**Fixed additive basis**

    Delta z_pi(x; chi)
      = Delta z_MB(x; chi) + 0.30 R sum_j a_j b_j(x),
      a_j in [-1, 1], max_x |b_j(x)| = 1.

This is simple and reproducible, but the transfer correction does not automatically scale with the local MB action.

**Condition-scaled basis**

    Delta z_pi(x; chi)
      = Delta z_MB(x; chi)
        + sum_j a_j s_j(chi) b_j(x; chi),

where `s_j(chi)` is an explicitly defined scale derived from the condition-specific MB correction. For example, `s_j` could be the local peak magnitude of `Delta z_MB` in a specified window, subject to a nonzero floor. This realizes the prose claim but changes the policy meaning across conditions.

**Stable global descriptor**

Define `a` as coefficients of fixed, dimensionless spatial modes in normalized mission coordinates and let the operating condition enter the policy map explicitly. This is the cleanest form for a contextual GP because the same `(a, chi)` has a reproducible physical meaning.

Whichever option is chosen, report basis centers, widths, normalization, units, sign convention, spatial-coordinate normalization, and the exact transformation used at off-nominal conditions.

### 2. The surrogate variance is understated

**Locations:** lines 198-242 and 740-760.

The manuscript first states a noisy model but later treats the campaign observations as deterministic. It then sets the physical posterior standard deviation equal to the residual-GP standard deviation. This omits:

- experimental variation in a new physical episode;
- uncertainty in a reward estimated from a finite number of repetitions;
- uncertainty in the affine intercept and slope;
- any uncertainty in the DT return;
- hyperparameter uncertainty; and
- mismatch introduced by the data-cleaning and trajectory-averaging procedure.

The root method at least includes return noise and affine-coefficient uncertainty. The MAV paper should use a heteroscedastic observation model whenever different policies have different numbers or variances of repetitions:

    y_i = f(a_i, chi_i) + epsilon_i,
    Var(epsilon_i) = s_i^2 / n_i,

where `s_i^2` is the sample variance of policy-level rewards and `n_i` is the repetition count. If most policies were flown once, report that limitation and use a shared noise estimate informed by repeated anchor policies.

The affine coefficients and covariance hyperparameters should be fitted jointly or by alternating generalized least squares and marginal likelihood, as in the root paper. At minimum, add the universal-kriging calibration term to the latent variance. Without it, EI can be overconfident precisely when the archive is small.

### 3. The EI incumbent is inconsistent with noisy physical rewards

**Locations:** lines 224-234 and 747-760.

Using the largest observed reward as `R_phys^+` is appropriate only if every reward is effectively deterministic. With experimental noise it introduces winner's curse: an unusually favorable realization becomes the target that future candidates must beat. The root paper avoids this by using the largest posterior mean among evaluated policies.

Recommended definition:

    mu_plus = max over evaluated policies of mu_phys(a_i, chi_i),

and use `mu_plus` in EI. If policy rewards are five-run means with negligible uncertainty relative to the observed gains, demonstrate this numerically rather than assuming it.

### 4. A fixed local library conflicts with the root paper's central result

**Locations:** lines 199, 238, 730, 738, 755-760, 865, 879-890, and 982.

The manuscript can validly study a local neighborhood. It cannot infer from that study that twin-guided confinement is generally beneficial. A fixed region makes the result conditional on a researcher-chosen policy basis and bounds. The best observed candidate may simply be the best inside that library.

At minimum, report:

- the final best coefficient vector and its distance from every face of `[-1,1]^3`;
- the GP length scales in the same normalized coordinates;
- whether EI's maximizer ever lies on or near a boundary;
- whether the 2,000-point library was fixed throughout the sequence;
- the minimum candidate separation and its metric; and
- a sensitivity study with an enlarged candidate region or shifted basis amplitudes.

A root-consistent expansion rule could double the half-width of coordinate `j` when the posterior-mean incumbent lies within a specified fraction of face `j`, subject to the outer admissible policy set and renewed DT screening. If no expansion is implemented, use “local refinement around the model-based policy” consistently and avoid claims about the broader policy optimum.

### 5. The expected-return objective is not connected to the implemented DT score

**Locations:** lines 117-123, 185-194, 709-726, and 740.

Equation 4 defines an expected physical reward. The specialized model-based optimization appears to use one deterministic trajectory from one identified twin and one nominal condition. This is not necessarily wrong, but the notation implies robustness to initial-condition, measurement, actuation, and disturbance variation that the implementation does not establish.

Define what is random in the physical objective and what expectation is approximated. If the study intentionally optimizes a nominal mission, write:

> For the present deterministic virtual campaign, `R_circle` is the nominal closed-loop mission reward under the synchronized initial condition and prescribed operating condition; it is not an estimate of an expectation over environmental uncertainty.

If repeated virtual scenarios are available, define the fixed bank and use the average in both model-based synthesis and surrogate calibration.

### 6. State synchronization is under-specified and may confound identification

**Locations:** lines 94-115, 356-370, and 568-598.

The manuscript must explain how the initial twin state is reconstructed for each replay. At least the following states matter:

- position and velocity;
- attitude and angular rate;
- cascaded-PID integral and derivative/filter states;
- motor or rotor-speed states;
- battery/voltage correction state; and
- reference-governor or interpolation state.

The review cannot determine whether only position is reset, whether all controller states are reinitialized, or whether a pre-obstacle synchronization window is used. Because the identified parameters act through closed-loop tracking, a biased vertical velocity or PID integrator at the branch can look like ground-effect mismatch.

Add a synchronization subsection containing: measured channels, estimator or nudging equations, window duration, gains/noise assumptions, branch location, initialized states, and confirmation that the twin is not corrected by measurements after the replay branch. State whether synchronization is rerun after every parameter update.

### 7. The inverse-Hessian scaling is not a calibrated covariance

**Locations:** lines 637-660 and 807-841.

The proposed indicator is

    Sigma_theta approximately J_p(theta_hat) H^-1,

after Hessian eigenvalue flooring. Because `J_p` is an average of episode-wise normalized mean-squared errors, this is not the usual residual-variance-times-information-inverse expression without a derivation that accounts for:

- the factor implied by differentiating a squared-error objective;
- the number of effective residuals and degrees of freedom;
- unequal episode lengths and equal episode weighting;
- spatial correlation after resampling and filtering;
- heteroscedastic tracking error; and
- the active parameter bounds.

Eigenvalue flooring also makes the magnitude depend on the arbitrary threshold `10^-6`. The paper acknowledges some of this at lines 652 and 660, but later calls the resulting change “improved confidence” (line 828) and says the model is “well constrained” (line 980).

The simplest defensible revision is to rename all uses as a **local curvature indicator** and avoid covariance or confidence terminology. A stronger revision would define a residual likelihood and use a sandwich covariance or bootstrap over entire episodes. Episode bootstrap is especially attractive because it preserves within-trajectory correlation.

### 8. The Fisher matrix is useful for ranking, not evidence of quantified information gain

**Locations:** lines 662-693 and 809-850.

The cumulative proxy

    F = sum_n Sbar_n^T Sbar_n / (K_n sigma_e^2)

is reasonable as a dimensionless local design metric, but several interpretations need correction.

- Dividing by `K_n` deliberately prevents longer records from carrying more weight. This is an episode-balanced design score, not the Fisher information that independent samples would provide.
- The residuals are spatially correlated. Using `sigma_e^2 I` is therefore not the inverse observation covariance required by a statistical Fisher matrix.
- Sensitivities are evaluated at an estimated parameter point under a misspecified static model. They are local and model-dependent.
- `D_theta` is itself derived from the uncalibrated inverse-Hessian indicator. If it changes after each fit, the meaning of `lambda_min` changes unless all archived experiments are recomputed with a common final scaling.
- The “repeated baseline” is a counterfactual repeated-design calculation using the same measured record. It does not represent statistically independent repeated experiments.

The post-campaign recomputation with a common final twin and scale is a good practice and should be moved earlier in the explanation. Replace statements such as “provides more than one order of magnitude more information” by “has a cumulative E-optimal design score more than one order of magnitude larger under the adopted final local scaling.”

The value `lambda_min = 1.000` after the broad stage also needs explanation. If normalized for plotting, report the normalization. If not normalized, report enough digits and state that the numerical scale is dimensionless and depends on the adopted scaling.

### 9. The novelty override makes the displayed optimizer incomplete

**Locations:** lines 171-181 and 682-691.

The displayed rule is an exact argmax of the E-optimal criterion, but the prose says a separate novelty check may select a less informative candidate. Then the displayed optimization is not the actual selection algorithm.

Define one reproducible rule, for example:

    Candidate set Q_safe is ranked by lambda_min(F_past + F_candidate).
    Starting from the highest score, select the first candidate whose trajectory
    distance from every archived experiment exceeds d_min.

Alternatively, use a constrained optimization or a scalarized criterion with a stated weight. Report the trajectory-distance metric, normalization, threshold, and which episodes were changed by the novelty rule.

### 10. The identification fit lacks out-of-sample validation

**Locations:** lines 577-635 and 807-850.

The cumulative loss always decreases or stabilizes when fitted to accumulated episodes; that alone does not show that the inferred `A,p` generalize. The root method uses episode-disjoint validation and accepts parameter updates only when validation improves.

With 13 records, full train/validation splitting may be expensive, but the manuscript can perform:

- leave-one-episode-out replay errors;
- broad-domain-to-near-wall and near-wall-to-broad-domain cross-validation;
- a held-out baseline repetition not used for fitting;
- parameter bootstrap over episodes; and
- comparison of analytic/reverse-mode gradients with central differences at several parameter points.

At least one such test is needed before describing the final parameters as converged in a predictive sense. Numerical optimizer convergence is not model validation.

### 11. The static power law is more restrictive than the literature discussion admits

**Locations:** lines 529-551 and 837-850.

The model

    f_GE(z) = 1 + A (R/z)^p

is monotone for `A>0, p>0`, singular as `z -> 0`, and always predicts thrust augmentation. The overlap factor makes the force turn on smoothly at obstacle edges but does not introduce wake memory, edge-induced asymmetry beyond disk overlap, negative ground effect, or rotor-rotor/fountain-flow interaction.

Recent multirotor results make these restrictions scientifically important. Tanabe et al. found non-monotonic power behavior near a rotor-radius clearance due to recirculation. Lei et al. reported a negative ground-effect region near `h/R approximately 1.5` for a close-spacing quadrotor. Sanchez-Cuevas et al. experimentally characterized partial ground effect, precisely the regime encountered while individual rotors cross a finite obstacle edge. He et al. showed that ground effect during landing can depend on velocity, throttle, platform motion, and past states.

The manuscript does acknowledge static-model limitations, but it should add these references and say explicitly that the two-parameter law is an intentionally misspecified control-oriented basis. The fitted `A,p` are **effective closed-loop parameters for the tested vehicle, surface geometry, speed, and preprocessing**, not universal aerodynamic coefficients.

Also define:

- lower and upper admissible bounds on `A` and `p`;
- how `z_i` is computed for tilted rotors and a finite-height obstacle;
- what happens outside the modeled clearance interval;
- whether `f_GE` is clipped;
- whether overlap is computed in the rotor-disk plane or its horizontal projection; and
- whether the correction changes thrust only or also moments/drag through individual rotor forces.

### 12. The cross-condition normalization does not put missions on a common statistical scale

**Locations:** lines 762-768 and 953-975.

The score

    S = 1 - J_pi / J_BL

sets each condition's baseline to zero and expresses fractional cost reduction. This is useful, but it does not by itself make different missions statistically commensurate. If `J_BL` is small, the ratio amplifies measurement noise; if the error distributions or physical consequences differ, equal values of `S` do not imply equal difficulty or risk. The DT and physical scores are normalized independently, so their numerical agreement can also improve or deteriorate through different denominators.

Replace “places missions ... on the same improvement scale” by “expresses performance as a fractional reduction relative to the condition-specific baseline.” Report uncertainty in `J_BL` and propagate it into `S`, especially with only five repetitions.

### 13. The contextual GP claim is too strong for the available data

**Locations:** lines 955-975.

The generalized discrepancy has at least five inputs: three policy coefficients plus clearance and velocity, and possibly an implicit condition-dependent policy mapping. The paper then adds only two physical evaluations at one off-nominal condition. A GP in this space is driven predominantly by its prior kernel and input scaling, not by the data.

The manuscript correctly calls this a proof of concept, but phrases such as “the condition-aware GP discrepancy redirected the search” still require the following details:

- product or additive kernel structure;
- kernel family per policy and context dimension;
- normalization of `a`, `z*/R`, and `v_x*/v_h`;
- length-scale bounds and initialization;
- whether hyperparameters are refitted with only the new points;
- whether nominal data are pooled with off-nominal data; and
- sensitivity of the selected candidates to plausible context length scales.

Krause and Ong's contextual GP bandit formulation is the natural theoretical reference. The present data support only local adaptation at one new context, not learning a condition-to-policy map.

### 14. “Safe” is not supported by the adopted mechanism

**Locations:** abstract; lines 47-58, 181-199, 238, 245, 358-363, 691, 704-738, 890, 975, 982, and 986.

The twin is explicitly structurally imperfect near obstacle edges. A hard constraint checked in that twin cannot guarantee the physical constraint. The `0.5R` penalty plus final virtual rejection is a model-dependent screen. It is valuable, but it is not equivalent to robust, probabilistic, or certified safe optimization.

Use:

- “DT-screened candidate”;
- “candidate satisfying the adopted virtual constraints”;
- “constraint-aware local search”;
- “conservative experimental envelope”; or
- “reduced-risk search.”

Reserve “safe” for a statement backed by uncertainty margins, a verified robust set, a safety filter/barrier, SafeOpt-style assumptions, or a documented physical abort mechanism. If the campaign used geofencing, pilot takeover, automatic abort thresholds, protective structures, or conservative clearance margins, report them as experimental risk controls rather than mathematical guarantees.

### 15. Experimental accounting is still incomplete

The results say that baseline and final comparison policies use five repetitions, but the number of repetitions for interpolation, Sobol, EI, transferred, and condition-specific EI policies is not systematically stated. A reader cannot reconstruct the effective physical budget or the observation variance.

Add a campaign table with one row per policy class and columns for:

- purpose;
- number of distinct policies;
- repetitions per policy;
- total physical episodes;
- whether used for identification, surrogate fitting, selection, or only assessment;
- operating condition;
- DT screening criteria; and
- reward mean and standard error.

Report every tested policy coefficient and reward in a supplement or machine-readable table. “A few evaluations” should be replaced everywhere by exact counts.

## Additional mathematical checks

### Ground-effect model domain and differentiability

For `A>0` and `p>0`, `f_GE` is differentiable for `z>0`, strictly decreasing with clearance, and approaches one as clearance grows. It is singular at zero. The `0.5R` virtual clearance bound keeps the optimizer away from the singularity only if the bound is enforced on every rotor throughout every differentiated rollout. State whether the clearance penalty is smooth at the boundary and whether the final hard check uses the same geometric definition.

The disk-overlap fraction `chi_i(x)` is said to vary continuously. Give its analytic formula. For a circular disk crossing a straight edge, the exact circular-segment area is continuous but has derivatives that become steep near first/last contact. If a smoothed approximation is used for reverse-mode differentiation, report it and its smoothing width. A purely streamwise overlap ignores lateral position and attitude unless these are proved negligible.

### Reward definition

`R = 1 - J_trk` is dimensionless and monotone in tracking MSE, so it is adequate for ranking. It is not naturally bounded below, and differences near one correspond directly to MSE differences. Report the physical RMSE or maximum clearance error alongside reward so that a gain from 0.855 to 0.952 has an interpretable magnitude.

Specify `Omega_R`, its spatial limits, resampling resolution, and whether all policies are compared at the same positions. Explain whether data cleaning removes failed or extreme flights and whether the rule was fixed before inspecting policy performance.

### Objective regularization

In `J_MB`, the norms of the amplitude and curvature vectors are not divided by the number of grid points. Their relative weight therefore depends on the discretization. Because the nodes are separated by `Delta x approximately R`, this may be fixed in the present experiment, but the formulation is not grid-invariant. Prefer discrete approximations of spatial integrals, including appropriate powers of `Delta x`, or state that the weights are tied to the adopted grid.

The clearance term is described as enforcing safety, but a finite penalty does not enforce a hard constraint. The final replay rejection provides a hard virtual check; distinguish the soft optimization penalty from the final admissibility test.

### Parameter identifiability

With

    f_GE - 1 = A (R/z)^p,

the local sensitivities are

    d f / d A = (R/z)^p,
    d f / d p = A (R/z)^p log(R/z).

At `z=R`, the second sensitivity vanishes because `log(R/z)=0`; at large clearance both sensitivities vanish; over a narrow range they can be strongly collinear. This analytically explains the observed correlation. Add this two-line derivation. It gives the reader a physical reason for the broad/near-wall design and prevents correlation from appearing to be only an optimizer artifact.

The near-wall domain includes `z/R` both below and above one, which changes the sign of the exponent sensitivity. That is potentially valuable for decorrelation and should be discussed explicitly.

### Repeated-baseline counterfactual

Repeating the same sensitivity matrix twelve times makes the Fisher proxy grow linearly even though it contributes no new sensitivity direction. The smallest eigenvalue can still grow if the original matrix is full rank, but this calculation measures repeated-design information under independent-noise assumptions. Reusing the identical measured record does not create independent residuals. Call it a “repeated-design counterfactual under the adopted proxy,” not repeated experimental evidence.

## Scientific wording and clarity review

### Opening paragraph

Line 40 contains several grammatical errors and should be rewritten completely. Suggested replacement:

> Interest and investment in unmanned aerial vehicles (UAVs) have grown substantially in recent years. A recent European Commission outlook estimates the European commercial drone market at approximately EUR 14.5 billion by 2030 and more than EUR 50 billion by 2033. This growth is supported by low operating costs, rapid deployment, and the ability to assist or replace human operators in hazardous tasks. Applications range from logistics and emergency response to infrastructure inspection. Micro aerial vehicles (MAVs) are particularly attractive in confined environments, where their small size enables access to locations that are difficult or unsafe for human operators.

Delete the claims about “preliminary mapping ... to guide deployment of human operations if retained necessary” unless this specific application is needed and supported.

### Contribution paragraph

Lines 60-62 should state what is demonstrated, not imply full implementation of the generic loop. Suggested replacement:

> This paper presents a two-stage experimental realization of Reinforcement Twinning on a Crazyflie 2.1+ crossing a finite obstacle in ground effect. In the first stage, sequentially designed reference trajectories identify two effective parameters of a deliberately low-order ground-effect correction. In the second stage, the identified twin generates an offline model-based reference, after which a local Gaussian-process discrepancy model uses paired virtual and physical rewards to refine the policy. The twin is frozen during the second stage; thus, the experiment isolates the roles of information-oriented identification and performance-oriented local policy refinement rather than implementing fully interleaved model and policy updates.

### Generic framework section

The generic RT section is long relative to the application and reproduces a simplified version of the root paper. This creates avoidable inconsistencies. Reduce it to four items:

1. physical and twin episode definitions;
2. factual replay versus counterfactual rollout;
3. the distinction between information and performance episodes; and
4. a short statement that the present campaign uses a sequential, frozen-twin specialization.

Then cite arXiv:2611.03540 for the scoring bank, universal-kriging surrogate, adaptive proposal region, and full algorithm. The application section should define exactly what was implemented.

### Recurring word replacements

| Current wording | Preferred wording |
|---|---|
| safe policy | DT-screened policy, unless a formal guarantee is shown |
| safety envelope | adopted virtual admissibility region |
| confidence improved | propagated local curvature indicator decreased |
| Fisher information | E-optimal Fisher proxy or local sensitivity-information score |
| repeated baseline experiments | repeated-baseline design counterfactual |
| converged model | numerically converged parameter fit; use validated only after held-out testing |
| optimal policy | best policy found in the tested/admissible library |
| few evaluations | exact number of distinct policies and flights |
| markedly/slightly | numerical change with uncertainty |
| on the same scale | expressed as fractional improvement from the condition-specific baseline |
| GP uncertainty | surrogate interpolation uncertainty, unless noise and calibration uncertainty are included |
| local GP discrepancy redirected the search | after the first new observation, the chosen second candidate changed under the specified fitted surrogate |

### Claims needing numerical support

- “Velocity dependence is limited” at line 544 should be restricted to the cited range and platform; the present off-nominal tests show that velocity changes the discrepancy.
- “Substantial,” “marked,” “slight,” and “modest” should be accompanied by rewards, RMSE, maximum error, and standard error.
- “Repeatable control strategy” at line 910 requires the number of independent high-reward policies and their repetitions.
- “Well constrained” at line 980 should be replaced by a statement about the local indicator and tested clearance interval.
- “Data efficiency” should be reported as the exact number of physical episodes required to exceed the MB policy, including initialization policies and repetitions.

### Abstract guidance

The abstract should avoid “safe” and should name the local nature of the search. A defensible result sentence would be:

> The identified twin improves the physical tracking reward from approximately 0.54 to 0.85 relative to the baseline controller. Local twin-guided Bayesian refinement then identifies a policy with reward approximately 0.95 within the tested three-parameter policy family. Off-nominal tests show that direct coefficient transfer is condition dependent, while two additional local evaluations recover an improvement at the more challenging condition.

Add repetition counts or uncertainty if space permits. Do not call the final policy globally optimal.

## Parallel literature review

### Assessment of the current bibliography

The bibliography covers the classical Cheeseman-Bennett relation, one forward-flight multirotor study, a recent near-surface experimental paper, general system identification, optimal experimental design, Gaussian processes, multifidelity calibration, and the authors' RT lineage. It is less complete in the areas most directly adjacent to the experiment:

1. partial and finite ground effect at obstacle edges;
2. dynamic and history-dependent ground effect;
3. multirotor fountain flow and non-monotonic thrust/power response;
4. ground-effect-specific control and adaptive compensation;
5. learned residual dynamics for quadrotor control;
6. iterative learning control for repeated spatial missions;
7. contextual Bayesian optimization across operating conditions; and
8. safe or trust-region Bayesian optimization, which is needed to distinguish screening from guarantees and fixed from adaptive local search.

The bibliography file also contains a full prose paragraph after the `CheesemanBennett1955` entry. Remove that paragraph from `references.bib`; it belongs in `main.tex`. BibTeX currently completes without warning, but free manuscript text in a database file is fragile and can break other parsers or future edits.

### Highest-priority additions

#### A. Ground-effect physics and finite surfaces

1. **Sanchez-Cuevas, Heredia, and Ollero (2017), “Characterization of the Aerodynamic Ground Effect and Its Influence in Multirotor Control,” DOI 10.1155/2017/1823056.** This is the most important missing reference. It experimentally treats multirotor and partial ground effect and connects the phenomenon to control. Cite it in lines 43-47 and in the finite-obstacle model discussion at lines 546-551.

2. **Del Cont Bernard, Riccardi, Giurato, and Lovera (2017), “A Dynamic Analysis of Ground Effect for a Quadrotor Platform,” DOI 10.1016/j.ifacol.2017.08.1500.** This provides direct experimental evidence that dynamic ground effect differs from static characterization. Cite it where the manuscript admits omitted edge transients (line 544).

3. **Xin, Li, Chen, and Liu (2017), “Theoretical Model and Experiment on Rotor in Finite Ground Effect,” DOI 10.7527/S1000-6893.2016.0221.** This is directly relevant to the finite obstacle rather than an extended plane. Cite it before introducing the overlap model.

4. **Prothin, Fernandez Escudero, Doue, and Jardin (2019), “Aerodynamics of MAV Rotors in Ground and Corner Effect,” DOI 10.1177/1756829319861596.** This strengthens the confined-flight motivation and shows why isolated surface effects do not exhaust the physics.

5. **Tanabe, Sugawara, Sunada, Yonezawa, and Tokutake (2021), “Quadrotor Drone Hovering in Ground Effect,” DOI 10.20965/jrm.2021.p0339.** It reports multirotor recirculation and non-monotonic power behavior, which qualifies the monotone power-law assumption.

6. **Wolf et al. (2024), “Volumetric Wake Investigation of a Free-Flying Quadcopter Using Shake-The-Box Lagrangian Particle Tracking,” DOI 10.1007/s00348-024-03880-3.** It supplies vehicle-level flow evidence for wake merging, recirculation, and anisotropic outwash in ground effect.

7. **Lei et al. (2026), “Interactional Aerodynamics and Flow Characteristics of a Quadrotor with Ground Effect,” DOI 10.1063/5.0337114.** This very recent study reports non-monotonic thrust and a negative-ground-effect region near `h/R approximately 1.5` for its geometry. It should be discussed as evidence that the identified monotone law is an effective model over the tested campaign, not a general quadrotor law.

#### B. Ground-effect modeling and control

8. **Wei, Chan, Lee, and Kong (2019), “Mitigating Ground Effect on Mini Quadcopters with Model Reference Adaptive Control,” DOI 10.1007/s41315-019-00098-z.** This is a direct experimental control comparator: platform-specific GE identification followed by adaptive compensation.

9. **Xu et al. (2022), “Identification of Ground Effect and Intelligent Control of Unmanned Aerial Vehicles,” DOI 10.1016/j.ast.2022.107976.** It compares adaptive and neural compensation with PID using experiments. Cite it when motivating why a low-order model plus data-driven correction is attractive.

10. **He et al. (2024), “Data-Driven Modeling of Ground Effect for UAV Landing on a Vertical Oscillating Platform,” DOI 10.1109/IROS58592.2024.10802474.** This is particularly relevant to the manuscript's stated limitation: it models velocity, throttle, platform motion, and history dependence while remaining parsimonious enough for onboard use.

11. **Yang et al. (2025), “Ground-Effect-Aware Modeling and Control for Multicopters,” arXiv:2506.19424.** Use as a clearly labeled preprint. It includes force, torque, rotor-drag, and mixing effects and offers a broader counterpoint to thrust-only correction.

#### C. Data-driven and repeated-mission control

12. **Torrente, Kaufmann, Foehn, and Scaramuzza (2021), “Data-Driven MPC for Quadrotors,” DOI 10.1109/LRA.2021.3061307.** This is a strong comparator for embedding GP residual dynamics in model-based quadrotor control. It helps clarify that the present paper learns a policy-level reward discrepancy rather than a state-transition residual.

13. **Meraglia and Lovera (2021), “Smoother-Based Iterative Learning Control for UAV Trajectory Tracking,” DOI 10.1109/LCSYS.2021.3116263.** The present mission is repeated along the same spatial path, and the learned reference is a feedforward correction. ILC therefore belongs in the introduction and discussion. The manuscript should explain why RT is preferable here: it uses a physics-based twin to design informative experiments and supplies a policy-level uncertainty model, whereas ILC directly updates repeated-task feedforward control.

#### D. Bayesian policy search and context

14. **Krause and Ong (2011), “Contextual Gaussian Process Bandit Optimization.”** This is the natural reference for modeling reward jointly over action/policy and operating context. Cite it in the generalized surrogate section, while emphasizing that the present data do not establish contextual regret or a learned continuous mapping.

15. **Eriksson et al. (2019), “Scalable Global Optimization via Local Bayesian Optimization.”** TuRBO is relevant to the distinction between a fixed local region and an adaptive trust region. It does not need to be implemented, but it provides terminology and precedent.

16. **Sui et al. (2015), “Safe Exploration for Optimization with Gaussian Processes,” and Sui et al. (2018), “Stagewise Safe Bayesian Optimization with Gaussian Processes.”** These references help explain what formal safe BO would require. Cite them only if the paper retains a paragraph distinguishing DT screening from probabilistic safety guarantees.

### Suggested literature-review structure

The introduction would be clearer as four short streams rather than one long progression.

**Stream 1 - Physical problem.** Review classical rotor GE, then multirotor, partial/finite-surface, and dynamic effects. End with the gap: a compact model is needed for flight control, but the obstacle-edge response is too complex for a static law to rank all policies accurately.

**Stream 2 - Existing control responses.** Cover PID limitations, adaptive/MRAC and learned GE compensation, data-driven MPC, and ILC for repeated trajectories. End with the gap: these methods either focus on disturbance compensation, learn a dynamics residual, or exploit repetition, but do not jointly design experiments for twin identification and use paired virtual/physical returns for local policy selection.

**Stream 3 - RT method.** Summarize the attached root paper accurately: synchronized factual replay, information episodes, calibrated twin-trend GP, and physically correctable local search. State which elements are retained and which are simplified here.

**Stream 4 - Contribution.** State the application-specific contribution with exact experimental scope, policy dimension, episode count, and operating conditions.

### Draft replacement paragraphs for the physical literature

> Classical ground-effect relations were developed primarily for isolated rotors above extended planes. Their direct transfer to multirotors is limited by rotor-rotor interaction, fuselage effects, and partial surface coverage. Experiments on multirotors have shown that partial ground effect can create asymmetric forces and moments when only part of the vehicle overlaps a surface, while studies of finite ground and confined configurations demonstrate that edge geometry and nearby walls modify the wake. These effects are directly relevant to a vehicle crossing a finite obstacle, for which individual rotors enter and leave the affected region at different times.

> Static clearance laws also omit the temporal structure of the interaction. Dynamic quadrotor experiments and recent data-driven landing models show dependence on vertical or forward velocity, throttle, platform motion, and past states. High-fidelity and volumetric-flow studies further report recirculation, fountain flow, anisotropic outwash, and, for some multirotor geometries, non-monotonic or negative ground effect over part of the clearance range. The two-parameter power law used here is therefore adopted as a deliberately misspecified, control-oriented approximation over the tested envelope rather than as a general aerodynamic model.

### Draft paragraph positioning against control alternatives

> Several approaches compensate near-ground disturbances without a digital-twin policy-search loop. Model-reference adaptive control and learned disturbance models have improved altitude tracking during takeoff and landing, while Gaussian-process residual dynamics have been embedded in model-predictive quadrotor control. For missions repeated along the same path, iterative learning control can directly update a feedforward command from previous tracking errors. The present work differs by using designed physical episodes to identify an interpretable low-order twin, using that twin to synthesize and screen a spatial reference, and then learning a policy-level discrepancy between virtual and physical returns. This distinction should be evaluated experimentally against at least one repeated-task baseline in future work.

## Suggested BibTeX additions

The following entries are ready to adapt to the manuscript's key style. Verify page ranges against the publisher export before final submission.

```bibtex
@article{SanchezCuevas2017,
  author  = {Sanchez-Cuevas, Pedro and Heredia, Guillermo and Ollero, Anibal},
  title   = {Characterization of the Aerodynamic Ground Effect and Its Influence in Multirotor Control},
  journal = {International Journal of Aerospace Engineering},
  volume  = {2017},
  pages   = {1823056},
  year    = {2017},
  doi     = {10.1155/2017/1823056}
}

@article{DelContBernard2017,
  author  = {Del Cont Bernard, Davide and Riccardi, Fabio and Giurato, Mattia and Lovera, Marco},
  title   = {A Dynamic Analysis of Ground Effect for a Quadrotor Platform},
  journal = {IFAC-PapersOnLine},
  volume  = {50},
  number  = {1},
  pages   = {10311--10316},
  year    = {2017},
  doi     = {10.1016/j.ifacol.2017.08.1500}
}

@article{Prothin2019,
  author  = {Prothin, Sebastien and Fernandez Escudero, C. and Doue, N. and Jardin, T.},
  title   = {Aerodynamics of {MAV} Rotors in Ground and Corner Effect},
  journal = {International Journal of Micro Air Vehicles},
  volume  = {11},
  year    = {2019},
  doi     = {10.1177/1756829319861596}
}

@article{Wei2019,
  author  = {Wei, Peng and Chan, Sui Nam and Lee, Seongkyu and Kong, Zhaodan},
  title   = {Mitigating Ground Effect on Mini Quadcopters with Model Reference Adaptive Control},
  journal = {International Journal of Intelligent Robotics and Applications},
  volume  = {3},
  number  = {3},
  pages   = {283--297},
  year    = {2019},
  doi     = {10.1007/s41315-019-00098-z}
}

@article{Tanabe2021,
  author  = {Tanabe, Yasutada and Sugawara, Hideaki and Sunada, Shigeru and Yonezawa, Koichi and Tokutake, Hiroshi},
  title   = {Quadrotor Drone Hovering in Ground Effect},
  journal = {Journal of Robotics and Mechatronics},
  volume  = {33},
  number  = {2},
  pages   = {339--347},
  year    = {2021},
  doi     = {10.20965/jrm.2021.p0339}
}

@article{Torrente2021,
  author  = {Torrente, Guillem and Kaufmann, Elia and Foehn, Philipp and Scaramuzza, Davide},
  title   = {Data-Driven {MPC} for Quadrotors},
  journal = {IEEE Robotics and Automation Letters},
  volume  = {6},
  number  = {2},
  pages   = {3769--3776},
  year    = {2021},
  doi     = {10.1109/LRA.2021.3061307}
}

@article{Meraglia2021,
  author  = {Meraglia, Salvatore and Lovera, Marco},
  title   = {Smoother-Based Iterative Learning Control for {UAV} Trajectory Tracking},
  journal = {IEEE Control Systems Letters},
  volume  = {6},
  pages   = {1501--1506},
  year    = {2022},
  doi     = {10.1109/LCSYS.2021.3116263}
}

@article{Xu2022GroundEffect,
  author  = {Xu, Guoxi and Sun, Zibin and Liu, Haiming and Zhou, Yan and Gong, Xiaoran and Gong, Shengping},
  title   = {Identification of Ground Effect and Intelligent Control of Unmanned Aerial Vehicles},
  journal = {Aerospace Science and Technology},
  volume  = {131},
  pages   = {107976},
  year    = {2022},
  doi     = {10.1016/j.ast.2022.107976}
}

@inproceedings{He2024,
  author    = {He, Binglin and Zhang, Heng and Lai, Baisheng and Liu, Song and Wang, Yang},
  title     = {Data-Driven Modeling of Ground Effect for {UAV} Landing on a Vertical Oscillating Platform},
  booktitle = {2024 IEEE/RSJ International Conference on Intelligent Robots and Systems},
  pages     = {8169--8174},
  year      = {2024},
  doi       = {10.1109/IROS58592.2024.10802474}
}

@article{Wolf2024,
  author  = {Wolf, C. Christian and Schanz, Daniel and Schwarz, Clemens and Heintz, Alexander and Bosbach, Johannes and Struebing, Tobias and Schroeder, Andreas},
  title   = {Volumetric Wake Investigation of a Free-Flying Quadcopter Using {Shake-The-Box} Lagrangian Particle Tracking},
  journal = {Experiments in Fluids},
  volume  = {65},
  pages   = {152},
  year    = {2024},
  doi     = {10.1007/s00348-024-03880-3}
}

@article{Lei2026,
  author  = {Lei, Yao and Zhang, Yuanfeng and Li, Xuan and Qiu, Jiafu and Yang, Hengxing},
  title   = {Interactional Aerodynamics and Flow Characteristics of a Quadrotor with Ground Effect},
  journal = {Physics of Fluids},
  volume  = {38},
  number  = {7},
  pages   = {075139},
  year    = {2026},
  doi     = {10.1063/5.0337114}
}

@inproceedings{KrauseOng2011,
  author    = {Krause, Andreas and Ong, Cheng Soon},
  title     = {Contextual Gaussian Process Bandit Optimization},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {24},
  year      = {2011}
}

@inproceedings{Eriksson2019,
  author    = {Eriksson, David and Pearce, Michael and Gardner, Jacob and Turner, Ryan D. and Poloczek, Matthias},
  title     = {Scalable Global Optimization via Local Bayesian Optimization},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {32},
  year      = {2019}
}

@article{MendezRT2026,
  author        = {Mendez, Miguel A. and Schena, Lorenzo and Poletti, Romain and Lecomte, Yannick and Randino, Sebastiano and Van den Berghe, Jan},
  title         = {Reinforcement Twinning via Twin-Calibrated Bayesian Policy Search and Replay-Driven Identification},
  journal       = {arXiv preprint arXiv:2611.03540},
  year          = {2026},
  eprint        = {2611.03540},
  archivePrefix = {arXiv},
  primaryClass  = {eess.SY},
  doi           = {10.48550/arXiv.2611.03540}
}
```

The current `Mendez2026` entry should be updated from “manuscript submitted” to the arXiv record above, while retaining any journal-submission note only if the authors want it and the target journal allows it.

## Reproducibility checklist

Before resubmission, the paper or supplement should contain all of the following.

### Physical campaign

- Exact obstacle dimensions and edge locations in both metres and rotor radii.
- Full operating-condition table, including desired and measured forward speed.
- Number of flights for every policy.
- Inclusion/exclusion and cleaning rules fixed independently of reward outcome.
- Position-system sampling rate, filtering, interpolation grid, and synchronization.
- Battery, propeller, mass, and controller-gain details sufficient to repeat the tests.
- Abort criteria and physical risk-mitigation procedures.

### Identification

- Bounds and transformations for `A,p`.
- Initial-state reconstruction algorithm and branch point.
- Complete Adam settings, maximum iterations, and convergence history.
- Gradient verification.
- Held-out or leave-one-episode-out validation.
- Residual correlation diagnostics.
- Episode-level bootstrap or an explicit statement that uncertainty is only a curvature indicator.
- Exact novelty rule and candidate library generation seed.

### Model-based policy

- Spatial optimization interval, number of nodes, and endpoint conditions.
- Grid-consistent definition of amplitude and curvature penalties.
- Exact clearance geometry and hard virtual check.
- Adam settings and number of random starts.
- Whether the reported policy is the best among multiple optimizer initializations.
- Fixed virtual scoring scenarios, if any.

### Reward-transfer search

- Table of every policy coefficient, DT reward, physical reward, repetitions, and standard error.
- Basis-function centers, widths, normalization, and units.
- Affine fit method and its uncertainty.
- GP kernel amplitude, length scales, bounds, noise, optimizer, initializations, and seed.
- Exact EI incumbent and candidate-pool update rule.
- Boundary diagnostics and enlarged-region sensitivity.
- Context kernel and input scaling for off-nominal tests.

### Reporting

- Physical RMSE and maximum excursion in addition to normalized reward.
- Confidence intervals or standard errors for repeated-policy comparisons.
- Total physical episode count, including initialization and assessment flights.
- Machine-readable data and code for the reward-transfer fit if release is possible.

## Detailed revision sequence

### Essential before submission

1. Resolve the policy-coordinate and transfer inconsistency at lines 732-768 and 942-962.
2. Decide whether the paper implements the full root method or an application-specific variant, and revise claims accordingly.
3. Replace deterministic jitter with a physical reward-noise treatment, or explicitly downgrade the posterior interpretation.
4. Correct the EI incumbent for noisy observations.
5. Add proposal-region boundary diagnostics and either adaptive expansion or a local-only claim.
6. Specify state synchronization and free factual replay.
7. Remove confidence/covariance claims from the Hessian and Fisher proxies unless statistically derived.
8. Replace unqualified safety language.
9. Add the most directly relevant ground-effect and repeated-mission control literature.
10. Provide complete experimental counts and a policy/reward table.

### Strongly recommended

11. Add episode-disjoint validation or leave-one-episode-out replay tests.
12. Use universal kriging/GLS or propagate affine-coefficient uncertainty.
13. Add a fixed virtual scoring bank or state clearly that the study is nominal and deterministic.
14. Show the analytic parameter sensitivities and explain the observed correlation.
15. Report kernel and optimization hyperparameters, seeds, and candidate-pool rules.
16. Add a sensitivity study for policy-region size and context length scales.
17. Shorten the generic RT derivation and cite the attached root paper more directly.

### Copy-editing and production

18. Rewrite line 40 and perform a full grammar pass.
19. Remove the prose paragraph accidentally appended to `references.bib`.
20. Fix the overfull equations reported around source lines 651 and 717 and the underfull boxes listed in `main.log`.
21. Standardize “digital twin,” “model-based,” “ground effect,” “off-nominal,” and “information-oriented” hyphenation.
22. Replace vague adjectives with numbers throughout the results.

## Final verdict

The paper has a worthwhile experimental contribution, but its strongest defensible claim is narrower than its current framing. The data show that an identified, low-order twin can produce a substantially better anticipatory reference than the baseline PID mission and that local physical reward observations can improve the ranking of nearby policy corrections. They do not yet show a complete, statistically calibrated, adaptively correctable implementation of the attached Reinforcement Twinning method, a general safe policy-search procedure, or a contextual policy map over clearance and velocity.

That distinction is fixable. A revision that explicitly separates the full RT method from this two-stage experimental specialization, repairs the policy-transfer equation, treats reward variability honestly, and engages the missing ground-effect/control literature would be much stronger. It would also be easier to read: the scientific message is not that the compact twin is fully accurate, but that it is useful as an interpretable starting point whose local performance ranking can be corrected with carefully budgeted physical evidence.

## Sources consulted for the parallel literature review

- Mendez et al., *Reinforcement Twinning via Twin-Calibrated Bayesian Policy Search and Replay-Driven Identification*: https://arxiv.org/abs/2611.03540
- Sanchez-Cuevas et al. (2017): https://doi.org/10.1155/2017/1823056
- Del Cont Bernard et al. (2017): https://doi.org/10.1016/j.ifacol.2017.08.1500
- Xin et al. (2017): https://doi.org/10.7527/S1000-6893.2016.0221
- Prothin et al. (2019): https://doi.org/10.1177/1756829319861596
- Wei et al. (2019): https://doi.org/10.1007/s41315-019-00098-z
- Tanabe et al. (2021): https://doi.org/10.20965/jrm.2021.p0339
- Torrente et al. (2021): https://doi.org/10.1109/LRA.2021.3061307
- Meraglia and Lovera (2021/2022): https://doi.org/10.1109/LCSYS.2021.3116263
- Xu et al. (2022): https://doi.org/10.1016/j.ast.2022.107976
- He et al. (2024): https://doi.org/10.1109/IROS58592.2024.10802474
- Wolf et al. (2024): https://doi.org/10.1007/s00348-024-03880-3
- Yang et al. (2025 preprint): https://arxiv.org/abs/2506.19424
- Lei et al. (2026): https://doi.org/10.1063/5.0337114
- Krause and Ong (2011): https://proceedings.neurips.cc/paper/2011/hash/f3f1b7fc5a8779a9e618e1f23a7b7860-Abstract.html
- Eriksson et al. (2019): https://proceedings.neurips.cc/paper/2019/hash/6c990b7aca7bc7058f5e98ea909e924b-Abstract.html
- Sui et al. (2015): https://proceedings.mlr.press/v37/sui15.html
- Sui et al. (2018): https://proceedings.mlr.press/v80/sui18a.html
