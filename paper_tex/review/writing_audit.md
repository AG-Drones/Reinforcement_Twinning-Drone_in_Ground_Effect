# Writing audit of `main_lf.tex` (RT for a MAV in ground effect)

Audit of `/home/claude/R1/material/main_lf.tex` (997 lines; identical to `paper/main.tex`) against the author's writing rules and the scientific-writing method. The audit is read-only and no file except this report was changed.

Conventions:

- Every **Current** string is copied character for character from the file, including double spaces and LaTeX, and occurs exactly once, so it can be found by string search. A script checked this.
- **Replace** gives exact LaTeX with the same meaning. *(delete)* means remove the string. `[...]` marks a value or decision that only the author can supply. `[CITE: ...]` marks a missing reference.
- Word counts are `wc -w` on the LaTeX source, which counts whitespace-separated tokens, so a `\cite{}` counts as one word. For the revised Introduction, each `[CITE: ...]` was counted as one word.
- Category tags are vague, improper word, grammar, repetition, long sentence, colon, undefined symbol, inconsistent term, signposting, unsupported claim, and logic. Logic was added for contradictions between sections.

---

## 0. Overview

| Item | Count |
|---|---|
| Introduction paragraphs diagnosed and rewritten | 14 (1730 → 1522 words) |
| Main findings outside the Introduction (Section 2) | 80 |
| Second-tier items (Section 2.10) | 72 |
| Mechanical fixes (Section 2.11) | 14 |
| Inconsistent terms (Section 3.1) | 26 |
| Symbol problems (Section 3.2) | 24 |
| Paragraphs to cut or compress (Section 4) | 17 (about 1,800 words saved) |
| Total words that could be saved | about 3,150, roughly a quarter of the running prose |

The main findings fall into these categories; a finding can carry several tags:

| Category | Main | Second tier |
|---|---|---|
| Repetition | 33 | 16 |
| Vague | 23 | 16 |
| Logic, contradiction, wrong reference, or method in Results | 24 | 3 |
| Colon | 13 | 5 |
| Improper word | 12 | 12 |
| Undefined symbol or acronym, or symbol clash | 11 | 10 |
| Signposting | 5 | 5 |
| Unsupported claim | 5 | 2 |
| Inconsistent term or number | 4 | 7 |
| Long sentence | 3 | 1 |
| Grammar | 2 | 3 |
| Missing number or citation | in IIC-14, IIID-6 (as vague) | 6 |
| Other (wordy, ambiguous, figure introduction) | 0 | 6 |

The five worst problems are these:

1. **Methods are written twice, with about 1,000 words of repetition** (II-A, the block list, and II-C). See IIA-3, IIA-17, IIC-11, IIC-17, and C1–C5.
2. **The stopping rule of the information phase differs between Methods and Results.** It appears six times and is never quantified ("appreciably"). See IIA-9 and IIIB-7.
3. **Key symbols are undefined or clash.** The reward of Eq. `reward` uses undefined $N_{\mathcal R}$, $\Omega_{\mathcal R}$, and $z_k$. Other problems are $\xi$ against $\boldsymbol\xi$, $\chi_i$ against $\boldsymbol\chi$, the undefined $\mathcal S_e$ and $\rho_{A,p}$, and $z^\ast$, $v_x^\ast$, and $R$ never defined in words. See IIC-13, IIA-15, and IIIE-5.
4. **Four logic gaps.** The transfer "scaling" is not supported by the additive Eq. `rt-policy` (IIC-18). Noise $\varepsilon$ is present at L212 but rewards are deterministic at L740 (IIA-12). Information-policy rewards are "used" at L146 but excluded at L881 (IIA-6). Repeatability is claimed from single runs, and the text contradicts the Fig. 10 caption (IIID-10).
5. **Vague quantities where numbers exist or are needed.** The number of EI flights is never given (IIC-14, IIID-6), and 44 vague intensifiers remain. "near-wall" is used for a horizontal surface (14 times), and "safe" or "safety" is used for DT checks (about 20 times).

Two source-level facts matter for the structure:

- **Lines 40 and 41**, and **lines 53 and 54**, have no blank line between them. Each pair therefore compiles as one paragraph, of 276 and 304 words. Add a blank line in both places. The revisions below assume two paragraphs in each case.
- **Methods are written twice.** Section II-A is a generic RT description, followed by a six-block list (lines 356–364) that restates it. Section II-C then specializes the same steps. As a result, factual replay is described 4 times, the E-optimal rule 4 times, the stopping rule 6 times, "parameters frozen" 12 times, and the reward-transfer surrogate and EI equations appear twice (Eqs. `rt-surrogate`/`reward-transfer`, `rt-expected-improvement`/`ei`, `rt-e-optimal`/`e-optimal-design`, `rt-fisher-update`/`cumulative-fisher`). This is the largest single source of length.

---

## 1. Introduction (lines 38–64)

### 1.1 Repetition across Introduction paragraphs

| # | Repeated fact | Where | Keep in |
|---|---|---|---|
| R1 | MAVs spare human operators from danger | P1 (L40, twice), P2 (L41) | P1 |
| R2 | Inspection and emergency response as applications | P1 (L40), P2 (L41) | P2 (as the MAV missions) |
| R3 | Feedback acts only after an error develops | P5 (L47), P6 (L49, twice); later II-C L566, III-A L780, III-C L857 | P6 (Intro); III-A once |
| R4 | The DT designs and screens policies before deployment | P9 (L54), P11 (L58); II-A L146, L245, L358, L362 | P9 (Intro); II-A L146 |
| R5 | Information and performance episodes are separate, not merged | P9 (L54), P11 (L58), P13 (L62); II-A L158, L196, L366 | P9 (Intro); II-A L158 |
| R6 | A compact model leaves a model discrepancy | P10 (L56), P11 (L58 "systematic bias"), P12 (L60); II-B L544 | P10 and P12 (two different facts once separated: general vs. this model) |
| R7 | Only a lightweight correction runs onboard above the standard controller | P9 (L54), P13 (L62); Abstract; II-C L697, L707 | P9 (Intro); II-C L697 |
| R8 | The model-based policy is the starting point of the search | P8 (L53), P11 (L58) | P11 |
| R9 | RT definition and acronyms | P7 (L51); II-A L72 (RT and DT defined a third time) | P7 |

No Introduction sentence exceeds 40 words. The longest is the L40 sentence beginning "In such context" (38 words).

### 1.2 Paragraph by paragraph

#### P1 (L40). Context and market. 153 → 105 words

- **Grammar.** "hass" (typo). "The interest and investments on ... hass grown" should read "interest and investment in ... have grown". Further errors: "Such increase", "substituting or support", "These includes", "In such context", "small onboard sensor". "if retained necessary" is a calque of "se ritenuto necessario" and should read "when needed". "guide deployment of human operations" should read "before human operators are sent in".
- **Vague or improper.** "grown significantly" is an intensifier without a number. Other vague phrases are "In specific applications", "can carry important advantages" ("carry" → "offer"), "plays a major role", and "the size of ... plays a major role as they can provide a preliminary mapping", which mixes size and mapping in one clause.
- **Unsupported.** The advantages and the list of application domains have no citation. Add [CITE: review of UAV applications].
- **Repetition.** R1 and R2 with P2.
- **Acronym.** "UAVs" is defined but never used again. The revision uses it once.

```latex
\IEEEPARstart{I}{nterest} and investment in unmanned aerial vehicles (UAVs) have grown in recent years. A recent European Commission outlook places the European commercial airborne-drone market at about EUR~14.5 billion by 2030 and indicates that it could exceed EUR~50 billion by 2033~\cite{EuropeanCommission2026}. UAVs are cheap to operate, quick to deploy, and can replace or support human operators in hazardous missions; their applications range from logistics to emergency response and infrastructure inspection~[CITE: review of UAV applications and their advantages]. Micro aerial vehicles (MAVs) extend these missions to cluttered spaces that are difficult or dangerous for people to enter. With small onboard sensors, a MAV can map a restricted zone before human operators are sent in.
```

#### P2 (L41). Indoor missions and why surfaces matter. 123 → 111 words

- **Vague.** "Indoor inspection, monitoring, and emergency-response missions are representative examples" leaves open what they exemplify. "These missions are also among the most demanding" is an unsupported superlative.
- **Improper word.** "obstacle avoidance leaves little room for tracking errors" should refer to the obstacles' proximity, not to avoidance. "The boundaries" is not defined; use "nearby surfaces".
- **Logic.** In the last sentence, "therefore" does not follow from the tracking-error sentence. The wake–surface interaction is a second, separate reason.
- **Colon.** "...passive geometric constraints: the wakes generated ..."
- **Unsupported.** No citation for GNSS loss, limited computation, or degraded communication. Add [CITE].
- **Repetition.** R1 and R2.

```latex
In indoor inspection, monitoring, and emergency response, a MAV can enter confined spaces, cross passages whose clearance is only a few rotor radii, and approach machinery, beams, pipes, and damaged structures without shutting down a facility or exposing an operator. These missions are also hard to fly. Satellite positioning is generally unavailable, onboard sensing and computation are limited, and the surrounding structure can degrade communication~[CITE: review of MAV navigation in GNSS-denied confined spaces]. Nearby obstacles leave little room for tracking errors, and they also alter the flight dynamics. The propeller wakes interact with nearby surfaces and change the forces and moments acting on the vehicle, so these surfaces are part of the aerodynamic environment rather than passive geometric constraints.
```

#### P3 (L43). Ground, wall, and ceiling effects. 141 → 123 words

- **Improper word.** "elementary interactions" should be "rotor–surface interactions".
- **Vague intensifiers.** "very close", "substantially smaller change in lift", and "pronounced force increase" have no numbers. Quote Carter's and Franzetti's or Cai's values if the size matters. Otherwise drop the intensifiers, as below.
- **Unsupported.** The tunnel scenario with combined floor, ceiling, and wall effects has no citation. Neither does "Wall and ceiling effects have received less attention than ground effect".
- **Function.** The paragraph sets up the focus on GE but never states it. P4's "by contrast" carries the link, which is acceptable.

```latex
Rotor--surface interactions are usually classified as ground, wall, and ceiling effects according to the orientation of the surface relative to the rotor plane~\cite{Matus2020,Carter2021,Franzetti2024}. In cluttered spaces they seldom occur in isolation. In a narrow tunnel, a vehicle can experience floor, ceiling, and lateral-wall interactions at once, in an asymmetric flow that affects both translation and attitude~[CITE: study of combined proximity effects in confined spaces]. Wall and ceiling effects have been studied less than ground effect, mostly for hovering rotors or vehicles. Wall effect remains weak until the rotor is close to the surface. Carter et al.~\cite{Carter2021}, for example, measured a smaller change in lift near a lateral wall than near a floor or ceiling. Ceiling effect is also confined to small clearances, where wake blockage and recirculation can increase the force~\cite{Franzetti2024,Cai2024}.
```

#### P4 (L45). Ground effect and its MAV-scale limits. 149 → 142 words

- **Missing citation.** "since the middle of the twentieth century" and "the Cheeseman-Bennett approximation" are uncited, although `\cite{CheesemanBennett1955}` exists and is first used at L529. The wake-turning physics needs [CITE: rotorcraft aerodynamics textbook].
- **Improper word, to check.** "Classical momentum-theory relations, including the Cheeseman-Bennett approximation" is doubtful because Cheeseman and Bennett used the method of images. The cited report is also titled *The Effect of Ground on a Helicopter Rotor in Forward Flight*, while the text says "hovering". "lift" for a rotor should be "thrust".
- **Vague.** "primarily through its normalized clearance" does not say normalized by what. "clearance alone is insufficient" does not say for what.
- **Logic.** P4 stresses that "velocity changes the response" (Kan), but II-B L544 says velocity dependence "is limited over the low-speed range considered here". State the advance-ratio range once and reconcile the two (see IIB-9).
- **Grammar.** "Cheeseman-Bennett" should use an en-dash, `Cheeseman--Bennett`.

```latex
Ground effect (GE), by contrast, has been studied in aviation and rotorcraft since the 1950s~\cite{CheesemanBennett1955}. An underlying surface changes the pressure field and turns the rotor wake radially, reducing the induced velocity and the induced power needed for a given thrust~[CITE: rotorcraft aerodynamics textbook]. This improves efficiency in takeoff, hover, and low-altitude flight. Classical relations, including the Cheeseman--Bennett approximation~\cite{CheesemanBennett1955}, describe the effect for an isolated rotor hovering above an extended plane mainly through the ratio of clearance to rotor radius. At MAV scale, however, four nearby rotors interact with one another and with the central body, and the low Reynolds number and wake recirculation make the response vehicle dependent~\cite{Matus2020,Carter2021}. Forward motion adds wake convection and a finite residence time over the surface. Kan et al.~\cite{Kan2019} confirmed the expected efficiency gain for small multirotors in forward flight, but showed that the response also depends on velocity.
```

#### P5 (L47). Why prediction is a safety requirement. 116 → 111 words

- **Vague referent.** "These limitations" could mean the classical models or the MAV-scale effects.
- **Vague.** "the purpose of an aerodynamic model is not only to reproduce a force measurement" is negative framing without a positive statement.
- **Grammar.** "compensating the interaction" should be "compensating for the interaction".
- **Improper word.** "The problem is especially clear over finite obstacles" uses "clear" for "explicit" or "acute".
- **Repetition.** R3 with P6.

```latex
For flight in cluttered spaces, an aerodynamic model must do more than reproduce a measured force. It must allow the controller to keep the vehicle on a collision-free path from one obstacle to the next. A thrust change above one surface can cause a vertical excursion that is harmless locally but uses up the clearance available at the next beam, ceiling, or doorway. The interaction must therefore be predicted and compensated for before a tracking error develops. Finite obstacles make this requirement explicit. The vehicle enters GE, remains in it briefly, and then crosses a trailing edge, so leading-edge exposure, transient wake development, and post-obstacle recovery all occur within one mission.
```

#### P6 (L49). PID versus MPC. 142 → 129 words

- **Unsupported.** "Most MAVs rely on cascaded proportional-integral-derivative (PID) loops" has no citation.
- **Vague.** "robust nominal behavior".
- **Colon.** "intrinsically reactive: an unmodeled disturbance ..."
- **Redundant.** "the computational burden related to its online computation".
- **Improper word.** "a confidently wrong correction" is informal. "micro drone" should be MAV.
- **Acronym.** "MPC" is defined but never used again. L707 spells out "model predictive control"; IIC-12 uses the acronym there.

```latex
Most MAVs are stabilized by cascaded proportional-integral-derivative (PID) loops~[CITE: survey of MAV flight control]. These loops are cheap to compute and robust near their nominal operating point, which suits small onboard processors. However, they are reactive. An unmodeled disturbance must first produce an error before feedback counters it, and close to an obstacle this delay can consume the available safety margin. Predictive methods instead modify the command or reference before the disturbance develops. Model predictive control (MPC) optimizes future behavior while accounting for dynamics and constraints~\cite{MPCReview2021}, but its performance depends on the prediction model and on the cost of solving it online. An incomplete model can produce a wrong correction, whereas a more faithful aerodynamic model may be hard to identify and too expensive to optimize repeatedly on the limited hardware of a MAV.
```

#### P7 (L51). RT and the active DT. 120 → 109 words

- **Vague referent.** "this tension" should be "this trade-off", which is the one stated at the end of P6.
- **Undefined term.** "physical environment" is RT jargon and appears here without explanation.
- **Unsupported.** "A conventional DT is often understood as ..." has no citation. Check whether `\cite{Wagg2025}` covers it.
- **Improper word.** "guide the next action of the physical environment" is wrong because the environment does not act; a policy is deployed in it.
- **Grammar.** "but still poorly experimentally validated" has no subject and no verb.
- **To check.** "gust rejection on a flapping-wing vehicle" and "flapping-wing flight" may be the same application listed twice.
- **Repetition.** R9 with II-A L72.

```latex
Reinforcement Twinning (RT) was introduced to address this trade-off. It couples the physical system, called the physical environment, with an active physics-based digital twin (DT)~\cite{SchenaRT2023,Mendez2026,PolettiRT2025}. A conventional DT reproduces the behavior of the physical environment~[CITE: definition of a digital twin, unless \cite{Wagg2025} covers it]. An active DT also learns from physical observations and uses the updated model to influence subsequent operation, acting as both a \emph{steering representation} and an \emph{acting model} in the decision process~\cite{Korenhof2021,Wagg2025}. Experimental data refine its uncertain physics, and virtual rollouts select the next policy deployed in the physical environment. RT has been applied to wind-turbine control, gust rejection on a flapping-wing vehicle, cryogenic thermal management, and flapping-wing flight~\cite{SchenaRT2023,PolettiRT2025}, but has seldom been validated experimentally.
```

#### P8 (L53). Early RT. 95 → 95 words

Add a blank line after this paragraph.

- **Vague.** "a model-free policy could improve when the model reached ..." has no object for "improve". "protected the first interactions" is unclear.
- **Inconsistent term.** "model-based optimum" against "model-based policy" (Section 3).
- The paragraph is otherwise sound. The edits are for precision only.

```latex
Early RT algorithms combined model-based and model-free control. A model-based policy gave an efficient, physically informed starting point, and a model-free policy kept improving when the model reached a local or structurally biased optimum. A referee switched between the two according to their observed or predicted performance. When learning stagnated, policy cloning copied the weights of the better policy to the other learner, so that the search resumed from a better region~\cite{SchenaRT2023,PolettiRT2025}. The model-based branch thus made the first interactions less risky and accelerated early learning, without tying the final controller to the model-based optimum.
```

#### P9 (L54). Bayesian RT, dual control, and the model-based anchor. 209 → 185 words

- **Structure.** The paragraph has three functions: the two episode purposes, the dual-control contrast, and the model-based policy with its onboard implementation. It can stay one paragraph, but it is the longest in the Introduction. An optional split falls before "Once the physical data ...".
- **Vague or improper.** "cast the same exchange" (which exchange?), "They retain two purposes for a physical episode" (unclear), and "sufficient for the task".
- **Undefined term.** "factual replay" appears here but is defined only at L114. The revision defines it in passing.
- **Colon.** "physically interpretable anchor: it already accounts ..."
- **Inconsistent term, important for an IEEE control venue.** In the control literature a "reference governor" is an online add-on that modifies the reference to enforce constraints. Here the policy is a precomputed spatial offset stored in a table. A T-CST reviewer will read the term in its technical sense. Use "reference correction" or cite and justify the term (Section 3, term 3).
- **Repetition.** R4, R5, and R7.

```latex
More recent RT formulations cast the exchange between model-based and data-driven learning as a twin-calibrated Bayesian policy search~\cite{Mendez2026}, in which each physical episode has one of two purposes. An information-oriented policy is chosen to improve the uncertain physics in the DT, and a performance-oriented policy to improve control. The two objectives are coupled through the accumulated data and the current DT, but they are not merged into one scalar objective. This distinguishes RT from dual control, which balances the regulation and information consequences of each action~\cite{Feldbaum1960,Filatov2000,Mesbah2018}. RT instead assigns the two roles to separate episodes, linked by the DT, which is updated by replaying the recorded episodes (factual replay). Once the physical data constrain the DT well enough for the task, the DT becomes the main tool for policy search. It solves the model-based control problem offline and screens candidate policies against state, clearance, and actuation constraints before deployment. The resulting model-based policy accounts for the dynamics learned from the experiments. If it is expressed as a compact feedforward reference correction, only this correction runs onboard, and the standard feedback controller still stabilizes the vehicle.
```

#### P10 (L56). Reward transfer. 129 → 103 words

- **Signposting.** "The role of Bayesian RT does not end at the model-based policy."
- **Inconsistent term.** Three names for one idea appear in one paragraph: "structural discrepancy", "model discrepancy", and "GP discrepancy". "a Gaussian process represents the remaining GP discrepancy" is circular, and the acronym GP is never defined. "Bayesian RT" is a second name for RT.
- **Vague.** "an affordable DT".
- **Repetition.** The last sentence ("The latter accounts for ...") restates the previous one.
- **Logic.** P11 opens "This reward-transfer surrogate", but P10 never introduces the name. The revision names it here.

```latex
Identification reduces parametric uncertainty but cannot remove the structural discrepancy between a compact physics model and the physical environment. Additional states and correction terms may reduce this model discrepancy, but a DT that remains cheap to optimize will still omit part of the physical response. RT therefore also learns how control performance transfers from the DT to the physical environment. Each tested policy yields a DT reward and a physical reward. In this reward-transfer surrogate, an affine relation captures the global calibration between the two rewards, and a Gaussian process (GP) represents the remaining discrepancy, whose uncertainty is largest in sparsely explored regions~\cite{Kennedy2001,Rasmussen2006}.
```

#### P11 (L58). EI search near the model-based policy. 142 → 110 words

- **Undefined.** "the final stage", and the acronym EI, which is used from L730 on.
- **Improper word.** "The policy can consequently move beyond" should be "The search". "safety envelope" is a DT check (use "admissible set"). "improved physics-based solution" means the model-based policy.
- **Repetition and undefined term.** The last sentence ("Information-oriented and performance-oriented interactions can in principle be interleaved ... RT selector") repeats R5, and "RT selector" is not defined in the Introduction. Cut it.

```latex
The surrogate turns the last stage of RT into a data-efficient policy search. Expected Improvement (EI) weighs the predicted physical reward against the surrogate uncertainty and proposes a candidate that is promising, insufficiently explored, or both~\cite{Mockus1975,Forrester2007}. The physical reward of the tested candidate updates the surrogate, and the search is repeated. The search can therefore move beyond the model-based policy even if the DT retains a systematic bias. Unlike a model-free search, however, it starts from the model-based policy and stays within a neighborhood that the DT has already simulated and screened. The DT supplies the initial direction and the admissible set, and physical data correct its ranking where needed.
```

#### P12 (L60). This work. 89 → 80 words

- **Wordy.** "presents an experimental demonstration of the present RT formulation".
- **Inconsistent term.** "Richardson and Pretorius" here is correct, because the bib entry has two authors. The body says "Richardson et al." five times (IIB-3).
- **Unsupported qualifier.** "independently validated" holds for free flight only. Say so.
- **Defensive.** "deliberately".
- **Improper word.** "retains a realistic discrepancy". A model *leaves* a discrepancy; retaining one is not a goal.
- **Inconsistent term.** GE is defined in P4, but "ground effect" is spelled out here.
- **Logic gap.** P7 states the gap ("seldom validated experimentally"), but no sentence states the contribution against it. Add one if it is true, e.g. "[first experimental RT campaign on a flying vehicle — verify]".

```latex
This paper demonstrates this RT formulation experimentally. A Crazyflie~2.1+ MAV crosses a finite horizontal obstacle at constant forward speed, so that GE appears and disappears within one mission. The initial DT is the six-degree-of-freedom Crazyflie model of Richardson and Pretorius~\cite{Richardson2025}, validated in free flight, with an added low-order static GE law whose two parameters start from the Cheeseman--Bennett values. This structure can be identified and used for control design, but it leaves a model discrepancy, mainly at the obstacle edges.
```

#### P13 (L62). Campaign outline. 76 → 94 words

The paragraph is longer because it gains the missing content listed below.

- **Logic gap.** The off-nominal tests of Section III-E, which the abstract announces, are not mentioned. The revision adds one sentence.
- **Inconsistent term.** "lightweight spatial reference governor" (see P9).
- **Vague.** "making their experimental roles explicit while retaining the same RT loop".
- **Repetition.** R5.

```latex
The campaign first flies information-oriented policies to identify these parameters and then freezes the model. The DT computes a model-based policy, applied as a spatial reference correction above the unchanged onboard PID controller. Physical rewards of nearby policies calibrate the reward-transfer surrogate, and EI searches for further gains. The two phases are consecutive rather than interleaved, so that the role of each episode is explicit. Finally, the correction learned at the nominal condition is transferred to two other combinations of clearance and speed, and a short EI search is tested at one of them.
```

#### P14 (L64). Roadmap. 46 → 25 words, or 0

- **Signposting.** The author's rule says to delete this paragraph. If the venue expects a roadmap, use one sentence.

```latex
Section~\ref{sec:methodology} describes the RT loop, the physical environment and DT, and the test campaign; Section~\ref{sec:results} reports the experiments; and Section~\ref{sec:conclusion} states the conclusions and limitations.
```

**Introduction total:** 1730 → 1522 words (−208, −12%), or 1497 without P14. The saving is net of about 45 words added for the missing contribution and generalization content and the citation placeholders.

---

## 2. Findings outside the Introduction

The findings are ranked within each section by consequence: repetition first, then improper or vague words, then grammar, then long sentences.

### 2.1 Abstract (L32)

The project notes record that the author rewrites the abstract himself. These four items are flags and cuts.

**AB-1 · L32 · vague / improper word**
- **Current:** `Experiments over a finite obstacle show that the proposed workflow constrains the dominant ground-effect response over the tested clearance range and improves trajectory tracking with a limited number of physical interactions.`
- **Problem:** A workflow does not "constrain" a response; the identified model reproduces it. "a limited number" is vague, and the paper has the numbers: physical reward 0.54 → 0.855 → 0.952.
- **Replace:** `Experiments over a finite obstacle show that the identified model reproduces the dominant ground-effect response over the tested clearance range. The physical tracking reward rises from 0.54 with the onboard controller alone to 0.855 with the model-based policy and to 0.952 after [number] surrogate-guided flights.`

**AB-2 · L32 · vague**
- **Current:** `A proof-of-concept extension to different operating conditions further illustrates how the same workflow can adapt a transferred correction when its performance changes away from the nominal condition.`
- **Problem:** The sentence does not say what was found.
- **Replace:** `At two other operating conditions, the transferred correction improves on the model-based policy at one condition but not at the other, where two further surrogate-guided flights find a better policy.`

**AB-3 · L32 · improper word ("safe")**
- **Current:** `model-based optimization first provides a safe and computationally efficient policy`
- **Problem:** "safe" describes a check made in the twin. The policy is not computationally efficient; it is cheap to run onboard.
- **Replace:** `model-based optimization first provides a DT-screened policy that is cheap to run onboard`

**AB-4 · L32 · grammar / improper word**
- **Current:** `The framework couples a Crazyflie 2.1+ as physical environment with its Digital Twin (DT) whose aerodynamic correction to account for ground effect is progressively identified from flight data.`
- **Problem:** A comma is missing before "whose", and an article before "physical environment". "aerodynamic correction to account for ground effect" is wordy, and "Digital Twin" is capitalized.
- **Replace:** `The framework couples a Crazyflie~2.1+, the physical environment, with a digital twin (DT) whose ground-effect correction is identified progressively from flight data.`

The remaining abstract items are AB-5 to AB-8 in Section 2.10.

### 2.2 Section II-A, Reinforcement Twinning Framework (L69–366)

**IIA-1 · L72 · repetition**
- **Current:** `Reinforcement Twinning (RT) couples the evolution of a physical environment with that of an active, physics-based Digital Twin (DT)~\cite{SchenaRT2023,Mendez2026}. The two environments evolve side by side and pursue complementary objectives.`
- **Problem:** RT and DT are defined for the third time, after the abstract and L51, and the RT definition repeats Intro L51.
- **Replace:** `In RT, the physical environment and an active, physics-based DT evolve side by side with complementary objectives~\cite{SchenaRT2023,Mendez2026}.`

**IIA-2 · L72 · repetition**
- **Current:** `The physical environment has a performance objective related to the policy parameters to be optimized, whereas the DT must improve the physical model that predicts the response of the physical environment.`
- **Problem:** The two objectives are also stated at L117–133 with equations, in the Fig. 1 panel titles, and in the Fig. 1 caption (L353). Keep L117–133.
- **Replace:** *(delete)*

**IIA-3 · L72 and L143 · repetition / colon**
- **Current (a):** `Experience from the physical environment is therefore used both as evidence to update the DT and as feedback on the policies designed with that DT.`
- **Replace (a):** `Physical data update the DT and score the policies it designs, and the DT proposes the next experiments and policies.`
- **Current (b):** `Conversely, the DT not only adapts from observations but also proposes the next experiments and control policies from which new observations are generated.`
- **Replace (b):** *(delete)*
- **Current (c):** `Equations~\eqref{eq:rt-physical-objective} and~\eqref{eq:rt-model-objective} are coupled: the model determines which policies appear promising or informative, while the resulting physical records determine how the model and the policy search evolve.`
- **Replace (c):** *(delete)*
- **Problem:** The coupling of the two loops is stated at L72 (twice), at L143 (with a colon), at L245, and in Intro L51. Keep the single sentence at L72.

**IIA-4 · L92 · repetition / inconsistency**
- **Current:** `The complete experimental record also contains the deployed policy, the applied inputs, the relevant operating conditions, and the physical reward $\mathcal R_{\bullet}^{(n)}$.`
- **Problem:** The record is described three times with different contents. L92 lists policy, inputs, operating conditions, and reward. The set at L136–142 has $\boldsymbol o_\bullet$, $\boldsymbol\theta_\pi$, $e_n$, $\mathbf d$, and $\mathcal R_\bullet$, with no operating condition and only $\boldsymbol\theta_\pi$ even for information episodes. Block 3 (L360) adds control signals. Keep the set at L134–142 and make it complete. Here, only introduce $\mathcal R_\bullet$.
- **Replace:** `Each episode also returns a physical reward $\mathcal R_{\bullet}^{(n)}$.`

**IIA-5 · L146 · repetition / colon**
- **Current:** `Policy design is therefore performed virtually: candidate interactions can be evaluated and optimized before the selected policy is transferred to the physical environment.`
- **Problem:** This repeats the preceding sentence. The same fact also appears at L245, in Block 1 (L358), in Block 5 (L362), and in Intro L54.
- **Replace:** *(delete)*

**IIA-6 · L146 · logic (contradicts L881)**
- **Current:** `while an information-oriented policy also yields a physical reward that supports subsequent performance-oriented policy design.`
- **Problem:** L881 excludes all information-oriented episodes from the surrogate. State the exclusion once, here in Methods, and delete it from Results (IIID-1).
- **Replace:** `while an information-oriented policy also yields a physical reward. The present campaign does not use these rewards, because the information-oriented references depart from the nominal clearance.`

**IIA-7 · L158 · colon / repetition / grammar**
- **Current:** `For simplicity, the present work adopts a sequential schedule: all information-oriented missions are performed first until the  model satisfies the adopted identification and convergence requirements.`
- **Problem:** There is a colon construction and a double space. Sequential phases are also stated at Intro L58 and L62, at L196, and in the whole of L366 (C2). Keep this one.
- **Replace:** `For simplicity, the present work performs all information-oriented episodes first, until the model meets the stopping criterion of the information phase.`

**IIA-8 · L181 · repetition / vague**
- **Current (a):** `This selection may be complemented by an explicit novelty criterion that compares each candidate with the existing dataset.`
- **Replace (a):** *(delete)*
- **Current (b):** `It allows a mission with a slightly lower predicted information content to be selected when its response is sufficiently different from the experiments already available.`
- **Replace (b):** *(delete)*
- **Problem:** The novelty check is described again at L691, and neither place says whether it was used. "slightly" and "sufficiently" have no number. Keep one statement, at L691 (IIC-11).

**IIA-9 · L183 · logic / vague / repetition**
- **Current:** `The information phase is terminated when the converged parameter estimates remain stable after adding new interactions and the magnitude of their estimated correlation no longer decreases appreciably.`
- **Problem:** The stopping rule appears six times, in different forms:
  - here: stable estimates and correlation;
  - L366: "convergence and uncertainty criteria";
  - L693: as here;
  - L828: adds "improved confidence" in $f_{\mathrm{GE}}$;
  - L841: adds an unchanged baseline replay;
  - L850: four conditions.

  "appreciably" has no threshold. Write the complete rule once, here, and let Results refer to it. Also delete the following sentence, "At this point, further experiments yield only marginal changes in the identified model and in the joint identifiability of its parameters."
- **Replace:** `The information phase ends when new episodes change the converged estimates of $\boldsymbol{\theta}_p$ by less than [tolerance] and reduce the magnitude of their correlation by less than [tolerance][, and when (list any further condition used in Results)].`

**IIA-10 · L199 · repetition**
- **Current:** `Exploring the full policy space with a purely model-free strategy would require substantially more physical tests and could expose the physical environment to unsafe policies.`
- **Problem:** The same argument appears at Intro L58, L865 (C7), L890 (C9), and L986. Keep Intro L58 and the Conclusions. "substantially" has no number.
- **Replace:** *(delete)*

**IIA-11 · L199 · improper word ("safe") / logic**
- **Current:** `A small set of safe policies around $\pi_{\mathrm{MB}}$ is first evaluated in the DT to verify safety and then in the physical environment.`
- **Problem:** The sentence is circular: "safe" policies are evaluated "to verify safety". It describes a DT check.
- **Replace:** `A small set of policies around $\pi_{\mathrm{MB}}$ is first screened in the DT and then flown.`

**IIA-12 · L212 · logic (contradicts L740)**
- **Current:** `while $\varepsilon$ represents experimental and reward-evaluation noise.`
- **Problem:** L740 treats rewards as deterministic, with a jitter of $10^{-8}$. The reader cannot reconcile the two statements.
- **Replace:** `while $\varepsilon$ represents experimental and reward-evaluation noise, reduced in the present campaign to a numerical jitter (Section~\ref{sec:performance-phase}).`

**IIA-13 · L212 · undefined symbol (GP)**
- **Current:** `The GP discrepancy $\delta(\boldsymbol\xi)$ models the policy-dependent part of the transfer that is not explained by that relation.`
- **Problem:** GP is used from L56 on but never defined as an acronym.
- **Replace:** `The Gaussian-process (GP) discrepancy $\delta(\boldsymbol\xi)$ models the policy-dependent part of the transfer that the affine relation does not explain.`

**IIA-14 · L222 · repetition**
- **Current:** `This quantity is the posterior uncertainty of the adopted surrogate, not a confidence interval for experimental repeatability. The DT reward supplies the global performance trend, while the GP learns the local discrepancy between the DT and physical rewards.`
- **Problem:** The first sentence repeats at L740 (keep that one) and L901. The second repeats L212 and Intro L56.
- **Replace:** *(delete)*

**IIA-15 · L224 · undefined symbol / symbol clash**
- **Current:** `Let $\mathcal R_{\bullet}^{+}$ denote the best physical reward and $\xi\geq0$ an optional exploration margin.`
- **Problem:** $\xi$, the exploration margin, clashes with $\boldsymbol\xi$, the descriptor, in the same equation (Eq. `rt-expected-improvement`). The clash recurs at L747. "best physical reward" should say observed so far. Renaming the margin (e.g. $\zeta$) changes the equations, so it is the author's decision.
- **Replace:** `Let $\mathcal R_{\bullet}^{+}$ denote the best physical reward observed so far and $\xi\geq0$ an optional exploration margin.`

**IIA-17 · L356–366 · repetition (block list)**
- **Current:** `The actions carried out in each block can be summarized as follows:`
- **Problem:** The six-block list (657 words) restates II-A almost sentence by sentence:
  - the exogenous input $\mathbf d$ and the hidden state (L85 and L359);
  - the record (L134 and L360);
  - factual replay (L114 and L361);
  - DT screening (L146 and L362);
  - E-optimal and EI selection (L181, L234 and L363);
  - the index $m$ (L114 and L363).

  It also contains defensive sentences: "This distinction is essential ...", "The purpose of this passage ..." (where "passage" is a calque of "passaggio" and should read "step"), and "This block is the main computational advantage of RT: ...". See C1 for a 206-word version. L366 repeats L158 (C2).
- **Replace:** see C1 and C2.

### 2.3 Section II-B, Test Case Physical and Digital Environments (L367–551)

**IIB-1 · L503, L505, L529 · repetition**
- **Current (a):** `This value is inherited from the Richardson model and is not identified in the present work.`
- **Replace (a):** *(delete)*
- **Current (b):** `The main physical parameters adopted in the DT are taken from the formulation of \cite{Richardson2025} and are summarized in Table~\ref{tab:dt_parameters}.`
- **Replace (b):** `Table~\ref{tab:dt_parameters} lists the main DT parameters.`
- **Current (c):** `The described nominal DT reproduces the vehicle dynamics in free flight and was validated in those conditions by Richardson et al.~\cite{Richardson2025}. The nominal DT, however,  does not account for`
- **Replace (c):** `The nominal DT, validated in free flight~\cite{Richardson2025}, does not account for`
- **Problem:** The fact that the parameters are inherited and not reidentified is stated five times: L432 (keep), L503, L505, the Table I caption, and L529. Intro L60 adds a sixth mention.

**IIB-2 · L505 · repetition / vague / logic**
- **Current:** `The nominal propulsion model retains the battery-voltage correction $V_b=f(\mathrm{SOC})$. However, both physical and DT missions start with a fully charged battery and last only a few seconds; therefore, the within-mission change of state of charge is neglected.`
- **Problem:** $V_b=f(\mathrm{SOC})$ is restated from L503. "only a few seconds" is doubtful: 10 s of hover plus 4.2 m at $0.35$ m/s makes about 20 s. If SOC is fixed at full charge, $\eta_V=V_b/V_{\mathrm{ref}}=1$ and the "retained" correction has no effect, which the text should say.
- **Replace:** `Both physical and DT missions start with a fully charged battery and last about [value]~s, and the change of state of charge within a mission is neglected[, so that $\eta_V=1$ — check].`

**IIB-3 · L432 · improper word (author name)**
- **Current:** `follows the modeling formulation proposed by Richardson et al.~\cite{Richardson2025} for low-speed free flight`
- **Problem:** The bib entry `Richardson2025` has two authors, Richardson and Pretorius, so "et al." is wrong. The same error appears at L432 (twice), L468, L503, L508, and L529. L60 has the correct form.
- **Replace:** `follows the model of Richardson and Pretorius~\cite{Richardson2025} for low-speed free flight`

**IIB-4 · L372 · undefined symbol / repetition**
- **Current:** `and $z/R$ is the corresponding nondimensional clearance, with $R=23$~mm.`
- **Problem:** $R$ is used without saying what it is. It is defined later at L529 and again at L561, and its value is also in Table I and L561. Define it here once and let L561 refer to the table (IIC-1).
- **Replace:** `and $z/R$ is the nondimensional clearance, with $R=23$~mm the rotor radius.`

**IIB-5 · L372 · undefined symbol / inconsistent term**
- **Current:** `where the MAV reaches the prescribed altitude and hovers for 10~s`
- **Problem:** $z^\ast$ is used in Fig. 2 and from L561 on, but never defined in words. "altitude" also competes with "clearance" for the same quantity (Section 3).
- **Replace:** `where the MAV climbs to the desired clearance $z^\ast$ and hovers for 10~s`

**IIB-6 · L374 · improper word (technically wrong)**
- **Current:** `To provide a continuous position reference, the Lighthouse deck is detected by two Lighthouse infrared stations.`
- **Problem:** The base stations emit infrared sweeps and the deck receives them. The stations do not detect the deck.
- **Replace:** `For continuous positioning, the Lighthouse deck receives the infrared sweeps of two Lighthouse base stations.`

**IIB-8 · L425 · forward reference / repetition / inconsistency**
- **Current:** `For GE identification, the physical and DT trajectories are aligned along the streamwise coordinate, and the adjoint optimization minimizes the normalized vertical-position discrepancy over the obstacle region.`
- **Problem:** "adjoint optimization" is introduced only at L600. The loss is defined at L577–598, where it is evaluated at the $K_n$ positions "encountered during the flight", not "over the obstacle region". State the region once, at L577.
- **Replace:** `For GE identification, the physical and DT trajectories are aligned along the streamwise coordinate (Section~\ref{sec:information-phase}).`

**IIB-9 · L544 · logic (contradicts Intro L45)**
- **Current:** `Measurements by Kan et al.~\cite{Kan2019} indicate that velocity dependence is limited over the low-speed range considered here, but it is not assumed to vanish.`
- **Problem:** The model has no velocity term, so it does assume the dependence vanishes. Intro L45 says Kan "showed that clearance alone is insufficient and that velocity changes the response". Give Kan's speed range once.
- **Replace:** `Kan et al.~\cite{Kan2019} found the velocity dependence to be limited over the low-speed range considered here [give their range of $v_x/v_h$], and the model neglects it.`

Further II-B items (IIB-7, IIB-10, and IIB-11 to IIB-21) are in Section 2.10.

### 2.4 Section II-C, Test Campaign Overview (L553–771)

**IIC-1 · L561 · repetition**
- **Current:** `where $T_{h,r}=mg/4$ is the hover thrust required from each rotor, $\rho_a$ is the air density, and $R$ is the rotor radius. With $m=32.42$~g, $R=0.023$~m, and $\rho_a=1.225$~kg/m$^3$,`
- **Problem:** $R$ is defined for the third time (after L372 and L529). The values of $m$ and $R$ are given a third time, after L372–374 and Table I.
- **Replace:** `where $T_{h,r}=mg/4$ is the hover thrust of each rotor and $\rho_a$ is the air density. With $m$ and $R$ from Table~\ref{tab:dt_parameters} and $\rho_a=1.225$~kg/m$^3$,`

**IIC-2 · L563 · signposting / inconsistent term**
- **Current (a):** `The test campaign follows the sequential RT schedule introduced above. All tests use the same physical environment, DT structure, reference frame, and data-processing procedure described in Sec.~\ref{sec:setup}.`
- **Replace (a):** *(delete)*
- **Current (b):** `The campaign is organized into five consecutive blocks, introduced below together with the notation used in the results.`
- **Replace (b):** `The campaign has five consecutive stages.`
- **Problem:** The deleted sentences state the obvious. "blocks" already names Blocks 1–6 of Fig. 1. Change "The final block" (L771) and "The final campaign block" (L940) to "stage" as well.

**IIC-3 · L566 · repetition**
- **Current:** `The campaign starts from the built-in cascaded PID controller at the nominal condition $(z^\ast/R,\,v_x^\ast/v_h)=(1.5,0.079)$. This policy is denoted by $\pi_{\mathrm{BL}}$ and is repeated experimentally to quantify run-to-run variability.`
- **Problem:** The nominal values are written six times: L563 (keep), L566, L780, L940, L944, and L964. A controller is not a policy; the policy is the constant reference.
- **Replace:** `The baseline policy $\pi_{\mathrm{BL}}$ is a constant reference at the nominal condition, tracked by the onboard cascaded PID controller. It is flown repeatedly to quantify run-to-run variability.`

**IIC-4 · L566 · logic**
- **Current:** `and the baseline tracking cost used to normalize the rewards reported later.`
- **Problem:** The rewards of Eq. `reward` are not normalized by the baseline. Only the scores $\mathcal S$ of Eq. `normalized-score` are. The same role is restated at L784 (IIIA-4).
- **Replace:** `and the baseline cost $J_{\mathrm{BL}}$ used in the normalized score of Eq.~\eqref{eq:normalized-score}.`

**IIC-5 · L566 · repetition**
- **Current:** `Since $\pi_{\mathrm{BL}}$ reacts only after the vehicle departs from the desired clearance, it also exposes the ground-effect excursion that the subsequent predictive policies are designed to anticipate.`
- **Problem:** That the PID controller is reactive is stated in Intro L49, here, at L780, and at L857. Keep Intro L49 and III-A L780.
- **Replace:** *(delete)*

**IIC-7 · L573 · long sentence / colon / improper word ("safe")**
- **Current (a):** `This first stage deliberately explores a wide set of altitude histories: it establishes the global scale and decay of the interaction without assuming in advance that the most useful data must come from the smallest admissible clearance,`
- **Replace (a):** `This first stage explores a wide set of clearance histories. It establishes the global scale and decay of the interaction without assuming that the most useful data come from the smallest admissible clearance,`
- **Current (b):** `and it verifies the response of the evolving DT over the complete safe operating range.`
- **Replace (b):** `and it tests the evolving DT over the whole admissible range.`
- **Problem:** The sentence is 52 words long, the longest in the paper. It has a colon, "deliberately", and "safe" used for an admissible range.

**IIC-8 · L575 · vague / colon / logic**
- **Current:** `but their marginal E-optimal contribution has become modest compared with the first information-oriented interaction. This behavior is physically consistent with Eq.~\eqref{eq:fge}: at larger clearances,`
- **Problem:** "modest" has no number, and there is a colon construction. This paragraph motivates the restriction by the slowing growth of $\lambda_{\min}$, whereas L815 motivates it by "clearance coverage and the uncertainty remaining below $z/R=2$". Give one motivation.
- **Replace:** `but each adds less to $\lambda_{\min}$ than the first information-oriented episode did (Section~\ref{sec:results-inf}). This agrees with Eq.~\eqref{eq:fge}. At larger clearances,`

**IIC-9 · L575 · repetition / signposting**
- **Current (a):** `The restriction is an adaptive design decision, not a rejection of the broad-domain data. All preceding episodes remain in the replay buffer,`
- **Replace (a):** `All preceding episodes remain in the replay buffer,`
- **Current (b):** `After every flight, the new record is appended to the cumulative dataset and the identification is warm-started from the preceding converged coefficients.`
- **Replace (b):** *(delete)*
- **Problem:** The defensive sentence adds nothing. The warm start is stated here, at L635 (keep), and in L693. "Earlier records remain" is repeated at L815.

**IIC-10 · L577 · undefined symbol**
- **Current:** `For physical episode $n$, the experimental record provides the measured altitude-tracking error, the deployed reference policy, and the reconstructed initial condition.`
- **Problem:** $e_z$ in Eqs. `episode-error-vectors` and `identification-loss` is never defined. It is unclear whether it is measured against the deployed reference $z_\pi$ or the nominal $z_{\mathrm{BL}}$.
- **Replace:** `For physical episode $n$, the record provides the measured altitude-tracking error $e_{z,n}^{\bullet}(x)$ [define, e.g. $z(x)-z_{\pi}(x)$], the deployed reference, and the reconstructed initial condition.`

**IIC-11 · L691 · repetition / vague**
- **Current (a):** `which selects the safe candidate predicted to increase the Fisher information along its weakest direction. The criterion already favors sensitivities that complement the accumulated dataset.`
- **Replace (a):** `which specializes Eq.~\eqref{eq:rt-e-optimal} to the present design variables.`
- **Current (b):** `A separate novelty check may nevertheless select a slightly less informative candidate when its predicted response is sufficiently different from the experiments already performed.`
- **Replace (b):** `[State whether a novelty check was used.] A novelty check selects a candidate with lower predicted information when its predicted response differs from the experiments already performed by more than [threshold].`
- **Problem:** The E-optimal rationale appears four times (L181, L363, L680, L691), and the novelty check twice (L181, L691). Eq. `e-optimal-design` duplicates Eq. `rt-e-optimal`.

**IIC-12 · L706–707 · repetition / signposting**
- **Current (a):** `The model-based policy is first obtained through model-predictive reference synthesis.`
- **Replace (a):** *(delete)*
- **Current (b):** `The model-based policy $\pi_{\mathrm{MB}}$ is obtained from a finite-horizon`
- **Replace (b):** `The model-based policy $\pi_{\mathrm{MB}}$ is obtained by model-predictive reference synthesis, from a finite-horizon`
- **Current (c):** `The optimized policy is therefore computed before the flight and then executed online as a lightweight interpolation table. In this work, \emph{model predictive control} refers to this model-predictive reference synthesis; a receding-horizon optimizer is not run onboard.`
- **Replace (c):** `Unlike MPC, no receding-horizon optimization runs onboard.`
- **Problem:** Two consecutive sentences have the same subject and verb. The table implementation is stated at L697 ("lookup table") and again here ("interpolation table"). The definition of "model predictive control" is defensive, because the method is called MPC nowhere else.

**IIC-13 · L709 · undefined symbol**
- **Current:** `Performance is evaluated against the original mission reference used by the nominal cascaded PID controller. The tracking cost and corresponding reward are`
- **Problem:** Eq. `reward`, the paper's central metric, uses $N_{\mathcal R}$, $\Omega_{\mathcal R}$, and $z_k$, and none of them is defined. $\Omega$ also names the rotor speed.
- **Replace:** `Performance is measured against the nominal reference $z_{\mathrm{BL}}$. With $z_k$ the altitude at the $N_{\mathcal R}$ streamwise positions $x_k$ of the region of interest $\Omega_{\mathcal R}$, the tracking cost and reward are`

**IIC-14 · L730 · vague (missing number)**
- **Current:** `Subsequent policies $\pi_{\mathrm{EI},i}$ are selected sequentially by Expected Improvement; after each flight, the physical reward is appended to the reward-transfer surrogate dataset.`
- **Problem:** The number of EI flights at the nominal condition is never stated. L910 says "a few" and L982 says "few". It is the paper's key data-efficiency number.
- **Replace:** `Then [number] policies $\pi_{\mathrm{EI},i}$ are selected sequentially by Expected Improvement, and each physical reward is added to the surrogate dataset.`

**IIC-15 · L732 and L738 · repetition / misplaced method details**
- **Current (a):** `Physical rewards are then used to refine this model-based policy and compensate for the remaining model discrepancy. Reinforcement Twinning uses these measurements to correct the local policy ranking predicted by the DT. A new candidate is written as`
- **Replace (a):** `A candidate policy is written as`
- **Current (b):** `A space-filling library is first evaluated in the DT; the same reference and rotor-clearance checks used for the MB solution define the admissible set $\mathcal A_{\mathrm{safe}}$.`
- **Replace (b):** `The three Gaussian basis functions are centered at $x/R\simeq35$, $54$, and $70$, with width [value], and $a_A,a_B,a_C\in[-1,1]$. The reference and rotor-clearance checks used for $\pi_{\mathrm{MB}}$ define the admissible set $\mathcal A_{\mathrm{safe}}$.`
- **Problem:** The purpose repeats L199, L242, and Intro L58. The Sobol library is stated at L730, here, at L892, and in the Fig. 7 caption. The basis centers and bounds appear only in Results (L892) and the width nowhere. Move them here (see IIID-3).

**IIC-16 · L740 · vague**
- **Current:** `The rewards are computed from the cleaned mean trajectories and are treated as deterministic campaign observations;`
- **Problem:** "cleaned" is never explained. The same phrase is used at L901.
- **Replace:** `The rewards are computed from the mean of the repeated trajectories after [describe the cleaning] and are treated as deterministic observations;`

**IIC-17 · L760 · repetition**
- **Current (a):** `The first term exploits candidates with a high predicted physical reward, whereas the second rewards unresolved but potentially useful regions.`
- **Replace (a):** *(delete)*
- **Current (b):** `The model-based policy remains the reference throughout the search; data are used to learn the GP discrepancy that affects physical performance.`
- **Replace (b):** *(delete)*
- **Problem:** The EI terms are explained at L234, and the role of the model-based policy at L199, L242, and L865. Eq. `ei` also duplicates Eq. `rt-expected-improvement` with a different argument ($\mathbf a$ against $\boldsymbol\xi$). Keeping one equation is the author's decision.

**IIC-18 · L768 · logic**
- **Current:** `Consequently, a correction learned where the model-based action is large is reduced automatically when the local MB solution requires little intervention, rather than being transferred as a fixed altitude offset.`
- **Problem:** Eq. `rt-policy` is additive: $\Delta z_\pi=\Delta z_{\mathrm{MB}}+R\,\mathbf b^{\mathsf T}\mathbf a$. A fixed $\mathbf a$ therefore gives a fixed offset unless $\mathbf b(x)$ scales with $\Delta z_{\mathrm{MB}}$, which the text never says. The claim is repeated at L942 ("This scaling preserves ...") and L771. The sentence also uses three names for one thing: "model-based action", "MB solution", and "MB deformation".
- **Replace:** `[State how $\mathbf b(x)$ depends on $\Delta z_{\mathrm{MB}}(x)$.] A correction learned where the model-based correction is large is therefore reduced where the local model-based correction is small, instead of being transferred as a fixed altitude offset.`

**IIC-19 · L771 · repetition / signposting**
- **Current:** `These tests distinguish direct transfer of the nominal correction from a local, proof-of-concept extension of the RT search at a new operating condition; they do not constitute convergence of a surrogate over the full velocity-clearance domain.`
- **Problem:** The disclaimer is repeated at L962, L975, and L984, and in the abstract. Keep it in III-E (C12) and in the Conclusions.
- **Replace:** `These tests separate direct transfer of the nominal correction from a local RT search at a new operating condition.`

**IIC-20 · L771 · logic / colon**
- **Current:** `Two off-nominal conditions are considered: $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and $(1,0.113)$. For each condition, a baseline policy $\pi_{\mathrm{BL}}$ and a model-based policy $\pi_{\mathrm{MB}}$ are computed with the frozen identified DT.`
- **Problem:** There is a colon construction, and the baseline policy is not computed with the DT. The two conditions are listed again with a colon at L942.
- **Replace:** `Two off-nominal conditions are tested, $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and $(1,0.113)$. At each, the baseline policy $\pi_{\mathrm{BL}}$ is flown, and a model-based policy $\pi_{\mathrm{MB}}$ is computed with the frozen DT.`

Paragraphs L571, L693, and L697 are compressed in Section 4 (C3, C4, C5).

### 2.5 Section III-A, Baseline Response (L777–791)

**IIIA-1 · L782 · colon / vague**
- **Current:** `The response changes markedly over the obstacle: the vehicle initially rises to approximately $z/R=2.5$ and subsequently settles around $z/R=2$.`
- **Problem:** There is a colon construction, and "markedly" is redundant because numbers follow.
- **Replace:** `Over the obstacle, the vehicle first rises to about $z/R=2.5$ and then settles around $z/R=2$.`

**IIIA-2 · L782 · logic / unsupported claim**
- **Current:** `The cascaded PID is tuned around hovering and contains no model that can anticipate the surface-induced thrust augmentation.`
- **Problem:** The lack of anticipation explains the overshoot. It does not explain the persistent offset: the vehicle settles at $z/R\approx2$ instead of $1.5$ for the whole 0.81 m, or about 2.3 s, over the obstacle, despite integral action. "tuned around hovering" has no source.
- **Replace:** `The cascaded PID, tuned for hover~\cite{BitcrazeControllers} [check], cannot anticipate the surface-induced thrust augmentation, and its integral action [explain why the offset over the obstacle persists, e.g. its time constant against the 2.3~s crossing].`

**IIIA-3 · L784 · vague**
- **Current:** `Both excursions are substantially larger than the run-to-run dispersion, indicating a repeatable interaction rather than experimental scatter.`
- **Problem:** "substantially" has no number. The RMS band width is never given.
- **Replace:** `Both excursions exceed the run-to-run dispersion, which is at most [value]$R$, so they are a repeatable interaction rather than experimental scatter.`

L780 is compressed in Section 4 (C14).

### 2.6 Section III-B, Information Phase (L793–850)

**IIIB-1 · L807 · repetition / vague**
- **Current:** `Both coefficients are initialized with the Cheeseman-Bennett values, $A=1/16$ and $p=2$, and change substantially after the first adjoint identification, performed using only the baseline record in the gray region.`
- **Problem:** The initialization is stated a fourth time (L542, L573, L60). "change substantially" should give the values after the first identification.
- **Replace:** `Both coefficients start from the Cheeseman--Bennett values (Section~\ref{sec:ge-model}) and change to $A=$[value] and $p=$[value] after the first identification, which uses only the baseline record (gray region).`

**IIIB-2 · L811 · vague**
- **Current:** `Across the following broad-domain episodes, $\lambda_{\min}(\mathbf F)$ continues to increase, but with a much smaller slope, reaching $1.000$ after the sixth information-oriented policy.`
- **Problem:** "much smaller" can be replaced by the numbers the paper already has.
- **Replace:** `Over the next five broad-domain episodes, $\lambda_{\min}(\mathbf F)$ rises only from $0.676$ to $1.000$.`

**IIIB-3 · L811 · undefined symbol**
- **Current:** `The estimated parameter correlation starts at $\rho_{A,p}=0.974$ for the baseline record`
- **Problem:** $\rho_{A,p}$ is not defined anywhere. Methods mentions only "their estimated correlation". It presumably comes from $\boldsymbol\Sigma_\theta$ of Eq. `parameter-covariance`. Define it there or here.
- **Replace:** `The correlation $\rho_{A,p}$ of $A$ and $p$, computed from $\boldsymbol{\Sigma}_{\theta}$ [check], starts at $0.974$ for the baseline record`

**IIIB-5 · L815 · logic / repetition**
- **Current:** `The observed clearance coverage and the uncertainty remaining below $z/R=2$ motivate the restriction of the reference domain to $0.5<z/R<1.5$. The earlier records remain in the cumulative replay buffer; only the admissible references for the next designs are changed.`
- **Problem:** The motivation differs from L575 (slowing $\lambda_{\min}$), and the second sentence repeats L575. Results should report the evidence and refer to the Methods decision.
- **Replace:** `The uncertainty that remains below $z/R=2$ supports the restriction to the low-clearance domain (Section~\ref{sec:information-phase}).`

**IIIB-6 · L828 · vague**
- **Current:** `Returning to Fig.~\ref{fig:fge-quality}, the final model changes only moderately at large clearance but differs substantially from the broad-domain estimate below $z/R=2$. The most important improvement in this region is the contraction of the relative uncertainty.`
- **Problem:** "moderately", "substantially", and "most important" have no numbers. The relative uncertainty is never quantified in the text.
- **Replace:** `In Fig.~\ref{fig:fge-quality}, the final model is close to the broad-domain estimate above $z/R=2$ and differs from it below, by [value] in $f_{\mathrm{GE}}$ at $z/R=0.5$. Below $z/R=2$, the relative uncertainty falls from [value] to [value].`

**IIIB-7 · L828 · repetition / logic**
- **Current:** `The coefficient stabilization, the limited further reduction of $\rho_{A,p}$, and the improved confidence in the control-relevant part of $f_{\mathrm{GE}}$ are taken together as the stopping condition for the information phase.`
- **Problem:** This is the stopping rule again, with a third ingredient that Methods does not list (IIA-9).
- **Replace:** `These observations meet the stopping criterion of Section~\ref{sec:rt-framework}.`

**IIIB-8 · L837 · colon / vague**
- **Current:** `The final coefficients differ substantially from the Cheeseman-Bennett initialization: the exponent returns close to two, but the identified amplitude is almost twice the classical value.`
- **Problem:** There is a colon construction, and "substantially" can be replaced by the paper's own numbers.
- **Replace:** `The final exponent, $p=1.980$, is close to the Cheeseman--Bennett value $p=2$, whereas the final amplitude, $A=0.121$, is almost twice $1/16$.`

**IIIB-9 · L837 · repetition / signposting**
- **Current:** `It does not imply that the two-parameter law resolves every transient feature; it establishes a more representative static model over the range that can be tested safely.`
- **Problem:** The static-law limitation is stated at L544, L863, L879, and L986. "safely" is also used here.
- **Replace:** *(delete)*

L796–798, L841, and L850 are compressed in Section 4 (C17, C6).

### 2.7 Section III-C, Model-Based Policy (L852–872)

**IIIC-1 · L855 · repetition / wrong reference**
- **Current:** `Their vertical coordinates are optimized by minimizing the tracking cost introduced in Section~\ref{sec:performance-phase}, with respect to the nominal clearance $z^\ast/R=1.5$ and subject to the prescribed safety constraints.`
- **Problem:** The policy minimizes $J_{\mathrm{MB}}$ (Eq. `mb-objective`), not the tracking cost alone. The cost is introduced in the "Model-based policy" paragraph (label `sec:mb-optimum`), not under `sec:performance-phase`; both labels print as "Section II-C". The whole paragraph repeats L697–726; see C16.
- **Replace:** `Their values minimize $J_{\mathrm{MB}}$ of Eq.~\eqref{eq:mb-objective}.`

**IIIC-2 · L859 · vague**
- **Current (a):** `These anticipatory actions produce a markedly lower experimental trajectory over the obstacle than the baseline response.`
- **Replace (a):** `Over the obstacle, the measured trajectory peaks at $z/R\approx$[value], against $2.5$ under $\pi_{\mathrm{BL}}$.`
- **Current (b):** `A substantial undershoot nevertheless remains after the trailing edge`
- **Replace (b):** `An undershoot to $z/R\approx$[value] nevertheless remains after the trailing edge`
- **Problem:** "markedly" and "substantial" have no numbers. The trajectory extrema are given for the baseline (L782, L784) but never for $\pi_{\mathrm{MB}}$.

**IIIC-3 · L861 · inconsistent number / vague**
- **Current:** `The DT reward increases from approximately $\mathcal R_{\circ}=0.68$ for $\pi_{\mathrm{BL}}$ to $\mathcal R_{\circ}=0.97$ for $\pi_{\mathrm{MB}}$. The corresponding physical reward increases from approximately $\mathcal R_{\bullet}=0.54$ to $\mathcal R_{\bullet}=0.85$.`
- **Problem:** L910 gives the same rewards as $0.968$ and $0.855$, and $0.855$ rounds to $0.86$, not $0.85$. Use one precision. "approximately" is redundant with two decimals.
- **Replace:** `The DT reward increases from $\mathcal R_{\circ}=0.68$ for $\pi_{\mathrm{BL}}$ to $0.968$ for $\pi_{\mathrm{MB}}$, and the physical reward from $\mathcal R_{\bullet}=0.54$ to $0.855$.`

**IIIC-4 · L861 · improper word**
- **Current:** `Their consistent ordering supports the conclusion that the identified DT contains sufficient causal information to design a policy that improves physical tracking, while the difference in their absolute values quantifies the remaining transfer error.`
- **Problem:** "causal information" is undefined, and "consistent ordering" of two points is an overstatement.
- **Replace:** `Both rewards rank $\pi_{\mathrm{MB}}$ above $\pi_{\mathrm{BL}}$, so the identified DT is accurate enough to design a policy that improves physical tracking. The gap between the two rewards measures the remaining transfer error.`

**IIIC-5 · L863 · inconsistent term / colon / vague**
- **Current (a):** `This difference is also visible in the trajectory replay.`
- **Replace (a):** `The DT prediction $\mathrm{DT}_{\mathrm{MB}}$ in Fig.~\ref{fig:mb-optimum} shows the same gap.`
- **Current (b):** `The larger discrepancy occurs around the trailing edge: the DT predicts that the reference increase should almost suppress the downstream undershoot, whereas a pronounced loss of clearance remains experimentally.`
- **Replace (b):** `The largest difference occurs at the trailing edge. The DT predicts that raising the reference almost suppresses the downstream undershoot, whereas the vehicle still loses [value]$R$ of clearance.`
- **Problem:** "replay" denotes factual replay elsewhere, while the Fig. 6 caption calls this curve a "DT prediction". (b) has a colon construction and "pronounced" without a number. "discrepancy" also has a fourth meaning here (Section 3).

L865 is cut in Section 4 (C7).

### 2.8 Section III-D, Performance Phase (L874–935)

**IIID-1 · L881 · logic / method in Results**
- **Current:** `The information-oriented policies used during identification are excluded because their large altitude excursions were designed to excite the model parameters, not to maintain the nominal clearance $z^{\ast}/R=1.5$.`
- **Problem:** This is a method decision that contradicts L146. Move it to Methods (IIA-6).
- **Replace:** *(delete)*

**IIID-2 · L881 · repetition**
- **Current (a):** `Two additional policies are then introduced by applying one and two thirds of the model-based reference correction to the baseline reference.`
- **Replace (a):** `Fig.~\ref{fig:intermediate-policies} shows the interpolation policies $\pi_{\lambda,i}$ of Section~\ref{sec:performance-phase}.`
- **Current (b):** `Their main role is consequently to establish the global DT-to-physical reward trend and calibrate the affine component of the reward-transfer surrogate before the GP discrepancy is introduced.`
- **Replace (b):** *(delete)*
- **Problem:** Both the definition and the purpose are already given at L730. Also delete the later "The resulting policies ... are reported in Fig.~..." because (a) now introduces the figure.

**IIID-3 · L892 · method details in Results**
- **Current:** `In the present work, local corrections are generated from three Gaussian basis functions centered on the model-based reference at $x/R\simeq35$, $54$, and $70$.`
- **Problem:** The basis definition belongs in II-C (IIC-15b), and its width is missing. "centered on the model-based reference" is ambiguous; it is unclear whether this means a position or a shape.
- **Replace:** `The basis centers A and B lie above the obstacle and C downstream of it (Fig.~\ref{fig:sobol}).` Then delete the following sentence, "The first two centers, denoted by A and B, ...".

**IIID-4 · L901 · long sentence / colon / repetition / symbol**
- **Current (a):** `These measurements improve the local calibration of $\widehat{\delta}(\mathbf a)$: the affine relation continues to describe the overall relation between the DT and physical rewards,`
- **Replace (a):** `These measurements calibrate the GP discrepancy $\delta(\mathbf a)$ near $\pi_{\mathrm{MB}}$.`
- **Current (b):** ` whereas the Gaussian process learns how policies with similar DT performance can be ranked differently by the physical environment.`
- **Replace (b):** *(delete; note the leading space)*
- **Problem:** The sentence is 43 words long and has a colon construction. The roles of the affine fit and the GP repeat L212 and L222. $\widehat\delta$ is a third symbol for the GP term, after $\delta$ and $\mu_\delta$.

**IIID-6 · L910 · vague (missing number)**
- **Current:** `Nevertheless, after only a few EI-guided evaluations, the search identifies $\pi_{\mathrm{EI}}^{\star}$.`
- **Problem:** See IIC-14. "a few" is the paper's main data-efficiency claim and has no number.
- **Replace:** `After [number] EI-guided evaluations, the search identifies $\pi_{\mathrm{EI}}^{\star}$.`

**IIID-7 · L910 · vague / colon**
- **Current:** `The marked difference between these two increments is the improvement enabled by the learned GP discrepancy: the DT alone regards the two policies as nearly equivalent, while the physical observations reveal a substantial performance gain.`
- **Problem:** There is a colon construction, and "marked" and "substantial" can be replaced by the paper's own numbers ($0.978-0.968$ against $0.952-0.855$).
- **Replace:** `The physical gain, $0.097$, is almost ten times the DT gain, $0.010$. The DT alone ranks the two policies as nearly equivalent, and the learned GP discrepancy reveals the difference.`

**IIID-8 · L910 · unsupported claim**
- **Current:** `Other high-reward evaluations approach a similar reference shape, supporting a repeatable control strategy rather than proving convergence to a unique optimum.`
- **Problem:** No figure shows the references of the other high-reward evaluations. Fig. 9 shows only $\pi_{\mathrm{EI}}^{\star}$.
- **Replace:** `[Show the other high-reward references, e.g. in Fig.~\ref{fig:ei-trajectory}, or delete the sentence.]`

**IIID-9 · L919 · vague / unsupported claim**
- **Current (a):** `which slightly reduces the remaining positive tracking excursion.`
- **Replace (a):** `which reduces the remaining positive excursion from [value] to [value].`
- **Current (b):** `The vehicle consequently reaches a somewhat larger clearance before leaving the obstacle and is better prepared for the subsequent loss of aerodynamic support. The downstream undershoot is markedly reduced and the recovery toward $z^{\ast}/R=1.5$ becomes smoother.`
- **Replace (b):** `The vehicle therefore leaves the obstacle at a larger clearance, which offsets the following loss of thrust. The downstream minimum rises from $z/R\approx$[value] to [value], and the recovery toward $z^{\ast}/R=1.5$ is smoother.`
- **Current (c):** `This reduction of the post-obstacle excursion supplies the dominant reward gain and clearly separates $\pi_{\mathrm{EI}}^{\star}$ from the purely model-based policy;`
- **Replace (c):** `This smaller post-obstacle excursion accounts for [share] of the reward gain [give the tracking cost before and after the trailing edge] and separates $\pi_{\mathrm{EI}}^{\star}$ from $\pi_{\mathrm{MB}}$;`
- **Problem:** Four vague intensifiers ("slightly", "somewhat", "markedly", "clearly") appear in one paragraph. "better prepared" is anthropomorphic. "dominant reward gain" is a quantitative claim without the split of the cost before and after the trailing edge.

**IIID-10 · L928 · unsupported claim / logic (caption)**
- **Current:** `The single-run paths reproduce the ordering observed in the mean trajectories, supporting the repeatability of the measured improvement. In particular, the three paths superposed in Fig.~\ref{fig:real-comparison}(c) make the large departure of the baseline policy immediately visible.`
- **Problem:** One flight per case cannot support repeatability; the five-run RMS bands do. The Fig. 10 caption says panel (c) shows only $\pi_{\mathrm{EI}}^{\star}$, not three superposed paths.
- **Replace:** `The single-run paths show the same ordering as the mean trajectories. [Panel (c) overlays the three paths — state this in the caption, or correct the reference.]`

L879 and L890 are compressed in Section 4 (C8, C9).

### 2.9 Section III-E and Conclusions (L937–986)

**IIIE-1 · L942 · repetition / logic**
- **Current (a):** `At each condition, the built-in PID controller executes the condition-specific baseline policy $\pi_{\mathrm{BL}}$, while a new model-based policy is computed using the same frozen parameter vector $\widehat{\boldsymbol{\theta}}_p$ identified at the end of the information phase.`
- **Replace (a):** *(delete)*
- **Current (b):** `This scaling preserves the learned correction structure without imposing the nominal reference correction as a fixed altitude offset.`
- **Replace (b):** *(delete)*
- **Problem:** (a) repeats L771. (b) repeats L768, and the "scaling" it refers to is not explained (IIC-18).

**IIIE-2 · L944 and L964 · repetition / vague**
- **Current (a):** `In both operating conditions, the condition-specific model-based policy markedly improves tracking relative to the corresponding baseline policy. At $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$, the transferred policy provides a further, albeit modest, improvement.`
- **Replace (a):** *(delete here; the numbers go in (b))*
- **Current (b):** `The transferred-policy diamond improves slightly on the model-based-policy square at the low-speed, larger-clearance condition. At the higher-speed, small-clearance condition, the ordering is reversed and the transferred policy performs slightly worse than $\pi_{\mathrm{MB}}$.`
- **Replace (b):** `At both conditions, $\pi_{\mathrm{MB}}$ raises $\mathcal S_{\bullet}$ to [value] and [value]. At the lower-speed, larger-clearance condition, the transferred policy (diamond) reaches $\mathcal S_{\bullet}=$[value], against [value] for $\pi_{\mathrm{MB}}$ (square). At the higher-speed, smaller-clearance condition the order is reversed, at [value] against [value].`
- **Problem:** The reward ranking is stated twice, at L944 (where Fig. 12 shows only trajectories) and at L964 (Fig. 13, which shows the scores). Keep it at L964, the figure that supports it. "markedly", "modest", and "slightly" (twice) carry no numbers. The paper gives no $\mathcal S$ values except 0.57 and 0.83.

**IIIE-3 · L944 · colon / vague / unsupported claim**
- **Current:** `At the higher-speed, small-clearance condition $(1,0.113)$, however, its physical reward is slightly lower than that of the model-based policy. This loss is important: the transferred correction was learned from discrepancies measured only at the nominal condition $(1.5,0.079)$,`
- **Problem:** The ranking duplicates (b) above. There is a colon construction and "important". The cause that follows is stated as fact but is a hypothesis.
- **Replace:** `The transferred correction was learned from discrepancies measured only at the nominal condition, and`. Then change the following "whereas the relative importance of the unmodeled transients changes" to `the relative importance of the unmodeled transients may change`.

**IIIE-5 · L953 · undefined symbol**
- **Current:** `By construction, $\mathcal S_e=0$ for the corresponding baseline policy and a larger value indicates a greater reduction of the tracking cost.`
- **Problem:** $\mathcal S_e$ is never defined. It presumably means $\mathcal S_\circ$ and $\mathcal S_\bullet$. Move these definitions to L762 (C11).
- **Replace:** `By construction, $\mathcal S_{\circ}=\mathcal S_{\bullet}=0$ for the baseline policy, and a larger score means a larger reduction of the tracking cost.`

**IIIE-6 · L955 · method in Results / undefined symbol**
- **Current:** `In this more general formulation, the GP discrepancy depends on both the policy and the operating condition,`
- **Problem:** Eq. `generalized-surrogate` is a method equation placed in Results. It is the third version of the surrogate, and $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}$ is undefined.
- **Replace:** `[Move this sentence and Eq.~\eqref{eq:generalized-surrogate} to Section~\ref{sec:performance-phase}, after Eq.~\eqref{eq:normalized-score}, and define $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}=\gamma_0+\gamma_1\mathcal S_{\circ}$ (check).]`

**IIIE-7 · L975 · improper word / improper word ("safe")**
- **Current (a):** `At a new operating condition, the local DT first supplies a model-based policy that already improves substantially over the baseline policy.`
- **Replace (a):** `At a new operating condition, the frozen DT first supplies a model-based policy that already improves on the baseline policy (Fig.~\ref{fig:generalization-reward}).`
- **Current (b):** `while retaining the model-based policy as the safe and data-efficient reference.`
- **Replace (b):** `while keeping the DT-screened model-based policy as the reference.`
- **Problem:** The DT is the same frozen DT everywhere, so "local DT" is wrong. "substantially" has no number, and "safe" describes a DT check.

**CON-1 · L980 · long sentence / colon / improper word**
- **Current:** `The information phase provided evidence that the designed experiments added more than visual diversity: the cumulative smallest Fisher eigenvalue grew much faster than for repeated baseline experiments,`
- **Problem:** The sentence is 48 words long and has a colon construction. "visual diversity" is undefined; no visual claim was made. "much faster" can be given as $3.242$ against $0.387$. See C13 for the full rewrite.
- **Replace:** `In the information phase, the designed experiments raised the smallest eigenvalue of the cumulative Fisher-information proxy to $3.242$ after twelve episodes, against $0.387$ for twelve repeated baseline episodes,`

**CON-2 · L982 and L986 · improper word ("safety")**
- **Current (a):** `while satisfying the adopted virtual safety constraints.`
- **Replace (a):** `while passing the DT clearance checks.`
- **Current (b):** `virtual safety screening`
- **Replace (b):** `DT screening`
- **Problem:** Both phrases describe checks made in the twin.

### 2.10 Second-tier items

These are lower-impact items. Each Current string is exact and unique. IDs stay stable, so a gap in the main numbering (IIA-16, IIB-7, IIB-10, IIC-6, IIIA-4, IIIB-4, IIID-5, IIIE-4) marks an item moved here to keep the main list near 80.

- **AB-5 · L32 · improper word.** `the remaining uncertainty on the corrective parameters guide the design of information-oriented policies to be deployed on the physical environment.` → `the remaining uncertainty in the correction parameters guide the design of information-oriented policies for the physical environment.`
- **AB-6 · L32 · wordy.** `This work presents an implementation of Reinforcement Twinning (RT) applied to a micro aerial vehicle operating in ground effect.` → `This work applies Reinforcement Twinning (RT) to a micro aerial vehicle flying in ground effect.`
- **AB-7 · L32 · inconsistent term.** `combines DT and physical environment rewards` → `combines DT and physical rewards`
- **AB-8 · L32 · inconsistent term (active vs. adaptive).** `These results support the use of an adaptive DT` → `These results support the use of an active DT`
- **IIA-16 · L242 · repetition.** `The DT restricts and guides the search around $\pi_{\mathrm{MB}}$, while the physical rewards allow RT to improve upon that policy.` → *(delete; also in Intro L58, L199, L760, L865, L982)*
- **IIA-18 · L117 · signposting / improper word.** `As anticipated, each of the two environments involved in the Reinforcement Twinning loop features its own objective. The physical environment aims for policy parameters` → `Each environment has its own objective. The physical environment seeks policy parameters`
- **IIA-19 · L143 · long sentence.** The sentence from L117 runs through two display equations and the record definition. Change the comma at the end of L142 to a period, and `and $\mathcal{L}_p$ compares the DT and physical observations selected for identification.` → `The loss $\mathcal{L}_p$ compares the DT and physical observations selected for identification.`
- **IIA-20 · L146 · vague intensifier / logic.** `The two policy families may have significantly different parameterizations because their classification reflects the objective used during policy design.` → `The two families are defined by the objective used to design them and may have different parameterizations.`
- **IIA-21 · L147 · inconsistent term.** `A binary interaction schedule $e_n\in\{0,1\}$ determines which policy is designed and deployed during each physical episode $n$:` → `A binary selector $e_n\in\{0,1\}$ determines which policy is designed and deployed in physical episode $n$,`
- **IIA-22 · L158 · grammar / signposting.** `We consequently distinguish a first \emph{information phase} and a subsequent separated \emph{performance phase}, which are described in detail below.` → `This defines an \emph{information phase} followed by a separate \emph{performance phase}.`
- **IIA-23 · L161 · improper word.** `As $\mathbf S(\boldsymbol{\theta}_{\iota})=\partial\mathbf o_{\circ}/\partial\boldsymbol{\theta}_p$ denotes the sensitivity of the predicted observations and $\boldsymbol{\Sigma}_{\nu}$ their noise covariance, the information expected after a candidate policy is` → `With $\mathbf S(\boldsymbol{\theta}_{\iota})=\partial\mathbf o_{\circ}/\partial\boldsymbol{\theta}_p$ the sensitivity of the predicted observations and $\boldsymbol{\Sigma}_{\nu}$ the covariance of the measurement noise $\boldsymbol{\nu}$, the information expected after a candidate policy is`
- **IIA-24 · L161 · repetition.** `Each candidate represents a possible next experiment and is evaluated in the DT before deployment.` → *(delete)*
- **IIA-25 · L185 · improper word ("safety").** `accounting for safety constraints and actuator limits within the DT,` → `subject to the clearance and actuator constraints checked in the DT,`
- **IIA-26 · L199 · unsupported claim (a result stated in Methods).** `because this model-based policy already improves upon the baseline policy and provides a physically informed reference.` → `because this model-based policy is expected to improve upon the baseline policy and provides a physically informed reference.`
- **IIA-27 · L213 · improper word.** `The GP is conditioned on the discrepancies between the physical rewards` → `The GP is conditioned on the residuals between the physical rewards`
- **IIA-28 · L245 · repetition.** `In both cases, the physical environment is exposed only to a policy that has first been generated and screened in the DT.` → *(delete)*
- **IIA-29 · L245 · improper word / figure introduction.** `The RT closed-loop is summarized in Fig.~\ref{fig:rt_framework}. The diagram represents one physical-digital iteration and makes explicit where information is created, where it is interpreted, and how it affects the next interaction with the physical environment.` → `Fig.~\ref{fig:rt_framework} shows one iteration of the RT loop, from the deployed policy to the choice of the next one.`
- **IIA-30 · L353 · repetition / inconsistent term.** `The physical environment and its active Digital Twin evolve side by side through physical observations and virtual candidate evaluations, in order to achieve their respective objectives.` → `The physical environment and its active DT evolve side by side through physical observations and virtual candidate evaluations.`
- **IIA-31 · L282 · inconsistent symbol (Fig. 1).** `hidden state $\mathbf{s}_\bullet$, input $\mathbf z$\\` → `hidden state $\mathbf{s}_\bullet$, exogenous input $\mathbf d$\\`. In addition, Fig. 1 uses $\mathcal J_{\mathrm{info}}$ and $\widehat{\mathcal R}_\bullet$, which never appear in the text. The text uses $\lambda_{\min}[\mathbf F_{n+1}]$ and $\mu_\bullet$ instead.
- **IIB-7 · L374 · repetition / grammar.** `The Lighthouse positioning system provides sub-centimetre-level absolute accuracy and sub-millimetre repeatability.` → *(delete; the next sentence gives the numbers from Taffanel et al., and the spelling is British)*
- **IIB-10 · L546 · symbol clash / vague pronoun.** `It is therefore weighted by $\chi_i(x)\in[0,1]$, defined as the fraction of rotor disk $i$ that overlaps the obstacle.` → `The augmentation is therefore weighted by the fraction $\chi_i(x)\in[0,1]$ of rotor disk $i$ that overlaps the obstacle.` $\chi_i$ also clashes with $\boldsymbol\chi$ (Section 3.2).
- **IIB-11 · L372 · vague.** `The horizontal reference frame retains its origin at $x=y=0$, whereas the vertical origin is placed at the upper surface of the obstacle, so that $z=0$ at the obstacle height.` → `The origin of $x$ and $y$ is the start position of each test [check], and $z=0$ at the upper surface of the obstacle.`
- **IIB-12 · L374 · vague number / repetition.** `Together with a 350 mAh battery, the drone mass is around $m=32.42$~g.` → `With its 350~mAh battery, the vehicle has mass $m=32.42$~g.` "around" does not fit four significant digits.
- **IIB-13 · L374 · wordy.** `This configuration reduces the probability of temporary tracking loss or a position-estimation disturbance caused by an interruption of the optical link between a Lighthouse station and the Lighthouse deck mounted on the Crazyflie.` → `This overlap reduces the risk of losing the position estimate when one optical link is interrupted.`
- **IIB-14 · L374 · undefined acronym.** `is equipped with an onboard IMU sensor for attitude control` → `carries an onboard inertial measurement unit (IMU) for attitude control`
- **IIB-15 · L425 · undefined acronym.** `and the individual motor PWM commands` → `and the individual motor pulse-width-modulation (PWM) commands`
- **IIB-16 · L427 · unsupported claim.** `ensuring consistency between the numerical and experimental closed-loop dynamics.` → `so that the DT and the vehicle run the same controller.`
- **IIB-17 · L432 · signposting.** `The finite-obstacle ground-effect correction is incorporated below as the unknown model component with associated $\boldsymbol{\theta}_p$ learned by RT.` → `RT identifies only the ground-effect correction of Eq.~\eqref{eq:corrected-thrust}, whose parameters form $\boldsymbol{\theta}_p$.`
- **IIB-18 · L505 · repetition.** `The vehicle dynamics are coupled with the same cascaded PID architecture used in the physical environment, providing the nominal closed-loop model on which the ground-effect correction is identified.` → *(delete; stated at L427)*
- **IIB-19 · L529 · improper word / to check.** `This interaction is introduced through a deliberately simple physical model inspired by the analytical formulation of Cheeseman and Bennett for an isolated rotor in hovering~\cite{CheesemanBennett1955}.` → `This interaction is modeled with a low-order law inspired by the Cheeseman--Bennett formulation for an isolated rotor in hover~\cite{CheesemanBennett1955}.` The cited report is titled "...in Forward Flight", so check "in hover". Also change `generated as the vehicle closely crosses the finite obstacle` → `generated as the vehicle crosses the finite obstacle at low clearance`.
- **IIB-20 · L542 · improper word.** `The original Cheeseman and Bennett formulation rearranged with the same unknowns would have retained $A=1/16$ and $p=2$.` → `Written in this form, the Cheeseman--Bennett formulation gives $A=1/16$ and $p=2$.` The match holds to first order in $(R/z_i)^2$; check.
- **IIB-21 · L544 · colon / signposting.** `This model is deliberately low order: ground effect is treated as a static function of the instantaneous rotor clearance.` → `The model is static. It treats ground effect as a function of the instantaneous rotor clearance only.` Also at L551: `where $T_{i,\mathrm{OGE}}$ is the nominal rotor thrust outside ground effect.` → *(delete; defined at L529)*.
- **IIC-6 · L573 · repetition.** `The model is initialized from the Cheeseman-Bennett coefficients, $A=1/16$ and $p=2$. Starting from the baseline record,` → `Starting from the baseline record,` The initialization is also stated at L542 (keep), L807, and Intro L60.
- **IIC-21 · L555 · undefined symbol.** `the desired forward velocity is normalized by the ideal induced velocity in hover,` → `the desired forward speed $v_x^\ast$ is normalized by the ideal induced velocity in hover,`
- **IIC-22 · L575 · inconsistent term.** `for the remaining six policies, defining the near-wall domain.` → `for the remaining six policies, defining the low-clearance domain.`
- **IIC-23 · L587 · inconsistent symbol.** `With $N$ episodes in the replay buffer, the identification loss is` → `With $N$ episodes in the replay buffer, the identification loss $\mathcal L_p$ of Eq.~\eqref{eq:rt-model-objective} becomes`. Renaming $J_p$ to $\mathcal L_p$ in the equations is the author's decision.
- **IIC-24 · L614 · missing citation / numbers.** `Adam uses this gradient to update the parameters over successive optimization steps.` → `Adam~[CITE: Kingma and Ba, Adam] updates the parameters with this gradient.` Also give $\beta_1$, $\beta_2$, and $\epsilon$.
- **IIC-25 · L635 · numbers without what they measure.** `The relative-loss, coefficient-range, and projected-gradient tolerances are $2\times10^{-4}$, $10^{-3}$, and $5\times10^{-3}$, respectively. The optimization is considered converged only when all three conditions remain satisfied over a complete monitoring window.` → `The fit has converged when, over a whole window, the relative change of $J_p$ stays below $2\times10^{-4}$, the range of each coefficient below $10^{-3}$, and the norm of the projected gradient below $5\times10^{-3}$.` Check the definitions.
- **IIC-26 · L660 · logic / repetition.** `Thus, $A$ and $p$ may retain a strongly elongated and correlated local uncertainty region even when the resulting ground-effect curve is tightly constrained.` → *(delete)*. "Thus" does not follow from Eq. `uncertainty-propagation`, and the fact is stated with evidence at L826 and L980.
- **IIC-27 · L680 · term before its definition.** `For the post-campaign comparison reported later, every episode and the repeated-baseline counterfactual are reevaluated` → `For the post-campaign comparison of Section~\ref{sec:results-inf}, every episode and the counterfactual sequence of repeated baseline episodes are reevaluated`
- **IIC-28 · L691 · missing numbers.** `Candidates that violate state, reference-rate, acceleration, actuator, or clearance constraints are discarded before deployment.` → `Candidates that violate the state, reference-rate, acceleration, actuator, or clearance limits in the DT ([give values]) are discarded before deployment.`
- **IIC-29 · L702 · two symbols for one thing.** `where $z_{\mathrm{BL}}$ is the nominal mission reference altitude which is constant along $x$.` → `where $z_{\mathrm{BL}}=z^\ast$ is the constant nominal reference.`
- **IIC-30 · L702 · improper word.** `This spatial representation is preferred over the time representation as it prevents small DT-experiment timing differences from desynchronizing the anticipatory command from the obstacle.` → `A spatial rather than temporal parameterization prevents small timing differences between DT and experiment from shifting the anticipatory command relative to the obstacle.`
- **IIC-31 · L704 · inconsistency with L855.** `over the complete crossing and interpolated between consecutive points.` → `over the complete crossing and linearly interpolated between consecutive points.` L855 gives the spacing as $\Delta x\simeq R$ and calls the points "nodes".
- **IIC-32 · L726 · improper word ("safety").** `and the clearance term enforces safety on the tilted rotor geometry rather than only on the vehicle center of mass.` → `and the clearance term applies the $0.5R$ limit to each tilted rotor rather than only to the CoM.` CoM is defined at L436 but never used.
- **IIC-33 · L730 · vague / missing citation.** `A scrambled Sobol library of 2000 coefficient vectors is screened in the DT, and seven admissible, mutually distinct policies $\pi_{\mathbf a,i}$ are deployed to train the local GP discrepancy.` → `A scrambled Sobol library~[CITE: Sobol sequence] of 2000 coefficient vectors is screened in the DT, and seven admissible policies $\pi_{\mathbf a,i}$, chosen by [criterion], are deployed to train the GP discrepancy.`
- **IIC-34 · L740 · ambiguous scaling.** `with each coordinate scaled by $0.30R$.` → `with kernel length scale [0.30 in each coordinate; check the unit, since $\mathbf a$ is dimensionless].`
- **IIC-35 · L747 · repetition / vague pronoun.** `Two policies with similar DT performance can receive different physical corrections. Its posterior mean and variance are updated after every performance-oriented episode.` → `The posterior mean and variance of $\delta$ are updated after every performance-oriented episode.`
- **IIC-36 · L768 · confusing.** `and $\boldsymbol{\chi}$ is augmented with the operating condition.` → `and the GP input is augmented with the operating condition $\boldsymbol{\chi}$.` L747 already says that $\boldsymbol\chi$ contains the operating condition.
- **IIC-37 · L771 · symbol clash.** `Where an additional condition-specific EI search is performed, its best physical policy is denoted by $\pi_{\mathrm{EI}}^{\star}$.` This is the same symbol as the nominal best at L730. Use a distinct symbol, e.g. `$\pi_{\mathrm{EI},\boldsymbol\chi}^{\star}$`, which is the author's decision.
- **IIIA-4 · L784 · repetition.** `The baseline experiment consequently provides the reference cost for all subsequent performance comparisons and the first factual record used during the information phase.` → *(delete; stated at L566, see IIC-4)*
- **IIIA-5 · L782 · vague.** `Before reaching the obstacle, the vehicle maintains an almost constant clearance close to the commanded value, supporting satisfactory tracking at this modest forward speed away from the surface interaction.` → `Before the obstacle, the vehicle holds a nearly constant clearance close to the commanded value.`
- **IIIB-4 · L813 · repetition.** `It describes uncertainty in the total thrust factor rather than in the smaller augmentation $f_{\mathrm{GE}}-1$, and it is not an exact confidence interval.` → *(delete; stated at L660. There are four "not a confidence interval" disclaimers, at L652, L660, L680, and L813, plus two for the GP, at L222 and L740)*
- **IIIB-10 · L798 · vague.** `request markedly different altitude histories across the obstacle` → `request different clearance histories across the obstacle`
- **IIIB-11 · L807 · repetition.** `The episodes designed with references in the broad domain $0.5<z/R<6$ occupy the olive region, while those using the near-wall domain $0.5<z/R<1.5$ occupy the green region.` → `Broad-domain episodes lie in the olive region and low-clearance episodes in the green region.`
- **IIIB-12 · L809 · number without symbol.** `The latter repeats the same measured baseline episode at $0.35$~m/s, including its sampling and residual level, for the same number of cumulative interactions.` → `The latter repeats the measured baseline episode at $v_x^\ast=0.35$~m/s, with its sampling and residual level, for the same number of episodes.`
- **IIIB-13 · L811 · vague.** `The reduction supports the conclusion that the designed missions add a new sensitivity direction, but the remaining value is still high.` → `This reduction indicates that the designed missions excite a new sensitivity direction, although the correlation remains above $0.88$.`
- **IIIB-14 · L813 · vague.** `but this portion of the curve is still associated with substantial local uncertainty.` → `but its relative uncertainty there is still [value].`. In the same paragraph, `the indicator is already small because` → `the indicator is below [value] because`.
- **IIIB-15 · L826 · colon / improper word ("safely").** `This residual coupling follows from the structure of the selected power law and the range that can be explored safely: coordinated variations of $A$ and $p$ can generate very similar $f_{\mathrm{GE}}(z/R)$ curves.` → `This residual coupling follows from the power law and from the clearance range above the $0.5R$ limit. Coordinated variations of $A$ and $p$ produce nearly identical $f_{\mathrm{GE}}(z/R)$ curves over this range.`
- **IIIB-16 · L839 · colon / vague.** `The model initialized with Cheeseman-Bennett predicts the qualitative trend: the increased thrust raises the vehicle above the obstacle, and the removal of that contribution produces a loss of altitude downstream. Its magnitude is nevertheless underestimated.` → `With the Cheeseman--Bennett coefficients, the DT predicts the rise over the obstacle and the loss of altitude downstream, but underestimates both [by value].`
- **IIIC-6 · L857 · repetition.** `The constant reference $\pi_{\mathrm{BL}}$, executed through the built-in PID controller, can react to the aerodynamic interaction only after a tracking error has developed.` → *(delete)*
- **IIIC-7 · L861 · signposting.** `The performance change can be quantified with the same reward definition used throughout the subsequent policy search.` → *(delete; the next sentence can start "With the reward of Eq.~\eqref{eq:reward}, ...")*
- **IIID-5 · L901 · repetition.** `The reward markers are computed from the cleaned mean trajectories; run-to-run dispersion is assessed in the trajectory comparisons and is not represented as a statistical error bar in the surrogate plots.` → *(delete; stated at L740)*
- **IIID-11 · L892 · grammar (dashes) / improper word.** `The subset spans different amplitude combinations and deliberately includes both apparently unfavorable changes-such as increasing the reference above the obstacle or reducing it downstream-and corrections that extend the compensating action already suggested by $\pi_{\mathrm{MB}}$.` → `The seven policies combine different amplitudes. They include changes that look unfavorable, such as raising the reference above the obstacle or lowering it downstream, and changes that extend the correction of $\pi_{\mathrm{MB}}$.`
- **IIID-12 · L892 · vague.** `identify the small subset selected for physical testing.` → `identify the seven policies flown.`
- **IIID-13 · L901 · vague.** `Most of the tested Sobol policies instead occupy a narrow neighborhood of $\pi_{\mathrm{MB}}$ on the DT-reward axis, while their physical rewards remain sufficiently separated to reveal a policy-dependent GP discrepancy.` → `Most Sobol policies have DT rewards within [range] of $\pi_{\mathrm{MB}}$, whereas their physical rewards span [range], which reveals a policy-dependent GP discrepancy.`
- **IIID-14 · L910 · colon / undefined term.** `The acquisition does not seek an immediate reward increase at every iteration: some policies are selected because their GP interpolation uncertainty makes them informative candidates, and their physical reward can therefore remain below the incumbent.` → `EI does not seek a reward increase at every iteration. Some policies are selected for their GP uncertainty, and their physical reward can remain below the best reward $\mathcal R_{\bullet}^{+}$ observed so far.`
- **IIIE-4 · L944 · repetition.** `Transfer therefore provides an informed initialization, but it does not replace condition-specific learning when the operating condition moves away from the region represented in the reward-transfer surrogate dataset.` → *(delete; stated at L964 after Fig. 13, which supports it, and again at L975 and L984)*
- **IIIE-8 · L942 · colon / inconsistent term.** `Two additional operating conditions are considered: a low-speed, larger-clearance crossing at $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and a higher-speed, small-clearance crossing at $(1,0.113)$.` → `Fig.~\ref{fig:generalization-trajectories} shows the lower-speed, larger-clearance crossing at $(2.5,0.045)$ and the higher-speed, smaller-clearance crossing at $(1,0.113)$.`
- **IIIE-9 · L973 · vague.** `The first explores an uncertain policy direction and performs poorly, yielding approximately $\mathcal S_{\bullet}=0.57$, as indicated by the small purple marker in Fig.~\ref{fig:generalization-reward}.` → `The first explores an uncertain policy direction and scores $\mathcal S_{\bullet}=0.57$ (small purple marker in Fig.~\ref{fig:generalization-reward}), below the [value] of $\pi_{\mathrm{MB}}$.`
- **CON-3 · L984 · vague.** `Directly transferring the nominal correction produced a modest gain at one operating condition but slightly underperformed the corresponding model-based policy at the other.` → `Directly transferring the nominal correction raised $\mathcal S_{\bullet}$ by [value] at one operating condition and lowered it by [value] at the other, relative to the model-based policy.`
- **CON-4 · L982 · inconsistent term / vague.** `Fractional and Sobol policies calibrated the reward-transfer surrogate` → `Interpolation and Sobol policies calibrated the reward-transfer surrogate`. In the same paragraph, `With few additional interactions` → `With [number] additional flights`.

### 2.11 Mechanical fixes

Search and replace. Meaning is unchanged.

| Find | Replace | Lines |
|---|---|---|
| `hass` | `has` (or `have`; see P1) | 40 |
| `Cheeseman-Bennett` | `Cheeseman--Bennett` | 45, 60, 573, 807, 813 (×2), 837, 839 (×2) |
| `rotor-surface` | `rotor--surface` | 529, 544, 986 |
| `$x=1.0$-$1.2$~m` / `$x=1.70$-$4.00$~m` | `$x=1.0$--$1.2$~m` / `$x=1.70$--$4.00$~m` | 372 |
| `$0.5-1$~cm` | `$0.5$--$1$~cm` | 374 |
| `Blocks~1-6` | `Blocks~1--6` | 366 |
| `changes-such as` / `downstream-and` | `changes---such as` / `downstream---and` (or commas, IIID-11) | 892 |
| double spaces `_{p}$  in`, `the  model`, `however,  does` | single space | 125, 158, 529 |
| `sub-centimetre`, `sub-millimetre` | `sub-centimeter`, `sub-millimeter` (or delete, IIB-7) | 374 |
| `350 mAh` | `350~mAh` | 374 |
| `$z^*/R=1.5$` | `$z^\ast/R=1.5$` | 782 |
| `Crazyflie 2.1+` | `Crazyflie~2.1+` | 32, 372, 374, 403 (Fig. 2), 432 (L60 already has `~`) |
| `Sec.~\ref` | `Section~\ref` | 563 |
| `The RT closed-loop` / `Twinning closed-loop adopted` | `closed loop` (noun) | 245, 353 |

Two further notes:

- **IEEE equation style.** IEEE style refers to equations as "(5)" and reserves "Equation (5)" for the start of a sentence. The manuscript uses "Eq.~\eqref" throughout. This is optional.
- **Stray text in `references.bib`.** Outside the manuscript, a stray prose paragraph sits after the `CheesemanBennett1955` entry ("The nominal DT described above reproduces ..."). BibTeX ignores it, but delete it.

### 2.12 Numbers the text needs but does not give

These are referenced in the findings above:

- the number of EI flights at the nominal condition (IIC-14, IIID-6, CON-4);
- the total number of physical flights;
- $A$ and $p$ after the first identification (IIIB-1);
- the peak and minimum $z/R$ under $\pi_{\mathrm{MB}}$ and $\pi_{\mathrm{EI}}^{\star}$ (IIIC-2, IIID-9);
- $\mathcal S_\bullet$ of $\pi_{\mathrm{MB}}$ and $\pi_{\mathrm{EI}}^{\mathrm{tr}}$ at both off-nominal conditions (IIIE-2);
- the fitted $\gamma_0$ and $\gamma_1$;
- the basis width and the node spacing of the information policies (IIC-15, C17);
- the reference-rate and acceleration limits (IIC-28);
- the mission duration (IIB-2);
- the maximum RMS band (IIIA-3);
- the relative-uncertainty values below and above $z/R=2$ (IIIB-6, IIIB-14);
- Adam $\beta_1$, $\beta_2$, $\epsilon$, and the model-based optimizer settings (IIC-24);
- the thresholds of the stopping and novelty criteria (IIA-9, IIC-11).

---

## 3. Inconsistent terms and symbols

### 3.1 Terms

Counts are occurrences in the source, including figure code where noted.

| # | Concept | Variants (count: lines) | Proposed single choice |
|---|---|---|---|
| 1 | Low clearance above the horizontal obstacle | "near-wall" (14: 575, 798 ×2, 803 caption, 807, 824, 833 caption, 839, 841 ×2, 846 caption, 850 ×2, 980); "near the wall" (1: 798); "close to the wall" (1: 850); "away from the wall" (1: 813) | **"low-clearance domain"** for $0.5<z/R<1.5$ and "at low clearance" for the region. Intro L43 reserves "wall effect" for lateral surfaces, so "near-wall" for a floor contradicts the paper's own taxonomy. |
| 2 | Digital twin | "Digital Twin" (6: 32, 51, 72, 353, 429 heading, 432); "digital twin" (2: 34 keywords, 125); "Digital twin" (269 in Fig. 1, 293 code comment); "twin" (54, 115, 125, 158, 361); "DT" (126 occurrences on 72 lines); acronym defined 3 times (32, 51, 72) | Define **"digital twin (DT)"** in the Abstract and at Intro L51, lowercase, and use **"DT"** everywhere else. Fig. 1 title "Digital twin" is fine. |
| 3 | The deployed policy representation | "reference governor" (4: 54, 62, 697, 707); "governor" (6 total: 54, 62, 697 ×2, 702, 707); "spatial reference correction" (32); "reference correction" (5: 32, 704, 771, 881, 942); "lookup table" (697); "interpolation table" (707); "spatial altitude reference" (697) | **"spatial reference correction $\Delta z_\pi(x)$"**, stored as a **"lookup table"** (stated once, at L697). Avoid "reference governor" unless the paper cites the reference-governor literature and explains the different usage. |
| 4 | The model-based policy and its correction | "model-based policy" (37 on 31 lines); "$\pi_{\mathrm{MB}}$"/MB (41); "MB solution" (738, 768); "MB deformation" (768); "model-based action" (768, 944); "model-based reference correction" (771, 881); "model-based reference" (892); "model-based optimum" (53); "purely model-based policy" (919); "local model-based" (949 caption) | **"model-based policy $\pi_{\mathrm{MB}}$"** for the policy and **"model-based correction $\Delta z_{\mathrm{MB}}$"** for its offset. Drop "MB solution", "MB deformation", and "model-based action". |
| 5 | Error of the physics model, and the GP term | "GP discrepancy" (16); "model discrepancy" (56, 732); "structural discrepancy" (56, 544); "systematic bias" (58); "realistic discrepancy" (60); "structural error" (879); "residual mismatch" (865, 940); "transfer error" (861); "discrepancy" for trajectories (425 "vertical-position discrepancy", 863 "larger discrepancy"); "discrepancies" for GP training data (213, 944); "condition-aware GP discrepancy" (973) | **"model discrepancy"** for the physics-model error; **"GP discrepancy $\delta$"** for the reward-transfer term; **"residuals"** for physical reward minus affine prediction; **"mismatch"** for trajectory differences. |
| 6 | Gaussian process | "Gaussian process" (56, 890, 901); "Gaussian-process" (212); "GP" (23, never defined as an acronym); symbols $\delta$, $\widehat\delta$ (901, 959, 975), $\mu_\delta$ (213) | Define **"Gaussian process (GP)"** at Intro L56 and L212, then use "GP". Use $\delta$ for the process and $\mu_\delta$ for its posterior mean. Drop $\widehat\delta$. |
| 7 | Information-oriented policies | "information-oriented" (23); "informative" (143, 146, 680, 691, 910; plus Fig. 1 304 and file name 802); symbol $\pi_\iota$ (146, 151, 276, 358) vs. $\pi_{\mathrm{INF}}^{(n)}$ (573, 684) vs. $\pi_{\mathrm{INF},1}$ (798 ×3, 809, 815); "information branch" (362) | **"information-oriented policy"** and **"information phase"**. One symbol, $\pi_{\mathrm{INF}}$, with one index convention ($\pi_{\mathrm{INF},n}$). |
| 8 | Physical environment | "physical environment" (32 on 20 lines); "physical vehicle" (796); "drone" (40 ×2, 49 "micro drone", 374); "MAV" (10); "Crazyflie"; "vehicle" (34) | Use **"physical environment"** only in the formal RT description (Intro L51, II-A). From II-B on, use **"the vehicle"** or "the Crazyflie". Use "drone" only in the market sentence. |
| 9 | "safe" / "safety" for DT checks | "safe" in prose (32, 199, 571, 573, 691, 890, 975); "safety" (58, 185, 199, 358, 362, 726, 855, 865, 879, 982, 986); "safely" (826, 837); "unsafe" (199); subscripts $\Theta_{\iota,\mathrm{safe}}$ (175, 181), $\Theta_{\pi,\mathrm{safe}}$ (189), $\mathcal X_{\mathrm{safe}}$ (238), $\Pi_{\mathrm{safe}}$ (685), $\mathcal A_{\mathrm{safe}}$ (738, 756). Legitimate physical uses are 47 (×2), 49, 828, 850. | **"DT-screened"**, **"admissible"**, or **"passes the DT clearance check"**. Keep "safety margin" for the physical clearance (47, 49, 828, 850). Renaming the subscript to "adm" is optional and changes the equations. |
| 10 | Ground effect | "ground effect" (10); "ground-effect" (19); "GE" in prose (45, 47, 374, 425, 811, 855, 863, 879 ×2); $f_{\mathrm{GE}}$ | Either use **"GE"** consistently after L45, or drop the acronym in prose and keep the subscript. The full term is short, so dropping the acronym is recommended. |
| 11 | Expected Improvement | "Expected Improvement" (10); "Expected-Improvement" (933 caption); "EI" (12 in prose, never defined) | Define **"Expected Improvement (EI)"** at Intro L58 and L224, then use "EI". |
| 12 | Interpolation policies | "interpolation policies" (730); "intermediate reference policies" (886 caption); "interpolated policies" (901); "Two additional policies" (881); "Fractional ... policies" (982) | **"interpolation policies $\pi_{\lambda,i}$"**. Drop the index $i$ if $\lambda$ identifies the policy. |
| 13 | Sobol policies | "Sobol library" (730); "space-filling library" (738); "faded-blue candidate family" (892); "Safe Sobol policy library" (897 caption); "local policies $\pi_{\mathbf a,i}$" (897); "Sobol policies" (901, 982) | **"Sobol library"** for the 2000 candidates and **"Sobol policies $\pi_{\mathbf a,i}$"** for the seven flown. |
| 14 | Selector $e_n$ | "binary interaction schedule" (147); "Policies and interaction schedule" (145 heading); "selector" (245, 353, 366); "RT selector" (58); "sequential schedule" (158); "sequential RT schedule" (563) | **"selector $e_n$"**, and "sequential schedule" only for the campaign order. |
| 15 | One deployment of a policy | "episode" (42); "mission" (19, also "the planned crossing"); "flight" (17); "run" (14, including "run-to-run"); "interaction"; "test"; "experiment" | **"episode"** for one policy deployment (the averaged repetitions); **"run"** for a single flight within it; **"mission"** for the planned crossing. State this once in II-B. |
| 16 | Vertical coordinate $z$ | "clearance" (60); "altitude" (15: 45, 372, 571, 573, 577, 662, 697 ×2, 702, 768, 796, 798, 839, 881, 942); "height" (372 "obstacle height", 796 "nodal heights") | **"clearance $z$"**. $z$ is measured from the obstacle top, so "altitude" is ambiguous. |
| 17 | Streamwise direction | "streamwise" (7); "longitudinal" (702, 796 ×2) | **"streamwise"** |
| 18 | Baseline controller | "built-in PID controller" (358, 857, 942); "built-in cascaded PID controller" (566); "onboard PID controller" (62, 796); "unchanged cascaded PID controller" (697); "nominal cascaded PID controller" (709); "onboard cascaded PID controller" (855); "standard (onboard) feedback controller" (32, 54); "cascaded PID" (8); "PID" as a policy label (949 caption) | **"onboard cascaded PID controller"** at first use, then **"PID controller"**. In captions, write $\pi_{\mathrm{BL}}$, not "PID". |
| 19 | Reference nodes | "control points" (704); "nodes" (796, 855 ×2); "nodal heights" (796) | **"nodes"** |
| 20 | Replay buffer | "replay buffer" (14); "cumulative replay buffer" (361, 815); "cumulative dataset" (360, 573, 575); "reward-transfer surrogate dataset" (730, 944) | **"replay buffer $\mathcal B$"** and **"surrogate dataset"** |
| 21 | Fisher quantity | "Fisher information" (171, 575, 691); "Fisher-information proxy" (672, 809); "cumulative Fisher matrix" (363); "exact statistical Fisher matrix" (680); "E-optimal quantity" (809); "cumulative smallest Fisher eigenvalue" (980) | **"Fisher-information proxy $\mathbf F$"** and "its smallest eigenvalue $\lambda_{\min}(\mathbf F)$" |
| 22 | Weak direction | "least-observed (joint parameter) direction" (181, 363, 571, 680); "weakest (joint / observable) direction" (362, 691, 809 ×2, 826, 980) | **"least-observed direction"** |
| 23 | Off-nominal labels | "low-speed, larger-clearance" (942, 964); "higher-speed, small-clearance" (942, 944, 964, 973); "smaller clearance" (798, 973) | **"lower-speed, larger-clearance"** and **"higher-speed, smaller-clearance"** (parallel comparatives) |
| 24 | Author names | "Richardson et al." (432 ×2, 468, 503, 508, 529); "Richardson model" (503); "Richardson and Pretorius" (60); "Cheeseman-Bennett" (9) vs. "Cheeseman and Bennett" (529, 542) | **"Richardson and Pretorius"** (two authors in the bib). **"Cheeseman--Bennett"** (en-dash) as the adjective and "Cheeseman and Bennett" for the authors. |
| 25 | RT name | "Reinforcement Twinning (RT)" defined 3 times (32, 51, 72); "Bayesian RT" (56 ×2); "twin-calibrated Bayesian policy search" (54); "present RT formulation" (60); "general RT formulation" (158); "more general RT approach" (196); spelled out after definition (117, 353, 732, 980) | Define once in the Abstract and once in the Introduction, then use **"RT"**. Use "general RT" for the formulation with interleaved phases. |
| 26 | Defensive or redundant adjectives and phrases | "deliberately" (60, 529, 544, 573, 890, 892); "lightweight" (32, 54, 62, 697, 707); "proof-of-concept" (32, 771, 975); "frozen/freezes" (12: 62, 158, 199, 245, 361, 366, 697, 730, 771, 855, 879, 942); "control-relevant" (738, 828, 879, 980) | Remove "deliberately" everywhere. Use "lightweight" at most once (L697). State that the parameters are frozen at L158 and once in III-C. Use "proof of concept" once, in III-E. |

Vague intensifiers in total are 44 occurrences of "markedly", "substantially", "significantly", "slightly", "modest", "somewhat", "moderately", "appreciably", "clearly", "much smaller/faster", "very similar", "marked", "substantial", and "pronounced", on lines 40, 43 (×2), 146, 181, 183, 199, 575, 691, 693, 782 (×2), 784, 798, 807, 811, 813, 826 (×2), 828 (×2), 837, 841, 859 (×2), 863, 890, 910 (×2), 919 (×4), 940, 944 (×3), 964 (×2), 973, 975, 980, 984 (×2). The findings above replace each one with a number or remove it.

Cross-references use "Sec.~" once (563) and "Section~" five times (64 ×3, 855, 879). Use **"Section~"**.

### 3.2 Symbols

These are symbols that name two things, or pairs of symbols that name one thing. Renaming a symbol changes equations, so every item is the author's decision.

| Symbol(s) | Problem | Lines | Suggestion |
|---|---|---|---|
| $\xi$ / $\boldsymbol\xi$ | exploration margin vs. descriptor, in the same equation | 224–239, 747–750 | rename the margin ($\zeta$) |
| $\chi_i(x)$ / $\boldsymbol\chi$ | overlap fraction vs. operating condition | 546–551 vs. 212, 747, 768 | rename the overlap fraction ($\varphi_i$) |
| $m$ / $m$ / $\mathbf m_t$ | mass vs. model-update index vs. Adam moment | 374, 441, 557, 561 vs. 101–114, 363 vs. 614–630 | index → $j$; Adam moments → $\mathbf M_t$, $\mathbf V_t$, or keep and say "Adam's" |
| $\mathbf v$ / $\mathbf v_t$ | velocity vs. Adam second moment | 434, 441 vs. 614–631 | as above |
| $\Phi$ / $\Phi_{\mathrm{clr}}$ | normal CDF vs. clearance penalty | 228, 753 vs. 723, 726 | penalty → $P_{\mathrm{clr}}$ |
| $\mathbf D^2$ / $\mathbf D_\theta$ | second-difference operator vs. parameter scaling | 722 vs. 664 | operator → $\boldsymbol\Delta^2$ |
| $\Omega_i$ / $\Omega_{\mathcal R}$ | rotor speed vs. evaluation region (undefined) | 434, 474, 503 vs. 712 | region → $\mathcal X_{\mathcal R}$ |
| $\lambda$ | interpolation factor vs. eigenvalues ($\lambda_{\min}$, $\lambda_1$, $\lambda_2$, $\lambda_H$) | 730, 881 vs. 176, 640, 642, 686, 809 | factor → $\alpha$ |
| $\tau$ | moments $\boldsymbol\tau=[\tau_x,\tau_y,\tau_z]$ vs. $\tau_R,\tau_P,\tau_Y$ vs. time constant $\tau_{\mathrm{rpm}}$ | 456–459, 481–496, 503, 522 | use one moment notation; time constant → $t_{\mathrm{rpm}}$ |
| $k$ | time index vs. kernel $k(\cdot,\cdot)$ vs. $k_T$, $k_Q$ | 75–83, 207, 212, 474 | kernel → $\kappa$ |
| $\mathbf d$ / $d$ / $\mathbf z$ | exogenous input vs. motor distance vs. "input $\mathbf z$" in Fig. 1 | 81, 140, 359 vs. 486, 500 vs. 282 | Fig. 1 → $\mathbf d$ (IIA-31) |
| $\mathcal L_p$ / $J_p$ | the same identification loss | 129, 143 vs. 589–672 | one symbol |
| $\mathbf F_n$ / $\mathbf F_{1:N}$ / $\mathbf F$; $\boldsymbol\Sigma_\nu$ / $\sigma_e^2$ | the same Fisher quantity and noise | 163–171 vs. 674–687, 809 | one notation |
| $\Theta_{\iota,\mathrm{safe}}$ / $\Pi_{\mathrm{safe}}$; $\Theta_{\pi,\mathrm{safe}}$ / $\mathcal X_{\mathrm{safe}}$ / $\mathcal A_{\mathrm{safe}}$; $\Theta$ / $\Theta_p$ | the same admissible sets under different names | 175, 685; 189, 238, 738; 635, 125 | one per set |
| $\pi_\iota$ / $\pi_{\mathrm{INF}}$ | information-oriented policy | 146–152 vs. 573, 684, 798 | one symbol |
| $\pi_\bullet$ | both the deployed policy and the performance-oriented family | 149–153, 275–277 | deployed policy → $\pi^{(n)}$ |
| $n$ / $N$ | episode count ($\mathcal B_n$) vs. $N$ in Eqs. `identification-loss` and `cumulative-fisher` | 134 vs. 587–676 | one |
| $z_{\mathrm{BL}}$ / $z^\ast$; $\mathbf x^{*}$ / $z^\ast$ / $z^*$ | same reference; `*` vs. `\ast` | 701–713 vs. 561 on; 427; 782 | one symbol, `\ast` throughout |
| $\mathcal S$ / $\mathcal S_\circ$, $\mathcal S_\bullet$ / $\mathcal S_e$; $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}$ | score notation; $\mathcal S_e$ and $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}$ undefined | 764, 953, 958 | define $\mathcal S_\circ$ and $\mathcal S_\bullet$ at L762 |
| $J_\pi$, $\mathcal R_\pi$ / $J_{\mathrm{trk}}(\pi)$, $\mathcal R(\pi)$ | same quantities | 764 vs. 711–715 | one form |
| $T_{i,\mathrm{IGE}}$ / $T_{i,\mathrm{corr}}$ | the same corrected thrust | 531 vs. 548 | one |
| $^T$ / $^\top$ / $^{\mathsf T}$; $[A,p]$ without transpose | three transpose styles | 434, 445, 459 / 166, 212, 539, 738, 892, 942 / 581–807; 570 | `^{\mathsf T}` |
| $\pi_{\mathrm{EI}}^{\star}$ | nominal best and condition-specific best | 730, 771 | distinct symbol (IIC-37) |
| Undefined at first use | $R$ (372), $z^\ast$ and $v_x^\ast$ (Fig. 2, 561), $e_z$ (577), $\rho_{A,p}$ (811), $N_{\mathcal R}$, $\Omega_{\mathcal R}$, $z_k$ (711), $\widehat{\mathbf m}_t$, $\widehat{\mathbf v}_t$, $\beta_{1,2}$, $\epsilon$ values (614–635), $\Omega_{\mathrm{PWM}}$ (503), $\mathcal J_{\mathrm{info}}$ and $\widehat{\mathcal R}_\bullet$ (Fig. 1), $\mathcal S_e$ (953), $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}$ (958) | | define each where it first appears (see the findings) |

---

## 4. Paragraphs to cut or compress

Before → after word counts use `wc -w`.

**C1. Block list after Fig. 1 (L356–364). 657 → 206 words (−451).** The list restates II-A. Each block now states only what it does, with the equation reference.

```latex
The blocks of Fig.~\ref{fig:rt_framework} perform the following operations.
\begin{enumerate}
    \item Policy deployment. The policy selected in the previous iteration is deployed. The first episode uses the baseline policy $\pi_{\mathrm{BL}}$, which sets the reference performance.
    \item Physical episode. The vehicle evolves under its hidden dynamics, the deployed policy, and the exogenous input $\mathbf d$, and returns the noisy observations $\mathbf o_{\bullet}$ of Eq.~\eqref{eq:rt-physical-observation}.
    \item Recording. The record $\mathcal E^{(n)}$ is appended to the replay buffer $\mathcal B$, so that every model update uses the complete dataset.
    \item Factual replay. For $e_n=1$, the DT replays the recorded episode, and the mismatch between $\mathbf o_{\circ}$ and $\mathbf o_{\bullet}$ updates $\boldsymbol{\theta}_p^{(m)}$ to $\boldsymbol{\theta}_p^{(m+1)}$. For $e_n=0$, the model stays frozen, and the new policy--reward pair enters the reward-transfer surrogate.
    \item Virtual candidate evaluation. The DT simulates candidate policies. Information-oriented candidates are scored by the information they add along the least-observed parameter direction. Performance-oriented candidates around $\pi_{\mathrm{MB}}$ that pass the DT checks receive a DT reward and a surrogate prediction of their physical reward. Many candidates are evaluated virtually, but only the selected one is flown.
    \item Choice of the next interaction. Equation~\eqref{eq:rt-e-optimal} ($e_n=1$) or Eq.~\eqref{eq:rt-next-performance} ($e_n=0$) selects the next policy, $n$ advances to $n+1$, and the loop returns to Block~1.
\end{enumerate}
```

**C2. L366, the paragraph after the list. 59 → 0 (−59).** It repeats L158 and ends with a signposting sentence. Delete it.

**C3. L571, the information-phase summary. 80 → 24 (−56).** It repeats II-A L161–183.

```latex
Each iteration of the information phase alternates factual replay, which identifies $A$ and $p$, and the design of the next experiment, as in Sec.~\ref{sec:rt-framework}.
```

**C4. L693. 67 → 21 (−46).** It repeats L183, L575, and L635, and states the stopping rule a third time.

```latex
After each flight, the identification is repeated on the enlarged replay buffer. The information phase ends with the criterion of Sec.~\ref{sec:rt-framework}.
```

**C5. L697, the opening of the model-based paragraph. 95 → 41 (−54).** "Frozen", "lightweight", and the description of the performance loop are already stated elsewhere. The new ending leads into Eq. `policy`. Then change "The governor modifies only ..." at L702 to `The correction modifies only ...`.

```latex
After identification, $A$ and $p$ are frozen, and the DT is used to improve altitude tracking across the obstacle. The policy is a spatial reference, computed offline and stored onboard as a lookup table, which the unchanged cascaded PID controller tracks,
```

**C6. L841 and L850, the closing paragraphs of III-B. 86 + 106 → 42 + 20 (−130).**

There is also a logic issue. L841 shows that the broad-domain model already reproduces the baseline replay. That supports stopping, but not the need for the second stage, which rests on the uncertainty reduction. The text defends this with "still valuable". Say it plainly once. L850 is a summary of the subsection; it can be deleted, or kept as one sentence.

```latex
The broad-domain and final replays of $\pi_{\mathrm{BL}}$ are nearly identical [give the replay loss of each]. The model obtained after the broad domain therefore already reproduces the dominant baseline response, and the low-clearance episodes refine $f_{\mathrm{GE}}$ below $z/R=2$ without changing this replay.
```

```latex
The information phase thus replaces the generic Cheeseman--Bennett law with a law identified for the tested vehicle and clearance range.
```

**C7. L865, the closing paragraph of III-C. 83 → 0 (−83).** It repeats L199 and Intro L58 (model-free search), and L879 repeats it again. Delete it. C8 carries the transition.

**C8. L879, the opening of III-D. 119 → 48 (−71).** This version also fixes an inconsistency. L879 says "leading and trailing edges", but L863 locates the main error at the trailing edge.

```latex
The performance phase learns the GP discrepancy between DT and physical rewards. Section~\ref{sec:results-mb} showed that the DT is optimistic around the trailing edge, where the static ground-effect law cannot represent the transient response. The reward-transfer surrogate accounts for the control-relevant part of this error without enlarging the model.
```

**C9. L890. 83 → 32 (−51).** It repeats the model-free argument and uses "safe", "deliberately", a colon construction, and "substantially".

```latex
The calibration is then refined near $\pi_{\mathrm{MB}}$. Three coefficients keep the number of flights needed to train the GP small; a richer correction could describe more shapes but would need more flights.
```

**C10. L940, the opening of III-E. 105 → 24 (−81).** It summarizes III-D, and its 41-word sentence uses "clear", "a few", "substantially", and "marginally".

```latex
The final stage tests whether the correction learned at the nominal condition remains useful when both the desired clearance and the forward speed change.
```

**C11. L953. 92 → 32 (−60).** It repeats L762–768. Move the definitions of $\mathcal S_\circ$ and $\mathcal S_\bullet$ to L762 and fix $\mathcal S_e$ (IIIE-5).

```latex
Rewards at different conditions are compared through the scores of Eq.~\eqref{eq:normalized-score}, $\mathcal S_{\circ}$ for the DT and $\mathcal S_{\bullet}$ for the experiment, which are zero for the baseline policy at each condition.
```

**C12. L962 and L975. 67 + 117 → 21 + 47 (−116).** These hold the third and fourth "not a converged surrogate" disclaimers. The first sentence of L962 repeats L738 and L747; delete it.

```latex
Additional experiments over the velocity--clearance domain would train this surrogate to propose a condition-specific correction instead of a single transferred one.
```

```latex
With only two EI iterations, this result is a proof of concept rather than a converged surrogate. When direct transfer fails to improve the model-based policy, a few physical episodes can reveal how the GP discrepancy has changed and redirect the search toward a better condition-specific policy.
```

**C13. Conclusions (L980–986). 434 → 242 words (−192).**

The current text largely restates Results. It contains the 48-word colon sentence (CON-1), "visual diversity", "virtual safety", "Fractional", "few", "modest", and "slightly", and three defensive sentences ("Parameter decorrelation was therefore not treated ...", "The remaining replay error then motivated ... rather than invalidating the DT", "Model-based optimization remained the backbone"). The version below keeps every claim, adds the numbers, and moves the limitations into one paragraph. It keeps "moving landing surfaces" from the author's future-work list.

```latex
This work demonstrated Reinforcement Twinning for predictive trajectory control of a MAV crossing a finite obstacle in ground effect.

In the information phase, the designed experiments raised the smallest eigenvalue of the cumulative Fisher-information proxy to $3.242$ after twelve episodes, against $0.387$ for twelve repeated baseline episodes. Restricting the design to the low-clearance domain restored the information gain once the broad domain began to saturate. The parameters remain correlated ($\rho_{A,p}=0.818$), but the ground-effect law is constrained to within [value] (relative $2\sigma$) over the control-relevant clearance range, which is what the controller uses.

The identified DT produced a model-based policy that raised the physical reward from $0.54$ to $0.855$, kept the onboard feedback controller, and passed the DT clearance checks. Interpolation and Sobol policies then calibrated the reward-transfer surrogate, and after [number] Expected-Improvement flights the search found a policy with physical reward $0.952$, mainly by reducing the post-obstacle undershoot that the static model does not predict.

At two off-nominal conditions, the transferred correction improved on the model-based policy at one condition but not at the other, where two EI flights found a better local policy. These tests do not establish a surrogate converged over the velocity--clearance domain.

The results are limited to a static two-parameter ground-effect law, to clearances $z/R\geq0.5$, and to two off-nominal conditions. Future work should cover a denser velocity--clearance domain, include repeated-measurement uncertainty in the surrogate, and test unsteady aerodynamic models, moving landing surfaces, and onboard or real-time policy adaptation.
```

Note "Expected-Improvement" is hyphenated here only as an attributive compound. If term 11 is adopted, "EI flights" is shorter.

**C14. L780, the opening of III-A. 71 → 25 (−46).** It repeats L566 (controller, nominal condition, reactive feedback).

```latex
Fig.~\ref{fig:stage0} shows the baseline crossing at the nominal condition, flown with the onboard cascaded PID controller alone. The dashed line is the constant reference $\pi_{\mathrm{BL}}$.
```

**C15. L72, the opening of II-A. 109 → about 40 (−69).** This item is the sum of IIA-1, IIA-2, and IIA-3. It is listed here for the total only.

**C16. L855 and the first sentence of L857. 110 → 20 (−90).** These repeat L697–726 and contain the wrong objective and reference (IIIC-1). The replacement also introduces Fig. 6, so delete "The comparison with the baseline policy is reported in Fig.~\ref{fig:mb-optimum}." at L857.

```latex
Fig.~\ref{fig:mb-optimum} compares the baseline policy with the model-based policy $\pi_{\mathrm{MB}}$, obtained by minimizing $J_{\mathrm{MB}}$ of Eq.~\eqref{eq:mb-objective} with the final DT.
```

**C17. L796 and L798, the opening of III-B. 227 → 64 here + 21 moved to II-C (−142).** These paragraphs contain method content: the parameterization of the information-oriented references (never given in II-C, and missing the node spacing) and the two domains, which repeat L573–575.

For III-B:

```latex
Fig.~\ref{fig:informative-policies} shows representative information-oriented references and the resulting physical trajectories. The broad-domain policies $\pi_{\mathrm{INF},1}$ and $\pi_{\mathrm{INF},6}$ request different clearance histories across the obstacle, whereas the low-clearance policy $\pi_{\mathrm{INF},9}$ keeps the crossing at smaller clearances. The domain bounds apply to the reference, not to the trajectory, which departs from it under the closed-loop dynamics. The physical trajectories are those used in factual replay and identification.
```

Add to II-C, after L573:

```latex
Each information-oriented reference is defined by its values at fixed streamwise nodes, spaced by [value], and is linearly interpolated between them.
```

---

## 5. Estimated words saved

| Source | Words saved |
|---|---|
| Introduction (Section 1; 1730 → 1522) | 208, or 233 if the roadmap is deleted |
| Section 4 compressions C1–C17 (C15 = IIA-1 to IIA-3) | about 1,800 |
| Main findings outside the paragraphs of Section 4 (net of added numbers and placeholders) | about 735 |
| Second-tier items outside Section 4 | about 430 |
| **Total** | **about 3,150 words**, roughly 25–28% of about 11,000–13,000 words of running prose |

Removing the duplicated equations would shorten Methods by about a further half column. These are Eq. `ei` (L748–759), Eq. `reward-transfer` (L741–746), and Eq. `e-optimal-design` (L683–690), each against its generic counterpart in II-A. That is the author's decision, because it changes equations.
