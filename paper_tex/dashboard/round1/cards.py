# -*- coding: utf-8 -*-
"""Cards of review round 1 on paper_tex/main.tex (4 November 2026).

Sources of the remarks quoted on the cards (full texts in review/):
  GPT review      PAPER_REVIEW_V2.md, the 15 major findings (GPT-1 ... GPT-15) and its wording and literature sections
  Panel           five role-separated seats: EIC (journal fit), R1 (methodology), R2 (domain), R3 (perspective), DA
  Code check      code_check_current.md (N1 ... N12), the text checked against the code and EXP/CLEAN
  Literature      literature_ge_identification.md, ground-effect modelling and identification, DOIs verified
  Writing audit   writing_audit.md, the Introduction paragraph by paragraph and the rest of the text
"""
from cardkit import C, card, remark, YOURS

H = {
"EIC-1": "Length and organization exceed every candidate venue and contain extensive duplication",
"EIC-2": "The contribution and its novelty relative to the authors' prior RT papers are not stated; the key method reference is unpublished",
"EIC-3": "The significance claims are comparative but no comparator and no experimental or computational budget is reported",
"EIC-4": "No consolidated results table, and the headline generalization numbers in the text disagree with Fig. 16",
"EIC-5": "Positioning against neighboring literature is thin (24 references) and omits the closest alternatives",
"EIC-6": "Control terminology does not match the conventions of the target community",
"EIC-7": "\"Safe\" is used as a guarantee, but safety rests only on screening in a twin that the paper shows to be optimistic",
"EIC-8": "The Introduction motivates a broader problem than the experiments address, and the assumptions are not stated",
"EIC-9": "The title, abstract and keywords do not convey the problem, the result or the scope",
"EIC-10": "Notation is overloaded and the language needs professional editing",
"R1-1": "The parameter-uncertainty indicator is mis-scaled; read at face value, it does not resolve the ground-effect augmentation",
"R1-2": "The performance phase treats noisy rewards as exact, reports a winner's-curse estimate, and credits EI with gains that came mostly from the space-filling exploration",
"R1-3": "The normalized scores in Fig. 16 cannot be reproduced from the reported rewards, and the text contradicts the figure",
"R1-4": "The reward-transfer surrogate is fitted in two stages, underreports its uncertainty, and is never shown to beat a plain GP",
"R1-5": "The E-optimal design was not actually optimized over the broad domain, and the comparison against repeated baselines is too easy to win",
"R1-6": "The Fisher-information proxy is defined inconsistently and its scale is partly circular",
"R1-7": "π_MB is not the maximizer of the DT reward, so the claim that \"the DT alone regards the two policies as nearly equivalent\" misattributes the gain",
"R1-8": "The identifiability argument and stopping rule depend on the parameterization, the law is likely misspecified, and A and p are confounded with nominal-model error",
"R1-9": "The policy parameterization and the GP inputs are not defined consistently",
"R1-10": "Safety screening uses a twin known to be optimistic, with no margin for model error",
"R1-11": "The campaign is not reported in enough detail to be reproduced or to check the data-efficiency claim",
"R1-12": "Notation clashes and inconsistencies between equations",
"R2-1": "The identified GE law is not benchmarked against existing Crazyflie data, and the \"twice the classical value\" result is expected multirotor physics",
"R2-2": "The clearance reference, its measurement, and the floor are undefined",
"R2-3": "The edge model (linear disk-overlap weighting) is assumed, not validated, in exactly the regions that matter",
"R2-4": "Attributing the trailing-edge discrepancy to \"transient\" GE is unsupported; the logged data can test it directly",
"R2-5": "The nominal twin is not validated out of ground effect, so any mismatch there is absorbed into (A, p)",
"R2-6": "Identifiability and uncertainty claims are stronger than the analysis supports",
"R2-7": "The virtual safety screening relies on the least-constrained part of the model; some references command clearances inside the obstacle",
"R2-8": "The work is not positioned against established ways to compensate GE and repeatable disturbances, and the only comparator is the stock PID",
"R2-9": "Literature coverage of GE modeling and, above all, of identification is thin",
"R2-10": "Velocity is aerodynamically secondary at these advance ratios; the explanation of the failed transfer is speculative",
"R2-11": "The physical interpretation of π_EI* versus π_MB overreaches the figure",
"R2-12": "Cheeseman–Bennett is misdescribed (expansion versus \"rearrangement\", constant power versus constant rotor speed)",
"R3-1": "No fair baseline supports the data-efficiency claim of the performance phase",
"R3-2": "π_MB is a regularized DT optimum, which confounds the gain attributed to model discrepancy",
"R3-3": "The control value of the 12-flight information phase is not shown, and its counterfactual is weak",
"R3-4": "Rewards are treated as deterministic, so the EI improvement has no uncertainty and is exposed to selection bias",
"R3-5": "Physical and computational cost is not reported, so \"a limited number of physical interactions\" cannot be checked",
"R3-6": "The safety and risk-reduction claims rely on a DT shown to be non-conservative where it matters, and some commanded references enter the obstacle",
"R3-7": "The paper is not positioned against its closest alternatives",
"R3-8": "The framing and terminology are hard for outsiders to follow, and partly nonstandard",
"R3-9": "The scope of generalization is unclear, and the off-nominal scores in the text do not match Fig. 16",
"R3-10": "The performance phase discards trajectory information, and the choice and scalability of the basis are not discussed",
"DA-1": "The nominal gain over π_MB is not shown to come from reward transfer or EI",
"DA-2": "Alternative explanation: reward compression and MB regularization, not discrepancy learning",
"DA-3": "The information phase is not shown to matter for control",
"DA-4": "The Fisher evidence for designed experiments is self-referential, and the comparator is a straw man",
"DA-5": "Parameter \"stabilization\" may be dilution; drift suggests misspecification; identification stopped while information was rising fastest",
"DA-6": "\"Well constrained\" is contradicted by the paper's own uncertainty indicator when applied to the augmentation",
"DA-7": "\"Safe\" is certified only by a DT that is known to be wrong at the edges",
"DA-8": "The data-efficiency claims are not benchmarked",
"DA-9": "The off-nominal evidence has inconsistent numbers and is too thin to support \"adapt\"",
"DA-10": "\"So what?\": the reward and the policy class do not match the stated motivation",
"GPT-1": "The local policy equation contradicts the transfer claim",
"GPT-2": "The surrogate variance is understated",
"GPT-3": "The EI incumbent is inconsistent with noisy physical rewards",
"GPT-4": "A fixed local library conflicts with the root paper's central result",
"GPT-5": "The expected-return objective is not connected to the implemented DT score",
"GPT-6": "State synchronization is under-specified and may confound identification",
"GPT-7": "The inverse-Hessian scaling is not a calibrated covariance",
"GPT-8": "The Fisher matrix is useful for ranking, not evidence of quantified information gain",
"GPT-9": "The novelty override makes the displayed optimizer incomplete",
"GPT-10": "The identification fit lacks out-of-sample validation",
"GPT-11": "The static power law is more restrictive than the literature discussion admits",
"GPT-12": "The cross-condition normalization does not put missions on a common statistical scale",
"GPT-13": "The contextual GP claim is too strong for the available data",
"GPT-14": "\"Safe\" is not supported by the adopted mechanism",
"GPT-15": "Experimental accounting is still incomplete",
"N1": "Number of repetitions. Grade A. Verdict: Disagrees",
"N2": "Information-phase numbers (Sec. III-B). Grade: values Agree; B for the ρ narrative; C for \"twelve repetitions\"",
"N3": "Rewards in Secs. III-C and III-D. Grade: values Agree; definition B",
"N4": "Generalization scores and statements. Grade A. Verdict: Disagrees (two reward definitions are mixed)",
"N5": "Transfer rule. Grade A. Verdict: Disagrees",
"N6": "GP description. Grade: Partly; B for the generalized GP, C for the wording items",
"N7": "Model-based policy. Grade A. Verdict: Disagrees",
"N8": "Information phase. Grade A. Verdict: Disagrees",
"N9": "DT provenance and parameters. Grade A. Verdict: Disagrees",
"N10": "Mission and setup. Grade B/C. Verdict: Partly",
"N11": "Basis functions, Sobol library and the a vectors. Grade B/C. Verdict: Partly",
"N12": "Other statements in Secs. II–IV and the Conclusions"
}

W = {
"AB-1": "A workflow does not \"constrain\" a response; the identified model reproduces it. \"a limited number\" is vague, and the paper has the numbers: physical reward 0.54 → 0.855 → 0.952.",
"AB-2": "The sentence does not say what was found.",
"AB-3": "\"safe\" describes a check made in the twin. The policy is not computationally efficient; it is cheap to run onboard.",
"AB-4": "A comma is missing before \"whose\", and an article before \"physical environment\". \"aerodynamic correction to account for ground effect\" is wordy, and \"Digital Twin\" is capitalized.",
"IIA-1": "RT and DT are defined for the third time, after the abstract and L51, and the RT definition repeats Intro L51.",
"IIA-2": "The two objectives are also stated at L117–133 with equations, in the Fig. 1 panel titles, and in the Fig. 1 caption (L353). Keep L117–133.",
"IIA-3": "The coupling of the two loops is stated at L72 (twice), at L143 (with a colon), at L245, and in Intro L51. Keep the single sentence at L72.",
"IIA-4": "The record is described three times with different contents. L92 lists policy, inputs, operating conditions, and reward. The set at L136–142 has $\\boldsymbol o_\\bullet$, $\\boldsymbol\\theta_\\pi$, $e_n$, $\\mathbf d$, and $\\mathcal R_\\bullet$, with no operating condition and only $\\boldsymbol\\theta_\\pi$ even for information episodes. Block 3 (L360) adds control signals. Keep the set at L134–142 and make it complete. Here, only introduce $\\mathcal R_\\bullet$.",
"IIA-5": "This repeats the preceding sentence. The same fact also appears at L245, in Block 1 (L358), in Block 5 (L362), and in Intro L54.",
"IIA-6": "L881 excludes all information-oriented episodes from the surrogate. State the exclusion once, here in Methods, and delete it from Results (IIID-1).",
"IIA-7": "There is a colon construction and a double space. Sequential phases are also stated at Intro L58 and L62, at L196, and in the whole of L366 (C2). Keep this one.",
"IIA-8": "The novelty check is described again at L691, and neither place says whether it was used. \"slightly\" and \"sufficiently\" have no number. Keep one statement, at L691 (IIC-11).",
"IIA-9": "The stopping rule appears six times, in different forms:\n  - here: stable estimates and correlation;\n  - L366: \"convergence and uncertainty criteria\";\n  - L693: as here;\n  - L828: adds \"improved confidence\" in $f_{\\mathrm{GE}}$;\n  - L841: adds an unchanged baseline replay;\n  - L850: four conditions.\n\n  \"appreciably\" has no threshold. Write the complete rule once, here, and let Results refer to it. Also delete the following sentence, \"At this point, further experiments yield only marginal changes in the identified model and in the joint identifiability of its parameters.\"",
"IIA-10": "The same argument appears at Intro L58, L865 (C7), L890 (C9), and L986. Keep Intro L58 and the Conclusions. \"substantially\" has no number.",
"IIA-11": "The sentence is circular: \"safe\" policies are evaluated \"to verify safety\". It describes a DT check.",
"IIA-12": "L740 treats rewards as deterministic, with a jitter of $10^{-8}$. The reader cannot reconcile the two statements.",
"IIA-13": "GP is used from L56 on but never defined as an acronym.",
"IIA-14": "The first sentence repeats at L740 (keep that one) and L901. The second repeats L212 and Intro L56.",
"IIA-15": "$\\xi$, the exploration margin, clashes with $\\boldsymbol\\xi$, the descriptor, in the same equation (Eq. `rt-expected-improvement`). The clash recurs at L747. \"best physical reward\" should say observed so far. Renaming the margin (e.g. $\\zeta$) changes the equations, so it is the author's decision.",
"IIA-17": "The six-block list (657 words) restates II-A almost sentence by sentence:\n  - the exogenous input $\\mathbf d$ and the hidden state (L85 and L359);\n  - the record (L134 and L360);\n  - factual replay (L114 and L361);\n  - DT screening (L146 and L362);\n  - E-optimal and EI selection (L181, L234 and L363);\n  - the index $m$ (L114 and L363).\n\n  It also contains defensive sentences: \"This distinction is essential ...\", \"The purpose of this passage ...\" (where \"passage\" is a calque of \"passaggio\" and should read \"step\"), and \"This block is the main computational advantage of RT: ...\". See C1 for a 206-word version. L366 repeats L158 (C2).",
"IIB-1": "The fact that the parameters are inherited and not reidentified is stated five times: L432 (keep), L503, L505, the Table I caption, and L529. Intro L60 adds a sixth mention.",
"IIB-2": "$V_b=f(\\mathrm{SOC})$ is restated from L503. \"only a few seconds\" is doubtful: 10 s of hover plus 4.2 m at $0.35$ m/s makes about 20 s. If SOC is fixed at full charge, $\\eta_V=V_b/V_{\\mathrm{ref}}=1$ and the \"retained\" correction has no effect, which the text should say.",
"IIB-3": "The bib entry `Richardson2025` has two authors, Richardson and Pretorius, so \"et al.\" is wrong. The same error appears at L432 (twice), L468, L503, L508, and L529. L60 has the correct form.",
"IIB-4": "$R$ is used without saying what it is. It is defined later at L529 and again at L561, and its value is also in Table I and L561. Define it here once and let L561 refer to the table (IIC-1).",
"IIB-5": "$z^\\ast$ is used in Fig. 2 and from L561 on, but never defined in words. \"altitude\" also competes with \"clearance\" for the same quantity (Section 3).",
"IIB-6": "The base stations emit infrared sweeps and the deck receives them. The stations do not detect the deck.",
"IIB-8": "\"adjoint optimization\" is introduced only at L600. The loss is defined at L577–598, where it is evaluated at the $K_n$ positions \"encountered during the flight\", not \"over the obstacle region\". State the region once, at L577.",
"IIB-9": "The model has no velocity term, so it does assume the dependence vanishes. Intro L45 says Kan \"showed that clearance alone is insufficient and that velocity changes the response\". Give Kan's speed range once.",
"IIC-1": "$R$ is defined for the third time (after L372 and L529). The values of $m$ and $R$ are given a third time, after L372–374 and Table I.",
"IIC-2": "The deleted sentences state the obvious. \"blocks\" already names Blocks 1–6 of Fig. 1. Change \"The final block\" (L771) and \"The final campaign block\" (L940) to \"stage\" as well.",
"IIC-3": "The nominal values are written six times: L563 (keep), L566, L780, L940, L944, and L964. A controller is not a policy; the policy is the constant reference.",
"IIC-4": "The rewards of Eq. `reward` are not normalized by the baseline. Only the scores $\\mathcal S$ of Eq. `normalized-score` are. The same role is restated at L784 (IIIA-4).",
"IIC-5": "That the PID controller is reactive is stated in Intro L49, here, at L780, and at L857. Keep Intro L49 and III-A L780.",
"IIC-7": "The sentence is 52 words long, the longest in the paper. It has a colon, \"deliberately\", and \"safe\" used for an admissible range.",
"IIC-8": "\"modest\" has no number, and there is a colon construction. This paragraph motivates the restriction by the slowing growth of $\\lambda_{\\min}$, whereas L815 motivates it by \"clearance coverage and the uncertainty remaining below $z/R=2$\". Give one motivation.",
"IIC-9": "The defensive sentence adds nothing. The warm start is stated here, at L635 (keep), and in L693. \"Earlier records remain\" is repeated at L815.",
"IIC-10": "$e_z$ in Eqs. `episode-error-vectors` and `identification-loss` is never defined. It is unclear whether it is measured against the deployed reference $z_\\pi$ or the nominal $z_{\\mathrm{BL}}$.",
"IIC-11": "The E-optimal rationale appears four times (L181, L363, L680, L691), and the novelty check twice (L181, L691). Eq. `e-optimal-design` duplicates Eq. `rt-e-optimal`.",
"IIC-12": "Two consecutive sentences have the same subject and verb. The table implementation is stated at L697 (\"lookup table\") and again here (\"interpolation table\"). The definition of \"model predictive control\" is defensive, because the method is called MPC nowhere else.",
"IIC-13": "Eq. `reward`, the paper's central metric, uses $N_{\\mathcal R}$, $\\Omega_{\\mathcal R}$, and $z_k$, and none of them is defined. $\\Omega$ also names the rotor speed.",
"IIC-14": "The number of EI flights at the nominal condition is never stated. L910 says \"a few\" and L982 says \"few\". It is the paper's key data-efficiency number.",
"IIC-15": "The purpose repeats L199, L242, and Intro L58. The Sobol library is stated at L730, here, at L892, and in the Fig. 7 caption. The basis centers and bounds appear only in Results (L892) and the width nowhere. Move them here (see IIID-3).",
"IIC-16": "\"cleaned\" is never explained. The same phrase is used at L901.",
"IIC-17": "The EI terms are explained at L234, and the role of the model-based policy at L199, L242, and L865. Eq. `ei` also duplicates Eq. `rt-expected-improvement` with a different argument ($\\mathbf a$ against $\\boldsymbol\\xi$). Keeping one equation is the author's decision.",
"IIC-18": "Eq. `rt-policy` is additive: $\\Delta z_\\pi=\\Delta z_{\\mathrm{MB}}+R\\,\\mathbf b^{\\mathsf T}\\mathbf a$. A fixed $\\mathbf a$ therefore gives a fixed offset unless $\\mathbf b(x)$ scales with $\\Delta z_{\\mathrm{MB}}$, which the text never says. The claim is repeated at L942 (\"This scaling preserves ...\") and L771. The sentence also uses three names for one thing: \"model-based action\", \"MB solution\", and \"MB deformation\".",
"IIC-19": "The disclaimer is repeated at L962, L975, and L984, and in the abstract. Keep it in III-E (C12) and in the Conclusions.",
"IIC-20": "There is a colon construction, and the baseline policy is not computed with the DT. The two conditions are listed again with a colon at L942.",
"IIIA-1": "There is a colon construction, and \"markedly\" is redundant because numbers follow.",
"IIIA-2": "The lack of anticipation explains the overshoot. It does not explain the persistent offset: the vehicle settles at $z/R\\approx2$ instead of $1.5$ for the whole 0.81 m, or about 2.3 s, over the obstacle, despite integral action. \"tuned around hovering\" has no source.",
"IIIA-3": "\"substantially\" has no number. The RMS band width is never given.",
"IIIB-1": "The initialization is stated a fourth time (L542, L573, L60). \"change substantially\" should give the values after the first identification.",
"IIIB-2": "\"much smaller\" can be replaced by the numbers the paper already has.",
"IIIB-3": "$\\rho_{A,p}$ is not defined anywhere. Methods mentions only \"their estimated correlation\". It presumably comes from $\\boldsymbol\\Sigma_\\theta$ of Eq. `parameter-covariance`. Define it there or here.",
"IIIB-5": "The motivation differs from L575 (slowing $\\lambda_{\\min}$), and the second sentence repeats L575. Results should report the evidence and refer to the Methods decision.",
"IIIB-6": "\"moderately\", \"substantially\", and \"most important\" have no numbers. The relative uncertainty is never quantified in the text.",
"IIIB-7": "This is the stopping rule again, with a third ingredient that Methods does not list (IIA-9).",
"IIIB-8": "There is a colon construction, and \"substantially\" can be replaced by the paper's own numbers.",
"IIIB-9": "The static-law limitation is stated at L544, L863, L879, and L986. \"safely\" is also used here.",
"IIIC-1": "The policy minimizes $J_{\\mathrm{MB}}$ (Eq. `mb-objective`), not the tracking cost alone. The cost is introduced in the \"Model-based policy\" paragraph (label `sec:mb-optimum`), not under `sec:performance-phase`; both labels print as \"Section II-C\". The whole paragraph repeats L697–726; see C16.",
"IIIC-2": "\"markedly\" and \"substantial\" have no numbers. The trajectory extrema are given for the baseline (L782, L784) but never for $\\pi_{\\mathrm{MB}}$.",
"IIIC-3": "L910 gives the same rewards as $0.968$ and $0.855$, and $0.855$ rounds to $0.86$, not $0.85$. Use one precision. \"approximately\" is redundant with two decimals.",
"IIIC-4": "\"causal information\" is undefined, and \"consistent ordering\" of two points is an overstatement.",
"IIIC-5": "\"replay\" denotes factual replay elsewhere, while the Fig. 6 caption calls this curve a \"DT prediction\". (b) has a colon construction and \"pronounced\" without a number. \"discrepancy\" also has a fourth meaning here (Section 3).\n\nL865 is cut in Section 4 (C7).",
"IIID-1": "This is a method decision that contradicts L146. Move it to Methods (IIA-6).",
"IIID-2": "Both the definition and the purpose are already given at L730. Also delete the later \"The resulting policies ... are reported in Fig.~...\" because (a) now introduces the figure.",
"IIID-3": "The basis definition belongs in II-C (IIC-15b), and its width is missing. \"centered on the model-based reference\" is ambiguous; it is unclear whether this means a position or a shape.",
"IIID-4": "The sentence is 43 words long and has a colon construction. The roles of the affine fit and the GP repeat L212 and L222. $\\widehat\\delta$ is a third symbol for the GP term, after $\\delta$ and $\\mu_\\delta$.",
"IIID-6": "See IIC-14. \"a few\" is the paper's main data-efficiency claim and has no number.",
"IIID-7": "There is a colon construction, and \"marked\" and \"substantial\" can be replaced by the paper's own numbers ($0.978-0.968$ against $0.952-0.855$).",
"IIID-8": "No figure shows the references of the other high-reward evaluations. Fig. 9 shows only $\\pi_{\\mathrm{EI}}^{\\star}$.",
"IIID-9": "Four vague intensifiers (\"slightly\", \"somewhat\", \"markedly\", \"clearly\") appear in one paragraph. \"better prepared\" is anthropomorphic. \"dominant reward gain\" is a quantitative claim without the split of the cost before and after the trailing edge.",
"IIID-10": "One flight per case cannot support repeatability; the five-run RMS bands do. The Fig. 10 caption says panel (c) shows only $\\pi_{\\mathrm{EI}}^{\\star}$, not three superposed paths.",
"IIIE-1": "(a) repeats L771. (b) repeats L768, and the \"scaling\" it refers to is not explained (IIC-18).",
"IIIE-2": "The reward ranking is stated twice, at L944 (where Fig. 12 shows only trajectories) and at L964 (Fig. 13, which shows the scores). Keep it at L964, the figure that supports it. \"markedly\", \"modest\", and \"slightly\" (twice) carry no numbers. The paper gives no $\\mathcal S$ values except 0.57 and 0.83.",
"IIIE-3": "The ranking duplicates (b) above. There is a colon construction and \"important\". The cause that follows is stated as fact but is a hypothesis.",
"IIIE-5": "$\\mathcal S_e$ is never defined. It presumably means $\\mathcal S_\\circ$ and $\\mathcal S_\\bullet$. Move these definitions to L762 (C11).",
"IIIE-6": "Eq. `generalized-surrogate` is a method equation placed in Results. It is the third version of the surrogate, and $\\widehat{\\mathcal S}_{\\bullet,\\mathrm{aff}}$ is undefined.",
"IIIE-7": "The DT is the same frozen DT everywhere, so \"local DT\" is wrong. \"substantially\" has no number, and \"safe\" describes a DT check.",
"CON-1": "The sentence is 48 words long and has a colon construction. \"visual diversity\" is undefined; no visual claim was made. \"much faster\" can be given as $3.242$ against $0.387$. See C13 for the full rewrite.",
"CON-2": "Both phrases describe checks made in the twin.",
"AB-5": "Improper word. `the remaining uncertainty on the corrective parameters guide the design of information-oriented policies to be deployed on the physical environment.` → `the remaining uncertainty in the correction parameters guide the design of information-oriented policies for the physical environment.`",
"AB-6": "Wordy. `This work presents an implementation of Reinforcement Twinning (RT) applied to a micro aerial vehicle operating in ground effect.` → `This work applies Reinforcement Twinning (RT) to a micro aerial vehicle flying in ground effect.`",
"AB-7": "Inconsistent term. `combines DT and physical environment rewards` → `combines DT and physical rewards`",
"AB-8": "Inconsistent term (active vs. adaptive). `These results support the use of an adaptive DT` → `These results support the use of an active DT`",
"IIA-16": "Repetition. `The DT restricts and guides the search around $\\pi_{\\mathrm{MB}}$, while the physical rewards allow RT to improve upon that policy.` → *(delete; also in Intro L58, L199, L760, L865, L982)*",
"IIA-18": "Signposting / improper word. `As anticipated, each of the two environments involved in the Reinforcement Twinning loop features its own objective. The physical environment aims for policy parameters` → `Each environment has its own objective. The physical environment seeks policy parameters`",
"IIA-19": "Long sentence. The sentence from L117 runs through two display equations and the record definition. Change the comma at the end of L142 to a period, and `and $\\mathcal{L}_p$ compares the DT and physical observations selected for identification.` → `The loss $\\mathcal{L}_p$ compares the DT and physical observations selected for identification.`",
"IIA-20": "Vague intensifier / logic. `The two policy families may have significantly different parameterizations because their classification reflects the objective used during policy design.` → `The two families are defined by the objective used to design them and may have different parameterizations.`",
"IIA-21": "Inconsistent term. `A binary interaction schedule $e_n\\in\\{0,1\\}$ determines which policy is designed and deployed during each physical episode $n$:` → `A binary selector $e_n\\in\\{0,1\\}$ determines which policy is designed and deployed in physical episode $n$,`",
"IIA-22": "Grammar / signposting. `We consequently distinguish a first \\emph{information phase} and a subsequent separated \\emph{performance phase}, which are described in detail below.` → `This defines an \\emph{information phase} followed by a separate \\emph{performance phase}.`",
"IIA-23": "Improper word. `As $\\mathbf S(\\boldsymbol{\\theta}_{\\iota})=\\partial\\mathbf o_{\\circ}/\\partial\\boldsymbol{\\theta}_p$ denotes the sensitivity of the predicted observations and $\\boldsymbol{\\Sigma}_{\\nu}$ their noise covariance, the information expected after a candidate policy is` → `With $\\mathbf S(\\boldsymbol{\\theta}_{\\iota})=\\partial\\mathbf o_{\\circ}/\\partial\\boldsymbol{\\theta}_p$ the sensitivity of the predicted observations and $\\boldsymbol{\\Sigma}_{\\nu}$ the covariance of the measurement noise $\\boldsymbol{\\nu}$, the information expected after a candidate policy is`",
"IIA-24": "Repetition. `Each candidate represents a possible next experiment and is evaluated in the DT before deployment.` → *(delete)*",
"IIA-25": "Improper word (\"safety\"). `accounting for safety constraints and actuator limits within the DT,` → `subject to the clearance and actuator constraints checked in the DT,`",
"IIA-26": "Unsupported claim (a result stated in methods). `because this model-based policy already improves upon the baseline policy and provides a physically informed reference.` → `because this model-based policy is expected to improve upon the baseline policy and provides a physically informed reference.`",
"IIA-27": "Improper word. `The GP is conditioned on the discrepancies between the physical rewards` → `The GP is conditioned on the residuals between the physical rewards`",
"IIA-28": "Repetition. `In both cases, the physical environment is exposed only to a policy that has first been generated and screened in the DT.` → *(delete)*",
"IIA-29": "Improper word / figure introduction. `The RT closed-loop is summarized in Fig.~\\ref{fig:rt_framework}. The diagram represents one physical-digital iteration and makes explicit where information is created, where it is interpreted, and how it affects the next interaction with the physical environment.` → `Fig.~\\ref{fig:rt_framework} shows one iteration of the RT loop, from the deployed policy to the choice of the next one.`",
"IIA-30": "Repetition / inconsistent term. `The physical environment and its active Digital Twin evolve side by side through physical observations and virtual candidate evaluations, in order to achieve their respective objectives.` → `The physical environment and its active DT evolve side by side through physical observations and virtual candidate evaluations.`",
"IIA-31": "Inconsistent symbol (fig. 1). `hidden state $\\mathbf{s}_\\bullet$, input $\\mathbf z$\\\\` → `hidden state $\\mathbf{s}_\\bullet$, exogenous input $\\mathbf d$\\\\`. In addition, Fig. 1 uses $\\mathcal J_{\\mathrm{info}}$ and $\\widehat{\\mathcal R}_\\bullet$, which never appear in the text. The text uses $\\lambda_{\\min}[\\mathbf F_{n+1}]$ and $\\mu_\\bullet$ instead.",
"IIB-7": "Repetition / grammar. `The Lighthouse positioning system provides sub-centimetre-level absolute accuracy and sub-millimetre repeatability.` → *(delete; the next sentence gives the numbers from Taffanel et al., and the spelling is British)*",
"IIB-10": "Symbol clash / vague pronoun. `It is therefore weighted by $\\chi_i(x)\\in[0,1]$, defined as the fraction of rotor disk $i$ that overlaps the obstacle.` → `The augmentation is therefore weighted by the fraction $\\chi_i(x)\\in[0,1]$ of rotor disk $i$ that overlaps the obstacle.` $\\chi_i$ also clashes with $\\boldsymbol\\chi$ (Section 3.2).",
"IIB-11": "Vague. `The horizontal reference frame retains its origin at $x=y=0$, whereas the vertical origin is placed at the upper surface of the obstacle, so that $z=0$ at the obstacle height.` → `The origin of $x$ and $y$ is the start position of each test [check], and $z=0$ at the upper surface of the obstacle.`",
"IIB-12": "Vague number / repetition. `Together with a 350 mAh battery, the drone mass is around $m=32.42$~g.` → `With its 350~mAh battery, the vehicle has mass $m=32.42$~g.` \"around\" does not fit four significant digits.",
"IIB-13": "Wordy. `This configuration reduces the probability of temporary tracking loss or a position-estimation disturbance caused by an interruption of the optical link between a Lighthouse station and the Lighthouse deck mounted on the Crazyflie.` → `This overlap reduces the risk of losing the position estimate when one optical link is interrupted.`",
"IIB-14": "Undefined acronym. `is equipped with an onboard IMU sensor for attitude control` → `carries an onboard inertial measurement unit (IMU) for attitude control`",
"IIB-15": "Undefined acronym. `and the individual motor PWM commands` → `and the individual motor pulse-width-modulation (PWM) commands`",
"IIB-16": "Unsupported claim. `ensuring consistency between the numerical and experimental closed-loop dynamics.` → `so that the DT and the vehicle run the same controller.`",
"IIB-17": "Signposting. `The finite-obstacle ground-effect correction is incorporated below as the unknown model component with associated $\\boldsymbol{\\theta}_p$ learned by RT.` → `RT identifies only the ground-effect correction of Eq.~\\eqref{eq:corrected-thrust}, whose parameters form $\\boldsymbol{\\theta}_p$.`",
"IIB-18": "Repetition. `The vehicle dynamics are coupled with the same cascaded PID architecture used in the physical environment, providing the nominal closed-loop model on which the ground-effect correction is identified.` → *(delete; stated at L427)*",
"IIB-19": "Improper word / to check. `This interaction is introduced through a deliberately simple physical model inspired by the analytical formulation of Cheeseman and Bennett for an isolated rotor in hovering~\\cite{CheesemanBennett1955}.` → `This interaction is modeled with a low-order law inspired by the Cheeseman--Bennett formulation for an isolated rotor in hover~\\cite{CheesemanBennett1955}.` The cited report is titled \"...in Forward Flight\", so check \"in hover\". Also change `generated as the vehicle closely crosses the finite obstacle` → `generated as the vehicle crosses the finite obstacle at low clearance`.",
"IIB-20": "Improper word. `The original Cheeseman and Bennett formulation rearranged with the same unknowns would have retained $A=1/16$ and $p=2$.` → `Written in this form, the Cheeseman--Bennett formulation gives $A=1/16$ and $p=2$.` The match holds to first order in $(R/z_i)^2$; check.",
"IIB-21": "Colon / signposting. `This model is deliberately low order: ground effect is treated as a static function of the instantaneous rotor clearance.` → `The model is static. It treats ground effect as a function of the instantaneous rotor clearance only.` Also at L551: `where $T_{i,\\mathrm{OGE}}$ is the nominal rotor thrust outside ground effect.` → *(delete; defined at L529)*.",
"IIC-6": "Repetition. `The model is initialized from the Cheeseman-Bennett coefficients, $A=1/16$ and $p=2$. Starting from the baseline record,` → `Starting from the baseline record,` The initialization is also stated at L542 (keep), L807, and Intro L60.",
"IIC-21": "Undefined symbol. `the desired forward velocity is normalized by the ideal induced velocity in hover,` → `the desired forward speed $v_x^\\ast$ is normalized by the ideal induced velocity in hover,`",
"IIC-22": "Inconsistent term. `for the remaining six policies, defining the near-wall domain.` → `for the remaining six policies, defining the low-clearance domain.`",
"IIC-23": "Inconsistent symbol. `With $N$ episodes in the replay buffer, the identification loss is` → `With $N$ episodes in the replay buffer, the identification loss $\\mathcal L_p$ of Eq.~\\eqref{eq:rt-model-objective} becomes`. Renaming $J_p$ to $\\mathcal L_p$ in the equations is the author's decision.",
"IIC-24": "Missing citation / numbers. `Adam uses this gradient to update the parameters over successive optimization steps.` → `Adam~[CITE: Kingma and Ba, Adam] updates the parameters with this gradient.` Also give $\\beta_1$, $\\beta_2$, and $\\epsilon$.",
"IIC-25": "Numbers without what they measure. `The relative-loss, coefficient-range, and projected-gradient tolerances are $2\\times10^{-4}$, $10^{-3}$, and $5\\times10^{-3}$, respectively. The optimization is considered converged only when all three conditions remain satisfied over a complete monitoring window.` → `The fit has converged when, over a whole window, the relative change of $J_p$ stays below $2\\times10^{-4}$, the range of each coefficient below $10^{-3}$, and the norm of the projected gradient below $5\\times10^{-3}$.` Check the definitions.",
"IIC-26": "Logic / repetition. `Thus, $A$ and $p$ may retain a strongly elongated and correlated local uncertainty region even when the resulting ground-effect curve is tightly constrained.` → *(delete)*. \"Thus\" does not follow from Eq. `uncertainty-propagation`, and the fact is stated with evidence at L826 and L980.",
"IIC-27": "Term before its definition. `For the post-campaign comparison reported later, every episode and the repeated-baseline counterfactual are reevaluated` → `For the post-campaign comparison of Section~\\ref{sec:results-inf}, every episode and the counterfactual sequence of repeated baseline episodes are reevaluated`",
"IIC-28": "Missing numbers. `Candidates that violate state, reference-rate, acceleration, actuator, or clearance constraints are discarded before deployment.` → `Candidates that violate the state, reference-rate, acceleration, actuator, or clearance limits in the DT ([give values]) are discarded before deployment.`",
"IIC-29": "Two symbols for one thing. `where $z_{\\mathrm{BL}}$ is the nominal mission reference altitude which is constant along $x$.` → `where $z_{\\mathrm{BL}}=z^\\ast$ is the constant nominal reference.`",
"IIC-30": "Improper word. `This spatial representation is preferred over the time representation as it prevents small DT-experiment timing differences from desynchronizing the anticipatory command from the obstacle.` → `A spatial rather than temporal parameterization prevents small timing differences between DT and experiment from shifting the anticipatory command relative to the obstacle.`",
"IIC-31": "Inconsistency with l855. `over the complete crossing and interpolated between consecutive points.` → `over the complete crossing and linearly interpolated between consecutive points.` L855 gives the spacing as $\\Delta x\\simeq R$ and calls the points \"nodes\".",
"IIC-32": "Improper word (\"safety\"). `and the clearance term enforces safety on the tilted rotor geometry rather than only on the vehicle center of mass.` → `and the clearance term applies the $0.5R$ limit to each tilted rotor rather than only to the CoM.` CoM is defined at L436 but never used.",
"IIC-33": "Vague / missing citation. `A scrambled Sobol library of 2000 coefficient vectors is screened in the DT, and seven admissible, mutually distinct policies $\\pi_{\\mathbf a,i}$ are deployed to train the local GP discrepancy.` → `A scrambled Sobol library~[CITE: Sobol sequence] of 2000 coefficient vectors is screened in the DT, and seven admissible policies $\\pi_{\\mathbf a,i}$, chosen by [criterion], are deployed to train the GP discrepancy.`",
"IIC-34": "Ambiguous scaling. `with each coordinate scaled by $0.30R$.` → `with kernel length scale [0.30 in each coordinate; check the unit, since $\\mathbf a$ is dimensionless].`",
"IIC-35": "Repetition / vague pronoun. `Two policies with similar DT performance can receive different physical corrections. Its posterior mean and variance are updated after every performance-oriented episode.` → `The posterior mean and variance of $\\delta$ are updated after every performance-oriented episode.`",
"IIC-36": "Confusing. `and $\\boldsymbol{\\chi}$ is augmented with the operating condition.` → `and the GP input is augmented with the operating condition $\\boldsymbol{\\chi}$.` L747 already says that $\\boldsymbol\\chi$ contains the operating condition.",
"IIC-37": "Symbol clash. `Where an additional condition-specific EI search is performed, its best physical policy is denoted by $\\pi_{\\mathrm{EI}}^{\\star}$.` This is the same symbol as the nominal best at L730. Use a distinct symbol, e.g. `$\\pi_{\\mathrm{EI},\\boldsymbol\\chi}^{\\star}$`, which is the author's decision.",
"IIIA-4": "Repetition. `The baseline experiment consequently provides the reference cost for all subsequent performance comparisons and the first factual record used during the information phase.` → *(delete; stated at L566, see IIC-4)*",
"IIIA-5": "Vague. `Before reaching the obstacle, the vehicle maintains an almost constant clearance close to the commanded value, supporting satisfactory tracking at this modest forward speed away from the surface interaction.` → `Before the obstacle, the vehicle holds a nearly constant clearance close to the commanded value.`",
"IIIB-4": "Repetition. `It describes uncertainty in the total thrust factor rather than in the smaller augmentation $f_{\\mathrm{GE}}-1$, and it is not an exact confidence interval.` → *(delete; stated at L660. There are four \"not a confidence interval\" disclaimers, at L652, L660, L680, and L813, plus two for the GP, at L222 and L740)*",
"IIIB-10": "Vague. `request markedly different altitude histories across the obstacle` → `request different clearance histories across the obstacle`",
"IIIB-11": "Repetition. `The episodes designed with references in the broad domain $0.5<z/R<6$ occupy the olive region, while those using the near-wall domain $0.5<z/R<1.5$ occupy the green region.` → `Broad-domain episodes lie in the olive region and low-clearance episodes in the green region.`",
"IIIB-12": "Number without symbol. `The latter repeats the same measured baseline episode at $0.35$~m/s, including its sampling and residual level, for the same number of cumulative interactions.` → `The latter repeats the measured baseline episode at $v_x^\\ast=0.35$~m/s, with its sampling and residual level, for the same number of episodes.`",
"IIIB-13": "Vague. `The reduction supports the conclusion that the designed missions add a new sensitivity direction, but the remaining value is still high.` → `This reduction indicates that the designed missions excite a new sensitivity direction, although the correlation remains above $0.88$.`",
"IIIB-14": "Vague. `but this portion of the curve is still associated with substantial local uncertainty.` → `but its relative uncertainty there is still [value].`. In the same paragraph, `the indicator is already small because` → `the indicator is below [value] because`.",
"IIIB-15": "Colon / improper word (\"safely\"). `This residual coupling follows from the structure of the selected power law and the range that can be explored safely: coordinated variations of $A$ and $p$ can generate very similar $f_{\\mathrm{GE}}(z/R)$ curves.` → `This residual coupling follows from the power law and from the clearance range above the $0.5R$ limit. Coordinated variations of $A$ and $p$ produce nearly identical $f_{\\mathrm{GE}}(z/R)$ curves over this range.`",
"IIIB-16": "Colon / vague. `The model initialized with Cheeseman-Bennett predicts the qualitative trend: the increased thrust raises the vehicle above the obstacle, and the removal of that contribution produces a loss of altitude downstream. Its magnitude is nevertheless underestimated.` → `With the Cheeseman--Bennett coefficients, the DT predicts the rise over the obstacle and the loss of altitude downstream, but underestimates both [by value].`",
"IIIC-6": "Repetition. `The constant reference $\\pi_{\\mathrm{BL}}$, executed through the built-in PID controller, can react to the aerodynamic interaction only after a tracking error has developed.` → *(delete)*",
"IIIC-7": "Signposting. `The performance change can be quantified with the same reward definition used throughout the subsequent policy search.` → *(delete; the next sentence can start \"With the reward of Eq.~\\eqref{eq:reward}, ...\")*",
"IIID-5": "Repetition. `The reward markers are computed from the cleaned mean trajectories; run-to-run dispersion is assessed in the trajectory comparisons and is not represented as a statistical error bar in the surrogate plots.` → *(delete; stated at L740)*",
"IIID-11": "Grammar (dashes) / improper word. `The subset spans different amplitude combinations and deliberately includes both apparently unfavorable changes-such as increasing the reference above the obstacle or reducing it downstream-and corrections that extend the compensating action already suggested by $\\pi_{\\mathrm{MB}}$.` → `The seven policies combine different amplitudes. They include changes that look unfavorable, such as raising the reference above the obstacle or lowering it downstream, and changes that extend the correction of $\\pi_{\\mathrm{MB}}$.`",
"IIID-12": "Vague. `identify the small subset selected for physical testing.` → `identify the seven policies flown.`",
"IIID-13": "Vague. `Most of the tested Sobol policies instead occupy a narrow neighborhood of $\\pi_{\\mathrm{MB}}$ on the DT-reward axis, while their physical rewards remain sufficiently separated to reveal a policy-dependent GP discrepancy.` → `Most Sobol policies have DT rewards within [range] of $\\pi_{\\mathrm{MB}}$, whereas their physical rewards span [range], which reveals a policy-dependent GP discrepancy.`",
"IIID-14": "Colon / undefined term. `The acquisition does not seek an immediate reward increase at every iteration: some policies are selected because their GP interpolation uncertainty makes them informative candidates, and their physical reward can therefore remain below the incumbent.` → `EI does not seek a reward increase at every iteration. Some policies are selected for their GP uncertainty, and their physical reward can remain below the best reward $\\mathcal R_{\\bullet}^{+}$ observed so far.`",
"IIIE-4": "Repetition. `Transfer therefore provides an informed initialization, but it does not replace condition-specific learning when the operating condition moves away from the region represented in the reward-transfer surrogate dataset.` → *(delete; stated at L964 after Fig. 13, which supports it, and again at L975 and L984)*",
"IIIE-8": "Colon / inconsistent term. `Two additional operating conditions are considered: a low-speed, larger-clearance crossing at $(z^\\ast/R,\\,v_x^\\ast/v_h)=(2.5,0.045)$ and a higher-speed, small-clearance crossing at $(1,0.113)$.` → `Fig.~\\ref{fig:generalization-trajectories} shows the lower-speed, larger-clearance crossing at $(2.5,0.045)$ and the higher-speed, smaller-clearance crossing at $(1,0.113)$.`",
"IIIE-9": "Vague. `The first explores an uncertain policy direction and performs poorly, yielding approximately $\\mathcal S_{\\bullet}=0.57$, as indicated by the small purple marker in Fig.~\\ref{fig:generalization-reward}.` → `The first explores an uncertain policy direction and scores $\\mathcal S_{\\bullet}=0.57$ (small purple marker in Fig.~\\ref{fig:generalization-reward}), below the [value] of $\\pi_{\\mathrm{MB}}$.`",
"CON-3": "Vague. `Directly transferring the nominal correction produced a modest gain at one operating condition but slightly underperformed the corresponding model-based policy at the other.` → `Directly transferring the nominal correction raised $\\mathcal S_{\\bullet}$ by [value] at one operating condition and lowered it by [value] at the other, relative to the model-based policy.`",
"CON-4": "Inconsistent term / vague. `Fractional and Sobol policies calibrated the reward-transfer surrogate` → `Interpolation and Sobol policies calibrated the reward-transfer surrogate`. In the same paragraph, `With few additional interactions` → `With [number] additional flights`.",
"P1": "**Grammar.** \"hass\" (typo). \"The interest and investments on ... hass grown\" should read \"interest and investment in ... have grown\". Further errors: \"Such increase\", \"substituting or support\", \"These includes\", \"In such context\", \"small onboard sensor\". \"if retained necessary\" is a calque of \"se ritenuto necessario\" and should read \"when needed\". \"guide deployment of human operations\" should read \"before human operators are sent in\". **Vague or improper.** \"grown significantly\" is an intensifier without a number. Other vague phrases are \"In specific applications\", \"can carry important advantages\" (\"carry\" → \"offer\"), \"plays a major role\", and \"the size of ... plays a major role as they can provide a preliminary mapping\", which mixes size and mapping in one clause. **Unsupported.** The advantages and the list of application domains have no citation. Add [CITE: review of UAV applications]. **Repetition.** R1 and R2 with P2. **Acronym.** \"UAVs\" is defined but never used again. The revision uses it once.",
"P2": "**Vague.** \"Indoor inspection, monitoring, and emergency-response missions are representative examples\" leaves open what they exemplify. \"These missions are also among the most demanding\" is an unsupported superlative. **Improper word.** \"obstacle avoidance leaves little room for tracking errors\" should refer to the obstacles' proximity, not to avoidance. \"The boundaries\" is not defined; use \"nearby surfaces\". **Logic.** In the last sentence, \"therefore\" does not follow from the tracking-error sentence. The wake–surface interaction is a second, separate reason. **Colon.** \"...passive geometric constraints: the wakes generated ...\" **Unsupported.** No citation for GNSS loss, limited computation, or degraded communication. Add [CITE]. **Repetition.** R1 and R2.",
"P3": "**Improper word.** \"elementary interactions\" should be \"rotor–surface interactions\". **Vague intensifiers.** \"very close\", \"substantially smaller change in lift\", and \"pronounced force increase\" have no numbers. Quote Carter's and Franzetti's or Cai's values if the size matters. Otherwise drop the intensifiers, as below. **Unsupported.** The tunnel scenario with combined floor, ceiling, and wall effects has no citation. Neither does \"Wall and ceiling effects have received less attention than ground effect\". **Function.** The paragraph sets up the focus on GE but never states it. P4's \"by contrast\" carries the link, which is acceptable.",
"P4": "**Missing citation.** \"since the middle of the twentieth century\" and \"the Cheeseman-Bennett approximation\" are uncited, although `\\cite{CheesemanBennett1955}` exists and is first used at L529. The wake-turning physics needs [CITE: rotorcraft aerodynamics textbook]. **Improper word, to check.** \"Classical momentum-theory relations, including the Cheeseman-Bennett approximation\" is doubtful because Cheeseman and Bennett used the method of images. The cited report is also titled *The Effect of Ground on a Helicopter Rotor in Forward Flight*, while the text says \"hovering\". \"lift\" for a rotor should be \"thrust\". **Vague.** \"primarily through its normalized clearance\" does not say normalized by what. \"clearance alone is insufficient\" does not say for what. **Logic.** P4 stresses that \"velocity changes the response\" (Kan), but II-B L544 says velocity dependence \"is limited over the low-speed range considered here\". State the advance-ratio range once and reconcile the two (see IIB-9). **Grammar.** \"Cheeseman-Bennett\" should use an en-dash, `Cheeseman--Bennett`.",
"P5": "**Vague referent.** \"These limitations\" could mean the classical models or the MAV-scale effects. **Vague.** \"the purpose of an aerodynamic model is not only to reproduce a force measurement\" is negative framing without a positive statement. **Grammar.** \"compensating the interaction\" should be \"compensating for the interaction\". **Improper word.** \"The problem is especially clear over finite obstacles\" uses \"clear\" for \"explicit\" or \"acute\". **Repetition.** R3 with P6.",
"P6": "**Unsupported.** \"Most MAVs rely on cascaded proportional-integral-derivative (PID) loops\" has no citation. **Vague.** \"robust nominal behavior\". **Colon.** \"intrinsically reactive: an unmodeled disturbance ...\" **Redundant.** \"the computational burden related to its online computation\". **Improper word.** \"a confidently wrong correction\" is informal. \"micro drone\" should be MAV. **Acronym.** \"MPC\" is defined but never used again. L707 spells out \"model predictive control\"; IIC-12 uses the acronym there.",
"P7": "**Vague referent.** \"this tension\" should be \"this trade-off\", which is the one stated at the end of P6. **Undefined term.** \"physical environment\" is RT jargon and appears here without explanation. **Unsupported.** \"A conventional DT is often understood as ...\" has no citation. Check whether `\\cite{Wagg2025}` covers it. **Improper word.** \"guide the next action of the physical environment\" is wrong because the environment does not act; a policy is deployed in it. **Grammar.** \"but still poorly experimentally validated\" has no subject and no verb. **To check.** \"gust rejection on a flapping-wing vehicle\" and \"flapping-wing flight\" may be the same application listed twice. **Repetition.** R9 with II-A L72.",
"P8": "**Vague.** \"a model-free policy could improve when the model reached ...\" has no object for \"improve\". \"protected the first interactions\" is unclear. **Inconsistent term.** \"model-based optimum\" against \"model-based policy\" (Section 3). The paragraph is otherwise sound. The edits are for precision only.",
"P9": "**Structure.** The paragraph has three functions: the two episode purposes, the dual-control contrast, and the model-based policy with its onboard implementation. It can stay one paragraph, but it is the longest in the Introduction. An optional split falls before \"Once the physical data ...\". **Vague or improper.** \"cast the same exchange\" (which exchange?), \"They retain two purposes for a physical episode\" (unclear), and \"sufficient for the task\". **Undefined term.** \"factual replay\" appears here but is defined only at L114. The revision defines it in passing. **Colon.** \"physically interpretable anchor: it already accounts ...\" **Inconsistent term, important for an IEEE control venue.** In the control literature a \"reference governor\" is an online add-on that modifies the reference to enforce constraints. Here the policy is a precomputed spatial offset stored in a table. A T-CST reviewer will read the term in its technical sense. Use \"reference correction\" or cite and justify the term (Section 3, term 3). **Repetition.** R4, R5, and R7.",
"P10": "**Signposting.** \"The role of Bayesian RT does not end at the model-based policy.\" **Inconsistent term.** Three names for one idea appear in one paragraph: \"structural discrepancy\", \"model discrepancy\", and \"GP discrepancy\". \"a Gaussian process represents the remaining GP discrepancy\" is circular, and the acronym GP is never defined. \"Bayesian RT\" is a second name for RT. **Vague.** \"an affordable DT\". **Repetition.** The last sentence (\"The latter accounts for ...\") restates the previous one. **Logic.** P11 opens \"This reward-transfer surrogate\", but P10 never introduces the name. The revision names it here.",
"P11": "**Undefined.** \"the final stage\", and the acronym EI, which is used from L730 on. **Improper word.** \"The policy can consequently move beyond\" should be \"The search\". \"safety envelope\" is a DT check (use \"admissible set\"). \"improved physics-based solution\" means the model-based policy. **Repetition and undefined term.** The last sentence (\"Information-oriented and performance-oriented interactions can in principle be interleaved ... RT selector\") repeats R5, and \"RT selector\" is not defined in the Introduction. Cut it.",
"P12": "**Wordy.** \"presents an experimental demonstration of the present RT formulation\". **Inconsistent term.** \"Richardson and Pretorius\" here is correct, because the bib entry has two authors. The body says \"Richardson et al.\" five times (IIB-3). **Unsupported qualifier.** \"independently validated\" holds for free flight only. Say so. **Defensive.** \"deliberately\". **Improper word.** \"retains a realistic discrepancy\". A model *leaves* a discrepancy; retaining one is not a goal. **Inconsistent term.** GE is defined in P4, but \"ground effect\" is spelled out here. **Logic gap.** P7 states the gap (\"seldom validated experimentally\"), but no sentence states the contribution against it. Add one if it is true, e.g. \"[first experimental RT campaign on a flying vehicle — verify]\".",
"P13": "**Logic gap.** The off-nominal tests of Section III-E, which the abstract announces, are not mentioned. The revision adds one sentence. **Inconsistent term.** \"lightweight spatial reference governor\" (see P9). **Vague.** \"making their experimental roles explicit while retaining the same RT loop\". **Repetition.** R5.",
"P14": "**Signposting.** The author's rule says to delete this paragraph. If the venue expects a roadmap, use one sentence."
}

WLOC = {
"AB-1": "L32",
"AB-2": "L32",
"AB-3": "L32",
"AB-4": "L32",
"IIA-1": "L72",
"IIA-2": "L72",
"IIA-3": "L72 and L143",
"IIA-4": "L92",
"IIA-5": "L146",
"IIA-6": "L146",
"IIA-7": "L158",
"IIA-8": "L181",
"IIA-9": "L183",
"IIA-10": "L199",
"IIA-11": "L199",
"IIA-12": "L212",
"IIA-13": "L212",
"IIA-14": "L222",
"IIA-15": "L224",
"IIA-17": "L356–366",
"IIB-1": "L503, L505, L529",
"IIB-2": "L505",
"IIB-3": "L432",
"IIB-4": "L372",
"IIB-5": "L372",
"IIB-6": "L374",
"IIB-8": "L425",
"IIB-9": "L544",
"IIC-1": "L561",
"IIC-2": "L563",
"IIC-3": "L566",
"IIC-4": "L566",
"IIC-5": "L566",
"IIC-7": "L573",
"IIC-8": "L575",
"IIC-9": "L575",
"IIC-10": "L577",
"IIC-11": "L691",
"IIC-12": "L706–707",
"IIC-13": "L709",
"IIC-14": "L730",
"IIC-15": "L732 and L738",
"IIC-16": "L740",
"IIC-17": "L760",
"IIC-18": "L768",
"IIC-19": "L771",
"IIC-20": "L771",
"IIIA-1": "L782",
"IIIA-2": "L782",
"IIIA-3": "L784",
"IIIB-1": "L807",
"IIIB-2": "L811",
"IIIB-3": "L811",
"IIIB-5": "L815",
"IIIB-6": "L828",
"IIIB-7": "L828",
"IIIB-8": "L837",
"IIIB-9": "L837",
"IIIC-1": "L855",
"IIIC-2": "L859",
"IIIC-3": "L861",
"IIIC-4": "L861",
"IIIC-5": "L863",
"IIID-1": "L881",
"IIID-2": "L881",
"IIID-3": "L892",
"IIID-4": "L901",
"IIID-6": "L910",
"IIID-7": "L910",
"IIID-8": "L910",
"IIID-9": "L919",
"IIID-10": "L928",
"IIIE-1": "L942",
"IIIE-2": "L944 and L964",
"IIIE-3": "L944",
"IIIE-5": "L953",
"IIIE-6": "L955",
"IIIE-7": "L975",
"CON-1": "L980",
"CON-2": "L982 and L986",
"AB-5": "L32",
"AB-6": "L32",
"AB-7": "L32",
"AB-8": "L32",
"IIA-16": "L242",
"IIA-18": "L117",
"IIA-19": "L143",
"IIA-20": "L146",
"IIA-21": "L147",
"IIA-22": "L158",
"IIA-23": "L161",
"IIA-24": "L161",
"IIA-25": "L185",
"IIA-26": "L199",
"IIA-27": "L213",
"IIA-28": "L245",
"IIA-29": "L245",
"IIA-30": "L353",
"IIA-31": "L282",
"IIB-7": "L374",
"IIB-10": "L546",
"IIB-11": "L372",
"IIB-12": "L374",
"IIB-13": "L374",
"IIB-14": "L374",
"IIB-15": "L425",
"IIB-16": "L427",
"IIB-17": "L432",
"IIB-18": "L505",
"IIB-19": "L529",
"IIB-20": "L542",
"IIB-21": "L544",
"IIC-6": "L573",
"IIC-21": "L555",
"IIC-22": "L575",
"IIC-23": "L587",
"IIC-24": "L614",
"IIC-25": "L635",
"IIC-26": "L660",
"IIC-27": "L680",
"IIC-28": "L691",
"IIC-29": "L702",
"IIC-30": "L702",
"IIC-31": "L704",
"IIC-32": "L726",
"IIC-33": "L730",
"IIC-34": "L740",
"IIC-35": "L747",
"IIC-36": "L768",
"IIC-37": "L771",
"IIIA-4": "L784",
"IIIA-5": "L782",
"IIIB-4": "L813",
"IIIB-10": "L798",
"IIIB-11": "L807",
"IIIB-12": "L809",
"IIIB-13": "L811",
"IIIB-14": "L813",
"IIIB-15": "L826",
"IIIB-16": "L839",
"IIIC-6": "L857",
"IIIC-7": "L861",
"IIID-5": "L901",
"IIID-11": "L892",
"IIID-12": "L892",
"IIID-13": "L901",
"IIID-14": "L910",
"IIIE-4": "L944",
"IIIE-8": "L942",
"IIIE-9": "L973",
"CON-3": "L984",
"CON-4": "L982",
"P1": "L40",
"P2": "L41",
"P3": "L43",
"P4": "L45",
"P5": "L47",
"P6": "L49",
"P7": "L51",
"P8": "L53",
"P9": "L54",
"P10": "L56",
"P11": "L58",
"P12": "L60",
"P13": "L62",
"P14": "L64"
}


WHO = {'EIC': 'Panel · journal fit', 'R1': 'Panel · methodology', 'R2': 'Panel · domain',
       'R3': 'Panel · perspective', 'DA': "Panel · devil's advocate"}

USER = ('My general comment, as having read only the intro so far, is that the text is quite ok but sometimes vague '
        'and uses improper wording, sometimes is a bit long/repetitive and has a relatively weak literature review on '
        'the problem of ground effect identification')

# Remarks quoted from the other material, word for word.
L = {
 'L-GE1': ('The current paragraph (line 45) covers the classical model and two multirotor studies only. The literature on '
           '*how GE parameters are obtained* splits into test-stand fits (most multirotor work), analytical/image models, '
           'CFD, learned models from flight data, and observer-based estimates. None of the works found designs flights '
           'to identify GE parameters. That is the gap to state, and it is defensible.'),
 'L-GE2': ('Two 2026 Vertical Flight Society papers are directly relevant to the obstacle-edge model and were not in either '
           'earlier review. **Yon and Li (2026)** correlate partial-coverage rotor thrust with a circular-segment rotor-ground '
           'overlap area, which is essentially your $\\chi_i$. **Herz et al. (2026)** fly a quadrotor over a building-like edge '
           'and find that full GE develops only after most of the vehicle has crossed it, with the airframe driving the onset. '
           'Cite the first at Eq. (corrected-thrust) as support and the second as a limitation.'),
 'L-GE3': ('**Lei et al. (2026)** report a *negative* GE region near $h/R\\approx1.5$ for their small-spacing quadrotor. Your '
           'nominal clearance is $z^\\ast/R=1.5$ and your law is monotone and positive. A referee may raise this. Add one '
           'sentence at the model paragraph saying that the identified law is an effective model over the tested clearances, '
           'not a general quadrotor law.'),
 'L-GE4': ('Your identified amplitude ($A=0.121$, about twice $1/16$) is consistent with Carter et al. (Crazyflie 2.0, lift '
           'increase more than twice the classical prediction) and Sharf et al. 2014 (stronger GE than theory on a small UAV).'),
 'L-Kan': ('Within *low-to-medium* speeds, ground effect depends "much more strongly" on altitude than on forward speed. '
           'This is drawn from Hummingbird data (their Fig. 4). [...] The forward-flight term of the Cheeseman–Bennett model, '
           '1/[1 − (R/4z)²/(1 + (V/v_i)²)], reduces the ground-effect increment by under 1.3% at 0.5 m/s, 0.6% at 0.35 m/s '
           'and 0.2% at 0.2 m/s.'),
 'L-Taffanel': ('The manuscript says the system provides "sub-centimetre-level absolute accuracy" and that Taffanel et al. '
                '"reported an average positioning error of approximately 0.5–1 cm and an RMS position jitter between 0.5 and '
                '1 mm". What the paper actually reports: in Results, the mean and median Euclidean error is 2–4 cm in all '
                'cases, with flight outliers up to about 5 cm. [...] Jitter is the RMS of consecutive-sample distances in the '
                '**stationary** test: LH2 0.3 mm (crossing beam) and 0.7 mm (EKF). [...] "0.5–1 cm" appears nowhere, and '
                'sub-centimeter accuracy is not supported.'),
 'L-Richardson': ('Richardson and Pretorius list m = 0.032 kg (not 0.03242 kg) and give no rotor radius. [...] Validation was '
                  'a 230-s flight with position steps near hover: RMSE x 2.32 cm, y 2.17 cm, z 1.73 cm. There was no '
                  'forward-flight test, so "validated ... for low speed free flight" should read "validated in near-hover '
                  'step maneuvers". Two authors: write "Richardson and Pretorius", not "Richardson et al.".'),
 'L-Poletti': ('**PolettiRT2025 (Introduction).** [...] Neither paper is experimental, and the clause contradicts the paper\'s '
               'own claim to be "the first experimental demonstration".'),
 'L-Forrester': ('It is cited for Expected Improvement, but it is a multi-fidelity co-kriging paper, so it fits better at the '
                 'reward-transfer sentence.'),
 'L-Kennedy2000': ('The affine-plus-GP reward transfer, R• = γ0 + γ1 R∘ + δ, is the autoregressive multi-fidelity model '
                   'introduced here. A referee will expect it named and credited, not presented as new.'),
 'L-Jones': ('It is the standard source for the closed-form Expected Improvement used in Eqs. (rt-expected-improvement) '
             'and (ei). Mockus1975 and Forrester2007 alone are not the usual attribution for that formula.'),
 'L-Eopt': ('The E-optimal, Fisher-based sequential design currently has no citation at all.'),
 'L-Uncited': ('IEEEtran prints only cited entries, so they are harmless but untidy. **Recommended: cite them.** Mehra1974 and '
               'Goodwin1977 go at the E-optimal design [...]. Ljung1999 goes at the Hessian-based covariance [...]. '
               'Chiuso2019 can be dropped.'),
 'L-Mendez': ('The current `Mendez2026` entry should be updated from "manuscript submitted" to the arXiv record above, while '
              'retaining any journal-submission note only if the authors want it and the target journal allows it.'),
 'GPT-litGE': ('The ground-effect literature is too narrow for the physical claims made. Missing work on partial ground '
               'effect, finite surfaces, dynamic ground effect, multirotor recirculation, and learned ground-effect '
               'compensation directly bears on the model chosen here.'),
 'GPT-litCtrl': ('The control literature is also incomplete. Since the experiment repeatedly executes the same spatial mission '
                 'and learns a feedforward/reference correction, iterative learning control and learned residual dynamics '
                 'are important comparators, not optional background.'),
 'GPT-path': ('The paper should be positioned as **an experimental, application-specific two-stage variant of Reinforcement '
              'Twinning for local policy refinement**, unless the missing elements of the full method are implemented.'),
 'GPT-contrib': ('Lines 60-62 should state what is demonstrated, not imply full implementation of the generic loop.'),
 'GPT-opening': ('Line 40 contains several grammatical errors and should be rewritten completely.'),
 'GPT-ident': ('At `z=R`, the second sensitivity vanishes because `log(R/z)=0`; at large clearance both sensitivities vanish; '
               'over a narrow range they can be strongly collinear. This analytically explains the observed correlation. '
               'Add this two-line derivation.'),
 'GPT-reward': ('Specify `Omega_R`, its spatial limits, resampling resolution, and whether all policies are compared at the '
                'same positions.'),
 'GPT-reg': ('In `J_MB`, the norms of the amplitude and curvature vectors are not divided by the number of grid points. '
             'Their relative weight therefore depends on the discretization.'),
 'GPT-bib': ('The bibliography file also contains a full prose paragraph after the `CheesemanBennett1955` entry. Remove that '
             'paragraph from `references.bib`; it belongs in `main.tex`.'),
 'Code-C15': ('Legacy run numbers (`EXP/legacy_name_map.json`): ALPHA_01–07 and EI_01–02 in It17, EI_03–08 in It18, then '
              'BL, INT_01, INT_02 and MB in It19. INF batches are It1, It2, It4 and It5; It3 and It6 were MB designs. [...] '
              '"It27" for INF_11/12 is a bookkeeping slot. Their metadata say "Imported from the legacy campaign".'),
 'Code-C6': ('"Reconstructed initial condition" (l. 114, 571, 577) is still wrong: replay starts at x = 1.70 m from the '
             'nominal steady out-of-ground-effect (OGE) state (`adjoint_identification.py:651-694`). Θ is not given; the code '
             'uses 0 ≤ p ≤ 6 and A ≥ −0.95·0.5^p. The 100-iteration minimum is not stated.'),
 'Code-C10': ('Cold start from (0,0): A = 0.12028, p = 1.96955, J_p = 0.0346547, 2195 iterations. Warm start: A = 0.12100, '
              'p = 1.98042, J_p = 0.0346530.'),
 'Code-C17': ('Data are radio-streamed via cflib, not recorded by the firmware (`run_next_experiment.py:567-725`). Periods: '
              'position 20 ms; most channels 50 ms; PID internals 100 ms. Stored rows are about 10 Hz.'),
 'Code-C18': ('x and y are velocity-commanded through `send_hover_setpoint(vx(x), vy, 0, z)` '
              '(`run_next_experiment.py:1006-1008`). The DT uses `XY_VELOCITY_MODE`. Only z uses the position loop.'),
 'Code-C20': ('σ_A = 0.084 and σ_p = 1.09 at E12; both marginal 2σ intervals include zero '
              '(`Warm_start/E12/adjoint_results.npz`).'),
 'Code-C19.4': ('Termination criterion (l. 183, 693, 828): no such test exists in the code.'),
 'Code-flight': ('The reference correction is evaluated on the ground station: `dz = np.interp(progress_x, x_policy, delta_z)` '
                 'and `send_hover_setpoint(vx(x), vy, 0, z_command)` at `SPATIAL_COMMAND_HZ = 50` '
                 '(`run_next_experiment.py:982-1010`).'),
 'Code-fit': ('`FIT_X_START = OBSTACLE_X_START`, `FIT_X_END = OBSTACLE_X_END` (`adjoint_identification.py:98-99`); '
              '`z_error = z_clean - HEIGHT_IN_ROTOR_RADII * ROTOR_RADIUS` (`:450-453`).'),
 'Code-geom': ('`TABLE_LENGTH_X = 3.21 - 2.40`, `TABLE_HEIGHT_Z = 0.63`, `TABLE_WIDTH_Y = 1.0`; "The Lighthouse deck is 7 mm '
               'above the COM; the propeller plane is another 1.5 mm above the Lighthouse deck"; `X_START = 0.20` '
               '(`jDT/params.py:52-66`).'),
 'Cut-C1': ('Block list after Fig. 1 (L356–364). 657 → 206 words (−451). The list restates II-A.'),
 'Cut-C2': ('L366, the paragraph after the list. 59 → 0 (−59). It repeats L158 and ends with a signposting sentence.'),
 'Cut-C3': ('L571, the information-phase summary. 80 → 24 (−56). It repeats II-A L161–183.'),
 'Cut-C5': ('L697, the opening of the model-based paragraph. 95 → 41 (−54). "Frozen", "lightweight", and the description of '
            'the performance loop are already stated elsewhere.'),
 'Cut-C6': ('L841 and L850, the closing paragraphs of III-B. 86 + 106 → 42 + 20 (−130).'),
 'Cut-C7': ('L865, the closing paragraph of III-C. 83 → 0 (−83). It repeats L199 and Intro L58 (model-free search), and L879 '
            'repeats it again.'),
 'Cut-C8': ('L879, the opening of III-D. 119 → 48 (−71). [...] L879 says "leading and trailing edges", but L863 locates the '
            'main error at the trailing edge.'),
 'Cut-C9': ('L890. 83 → 32 (−51). It repeats the model-free argument and uses "safe", "deliberately", a colon construction, '
            'and "substantially".'),
 'Cut-C10': ('L940, the opening of III-E. 105 → 24 (−81). It summarizes III-D, and its 41-word sentence uses "clear", "a few", '
             '"substantially", and "marginally".'),
 'Cut-C11': ('L953. 92 → 32 (−60). It repeats L762–768. Move the definitions of $\\mathcal S_\\circ$ and $\\mathcal S_\\bullet$ '
             'to L762 and fix $\\mathcal S_e$.'),
 'Cut-C12': ('L962 and L975. 67 + 117 → 21 + 47 (−116). These hold the third and fourth "not a converged surrogate" '
             'disclaimers.'),
 'Cut-C13': ('Conclusions (L980–986). 434 → 242 words (−192). The current text largely restates Results.'),
 'Cut-C14': ('L780, the opening of III-A. 71 → 25 (−46). It repeats L566 (controller, nominal condition, reactive feedback).'),
 'Cut-C16': ('L855 and the first sentence of L857. 110 → 20 (−90). These repeat L697–726 and contain the wrong objective and '
             'reference (IIIC-1).'),
 'Cut-C17': ('L796 and L798, the opening of III-B. 227 → 64 here + 21 moved to II-C (−142). These paragraphs contain method '
             'content.'),
}


def rk(*ids):
    """Remarks for a card, from the identifiers of the material."""
    out = []
    for i in ids:
        if i == 'You':
            out.append(remark('You', 'Your remark', USER, 'Introduction'))
        elif i in L:
            who = ('Literature check' if i.startswith('L-') else 'GPT review (V2)' if i.startswith('GPT-')
                   else 'Code check' if i.startswith('Code-') else 'Writing audit')
            out.append(remark(i, who, L[i]))
        elif i.startswith('GPT-'):
            out.append(remark(i, 'GPT review (V2)', H[i]))
        elif i[0] == 'N' and i[1:].isdigit():
            out.append(remark(i, 'Code check', H[i]))
        elif i.split('-')[0] in WHO:
            out.append(remark(i, WHO[i.split('-')[0]], H[i]))
        else:
            out.append(remark(i, 'Writing audit', W[i], WLOC.get(i, '')))
    return out


def code(*lines):
    return [{'label': 'Checked in the code and data', 'text': '\n'.join(lines)}]


ROUND = dict(
    id='round1',
    port=8765,
    manuscript='main.tex',
    snapshot='be81c7343b86dbbf2fd766d5f33dae39ea44e7b330120ba891997a28bcd744e3',
    label='Review round 1 · paper_tex/main.tex · 4 November 2026',
    title='IEEE draft: Introduction, ground-effect literature, GPT review V2, panel and code check',
    intro=('The remarks on the cards come from five sources: your remark on the Introduction; the GPT review '
           'PAPER_REVIEW_V2 (its 15 major findings); a simulated five-seat panel (journal fit, methodology, domain, '
           'perspective, devil\'s advocate); a check of Sections II and III against the code and EXP/CLEAN; a literature '
           'search on ground-effect modelling and identification with verified DOIs; and a writing audit. Cards follow the '
           'order of the manuscript. Suggestion cards hold decisions that need you, or new work.'),
    bib='references.bib',
)

NOTES = [
    'Your remark on the Introduction is answered in group I, one card per paragraph: grammar fixed, vague words replaced, '
    'repetitions cut. The ground-effect literature becomes three paragraphs (modelling, edges and dynamics, identification '
    'and compensation in control), ending on the gap that no study designs flights to identify the ground effect: '
    '[[t:Ground effect: three paragraphs]]. A new paragraph places RT against iterative learning control and sim-to-real '
    'Bayesian optimization: [[t:Related approaches]].',
    'Decisions only you can take: [[t:Framing]], [[t:Which model designed]], [[t:Campaign order]], '
    '[[t:Generalization: which reward]] and [[t:Target journal]]. The cards of groups I and II-A are written for the '
    'two-stage framing; if you choose otherwise, say so in the Framing note.',
    'Statements that disagree with the code or the data are graded A, with the code quoted under the card: three '
    'repetitions instead of five, two archived information records, the battery model, the transfer rule, the identification '
    'window, the reference sent from the ground station. The proposed text follows the code; if the code is what is wrong, '
    'say so in the note and the card is not applied.',
    'New references (20 on ground effect, 8 on control and methods, DOIs verified) travel with the cards that cite them. '
    'Corrections to existing entries are in [[t:Bibliography]]. The five rename cards apply after all edits, also inside '
    'the new texts. Equation numbers on the cards are the current ones.',
    'Not in this round: your abstract (cards only cut), new analyses and flights ([[t:Analyses on existing data]], '
    '[[t:New flights]]), equations removed for length ([[t:Length: equations]]), figures to regenerate (legends with '
    'π_k and "near wall", Fig. 15). They are listed in review/round1_not_in_cards.md, with the panel reports in '
    'review/round1_panel/.',
]

# New bibliography entries (DOIs verified on CrossRef, DataCite, OpenAlex or the publisher; see
# review/literature_ge_identification.md and review/literature_scan_round_SER.md).
X = {
'Curtiss1984': r"""@article{Curtiss1984,
  author  = {Curtiss, Jr., H. C. and Sun, Mao and Putman, William F. and Hanker, Edward J.},
  title   = {Rotor Aerodynamics in Ground Effect at Low Advance Ratios},
  journal = {Journal of the American Helicopter Society},
  volume  = {29}, number = {1}, pages = {48--55}, year = {1984},
  doi     = {10.4050/JAHS.29.48}
}""",
'SanchezCuevas2017': r"""@article{SanchezCuevas2017,
  author  = {Sanchez-Cuevas, Pedro and Heredia, Guillermo and Ollero, Anibal},
  title   = {Characterization of the Aerodynamic Ground Effect and Its Influence in Multirotor Control},
  journal = {International Journal of Aerospace Engineering},
  volume  = {2017}, pages = {1823056}, year = {2017},
  doi     = {10.1155/2017/1823056}
}""",
'He2019': r"""@article{He2019,
  author  = {He, Xiang and Kou, Gordon and Calaf, Marc and Leang, Kam K.},
  title   = {In-Ground-Effect Modeling and Nonlinear-Disturbance Observer for Multirotor Unmanned Aerial Vehicle Control},
  journal = {Journal of Dynamic Systems, Measurement, and Control},
  volume  = {141}, number = {7}, pages = {071013}, year = {2019},
  doi     = {10.1115/1.4043221}
}""",
'HeLeang2020': r"""@article{HeLeang2020,
  author  = {He, Xiang and Leang, Kam K.},
  title   = {Quasi-Steady In-Ground-Effect Model for Single and Multirotor Aerial Vehicles},
  journal = {AIAA Journal},
  volume  = {58}, number = {12}, pages = {5318--5331}, year = {2020},
  doi     = {10.2514/1.J059223}
}""",
'Franzetti2024ICUAS': r"""@inproceedings{Franzetti2024ICUAS,
  author    = {{David Du Mutel de Pierrepont Franzetti}, Iris and Parin, Riccardo and Carminati, Davide and Capello, Elisa},
  title     = {Modelling of Ground and Ceiling Effects for Quadcopters Based on Experimental Data},
  booktitle = {Proc. Int. Conf. Unmanned Aircraft Systems (ICUAS)},
  pages     = {405--412}, year = {2024},
  doi       = {10.1109/ICUAS60882.2024.10557056}
}""",
'Tanabe2021': r"""@article{Tanabe2021,
  author  = {Tanabe, Yasutada and Sugawara, Hideaki and Sunada, Shigeru and Yonezawa, Koichi and Tokutake, Hiroshi},
  title   = {Quadrotor Drone Hovering in Ground Effect},
  journal = {Journal of Robotics and Mechatronics},
  volume  = {33}, number = {2}, pages = {339--347}, year = {2021},
  doi     = {10.20965/jrm.2021.p0339}
}""",
'Lei2026': r"""@article{Lei2026,
  author  = {Lei, Yao and Zhang, Yuanfeng and Li, Xuan and Qiu, Jiafu and Yang, Hengxing},
  title   = {Interactional Aerodynamics and Flow Characteristics of a Quadrotor with Ground Effect},
  journal = {Physics of Fluids},
  volume  = {38}, number = {7}, pages = {075139}, year = {2026},
  doi     = {10.1063/5.0337114}
}""",
'Yon2026': r"""@inproceedings{Yon2026,
  author    = {Yon, Steven and Li, Sicheng},
  title     = {Experimental Investigation of Half-Ground Effects on Hovering Rotor Aerodynamics},
  booktitle = {Proc. Vertical Lift Aircraft Design and Aeromechanics Specialists' Conf.},
  address   = {San Jose, CA, USA}, publisher = {Vertical Flight Society},
  pages     = {1--11}, month = jan, year = {2026},
  doi       = {10.4050/SM-2026-VLADA-5207}
}""",
'Herz2026': r"""@inproceedings{Herz2026,
  author    = {Herz, Sage and Taylor, Julia and Clar, Lauren and McCrink, Matthew},
  title     = {Effects of Partial Boundaries and Variable Wind Conditions on a Free-Flying Multirotor Platform},
  booktitle = {Proc. Vertical Flight Society 82nd Annual Forum and Technology Display},
  address   = {West Palm Beach, FL, USA},
  pages     = {1--18}, month = may, year = {2026},
  doi       = {10.4050/F-0082-2026-0091}
}""",
'HeLeang2025': r"""@article{HeLeang2025,
  author  = {He, Xiang and Leang, Kam K.},
  title   = {Rotorcraft In-Ground Effect Models in Axial and Forward Flight},
  journal = {Aerospace Science and Technology},
  volume  = {156}, pages = {109748}, year = {2025},
  doi     = {10.1016/j.ast.2024.109748}
}""",
'He2024': r"""@inproceedings{He2024,
  author    = {He, Binglin and Zhang, Heng and Lai, Baisheng and Liu, Song and Wang, Yang},
  title     = {Data-Driven Modeling of Ground Effect for {UAV} Landing on a Vertical Oscillating Platform},
  booktitle = {Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)},
  pages     = {8169--8174}, year = {2024},
  doi       = {10.1109/IROS58592.2024.10802474}
}""",
'DelContBernard2017': r"""@article{DelContBernard2017,
  author  = {{Del Cont Bernard}, Davide and Riccardi, Fabio and Giurato, Mattia and Lovera, Marco},
  title   = {A Dynamic Analysis of Ground Effect for a Quadrotor Platform},
  journal = {IFAC-PapersOnLine},
  volume  = {50}, number = {1}, pages = {10311--10316}, year = {2017},
  doi     = {10.1016/j.ifacol.2017.08.1500}
}""",
'Wei2019': r"""@article{Wei2019,
  author  = {Wei, Peng and Chan, Sui Nam and Lee, Seongkyu and Kong, Zhaodan},
  title   = {Mitigating Ground Effect on Mini Quadcopters with Model Reference Adaptive Control},
  journal = {International Journal of Intelligent Robotics and Applications},
  volume  = {3}, number = {3}, pages = {283--297}, year = {2019},
  doi     = {10.1007/s41315-019-00098-z}
}""",
'LiX2024': r"""@article{LiX2024,
  author  = {Li, Xia and Qi, Guoyuan and Wang, Shuai and Li, Kuo and Deng, Jiahao and Guo, Xitong and Quan, Quan},
  title   = {Stable Hovering of Proximity Quadrotor {UAV} In-Ground Effect via Model Compensation Controller},
  journal = {Nonlinear Dynamics},
  volume  = {112}, number = {17}, pages = {15349--15375}, year = {2024},
  doi     = {10.1007/s11071-023-09124-z}
}""",
'Shi2019': r"""@inproceedings{Shi2019,
  author    = {Shi, Guanya and Shi, Xichen and O'Connell, Michael and Yu, Rose and Azizzadenesheli, Kamyar and Anandkumar, Animashree and Yue, Yisong and Chung, Soon-Jo},
  title     = {Neural Lander: Stable Drone Landing Control Using Learned Dynamics},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {9784--9790}, year = {2019},
  doi       = {10.1109/ICRA.2019.8794351}
}""",
'Yang2025': r"""@misc{Yang2025,
  author       = {Yang, Tiankai and Chai, Kaixin and Ji, Jialin and Wu, Yuze and Xu, Chao and Gao, Fei},
  title        = {Ground-Effect-Aware Modeling and Control for Multicopters},
  howpublished = {arXiv:2506.19424},
  year         = {2025},
  doi          = {10.48550/arXiv.2506.19424}
}""",
'Vitale2010': r"""@article{Vitale2010,
  author  = {Vitale, Antonio and Genito, Nicola and Garbarino, Luca and Ciniglio, Umberto and Corraro, Federico},
  title   = {A Hybrid Frequency-Time Domain Technique for Ground Effect Identification},
  journal = {The Aeronautical Journal},
  volume  = {114}, number = {1156}, pages = {377--385}, year = {2010},
  doi     = {10.1017/S0001924000003833}
}""",
'Jategaonkar2015': r"""@book{Jategaonkar2015,
  author    = {Jategaonkar, Ravindra V.},
  title     = {Flight Vehicle System Identification: A Time-Domain Methodology},
  edition   = {2nd}, series = {Progress in Astronautics and Aeronautics}, volume = {245},
  publisher = {American Institute of Aeronautics and Astronautics},
  address   = {Reston, VA, USA}, year = {2015},
  doi       = {10.2514/4.102790}
}""",
'Morelli2016': r"""@book{Morelli2016,
  author    = {Morelli, Eugene A. and Klein, Vladislav},
  title     = {Aircraft System Identification: Theory and Practice},
  edition   = {2nd}, publisher = {Sunflyte Enterprises}, year = {2016},
  isbn      = {978-0-9974306-1-5}
}""",
'Bahnemann2017': r"""@inproceedings{Bahnemann2017,
  author    = {B{\"a}hnemann, Rik and Burri, Michael and Galceran, Enric and Siegwart, Roland and Nieto, Juan},
  title     = {Sampling-Based Motion Planning for Active Multirotor System Identification},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {3931--3938}, year = {2017},
  doi       = {10.1109/ICRA.2017.7989453}
}""",
'Wilson2014': r"""@article{Wilson2014,
  author  = {Wilson, Andrew D. and Schultz, Jarvis A. and Murphey, Todd D.},
  title   = {Trajectory Synthesis for {Fisher} Information Maximization},
  journal = {IEEE Transactions on Robotics},
  volume  = {30}, number = {6}, pages = {1358--1370}, year = {2014},
  doi     = {10.1109/TRO.2014.2345918}
}""",
'Prothin2019': r"""@article{Prothin2019,
  author  = {Prothin, S. and {Fernandez Escudero}, C. and Dou{\'e}, N. and Jardin, T.},
  title   = {Aerodynamics of {MAV} Rotors in Ground and Corner Effect},
  journal = {International Journal of Micro Air Vehicles},
  volume  = {11}, pages = {1756829319861596}, year = {2019},
  doi     = {10.1177/1756829319861596}
}""",
'Sharf2014': r"""@inproceedings{Sharf2014,
  author    = {Sharf, I. and Nahon, M. and Harmat, A. and Khan, W. and Michini, M. and Speal, N. and Trentini, M. and Tsadok, T. and Wang, T.},
  title     = {Ground Effect Experiments and Model Validation with {Draganflyer X8} Rotorcraft},
  booktitle = {Proc. Int. Conf. Unmanned Aircraft Systems (ICUAS)},
  address   = {Orlando, FL, USA}, pages = {1158--1166}, year = {2014},
  doi       = {10.1109/ICUAS.2014.6842370}
}""",
'Torrente2021': r"""@article{Torrente2021,
  author  = {Torrente, Guillem and Kaufmann, Elia and F{\"o}hn, Philipp and Scaramuzza, Davide},
  title   = {Data-Driven {MPC} for Quadrotors},
  journal = {IEEE Robotics and Automation Letters},
  volume  = {6}, number = {2}, pages = {3769--3776}, year = {2021},
  doi     = {10.1109/LRA.2021.3061307}
}""",
'Bristow2006': r"""@article{Bristow2006,
  author  = {Bristow, Douglas A. and Tharayil, Marina and Alleyne, Andrew G.},
  title   = {A Survey of Iterative Learning Control},
  journal = {IEEE Control Systems Magazine},
  volume  = {26}, number = {3}, pages = {96--114}, year = {2006},
  doi     = {10.1109/MCS.2006.1636313}
}""",
'Schoellig2012': r"""@article{Schoellig2012,
  author  = {Schoellig, Angela P. and Mueller, Fabian L. and D'Andrea, Raffaello},
  title   = {Optimization-Based Iterative Learning for Precise Quadrocopter Trajectory Tracking},
  journal = {Autonomous Robots},
  volume  = {33}, number = {1--2}, pages = {103--127}, year = {2012},
  doi     = {10.1007/s10514-012-9283-2}
}""",
'Meraglia2021': r"""@article{Meraglia2021,
  author  = {Meraglia, Salvatore and Lovera, Marco},
  title   = {Smoother-Based Iterative Learning Control for {UAV} Trajectory Tracking},
  journal = {IEEE Control Systems Letters},
  volume  = {6}, pages = {1501--1506}, year = {2022},
  doi     = {10.1109/LCSYS.2021.3116263}
}""",
'Berkenkamp2016': r"""@inproceedings{Berkenkamp2016,
  author    = {Berkenkamp, Felix and Schoellig, Angela P. and Krause, Andreas},
  title     = {Safe Controller Optimization for Quadrotors with {Gaussian} Processes},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {491--496}, year = {2016},
  doi       = {10.1109/ICRA.2016.7487170}
}""",
'Marco2017': r"""@inproceedings{Marco2017,
  author    = {Marco, Alonso and Berkenkamp, Felix and Hennig, Philipp and Schoellig, Angela P. and Krause, Andreas and Schaal, Stefan and Trimpe, Sebastian},
  title     = {Virtual vs. Real: Trading Off Simulations and Physical Experiments in Reinforcement Learning with {Bayesian} Optimization},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  address   = {Singapore}, pages = {1557--1563}, year = {2017},
  doi       = {10.1109/ICRA.2017.7989186}
}""",
'Kennedy2000': r"""@article{Kennedy2000,
  author  = {Kennedy, Marc C. and O'Hagan, Anthony},
  title   = {Predicting the Output from a Complex Computer Code When Fast Approximations Are Available},
  journal = {Biometrika},
  volume  = {87}, number = {1}, pages = {1--13}, year = {2000},
  doi     = {10.1093/biomet/87.1.1}
}""",
'Jones1998': r"""@article{Jones1998,
  author  = {Jones, Donald R. and Schonlau, Matthias and Welch, William J.},
  title   = {Efficient Global Optimization of Expensive Black-Box Functions},
  journal = {Journal of Global Optimization},
  volume  = {13}, number = {4}, pages = {455--492}, year = {1998},
  doi     = {10.1023/A:1008306431147}
}""",
'Franceschini2008': r"""@article{Franceschini2008,
  author  = {Franceschini, Gaia and Macchietto, Sandro},
  title   = {Model-Based Design of Experiments for Parameter Precision: State of the Art},
  journal = {Chemical Engineering Science},
  volume  = {63}, number = {19}, pages = {4846--4872}, year = {2008},
  doi     = {10.1016/j.ces.2007.11.034}
}""",
'Kingma2015': r"""@inproceedings{Kingma2015,
  author    = {Kingma, Diederik P. and Ba, Jimmy},
  title     = {Adam: A Method for Stochastic Optimization},
  booktitle = {Proc. 3rd Int. Conf. Learn. Represent. (ICLR)},
  address   = {San Diego, CA, USA}, year = {2015},
  doi       = {10.48550/arXiv.1412.6980}
}""",
'Owen1998': r"""@article{Owen1998,
  author  = {Owen, Art B.},
  title   = {Scrambling {Sobol'} and {Niederreiter--Xing} Points},
  journal = {Journal of Complexity},
  volume  = {14}, number = {4}, pages = {466--489}, year = {1998},
  doi     = {10.1006/jcom.1998.0487}
}""",
'KrauseOng2011': r"""@inproceedings{KrauseOng2011,
  author    = {Krause, Andreas and Ong, Cheng S.},
  title     = {Contextual {Gaussian} Process Bandit Optimization},
  booktitle = {Advances in Neural Information Processing Systems 24},
  publisher = {Curran Associates}, pages = {2447--2455}, year = {2011}
}""",
}


def bib(*keys):
    return '\n\n'.join(X[k] for k in keys)

# ================================================================ Whole paper
G = 'Whole paper'
card(G, 'Target journal and length', grade='A',
     remarks=rk('EIC-1', 'EIC-9'),
     why='The venue fixes the page budget, and the budget decides how much of the method section can stay. The journal-fit '
         'seat checked the limits online: IEEE T-CST returns regular papers above 16 pages without review, RA-L allows 8, '
         'and T-RO 20 with charges from page 13. The paper has 20 pages now.',
     suggestion='(a) IEEE Transactions on Control Systems Technology, regular paper: aim at 14 pages. This round removes '
                'about 2,000 words of repetition; round 2 then removes the textbook equations and the duplicated ones (see '
                '[[t:Length: equations]]).\n(b) IEEE Transactions on Robotics: 20 pages is the maximum, with overlength '
                'charges, and the seat expects a broader scope (several surfaces, unmapped obstacles).\n(c) RA-L letter, 8 '
                'pages, on the nominal loop only.\nApply = (a). Another venue: name it in the note. Keep as is = no decision '
                'now; the length cuts of this round apply anyway.')

card(G, 'Framing: the full RT loop or a two-stage experimental variant', grade='A',
     flags=['Linked: [[t:Paragraph 12]]', 'Linked: [[t:Paragraph 13]]'],
     remarks=rk('GPT-path', 'GPT-4', 'GPT-5', 'R3-8', 'EIC-2'),
     why='The campaign implements a simplified, sequential version of the method of your RT paper (arXiv:2611.03540). The GPT '
         'review asks you to say so, or to implement what is missing. The cards of groups I and II-A are written for (a).',
     suggestion='(a) Present the paper as a two-stage experimental variant of RT. Section II-A keeps the episode definitions, '
                'factual replay and the two kinds of episode, and cites the method paper for the general loop. A short list, '
                'added in round 2, states what this campaign simplifies: rewards treated as noise-free means, an affine fit '
                'by least squares followed by a GP, the best measured reward as EI incumbent, a fixed candidate library, no '
                'held-out validation of the identification, a replay that starts from a steady commanded state rather than a '
                'synchronized one, and a model-based design that optimizes one nominal rollout rather than an expected '
                'reward.\n(b) Align the implementation with the method paper: a reward-noise model from the '
                'repetitions, a joint calibration, a posterior-mean incumbent, a search region that can expand, '
                'episode-disjoint validation. Part of this can be done on the existing data (see [[t:Analyses on existing '
                'data]]).\n(c) Keep the present framing.\nApply = (a). Keep as is = (c).')

# ================================================================ Title, abstract, keywords
G = 'Title, abstract and keywords'
card(G, 'Title and keywords', grade='B', flags=[YOURS],
     remarks=rk('EIC-9', 'EIC-6', 'R3-8'),
     why='"Applied to" reads as an application note, "Vehicles" is plural for one vehicle, and the task (crossing a finite '
         'obstacle) is missing. "Predictive control" promises an online MPC that the paper does not have. Untick either '
         'edit, or write your own title.',
     edits=[(r"\title{Reinforcement Twinning applied to Micro Aerial Vehicles in Ground Effect}",
             r"\title{Reinforcement Twinning for Ground-Effect Compensation of a Micro Aerial Vehicle Crossing a Finite Obstacle}"),
            (r"system identification, predictive control, Bayesian optimization.",
             r"system identification, optimal experiment design, Bayesian optimization, Gaussian processes.")])

card(G, 'Abstract: cuts and grammar only', grade='B', flags=[YOURS],
     remarks=rk('AB-3', 'AB-4', 'AB-8', 'EIC-3', 'GPT-14'),
     why='You rewrite the abstract yourself, so this card only cuts two claims that no result supports ("safe and '
         'computationally efficient", "without exhaustive model-free exploration") and fixes one sentence. For your '
         'rewrite: the physical reward goes from 0.544 (PID) to 0.855 (model-based) to 0.952 (ninth EI policy); the dataset '
         'has 41 policies and 137 flights; "constrains the dominant ground-effect response" says little. The abstract has 208 '
         'words now.',
     edits=[(r"The framework couples a Crazyflie 2.1+ as physical environment with its Digital Twin (DT) whose aerodynamic correction to account for ground effect is progressively identified from flight data.",
             r"The framework couples a Crazyflie~2.1+, the physical environment, with a digital twin (DT) whose ground-effect correction is identified progressively from flight data."),
            (r"model-based optimization first provides a safe and computationally efficient policy, while",
             r"model-based optimization first provides a DT-screened policy, while"),
            (r"These results support the use of an adaptive DT for model learning and control improvement without exhaustive model-free exploration in the physical environment.",
             r"These results support the use of an active DT for model learning and control improvement.")])

# ================================================================ Introduction
G = 'I. Introduction'
card(G, 'Paragraph 1: interest in UAVs and MAVs', grade='A', flags=[YOURS],
     remarks=rk('You', 'P1', 'GPT-opening', 'EIC-10'),
     why='Rewrites the opening paragraph, which has six grammatical errors ("hass", "These includes", "substituting or '
         'support", "if retained necessary", ...). The content is kept: market figures, advantages, applications, the role '
         'of small vehicles. A blank line now separates it from the next paragraph, which LaTeX merged into it. "UAVs" is '
         'not used again, so the acronym goes.',
     edits=[('\\IEEEPARstart{T}{he} interest and investments on Unmanned Aerial Vehicles (UAVs) hass grown significantly in recent years. A recent European Commission outlook places the European commercial airborne-drone market at about EUR~14.5 billion by 2030 and indicates that it could exceed EUR~50 billion by 2033~\\cite{EuropeanCommission2026}. Such increase in interest is mainly supported by the intrinsic features of these vehicles, including low operating cost, rapid deployment and the possibility of substituting or support human operators in hazardous missions. Their applications now span different domains, from logistics to emergency response and infrastructure inspection. In specific applications, drones of reduced size can carry important advantages. These includes especially operations in cluttered environments, where accessibility is limited and dangerous for human operators. In such context, the size of Micro Aerial Vehicles (MAVs) plays a major role as they can provide a preliminary mapping of the restricted zone with small onboard sensor to guide deployment of human operations if retained necessary.',
             "\\IEEEPARstart{I}{nterest} and investment in unmanned aerial vehicles have grown in recent years. A recent "
             "European Commission outlook places the European commercial airborne-drone market at about EUR~14.5 billion "
             "by 2030 and indicates that it could exceed EUR~50 billion by 2033~\\cite{EuropeanCommission2026}. This growth "
             "rests on low operating cost, rapid deployment, and the possibility of replacing or assisting human operators "
             "in hazardous missions. Applications range from logistics to emergency response and infrastructure inspection. "
             "Small vehicles are "
             "particularly useful in cluttered environments that are difficult or dangerous for people to enter. There, "
             "micro aerial vehicles (MAVs) with small onboard sensors can map a restricted zone before human operators are "
             "sent in.\n")])

card(G, 'Paragraph 2: missions in confined spaces', grade='B', flags=[YOURS],
     remarks=rk('You', 'P2'),
     why='Same content, tighter. "Representative examples" of nothing, "among the most demanding", "the boundaries" and '
         'the colon go; the two reasons why nearby surfaces matter (little room for error, changed aerodynamics) are now '
         'two sentences.',
     edits=[('Indoor inspection, monitoring, and emergency-response missions are representative examples. A MAV can enter confined spaces and cross passages whose clearance is only a few rotor radii. It can approach machinery, beams, pipes, and damaged structures that would otherwise require shutting down a facility or exposing an operator to danger. These missions are also among the most demanding. Satellite positioning is generally unavailable, onboard sensing and computation are limited, and communication can be degraded by the surrounding structure. At the same time, obstacle avoidance leaves little room for tracking errors. The boundaries therefore become part of the aerodynamic environment rather than passive geometric constraints: the wakes generated by the propellers interact with nearby surfaces and alter the forces and moments acting on the vehicle.',
             r"In indoor inspection, monitoring, and emergency response, a MAV can enter confined spaces and cross passages "
             r"whose clearance is only a few rotor radii. It can approach machinery, beams, pipes, and damaged structures "
             r"without shutting down a facility or exposing an operator to danger. These missions are also demanding. "
             r"Satellite positioning is generally unavailable, onboard sensing and computation are limited, and the "
             r"surrounding structure can degrade communication. Nearby surfaces leave little room for tracking errors and "
             r"also change the flight dynamics. The propeller wakes interact with these surfaces and alter the forces and "
             r"moments acting on the vehicle, so the surfaces are part of the aerodynamic environment rather than passive "
             r"geometric constraints.")])

card(G, 'Paragraph 3: ground, wall and ceiling effects', grade='B',
     remarks=rk('You', 'P3'),
     why='"Elementary interactions" becomes "rotor–surface interactions", and the three intensifiers ("very close", '
         '"substantially smaller", "pronounced") become the numbers Carter et al. measured on a Crazyflie. The tunnel '
         'sentence gains a reference on corner effect.',
     sources=[{'label': 'Carter et al. 2021 (full text read)',
               'text': 'Crazyflie 2.0 tethered to a load cell. Lift rises by up to about 20% near the ground, more than '
                       'twice the classical prediction. Ceiling gives up to about 60%, the wall under 5%.'}],
     extra=bib('Prothin2019'),
     edits=[(r"The elementary interactions with nearby surfaces are usually classified",
             r"Rotor--surface interactions are usually classified"),
            (r"with an asymmetric flow field that affects both translation and attitude.",
             r"with an asymmetric flow field that affects both translation and attitude. Even an isolated MAV rotor "
             r"responds differently in a wall--ground corner than above a floor~\cite{Prothin2019}."),
            (r"Wall effect is generally weak until the rotor is very close to the surface; Carter et al.~\cite{Carter2021}, for example, measured a substantially smaller change in lift near a lateral wall than near a floor or ceiling. Ceiling effect is also localized at small clearances, although wake blockage and recirculation can produce a pronounced force increase there~\cite{Franzetti2024,Cai2024}.",
             r"Wall effect remains weak until the rotor is close to the surface. On a Crazyflie, Carter et "
             r"al.~\cite{Carter2021} measured a lift change below 5\% near a lateral wall, against up to about 20\% near a "
             r"floor and 60\% near a ceiling. Ceiling effect is also confined to small clearances, where wake blockage and "
             r"recirculation increase the force~\cite{Franzetti2024,Cai2024}.")])

card(G, 'Ground effect: three paragraphs on modelling, edges and identification', grade='A', flags=[YOURS,
     'Linked: [[t:Paragraph 5]]'],
     remarks=rk('You', 'R2-9', 'EIC-5', 'GPT-litGE', 'L-GE1', 'L-GE2', 'P4'),
     why='Replaces the single ground-effect paragraph (two multirotor studies) by three. The first covers the classical '
         'model and multirotor models with how their parameters were obtained, and puts the Crazyflie result of Carter et '
         'al. next to the nonmonotonic responses reported recently. The second covers partial coverage at edges and dynamic '
         'effects, which bear directly on your overlap weighting and static law. The third covers identification and '
         'compensation in control, and ends on the gap: no study selects flights by their information on the GE '
         'parameters. Kan et al. now support "GE varies with speed" in general; the low-speed range of this paper is '
         'handled at Sec. II-B ([[t:Ground-effect law]]). 22 references, 21 of them new.',
     sources=[{'label': 'Sentence by sentence: what each source supports',
               'text': 'Curtiss 1984: three flow regimes with advance ratio; translational acceleration significant '
                       '(abstract). Sanchez-Cuevas 2017: image rotors plus body coefficient K_b≈2 from a test bench; a plate '
                       'under one rotor raised pitch and PID corrected it poorly (full text). He 2019: exponential per-rotor '
                       'quasi-steady model with a disturbance observer. He & Leang 2020: blade-element and image coefficients '
                       'plus an empirical thrust-loss term. Franzetti ICUAS 2024: exponential fit and GP regression of '
                       'test-bed thrust. Carter 2021: "more than twice what classic theory predicts" (full text). Tanabe '
                       '2021: power rises locally near one radius (CFD). Lei 2026: negative GE near h/R≈1.5. Yon & Li 2026: '
                       'thrust correlated with a circular-segment overlap area. Herz 2026: partial GE unlike full GE until '
                       'most of the vehicle has passed over. Kan 2019, He & Leang 2025, He 2024, Del Cont Bernard 2017: '
                       'speed, climb, platform motion, dynamic tests. Wei 2019 (MRAC), Li X. 2024 (observer, GE model fitted '
                       'to its estimates in hover), Shi 2019 (DNN residual), Yang 2025 (preprint; torques, rotor drag). '
                       'Vitale 2010: GE identified from aircraft flight data without dedicated maneuvers. Mehra 1974, '
                       'Jategaonkar 2015, Morelli & Klein 2016: input design for identification. Bähnemann 2017: informative '
                       'trajectories for multirotor parameters, flight-validated. Wilson 2014: trajectory synthesis that '
                       'maximizes the Fisher information, smallest eigenvalue included.'},
              {'label': 'Not proposed, and why',
               'text': 'Hayden 1976 (primary not found); Curtiss, Erdman & Sun 1985 (venue unverified); Xu et al. 2022 '
                       '(exists, content unverified); Leishman 2006 (GE pages unchecked); simulation-only GE estimators '
                       '(Nobahari 2014, Keshavarzian 2020).'}],
     extra=bib('Curtiss1984', 'SanchezCuevas2017', 'He2019', 'HeLeang2020', 'Franzetti2024ICUAS', 'Tanabe2021', 'Lei2026',
               'Yon2026', 'Herz2026', 'HeLeang2025', 'He2024', 'DelContBernard2017', 'Wei2019', 'LiX2024', 'Shi2019',
               'Yang2025', 'Vitale2010', 'Jategaonkar2015', 'Morelli2016', 'Wilson2014', 'Bahnemann2017'),
     edits=[('Ground effect (GE), by contrast, has been investigated since the middle of the twentieth century in classical aviation and rotorcraft. An underlying surface changes the pressure field and redirects the rotor wake radially, reducing the induced velocity and induced power required for a given lift. This can improve aerodynamic efficiency during takeoff, hover, and low-altitude flight. Classical momentum-theory relations, including the Cheeseman-Bennett approximation, describe the effect for an isolated rotor hovering above an extended plane primarily through its normalized clearance. At MAV scale, however, four nearby rotors interact with one another and with the central body, while low Reynolds number and wake recirculation make the response vehicle dependent~\\cite{Matus2020,Carter2021}. Forward motion adds wake convection and a finite residence time over the surface. Kan et al.~\\cite{Kan2019} confirmed the expected efficiency gain for small multirotors in forward flight, but also showed that clearance alone is insufficient and that velocity changes the response.',
             r"Ground effect (GE), by contrast, has been studied since the 1950s for helicopter rotors. A surface below the "
             r"rotor redirects the wake radially and reduces the induced velocity and the power required for a given "
             r"thrust. Cheeseman and Bennett derived the resulting thrust gain of an isolated rotor from its "
             r"clearance-to-radius ratio and forward speed~\cite{CheesemanBennett1955}, and rotor experiments showed that "
             r"the near-ground flow changes regime with advance ratio and depends on translational "
             r"acceleration~\cite{Curtiss1984}. In multirotors, rotor--rotor interaction and the flow beneath the central "
             r"body change this response~\cite{Matus2020}. It has been described by adding image rotors and an empirical "
             r"body coefficient to the classical model~\cite{SanchezCuevas2017}, or by exponential, quasi-steady, and "
             r"Gaussian-process models of the measured thrust~\cite{He2019,HeLeang2020,Franzetti2024ICUAS}. On a tethered "
             r"Crazyflie~2.0, the near-ground lift increase exceeded twice the classical prediction~\cite{Carter2021}, "
             r"whereas experiments and computations on other quadrotors report a nonmonotonic thrust or power response near "
             r"one to one and a half rotor radii~\cite{Tanabe2021,Lei2026}." "\n\n"
             r"Flight near obstacles adds two complications. First, the surface may lie under only some of the rotors. The "
             r"resulting thrust imbalance produces a moment that a cascaded PID controller rejects "
             r"poorly~\cite{SanchezCuevas2017}. For a single rotor, the thrust under partial coverage has been correlated "
             r"with the overlap area between rotor disk and surface~\cite{Yon2026}. Free-flight tests near a "
             r"building-like edge, however, found that full GE develops only after most of the vehicle has crossed the "
             r"edge~\cite{Herz2026}. Second, GE is not static. It varies with forward and climb "
             r"speed~\cite{Kan2019,HeLeang2025} and with the motion of the surface~\cite{He2024}, and dynamic quadrotor "
             r"tests have complemented the static characterizations~\cite{DelContBernard2017}." "\n\n"
             r"Control studies compensate GE online or learn it from flight data. Adaptive control~\cite{Wei2019} and "
             r"disturbance observers~\cite{He2019,LiX2024} counter the near-ground force, and Li et al.~\cite{LiX2024} also "
             r"fitted a GE model to observer estimates recorded in hovering flights. Deep networks trained on flight "
             r"data~\cite{Shi2019} and richer models that include surface motion and past states~\cite{He2024} or GE "
             r"torques and rotor drag~\cite{Yang2025} provide feedforward or model-based compensation. In aircraft, GE "
             r"coefficients have been identified from flight data recorded without dedicated maneuvers~\cite{Vitale2010}. "
             r"Flight-vehicle system identification, by contrast, designs the inputs to maximize the information on the "
             r"unknown parameters~\cite{Mehra1974,Jategaonkar2015,Morelli2016}. Robot trajectories have been synthesized to "
             r"maximize the Fisher information~\cite{Wilson2014}, and informative trajectories have been planned for other "
             r"multirotor parameters~\cite{Bahnemann2017}. To our knowledge, no study has selected the "
             r"flights of a multirotor by their information on the GE parameters.")])

card(G, 'Paragraph 5: why the interaction must be predicted', grade='B', flags=[YOURS,
     'Linked: [[t:Ground effect: three paragraphs]]'],
     remarks=rk('You', 'P5'),
     why='"These limitations" pointed to the old paragraph; the new opening follows from the gap stated just before. The '
         'negative framing ("not only to reproduce") becomes a positive statement, "safe path" becomes "collision-free '
         'path", and "especially clear" becomes "explicit".',
     edits=[('These limitations matter in cluttered flight because the purpose of an aerodynamic model is not only to reproduce a force measurement. The vehicle must remain on a safe path while moving from one obstacle to the next. A thrust variation above one surface can produce a small vertical excursion that appears benign locally but consumes the clearance available at a following beam, ceiling, or doorway. Predicting and compensating the interaction before the tracking error develops is therefore a safety requirement. The problem is especially clear over finite obstacles, where the vehicle enters GE, remains in it briefly, and then crosses a trailing edge. Leading-edge exposure, transient wake development, and post-obstacle recovery all occur within one mission.',
             r"Accurate GE prediction matters in cluttered flight because an aerodynamic model must do more than reproduce "
             r"a measured force. It must let the controller keep the vehicle on a collision-free path from one obstacle to "
             r"the next. A thrust change above one surface can produce a vertical excursion that is harmless locally but "
             r"uses up the clearance available at a following beam, ceiling, or doorway. The interaction must therefore be "
             r"predicted and compensated for before a tracking error develops. Finite obstacles make this requirement "
             r"explicit. The vehicle enters GE, remains in it briefly, and then crosses a trailing edge, so leading-edge "
             r"exposure, transient wake development, and post-obstacle recovery all occur within one mission.")])

card(G, 'Paragraph 6: PID and model predictive control', grade='B',
     remarks=rk('You', 'P6', 'GPT-litCtrl'),
     why='Removes the colon, "intrinsically", "confidently wrong" and "micro drone", and adds a quadrotor reference for MPC '
         'with learned residual dynamics, the closest MPC variant to the learning in this paper. "MPC" is not used again, '
         'so the acronym goes.',
     extra=bib('Torrente2021'),
     edits=[(r"Their low computational cost and robust nominal behavior make them well suited to small onboard processors. However, they are intrinsically reactive: an unmodeled disturbance must first produce an error before feedback counters it. Close to an obstacle, this delay can consume the available safety margin.",
             r"They are cheap to compute and robust near their nominal operating point, which suits small onboard "
             r"processors. However, they are reactive. An unmodeled disturbance must first produce an error before feedback "
             r"counters it, and close to an obstacle this delay can consume the available safety margin."),
            ('Model-based predictive methods can instead modify the command or reference before the disturbance fully develops. Model predictive control (MPC), in particular, offers a systematic way to optimize future behavior while accounting for dynamics and constraints~\\cite{MPCReview2021}. Its effectiveness is nevertheless tied to the model used for prediction and the computational burden related to its online computation. An incomplete model can generate a confidently wrong correction, whereas a more faithful aerodynamic model may be difficult to identify and too expensive to optimize repeatedly on the limited hardware of a micro drone.',
             r"Predictive methods instead modify the command or reference before the disturbance develops. Model "
             r"predictive control optimizes future behavior while accounting for dynamics and "
             r"constraints~\cite{MPCReview2021}, also on quadrotors with learned residual dynamics~\cite{Torrente2021}. Its "
             r"effectiveness depends on the prediction model and on the cost of solving the optimization online. An "
             r"incomplete model can produce a wrong correction, whereas a more faithful aerodynamic model may be difficult "
             r"to identify and too expensive to optimize repeatedly on the limited hardware of a MAV.")])

card(G, 'Paragraph 7: RT and the active twin; earlier RT studies were numerical', grade='A',
     remarks=rk('You', 'P7', 'L-Poletti', 'EIC-5'),
     why='The last sentence attributed four applications to two papers and said RT was "still poorly experimentally '
         'validated", a clause without subject or verb. All earlier RT studies, including your method paper, are numerical; '
         'saying so states the gap this paper fills without a "first" claim. "Tension" becomes "trade-off" (the one stated '
         'at the end of the previous paragraph), "physical environment" is introduced as a term, and the environment no '
         'longer "acts".',
     sources=[{'label': 'Checked in the cited papers',
               'text': 'Schena et al. 2024: wind turbine, flapping-wing MAV in gusts, cryogenic tank, all simulated. '
                       'Poletti et al. 2025: hybrid control of a flapping-wing drone, simulation only. Mendez et al. '
                       '(arXiv:2611.03540): a simulated physical system (1-D flow-control benchmark).'}],
     edits=[(r"Reinforcement Twinning (RT) was introduced to address this tension. It couples a physical environment such as a MAV with an active physics-based Digital Twin (DT)~\cite{SchenaRT2023,Mendez2026,PolettiRT2025}.",
             r"Reinforcement Twinning (RT) was introduced to address this trade-off. It couples a physical system, called "
             r"the physical environment, with an active physics-based digital twin "
             r"(DT)~\cite{SchenaRT2023,Mendez2026,PolettiRT2025}."),
            ('Experimental data refine its uncertain physics, while virtual rollouts guide the next action of the physical environment. This principle has been explored for wind-turbine control, gust rejection on a flapping-wing vehicle, cryogenic thermal management, and flapping-wing flight~\\cite{SchenaRT2023,PolettiRT2025}, but still poorly experimentally validated.',
             r"Experimental data refine its uncertain physics, and virtual rollouts select the next policy deployed in the "
             r"physical environment. RT has been applied to wind-turbine control, gust rejection on a flapping-wing "
             r"vehicle, and cryogenic thermal management~\cite{SchenaRT2023}, to the hybrid control of a flapping-wing "
             r"drone~\cite{PolettiRT2025}, and to a flow-control benchmark~\cite{Mendez2026}, all in simulation.")])

card(G, 'Paragraph 8: early RT', grade='C',
     remarks=rk('P8'),
     why='Precision only: "could improve" had no object and "protected the first interactions" was unclear. A blank line '
         'now separates it from the next paragraph, which LaTeX merged into it.',
     edits=[('Early RT algorithms combined model-based and model-free control. A model-based policy supplied an efficient, physically informed starting point, while a model-free policy could improve when the model reached a local or structurally biased optimum. A referee switched between them according to their observed or predicted performance. When learning stagnated, policy cloning transferred the weights of the more successful policy to the other learner, allowing the search to resume from a better region~\\cite{SchenaRT2023,PolettiRT2025}. The model-based branch thus protected the first interactions and accelerated early learning without forcing the final controller to remain at the model-based optimum.',
             "Early RT algorithms combined model-based and model-free control. A model-based policy supplied an efficient, "
             "physically informed starting point, and a model-free policy kept improving when the model-based one reached a "
             "local or structurally biased optimum. A referee switched between the two according to their observed or "
             "predicted performance. When learning stagnated, policy cloning copied the weights of the better policy to the "
             "other learner, so that the search resumed from a better region~\\cite{SchenaRT2023,PolettiRT2025}. The "
             "model-based branch thus made the first interactions less risky and accelerated early learning, without tying "
             "the final controller to the model-based optimum.\n")])

card(G, 'Paragraph 9: twin-calibrated Bayesian policy search', grade='B', flags=[YOURS],
     remarks=rk('P9', 'EIC-6', 'R3-8', 'Code-flight'),
     why='"The same exchange" and "they retain two purposes" now say what they mean, "factual replay" is defined where it '
         'first appears, and the colon goes. "Reference governor" has a fixed meaning in control (an online add-on that '
         'enforces constraints), so the policy is called a reference correction. The last sentence no longer says the '
         'correction runs onboard: in the campaign the ground station interpolates it and sends the setpoint by radio.',
     edits=[('More recent RT formulations cast the same exchange as a twin-calibrated Bayesian policy search~\\cite{Mendez2026}. They retain two purposes for a physical episode. An information-oriented policy is selected because its response can improve the uncertain physics in the DT; a performance-oriented policy is selected because it is expected to improve control. The objectives are coupled through the accumulated data and current DT, but they need not be collapsed into one scalar objective at every interaction. This also distinguishes RT from dual control. Dual control balances the immediate regulation and information consequences of each action~\\cite{Feldbaum1960,Filatov2000,Mesbah2018}. RT instead gives explicit roles to separate episodes and connects them through factual replay and the evolving DT. Once the information collected from the physical environment is sufficient for the task, the updated DT becomes the main instrument for policy search. It can solve the model-based control problem offline and evaluate candidate policies before they are deployed. The resulting model-based policy provides a physically interpretable anchor: it already accounts for the dynamics learned from the experiments and can be screened against state, clearance, and actuation constraints. If the final policy is expressed as a compact feedforward correction or reference governor, only this lightweight representation must run onboard, while the standard feedback controller remains responsible for stabilization.',
             r"More recent RT formulations cast the exchange between model-based and data-driven learning as a "
             r"twin-calibrated Bayesian policy search~\cite{Mendez2026}, in which each physical episode has one of two "
             r"purposes. An information-oriented policy is chosen to improve the uncertain physics in the DT, and a "
             r"performance-oriented policy to improve control. The two objectives are coupled through the accumulated data "
             r"and the current DT, but they need not be merged into one scalar objective. This distinguishes RT from dual "
             r"control, which balances the regulation and information consequences of each "
             r"action~\cite{Feldbaum1960,Filatov2000,Mesbah2018}. RT instead assigns the two roles to separate episodes, "
             r"linked by the DT, which is updated by replaying the recorded episodes (factual replay). Once the physical "
             r"data constrain the DT well enough for the task, the DT solves the model-based control problem offline and "
             r"screens candidate policies against state and clearance constraints before deployment. The "
             r"resulting model-based policy accounts for the dynamics learned from the experiments. If it is expressed as a "
             r"compact feedforward reference correction, the standard feedback controller is left unchanged and still "
             r"stabilizes the vehicle.")])

card(G, 'Paragraph 10: reward transfer, and its multi-fidelity origin', grade='B',
     flags=['Linked: [[t:Paragraph 11]]'],
     remarks=rk('P10', 'L-Kennedy2000', 'L-Forrester', 'EIC-2'),
     why='Drops the signposting opening, uses one name for one thing (model discrepancy, then the GP discrepancy), defines '
         'GP, and names the reward-transfer surrogate, which the next paragraph uses. The last sentence credits the '
         'affine-plus-GP structure to Kennedy and O\'Hagan, as a referee will expect; Forrester et al. moves here from the '
         'EI sentence, where it did not fit.',
     extra=bib('Kennedy2000'),
     edits=[('The role of Bayesian RT does not end at the model-based policy. Identification reduces parametric uncertainty but cannot remove a structural discrepancy between a compact physics model and the physical environment. Adding states and correction terms may reduce this model discrepancy, yet an affordable DT will still omit part of the physical response. Bayesian RT therefore learns how control performance transfers from the DT to the physical environment. Each tested policy supplies a DT reward and a physical reward. An affine relation captures the global calibration between the two, while a Gaussian process represents the remaining GP discrepancy and the uncertainty associated with sparsely explored regions~\\cite{Kennedy2001,Rasmussen2006}. The latter accounts for the part of the transfer that is not described consistently by either the physics model or the affine trend.',
             r"Identification reduces parametric uncertainty but cannot remove the structural discrepancy between a compact "
             r"physics model and the physical environment. Additional states and correction terms may reduce this model "
             r"discrepancy, but a DT that remains cheap to optimize still omits part of the physical response. RT therefore "
             r"also learns how control performance transfers from the DT to the physical environment. Each tested policy "
             r"yields a DT reward and a physical reward. In the resulting reward-transfer surrogate, an affine relation "
             r"captures the global calibration between the two rewards, and a Gaussian process (GP) represents the "
             r"remaining discrepancy, whose uncertainty is largest in sparsely explored regions. This is the autoregressive "
             r"multi-fidelity structure of Kennedy and "
             r"O'Hagan~\cite{Kennedy2000,Kennedy2001,Forrester2007,Rasmussen2006}.")])

card(G, 'Paragraph 11: Expected Improvement near the model-based policy', grade='B',
     flags=['Linked: [[t:Paragraph 10]]'],
     remarks=rk('P11', 'L-Jones'),
     why='Defines EI, which the paper uses from Section II on, cites the standard source of its closed form, and replaces '
         '"safety envelope" by the admissible set that the DT checks. The last sentence (interleaving and the "RT selector") '
         'repeats the episode structure already stated, with a term the Introduction does not define.',
     extra=bib('Jones1998'),
     edits=[('This reward-transfer surrogate turns the final stage into a data-efficient policy search. Expected Improvement balances the predicted physical reward against the uncertainty of the surrogate and proposes a candidate that is promising, insufficiently explored, or both~\\cite{Mockus1975,Forrester2007}. After the candidate is tested, its physical reward updates the surrogate and the search is repeated. The policy can consequently move beyond the model-based policy even if the DT retains a systematic bias. In contrast with a fully model-free search, however, exploration begins from an improved physics-based solution and remains within a neighborhood that has already been simulated and screened by the DT. The model supplies the initial direction and the safety envelope; physical data correct its ranking where this is needed. Information-oriented and performance-oriented interactions can in principle be interleaved within this loop, with the purpose of each episode made explicit by the RT selector.',
             r"The surrogate turns the last stage of RT into a Bayesian policy search. Expected Improvement (EI) weighs the "
             r"predicted physical reward against the surrogate uncertainty and proposes a candidate that is promising, "
             r"insufficiently explored, or both~\cite{Mockus1975,Jones1998}. The physical reward of the tested candidate "
             r"updates the surrogate, and the search is repeated. The search can therefore move beyond the model-based "
             r"policy even if the DT retains a systematic bias. Unlike a model-free search, however, it starts from the "
             r"model-based policy and stays within a neighborhood that the DT has already simulated and screened. The DT "
             r"supplies the initial direction and the admissible set, and physical data correct its ranking where needed.")])

card(G, 'Related approaches: iterative learning control and sim-to-real Bayesian optimization', grade='A',
     remarks=rk('EIC-5', 'R2-8', 'R3-7', 'GPT-litCtrl'),
     why='A new paragraph before "This paper ...". A repeated mission with a learned feedforward correction is the setting '
         'of iterative learning control, and Bayesian optimization on hardware with a simulator is the closest '
         'policy-search alternative. All five seats and the GPT review ask for this comparison. The paragraph states the '
         'difference without claiming that RT is better, since no comparator was flown.',
     extra=bib('Bristow2006', 'Schoellig2012', 'Meraglia2021', 'Berkenkamp2016', 'Marco2017'),
     edits=[(r"This paper presents an experimental demonstration",
             r"The repeated mission also invites comparison with two established approaches. Iterative learning control "
             r"refines a feedforward signal from the tracking errors of previous trials of the same "
             r"task~\cite{Bristow2006}, and it has been applied to quadrotor trajectory "
             r"tracking~\cite{Schoellig2012,Meraglia2021}. Bayesian optimization has tuned quadrotor controllers directly on "
             r"hardware~\cite{Berkenkamp2016} and has combined simulations and physical experiments as information sources "
             r"of different cost~\cite{Marco2017}. RT differs from both in that the flights first identify an interpretable "
             r"twin, which then designs and screens the policies, and the physical data correct the twin's ranking of "
             r"candidate policies." "\n\n"
             r"This paper presents an experimental demonstration")])

card(G, 'Paragraph 12: this paper, its scope and assumptions', grade='A', flags=[YOURS,
     'Linked: [[t:Framing]]'],
     remarks=rk('P12', 'GPT-contrib', 'EIC-8', 'L-Richardson'),
     why='Says which form of RT is shown, and adds the assumptions a referee looks for: the obstacle is known and the '
         'positioning is external, which isolates the ground-effect transient from perception and planning. '
         '"Independently validated" goes: Richardson and Pretorius validated their model in near-hover step maneuvers, as '
         'Sec. II-B now says. "Deliberately" and "retains a realistic discrepancy" go.',
     edits=[('of the present RT formulation on a physical MAV. A Crazyflie~2.1+ crosses a finite horizontal obstacle at constant forward speed, experiencing the onset and removal of ground effect within the same mission. The starting DT is the independently validated six-degree-of-freedom Crazyflie model of Richardson and Pretorius~\\cite{Richardson2025}, augmented with a deliberately low-order static ground-effect law whose unknown parameters are initialized from the Cheeseman-Bennett model. Its limited structure retains a realistic discrepancy, particularly around the obstacle edges, while remaining suitable for identification and control design.',
             r"of a two-stage form of RT on a physical MAV. A Crazyflie~2.1+ crosses a finite horizontal obstacle at "
             r"constant forward speed, so that GE appears and disappears within one mission. The mission is repeated over an "
             r"obstacle of known position and geometry, with external positioning, which isolates the GE transient from "
             r"perception and planning. The initial DT is the six-degree-of-freedom Crazyflie model of Richardson and "
             r"Pretorius~\cite{Richardson2025}, with an added static GE law "
             r"whose two parameters start from the Cheeseman-Bennett values. This low-order structure can be identified and "
             r"used for control design, but it leaves a model discrepancy, mainly at the obstacle edges.")])

card(G, 'Paragraph 13: the two stages and the off-nominal tests', grade='B',
     flags=['Linked: [[t:Framing]]'],
     remarks=rk('P13'),
     why='Names the two stages, drops "reference governor" and "lightweight", and adds the off-nominal tests, which the '
         'abstract announces but the Introduction never mentions.',
     edits=[('The campaign first uses information-oriented policies to identify these parameters and then freezes the updated model. The DT subsequently produces a model-based policy implemented as a lightweight spatial reference governor above the unchanged onboard PID controller. Physical rewards from nearby policies calibrate the reward-transfer surrogate, and Expected Improvement searches for further performance gains. Information-oriented and performance-oriented episodes are treated as consecutive phases in this work, making their experimental roles explicit while retaining the same RT loop.',
             r"In the first stage, E-optimal information-oriented flights identify the two GE parameters, which are then "
             r"frozen. In the second stage, the DT computes a model-based policy, applied as a spatial reference correction "
             r"above the unchanged onboard PID controller. Physical rewards of nearby policies calibrate the reward-transfer "
             r"surrogate, and EI searches for further gains. The two stages are consecutive rather than interleaved, so that "
             r"the role of each flight is explicit. Finally, the correction learned at the nominal condition is transferred "
             r"to two other combinations of clearance and speed, and a short EI search is tested at one of them.")])

card(G, 'Contributions paragraph', grade='A',
     remarks=rk('EIC-2', 'GPT-contrib'),
     why='The paper has no contributions statement, and the journal-fit seat names it as the first thing an editor looks '
         'for. The three items follow the results as they stand; the numbers are those of Sections III-C and III-D. Adjust '
         'freely.',
     edits=[(r"The remainder of the paper is organized as follows.",
             r"The paper makes three contributions. First, it applies RT to a physical vehicle. A differentiable DT of a "
             r"Crazyflie~2.1+ and its onboard controller designs both the identification flights and the control reference. "
             r"Second, E-optimal flights over two clearance domains identify a static GE law whose amplitude is about twice "
             r"the Cheeseman-Bennett value, and the DT yields a reference correction that raises the physical tracking "
             r"reward from $0.544$ to $0.855$ without changing the onboard controller. Third, after nine EI-selected "
             r"policies, a reward-transfer surrogate finds a correction with physical reward $0.952$ that the DT ranks as "
             r"nearly equivalent to the model-based one. The transfer of this correction to two off-nominal conditions is "
             r"also tested." "\n\n"
             r"The remainder of the paper is organized as follows.")])

card(G, 'Roadmap in one sentence', grade='C',
     remarks=rk('P14'),
     why='Your rule is no signposting; if the journal expects a roadmap, one sentence is enough. To delete it instead, write '
         'so in the note.',
     edits=[('Section~\\ref{sec:methodology} introduces the RT workflow, the physical environment and DT, and the information and performance phases. Section~\\ref{sec:results} presents and discusses the experimental campaign following the phases defined in the methodology. Section~\\ref{sec:conclusion} summarizes the main findings and limitations.',
             r"Section~\ref{sec:methodology} describes the RT loop, the physical environment and DT, and the test campaign; "
             r"Section~\ref{sec:results} reports the experiments; and Section~\ref{sec:conclusion} states the conclusions "
             r"and limitations.")])

# ================================================================ II-A
G = 'II-A. Reinforcement Twinning framework'
card(G, 'II-A opening: the two environments and their objectives, stated once', grade='B',
     remarks=rk('IIA-1', 'IIA-2', 'IIA-3', 'IIA-18'),
     why='RT and DT are defined a third time here, and the coupling of the two objectives is stated four times in II-A. One '
         'sentence each is kept; the objectives themselves stay in their equations.',
     edits=[('Reinforcement Twinning (RT) couples the evolution of a physical environment with that of an active, physics-based Digital Twin (DT)~\\cite{SchenaRT2023,Mendez2026}. The two environments evolve side by side and pursue complementary objectives. The physical environment has a performance objective related to the policy parameters to be optimized, whereas the DT must improve the physical model that predicts the response of the physical environment. Experience from the physical environment is therefore used both as evidence to update the DT and as feedback on the policies designed with that DT. Conversely, the DT not only adapts from observations but also proposes the next experiments and control policies from which new observations are generated.',
             r"In RT, the physical environment and an active, physics-based DT evolve side by side with complementary "
             r"objectives~\cite{SchenaRT2023,Mendez2026}. Physical data update the DT and score the policies it designs, and "
             r"the DT proposes the next experiments and policies."),
            (r"As anticipated, each of the two environments involved in the Reinforcement Twinning loop features its own objective. The physical environment aims for policy parameters",
             r"Each environment has its own objective. The physical environment seeks policy parameters"),
            ('and $\\mathcal{L}_p$ compares the DT and physical observations selected for identification. Equations~\\eqref{eq:rt-physical-objective} and~\\eqref{eq:rt-model-objective} are coupled: the model determines which policies appear promising or informative, while the resulting physical records determine how the model and the policy search evolve.',
             r"and $\mathcal{L}_p$ compares the DT and physical observations selected for identification.")])

card(G, 'Policies: what the information-policy rewards are used for', grade='B',
     flags=['Linked: [[t:Interpolation policies]]'],
     remarks=rk('IIA-5', 'IIA-6', 'IIA-20', 'IIA-21'),
     why='Here the rewards of information-oriented policies "support subsequent performance-oriented policy design"; in '
         'Sec. III-D they are excluded. The exclusion is now stated once, here, with its reason. Also drops a sentence that '
         'repeats the previous one, and "significantly".',
     edits=[(r"Policy design is therefore performed virtually: candidate interactions can be evaluated and optimized before the selected policy is transferred to the physical environment. The resulting",
             r"The resulting"),
            (r"The two policy families may have significantly different parameterizations because their classification reflects the objective used during policy design.",
             r"The two families are defined by the objective used to design them and may have different parameterizations."),
            (r"while an information-oriented policy also yields a physical reward that supports subsequent performance-oriented policy design.",
             r"while an information-oriented policy also yields a physical reward. The present campaign does not use these "
             r"rewards, because the information-oriented references depart from the nominal clearance."),
            (r"A binary interaction schedule $e_n\in\{0,1\}$ determines which policy is designed and deployed during each physical episode $n$:",
             r"A binary selector $e_n\in\{0,1\}$ determines which policy is designed and deployed in physical episode $n$,")])

card(G, 'Sequential schedule', grade='B',
     remarks=rk('IIA-7', 'IIA-22'),
     why='Removes the colon and the signposting ("described in detail below"), and points to the stopping criterion, which '
         'is now stated once ([[t:Stopping rule]]).',
     edits=[('For simplicity, the present work adopts a sequential schedule: all information-oriented missions are performed first until the  model satisfies the adopted identification and convergence requirements. The model parameters are then frozen and the campaign proceeds with performance-oriented missions. We consequently distinguish a first \\emph{information phase} and a subsequent separated \\emph{performance phase}, which are described in detail below.',
             r"For simplicity, the present work performs all information-oriented episodes first, until the model meets the "
             r"stopping criterion of the information phase. The model parameters are then frozen, and the campaign proceeds "
             r"with performance-oriented episodes. This defines an \emph{information phase} followed by a separate "
             r"\emph{performance phase}.")])

card(G, 'E-optimal design in II-A: its references, and the novelty check stated once', grade='B',
     remarks=rk('L-Eopt', 'L-Uncited', 'IIA-8', 'IIA-24'),
     why='The E-optimal criterion has no citation; two references already in the bibliography but uncited (Mehra, Goodwin '
         'and Payne) and one review are added. The generic novelty check goes: Sec. II-C now says what the campaign did '
         '([[t:Information design as flown]]). A sentence that repeats the previous one goes too.',
     extra=bib('Franceschini2008'),
     edits=[(r"Each candidate represents a possible next experiment and is evaluated in the DT before deployment. The DT",
             r"The DT"),
            (r"The policy deployed in episode $n+1$ is selected with an E-optimal criterion,",
             r"The policy deployed in episode $n+1$ is selected with an E-optimal "
             r"criterion~\cite{Mehra1974,Goodwin1977,Franceschini2008},"),
            ('and clearance constraints. This selection may be complemented by an explicit novelty criterion that compares each candidate with the existing dataset. It allows a mission with a slightly lower predicted information content to be selected when its response is sufficiently different from the experiments already available.',
             r"and clearance constraints.")])

card(G, 'Stopping rule of the information phase', grade='A',
     remarks=rk('IIA-9', 'IIIB-7', 'Code-C19.4', 'DA-5', 'R1-8'),
     why='The rule appears six times in different forms, with "appreciably" and "meaningful" as thresholds, and the code '
         'has no stopping test. The card states the rule once, in II-A, says that it was a judgment made without a '
         'threshold, and lets II-C and III-B refer to it. If a threshold was used, write it in the note.',
     edits=[('The information phase is terminated when the converged parameter estimates remain stable after adding new interactions and the magnitude of their estimated correlation no longer decreases appreciably. At this point, further experiments yield only marginal changes in the identified model and in the joint identifiability of its parameters.',
             r"The information phase ends when new episodes no longer change the converged estimates appreciably or reduce "
             r"the magnitude of their correlation. In the present campaign this was judged from the parameter history, the "
             r"correlation, and the replay of the baseline episode (Section~\ref{sec:results-inf}); no numerical threshold "
             r"was set in advance."),
            ('After the selected flight, its record is added to the replay buffer and the adjoint-Adam identification is repeated. The inner Adam loop is stopped by the numerical convergence conditions defined above. The complete information phase is terminated only when adding new episodes no longer changes the converged values of $A$ and $p$ appreciably and no longer produces a meaningful reduction in the magnitude of their estimated correlation.',
             r"The identification is then repeated on the enlarged replay buffer, and the information phase ends with the "
             r"criterion of Section~\ref{sec:rt-framework}."),
            (r"The coefficient stabilization, the limited further reduction of $\rho_{A,p}$, and the improved confidence in the control-relevant part of $f_{\mathrm{GE}}$ are taken together as the stopping condition for the information phase.",
             r"These observations and the replay of Fig.~\ref{fig:baseline-dt} are the basis for ending the information phase "
             r"(Section~\ref{sec:rt-framework}).")])

card(G, 'Performance phase in II-A: "safe" and a repeated argument', grade='B',
     remarks=rk('IIA-10', 'IIA-11', 'IIA-25', 'IIA-26', 'IIA-16', 'GPT-14', 'EIC-7'),
     why='"Safe policies ... evaluated in the DT to verify safety" is circular, and the DT checks guarantee nothing on the '
         'vehicle. The model-free argument appears five times; it stays in the Introduction and the Conclusions. In Methods, '
         'the improvement of the model-based policy is expected, not yet shown.',
     edits=[(r"accounting for safety constraints and actuator limits within the DT,",
             r"subject to the reference-amplitude and clearance constraints checked in the DT,"),
            ('because this model-based policy already improves upon the baseline policy and provides a physically informed reference. Exploring the full policy space with a purely model-free strategy would require substantially more physical tests and could expose the physical environment to unsafe policies.',
             r"because this model-based policy is expected to improve upon the baseline policy and provides a physically "
             r"informed reference."),
            (r"A small set of safe policies around $\pi_{\mathrm{MB}}$ is first evaluated in the DT to verify safety and then in the physical environment.",
             r"A small set of policies around $\pi_{\mathrm{MB}}$ is first screened in the DT and then flown."),
            (r"and the reward-transfer surrogate is updated. The DT restricts and guides the search around $\pi_{\mathrm{MB}}$, while the physical rewards allow RT to improve upon that policy.",
             r"and the reward-transfer surrogate is updated.")])

card(G, 'Surrogate in II-A: noise term, GP acronym, repeated statements', grade='A',
     remarks=rk('IIA-12', 'IIA-13', 'IIA-14', 'IIA-27', 'GPT-2'),
     why='Eq. (rt-surrogate) has a noise term, but Sec. II-C treats the rewards as exact with a jitter of 1e-8; a reader '
         'cannot reconcile the two. One sentence now says what the campaign did. GP is defined at first use in Methods, the '
         'GP is conditioned on residuals (not "discrepancies"), and a sentence repeated in Sec. II-C goes.',
     edits=[(r"The GP discrepancy $\delta(\boldsymbol\xi)$ models the policy-dependent part of the transfer that is not explained by that relation.",
             r"The Gaussian-process (GP) discrepancy $\delta(\boldsymbol\xi)$ models the policy-dependent part of the "
             r"transfer that the affine relation does not explain."),
            (r"while $\varepsilon$ represents experimental and reward-evaluation noise.",
             r"while $\varepsilon$ represents experimental and reward-evaluation noise. The present campaign reduces "
             r"$\sigma_{\varepsilon}$ to a numerical jitter (Section~\ref{sec:performance-phase})."),
            (r"The GP is conditioned on the discrepancies between the physical rewards",
             r"The GP is conditioned on the residuals between the physical rewards"),
            ('$\\sigma_{\\bullet}(\\boldsymbol\\xi)=\\sigma_{\\delta}(\\boldsymbol\\xi)$. This quantity is the posterior uncertainty of the adopted surrogate, not a confidence interval for experimental repeatability. The DT reward supplies the global performance trend, while the GP learns the local discrepancy between the DT and physical rewards.',
             r"$\sigma_{\bullet}(\boldsymbol\xi)=\sigma_{\delta}(\boldsymbol\xi)$.")])

card(G, 'EI incumbent: the best reward observed so far', grade='C',
     flags=['Linked: [[t:Analyses on existing data]]'],
     remarks=rk('IIA-15', 'GPT-3'),
     why='Says which "best physical reward". Whether to replace it by the best posterior mean, as your method paper does '
         'for noisy rewards, is part of [[t:Analyses on existing data]].',
     edits=[(r"Let $\mathcal R_{\bullet}^{+}$ denote the best physical reward and",
             r"Let $\mathcal R_{\bullet}^{+}$ denote the best physical reward observed so far and")])

card(G, 'Fig. 1: symbols and caption', grade='B',
     remarks=rk('IIA-30', 'IIA-31', 'EIC-10'),
     why='The figure calls the exogenous input z (the text uses d) and uses two symbols the text never defines. The caption '
         'now defines them and drops "in order to achieve their respective objectives".',
     edits=[(r"hidden state $\mathbf{s}_\bullet$, input $\mathbf z$",
             r"hidden state $\mathbf{s}_\bullet$, input $\mathbf d$"),
            ('\\caption{Reinforcement Twinning closed-loop adopted in this work. The physical environment and its active Digital Twin evolve side by side through physical observations and virtual candidate evaluations, in order to achieve their respective objectives. The selector $e_n$ distinguishes information-oriented ($e_n=1$) and performance-oriented ($e_n=0$) interactions, keeping a common loop for both cases.}',
             r"\caption{RT loop adopted in this work. The physical environment and its active DT evolve side by side through "
             r"physical observations and virtual candidate evaluations. The selector $e_n$ distinguishes "
             r"information-oriented ($e_n=1$) and performance-oriented ($e_n=0$) episodes within a common loop. In the "
             r"figure, $\mathcal J_{\mathrm{info}}$ is the E-optimal criterion of Eq.~\eqref{eq:rt-e-optimal} and "
             r"$\widehat{\mathcal R}_\bullet$ the surrogate prediction of the physical reward, written $\mu_\bullet$ in "
             r"Eq.~\eqref{eq:rt-surrogate-mean}.}")])

card(G, 'Block list after Fig. 1: one line per block', grade='B',
     remarks=rk('IIA-17', 'Cut-C1', 'Cut-C2', 'IIA-28', 'IIA-29', 'EIC-1'),
     why='The six-block list (657 words) restates II-A almost sentence by sentence, and the paragraph after it repeats the '
         'sequential schedule. Each block now says what it does, with the equation it uses (206 words). The summary '
         'paragraph before Fig. 1 loses its defensive sentences. About 500 words saved.',
     edits=[(r"The RT closed-loop is summarized in Fig.~\ref{fig:rt_framework}. The diagram represents one physical-digital iteration and makes explicit where information is created, where it is interpreted, and how it affects the next interaction with the physical environment. The selector",
             r"Fig.~\ref{fig:rt_framework} shows one iteration of the RT loop, from the deployed policy to the choice of the "
             r"next one. The selector"),
            (r"and updates the reward-transfer surrogate. In both cases, the physical environment is exposed only to a policy that has first been generated and screened in the DT.",
             r"and updates the reward-transfer surrogate."),
            ('The actions carried out in each block can be summarized as follows:\n\\begin{enumerate}\n    \\item Policy deployment: the iteration starts from the parameters selected at the end of the previous DT evaluation. The first interaction uses the baseline policy $\\pi_{\\mathrm{BL}}$, executed through the built-in PID controller, and provides the reference performance for comparison with the optimized policies. For $e_n=1$, the deployed policy is an information-oriented policy $\\pi_{\\iota}(\\cdot\\mid\\boldsymbol{\\theta}_{\\iota}^{(n)})$; for $e_n=0$, it is a performance-oriented policy $\\pi_{\\bullet}(\\cdot\\mid\\boldsymbol{\\theta}_{\\pi}^{(n)})$. This first block converts a design decision made in the DT into an executable command for the physical controller. The policy representation, its admissible parameter set, and all safety checks are application dependent, but the RT principle is unchanged: the DT proposes the interaction, while the physical environment supplies the evidence that determines whether the proposal was useful.\n    \\item Physical episode: the physical environment evolves under its hidden dynamics, the deployed policy, and the exogenous input $\\mathbf d$. The latter collects quantities that influence the episode without being selected by the policy, such as environmental disturbances, initial-condition variations, or changes in available actuation. The internal state $\\mathbf s_{\\bullet}$ is not generally known. RT receives the noisy observations $\\mathbf o_{\\bullet}$, the commanded inputs, and the operating conditions that are needed to reconstruct the episode. This distinction is essential because the DT is updated from what the experiment can actually measure.\n    \\item Recording: the observations, deployed policy, operating condition, control signals, exogenous inputs, and evaluated physical reward are collected in the episode record $\\mathcal E^{(n)}$ and appended to the replay buffer $\\mathcal B$. The purpose of this passage is to preserve a common, traceable description of the interaction before the information and performance branches use it differently. The replay buffer therefore links all later virtual operations to the experiment that produced their data and permits a model update to be repeated on the complete cumulative dataset.\n    \\item Factual replay: the DT reconstructs the initial state and replays the recorded policy under the measured operating conditions. When $e_n=1$, DT observations $\\mathbf o_{\\circ}$ are compared with $\\mathbf o_{\\bullet}$ and the mismatch is differentiated through the closed-loop twin. The model parameters are then updated from $\\boldsymbol{\\theta}_p^{(m)}$ to $\\boldsymbol{\\theta}_p^{(m+1)}$ using the cumulative replay buffer. When $e_n=0$, the model parameters remain frozen, so that $\\boldsymbol{\\theta}_p^{(m+1)}=\\boldsymbol{\\theta}_p^{(m)}$. The new policy-reward pair bypasses identification and instead augments the dataset used to learn the reward-transfer surrogate. Factual replay thus has a different learning target in the two phases, while the recorded evidence entering the loop remains the same.\n    \\item Virtual candidate evaluation: with the current model parameters, the DT evaluates interactions that have not yet been carried out. In the information branch, information-oriented policies are propagated through the closed-loop model, differentiated with respect to $\\boldsymbol{\\theta}_p$, and scored by the information they are expected to add to the weakest parameter direction. In the performance branch, the converged DT first provides the model-based policy $\\pi_{\\mathrm{MB}}$. Candidate deviations around this policy are then simulated, rejected if they violate the DT safety checks, and assigned both a DT reward and a reward-transfer surrogate prediction of their physical reward. This block is the main computational advantage of RT: a large candidate set can be explored in the DT while only a small number of selected policies reaches the physical environment.\n    \\item Choice of the next interaction: the final block converts the virtual evaluations into the next physical policy. For $e_n=1$, Eq.~\\eqref{eq:rt-e-optimal} selects the candidate that maximizes the smallest eigenvalue of the cumulative Fisher matrix and therefore strengthens the least-observed joint parameter direction. For $e_n=0$, Eq.~\\eqref{eq:rt-next-performance} selects the candidate with the largest Expected Improvement, balancing a high predicted physical reward against uncertainty in the learned transfer. The selected parameters are returned to Block~1, the physical episode index advances from $n$ to $n+1$, and the loop repeats. In the present work, the model-update index $m$ advances only in the information phase; separating the two indices makes clear that collecting a new performance episode does not imply a new model update.\n\\end{enumerate}\n\nThe selector value is scheduled within the test campaign. The loop first repeats Blocks~1-6 with $e_n=1$ until the model satisfies the adopted convergence and uncertainty criteria. It then switches once to $e_n=0$ and keeps the identified parameters fixed while the reward-transfer surrogate is refined. The following subsection specializes every element of this generic loop for the adopted test case.',
             "The blocks of Fig.~\\ref{fig:rt_framework} perform the following operations.\n"
             "\\begin{enumerate}\n"
             "    \\item Policy deployment. The policy selected in the previous iteration is deployed; the first episode uses "
             "the baseline policy $\\pi_{\\mathrm{BL}}$, which sets the reference performance.\n"
             "    \\item Physical episode. The physical environment evolves under its hidden dynamics, the deployed policy, and "
             "the exogenous input $\\mathbf d$, and returns the noisy observations $\\mathbf o_{\\bullet}$ of "
             "Eq.~\\eqref{eq:rt-physical-observation}.\n"
             "    \\item Recording. The record $\\mathcal E^{(n)}$ is appended to the replay buffer $\\mathcal B$, so that every "
             "model update uses the complete dataset.\n"
             "    \\item Factual replay. For $e_n=1$, the DT replays the recorded episode, and the mismatch between "
             "$\\mathbf o_{\\circ}$ and $\\mathbf o_{\\bullet}$ updates $\\boldsymbol{\\theta}_p^{(m)}$ to "
             "$\\boldsymbol{\\theta}_p^{(m+1)}$. For $e_n=0$, the model stays frozen, and the new policy--reward pair enters "
             "the reward-transfer surrogate.\n"
             "    \\item Virtual candidate evaluation. The DT simulates candidate policies. Information-oriented candidates are "
             "scored by their predicted information on $\\boldsymbol{\\theta}_p$. Performance-oriented "
             "candidates around $\\pi_{\\mathrm{MB}}$ that pass the DT checks receive a DT reward and a surrogate prediction "
             "of their physical reward. Many candidates are evaluated virtually, but only the selected one is flown.\n"
             "    \\item Choice of the next interaction. Equation~\\eqref{eq:rt-e-optimal} ($e_n=1$) or "
             "Eq.~\\eqref{eq:rt-next-performance} ($e_n=0$) selects the next policy, $n$ advances to $n+1$, and the loop "
             "returns to Block~1.\n"
             "\\end{enumerate}")])

# ================================================================ II-B
G = 'II-B. Physical and digital environments'
card(G, 'Mission geometry: clearance datum, obstacle size, start position', grade='A',
     flags=['Check the table height, 0.63 m'],
     remarks=rk('R2-2', 'EIC-7', 'N10', 'IIB-4', 'IIB-5', 'IIB-11'),
     why='A referee cannot tell which point of the vehicle z refers to, or how high and wide the obstacle is. The code '
         'answers both: z is the height of the rotor plane above the table top, the table is 0.81 m long, 1.0 m wide and '
         '0.63 m high, and the hover point is x = 0.20 m, not x = 0. R is defined at first use. Check that 0.63 m is the '
         'height above the floor (TABLE_HEIGHT_Z in the Lighthouse frame).',
     sources=code(L['Code-geom'],
                  'Hover: `run_next_experiment.py:305-308,1054-1070`, takeoff 2 s, go_to 2 s, hold 10 s at x = 0.20 m. '
                  'Experimental z: rotor-plane height above the obstacle top (`pp_EXP.py:340-344`).'),
     edits=[('The horizontal reference frame retains its origin at $x=y=0$, whereas the vertical origin is placed at the upper surface of the obstacle, so that $z=0$ at the obstacle height. Positive $z$ therefore measures the vertical distance of the vehicle from this surface, and $z/R$ is the corresponding nondimensional clearance, with $R=23$~mm. Each test begins at $x=0$~m, where the MAV reaches the prescribed altitude and hovers for 10~s.',
             r"The horizontal axes keep the origin $x=y=0$ of the positioning frame, whereas the vertical origin is the upper "
             r"surface of the obstacle, a table whose top is $0.63$~m above the floor. Positive $z$ is the height above this "
             r"surface of the rotor plane, which lies $8.5$~mm above the center of mass and $1.5$~mm above the Lighthouse "
             r"deck. With $R=23$~mm the rotor radius, $z/R$ is the nondimensional clearance. After takeoff, the MAV moves to $x=0.20$~m, climbs to the desired clearance $z^\ast$, and "
             r"hovers there for 10~s."),
            (r"around $x=1.0$-$1.2$~m", r"around $x=1.0$--$1.2$~m"),
            (r"spans $x=1.70$-$4.00$~m", r"spans $x=1.70$--$4.00$~m"),
            (r"corresponding to a streamwise length of $0.81$~m.",
             r"a streamwise length of $0.81$~m, and it is $1.0$~m wide.")])

card(G, 'Lighthouse positioning: what Taffanel et al. report', grade='A',
     remarks=rk('L-Taffanel', 'IIB-6', 'IIB-7', 'IIB-12', 'IIB-13', 'IIB-14', 'R2-2'),
     why='The accuracy figures attributed to Taffanel et al. are not in their paper: they report mean errors of 2–4 cm in '
         'flight and a stationary jitter of 0.3–0.7 mm. That error is 0.9–1.7R, which matters for a clearance of 1.5R. '
         'Also: the stations emit sweeps that the deck receives, the mass was measured, IMU is defined, and British '
         'spellings go. Say in the note which Lighthouse version and estimator the campaign used.',
     edits=[('The Crazyflie 2.1+ is equipped with an onboard IMU sensor for attitude control and a Lighthouse positioning deck for position control. Together with a 350 mAh battery, the drone mass is around $m=32.42$~g. To provide a continuous position reference, the Lighthouse deck is detected by two Lighthouse infrared stations.',
             r"The Crazyflie~2.1+ carries an onboard inertial measurement unit (IMU) for attitude control and a Lighthouse "
             r"positioning deck for position control. With its 350~mAh battery, its measured mass is $m=32.42$~g. For "
             r"continuous positioning, the Lighthouse deck receives the infrared sweeps of two Lighthouse base stations."),
            ('This configuration reduces the probability of temporary tracking loss or a position-estimation disturbance caused by an interruption of the optical link between a Lighthouse station and the Lighthouse deck mounted on the Crazyflie. The Lighthouse positioning system provides sub-centimetre-level absolute accuracy and sub-millimetre repeatability. In flight experiments, Taffanel et al.~\\cite{Taffanel2021Lighthouse} reported an average positioning error of approximately $0.5-1$~cm and an RMS position jitter between $0.5$ and $1$~mm, depending on the adopted estimator.',
             r"This overlap reduces the risk of losing the position estimate when one optical link is interrupted. For "
             r"Lighthouse~V2, Taffanel et al.~\cite{Taffanel2021Lighthouse} reported mean Euclidean errors of 2--4~cm in "
             r"flight, with outliers up to about 5~cm, and a stationary jitter of 0.3--0.7~mm depending on the estimator.")])

card(G, 'Data logging, flight commands and safeguards as flown', grade='A',
     remarks=rk('Code-C17', 'Code-C18', 'Code-flight', 'IIB-8', 'IIB-15', 'IIB-16', 'EIC-3', 'EIC-7'),
     why='Three statements disagree with the flight code: the data are streamed by radio, not recorded by the firmware; the '
         'horizontal channels are velocity-commanded, not tracked by a position loop; and the correction is interpolated on '
         'the ground station and sent at 50 Hz. The card also states the safeguards of the flight script, which the panel '
         'asks for when it questions "safe". Identification details move to II-C.',
     sources=code('`run_next_experiment.py:982-1010`: `dz = np.interp(progress_x, x_policy, delta_z)`; '
                  '`send_hover_setpoint(spatial_velocity_reference(progress_x), vy_command, 0.0, z_command)` every '
                  '1/SPATIAL_COMMAND_HZ = 20 ms; abort if the position log is older than SPATIAL_LOG_TIMEOUT = 0.35 s or the '
                  'stop position is not reached before the timeout; vy = −1.0·(y − y_target), clipped to ±0.15 m/s.',
                  '`run_next_experiment.py:238-252`: the first correction must be zero; reject |Δz| > 4.55R; reject a '
                  'DT-predicted lowest-rotor clearance below 0.5R (reference-correction policies).',
                  'Loop rates in the DT: position and velocity 100 Hz, attitude and rate 500 Hz (`jDT/controller.py:179-239`).'),
     edits=[(r"During each run, the Crazyflie firmware records the vehicle state, control response, and operating conditions.",
             r"During each run, flight data are streamed by radio to the ground station (position every 20~ms, the other "
             r"channels every 50 or 100~ms), where synchronized records are stored at about 10~Hz."),
            (r"and the individual motor PWM commands.",
             r"and the individual motor pulse-width-modulation (PWM) commands."),
            (r"For GE identification, the physical and DT trajectories are aligned along the streamwise coordinate, and the adjoint optimization minimizes the normalized vertical-position discrepancy over the obstacle region.",
             r"For GE identification, the physical and DT trajectories are aligned along the streamwise coordinate "
             r"(Section~\ref{sec:information-phase})."),
            (r"The remaining channels support initialization and replay of the measured operating conditions, but do not enter the identification objective directly.",
             r"The other logged channels serve trajectory assessment and do not enter the identification objective."),
            (r"An outer position loop tracks the desired position $\mathbf{x}^{*}$ and generates the corresponding velocity references $\mathbf{v}^{*}$. A velocity loop",
             r"During the crossing, the ground station sends a forward-velocity command scheduled on the measured $x$, a "
             r"lateral velocity command that holds $y=0$, and the altitude setpoint, every 20~ms. An outer position loop "
             r"converts the altitude setpoint into a vertical velocity reference. A velocity loop"),
            (r"The same control architecture and firmware logic are reproduced in the DT from the official implementation~\cite{BitcrazeFirmware}, ensuring consistency between the numerical and experimental closed-loop dynamics.",
             r"The DT reproduces this command mode, the firmware logic~\cite{BitcrazeFirmware}, and the loop rates (100~Hz "
             r"for position and velocity, 500~Hz for attitude and rates), so that the DT and the vehicle run the same "
             r"controller. The flight script aborts a mission when the position log is older than 0.35~s or the end of the "
             r"mission is not reached in time, and it rejects reference corrections larger than $4.55R$.")])

card(G, 'DT parameters: inherited, measured and calibrated; the battery model', grade='A',
     remarks=rk('N9', 'L-Richardson', 'IIB-1', 'IIB-2', 'IIB-3', 'R2-5'),
     why='The text says all parameters come unchanged from Richardson and Pretorius and that a battery-voltage correction is '
         'applied. In the code the mass is measured, the command-to-thrust gain is calibrated from hover (4.3% below the '
         'platform value), and the battery correction is never called: with the firmware compensation on, a command is a '
         'thrust request. The table follows. Richardson and Pretorius validated their model in near-hover step maneuvers.',
     sources=code('`jDT/params.py:32-38`: m = 0.03242 kg "measured on a precision scale"; FIRMWARE_THRUST_MAX_PER_MOTOR = '
                  '0.1148 N "calibrated from the measured mass and the pre-obstacle steady-hover collective command"; the '
                  'platform value 0.12 N "overestimates ... by about 4.3 %".',
                  '`jDT/simulator.py:331-346`: `battery_omega_factor` is not called; T_i = 0.1148·c_i/65535 N and '
                  'Ω_i = (T_i/k_T)^½. `params.py:115-116`: TAU_RPM = 0.02, rate limit 2·10⁵ rpm/s. C_D = 0; RK4 at 2 ms.',
                  '`simulator.py:304-314`: rotors at (±d/2, ±d/2), so d = 0.065 m is the adjacent-motor spacing.'),
     edits=[(r"The Digital Twin developed in this work follows the modeling formulation proposed by Richardson et al.~\cite{Richardson2025} for low-speed free flight and is tailored to reproduce the dynamics of the Crazyflie 2.1+ employed in the experimental campaign.",
             r"The DT follows the model of Richardson and Pretorius~\cite{Richardson2025}, validated by its authors in "
             r"near-hover flight, and is tailored to the Crazyflie~2.1+ of the campaign."),
            (r"propulsion system, battery dependence, actuator dynamics,",
             r"propulsion system, actuator dynamics,"),
            (r"Their parameters are inherited unchanged from Richardson et al.; they are neither reidentified nor independently revalidated in the present campaign.",
             r"The rigid-body, inertia, rotor-coefficient, actuator, and controller parameters are inherited from Richardson "
             r"and Pretorius. The vehicle mass was measured, and the effective command-to-thrust gain $T_{\max}=0.1148$~N "
             r"per motor was calibrated from the measured mass and the steady-hover collective command before the obstacle. "
             r"No other parameter is reidentified."),
            (r"where $d$ is the motor-to-motor distance",
             r"where $d$ is the distance between adjacent motors"),
            ('The connection between the motor commands and propeller speed follows the Crazyflie propulsion characterization adopted by Richardson et al. The effect of battery state is included through the battery voltage $V_b=f(\\mathrm{SOC})$, where $\\mathrm{SOC}$ denotes the battery state of charge. A voltage correction factor is defined as $\\eta_V=V_b/V_{\\mathrm{ref}}$, where $V_{\\mathrm{ref}}$ is the voltage of a fully charged battery. The rotor-speed command associated with the PWM input is corrected as $\\Omega_{\\mathrm{cmd}}=\\eta_V\\Omega_{\\mathrm{PWM}}$. The realized rotor speed follows this command through a first-order actuator model with time constant $\\tau_{\\mathrm{rpm}}=0.020$~s. This value is inherited from the Richardson model and is not identified in the present work.',
             r"With the firmware battery compensation enabled, each motor command $c_i\in[0,65535]$ is a "
             r"voltage-independent thrust request. The DT therefore maps it linearly to rotor thrust, "
             r"$T_i=T_{\max}c_i/65535$, and sets the commanded rotor speed $\Omega_{i,\mathrm{cmd}}=(T_i/k_T)^{1/2}$. The "
             r"realized speed follows this command through a first-order lag with time constant "
             r"$\tau_{\mathrm{rpm}}=0.020$~s and a rate limit of $2\times10^5$~rpm/s."),
            ('The main physical parameters adopted in the DT are taken from the formulation of \\cite{Richardson2025} and are summarized in Table~\\ref{tab:dt_parameters}. The nominal propulsion model retains the battery-voltage correction $V_b=f(\\mathrm{SOC})$. However, both physical and DT missions start with a fully charged battery and last only a few seconds; therefore, the within-mission change of state of charge is neglected. The vehicle dynamics are coupled with the same cascaded PID architecture used in the physical environment, providing the nominal closed-loop model on which the ground-effect correction is identified.',
             r"Table~\ref{tab:dt_parameters} lists the DT parameters; the DT also uses the products of inertia of Richardson "
             r"and Pretorius, up to $1.80\times10^{-6}$~kg~m$^2$. The dynamics are integrated with a fourth-order "
             r"Runge--Kutta scheme at a 2~ms step, and aerodynamic drag is neglected."),
            (r"\caption{Baseline DT parameters adopted from Richardson et al.~\cite{Richardson2025}.}",
             r"\caption{DT parameters. The mass is measured, $R$ is the propeller radius, and $T_{\max}$ is calibrated from "
             r"hover; the other values are those of Richardson and Pretorius~\cite{Richardson2025}.}"),
            (r"$V_{\mathrm{ref}}$ & $4.20$ V \\", r"$T_{\max}$ & $0.1148$ N \\")])

card(G, 'Ground-effect law: provenance, Cheeseman–Bennett, speed and sign', grade='A',
     flags=['Linked: [[t:Ground effect: three paragraphs]]'],
     remarks=rk('R2-12', 'R2-10', 'IIB-9', 'IIB-19', 'IIB-20', 'IIB-21', 'GPT-11', 'L-GE3', 'L-Kan'),
     why='Three corrections. The law 1 + (1/16)(R/z)² is the first-order expansion of the Cheeseman–Bennett constant-power '
         'relation, not a rearrangement, and the DT applies it to the thrust at the actual rotor speed, so A and p are effective '
         'coefficients. Kan et al. found ground effect at low and medium speed to depend much more on clearance than on '
         'speed, and the Cheeseman–Bennett forward-flight term changes the augmentation by less than 2% here; the model '
         'neglects speed, which the old wording denied. A negative ground effect near z/R ≈ 1.5 has been reported for one '
         'quadrotor, so the identified law is an effective model over the tested clearances.',
     sources=code('`jDT/simulator.py:374-384`: only the rotor thrust is multiplied by the ground-effect factor, at the '
                  'realized, lagged rotor speed (`simulator.py:358-363,406`); Q_i is not corrected. `simulator.py:315-324` stores velocity terms but '
                  'never uses them.'),
     edits=[('The described nominal DT reproduces the vehicle dynamics in free flight and was validated in those conditions by Richardson et al.~\\cite{Richardson2025}. The nominal DT, however,  does not account for the additional rotor-surface interaction generated as the vehicle closely crosses the finite obstacle. This interaction is introduced through a deliberately simple physical model inspired by the analytical formulation of Cheeseman and Bennett for an isolated rotor in hovering~\\cite{CheesemanBennett1955}.',
             r"The nominal DT does not account for the rotor--surface interaction generated as the vehicle crosses the "
             r"finite obstacle at low clearance. This interaction is modeled with a low-order law inspired by the "
             r"Cheeseman-Bennett relation for an isolated rotor~\cite{CheesemanBennett1955}."),
            ('The original Cheeseman and Bennett formulation rearranged with the same unknowns would have retained $A=1/16$ and $p=2$. These values initialize the identification in the present work, while both coefficients remain free to adapt to the present vehicle and operating conditions.',
             r"For a hovering rotor at constant power, Cheeseman and Bennett obtained "
             r"$T_{\mathrm{IGE}}/T_{\mathrm{OGE}}=[1-(R/4z)^2]^{-1}$~\cite{CheesemanBennett1955}, whose first-order expansion "
             r"gives $A=1/16$ and $p=2$. These values initialize the identification. The DT applies $f_{\mathrm{GE}}$ to the "
             r"thrust at the actual rotor speed, not at constant power, so the identified $A$ and $p$ are effective coefficients of the vehicle "
             r"in closed loop."),
            ('This model is deliberately low order: ground effect is treated as a static function of the instantaneous rotor clearance. Measurements by Kan et al.~\\cite{Kan2019} indicate that velocity dependence is limited over the low-speed range considered here, but it is not assumed to vanish. The formulation also omits the transient development and decay of the rotor-surface interaction as the vehicle crosses the obstacle edges.',
             r"The model is static. It treats ground effect as a function of the instantaneous rotor clearance only. Kan et "
             r"al.~\cite{Kan2019} found that, at low and medium speeds, ground effect depends much more on clearance than "
             r"on forward speed. Up to the $0.5$~m/s flown here, the forward-flight term of the Cheeseman-Bennett relation "
             r"also changes the augmentation by less than $2\%$. The model therefore neglects the speed dependence. It also "
             r"omits the transient development and decay of the rotor--surface interaction at the obstacle "
             r"edges~\cite{Curtiss1984}, and it is monotone in clearance, whereas a negative "
             r"ground effect near $z/R\approx1.5$ has been reported for a closely spaced quadrotor~\cite{Lei2026}. The "
             r"identified law is therefore an effective model over the tested clearances, not a general quadrotor law.")])

card(G, 'Overlap weighting at the obstacle edges: support and limits', grade='B',
     remarks=rk('R2-3', 'L-GE2', 'GPT-11', 'IIB-10', 'IIB-21'),
     why='The weighting by the overlapping fraction of each rotor disk is assumed. One recent measurement supports it, and '
         'one free-flight study shows its limit: the airframe delays full ground effect until most of the vehicle has '
         'crossed the edge. Both are now cited where the weighting is introduced. A definition repeated from Eq. '
         '(ge-thrust-factor) goes.',
     edits=[(r"It is therefore weighted by $\chi_i(x)\in[0,1]$, defined as the fraction of rotor disk $i$ that overlaps the obstacle.",
             r"The augmentation is therefore weighted by the fraction $\chi_i(x)\in[0,1]$ of rotor disk $i$ that overlaps "
             r"the obstacle, in line with measurements on a partially covered rotor whose thrust correlates with the "
             r"overlapping disk area~\cite{Yon2026}."),
            (r"where $T_{i,\mathrm{OGE}}$ is the nominal rotor thrust outside ground effect. The overlap fraction is zero when",
             r"where the overlap fraction is zero when"),
            (r"Its continuous variation across the leading and trailing edges avoids discontinuous force changes and naturally accounts for the four rotors entering and leaving the obstacle region at different streamwise positions.",
             r"Its continuous variation across the leading and trailing edges avoids discontinuous force changes and "
             r"accounts for the four rotors entering and leaving the obstacle at different streamwise positions. It weights "
             r"each rotor independently, whereas free-flight tests near a building-like edge found that full ground effect "
             r"develops only after most of the vehicle has crossed the edge~\cite{Herz2026}.")])

# ================================================================ II-C
G = 'II-C. Test campaign'
card(G, 'Normalized speed: one definition of each symbol', grade='C',
     remarks=rk('IIC-21', 'IIC-1'),
     why='Names the symbol v_x* where the speed is normalized, and stops redefining R and repeating m and R, which Table I '
         'gives.',
     edits=[(r"the desired forward velocity is normalized by the ideal induced velocity in hover,",
             r"the desired forward speed $v_x^\ast$ is normalized by the ideal induced velocity in hover,"),
            (r"where $T_{h,r}=mg/4$ is the hover thrust required from each rotor, $\rho_a$ is the air density, and $R$ is the rotor radius. With $m=32.42$~g, $R=0.023$~m, and $\rho_a=1.225$~kg/m$^3$,",
             r"where $T_{h,r}=mg/4$ is the hover thrust of each rotor and $\rho_a$ is the air density. With $m$ and $R$ "
             r"from Table~\ref{tab:dt_parameters} and $\rho_a=1.225$~kg/m$^3$,")])

card(G, 'Campaign overview: two sentences that state the obvious', grade='C',
     remarks=rk('IIC-2'),
     why='Deletes the first two sentences of the overview.',
     edits=[(r"The test campaign follows the sequential RT schedule introduced above. All tests use the same physical environment, DT structure, reference frame, and data-processing procedure described in Sec.~\ref{sec:setup}. The nominal",
             r"The nominal")])

card(G, 'Campaign table: 41 policies, 137 flights', grade='A',
     remarks=rk('GPT-15', 'EIC-4', 'R1-11', 'R3-5', 'DA-8'),
     why='The number of flights is never given, and "a few" EI evaluations is the paper\'s data-efficiency claim. The table '
         'counts the flights averaged in each record of EXP/CLEAN. Flights flown and discarded, if any, are not in it: add '
         'them in the note if you want them counted.',
     sources=code('`EXP/CLEAN/*_reward.json`, field number_of_repetitions: BL 3; INF_01–10 3 each, INF_11 4, INF_12 3; MB 3; '
                  'INT_01–02 4, 4; ALPHA_01–07 3, 4, 4, 5, 3, 4, 4; EI_01–10 6, 4, 3, 4, 3, 3, 4, 3, 3, 4; '
                  '(2.5, 0.045): BL 2, MB 2, TR 3; (1, 0.113): BL 3, MB 2, TR 3, EI_01 3, EI★ 4. 41 records, 137 flights.'),
     edits=[(r"and reward evaluation refer to this condition.",
             r"and reward evaluation refer to this condition. Table~\ref{tab:campaign} lists the policies flown and the "
             r"number of flights."),
            (r"\paragraph*{\textit{Baseline policy}}",
             "\\begin{table}[t]\n"
             "\\centering\n"
             "\\caption{Policies and flights of the campaign. The record of each policy is the mean of its retained flights.}\n"
             "\\label{tab:campaign}\n"
             "\\begin{tabular}{lccc}\n"
             "\\hline\n"
             "Stage and policies & Policies & Flights each & Flights \\\\\n"
             "\\hline\n"
             "Baseline $\\pi_{\\mathrm{BL}}$ & 1 & 3 & 3 \\\\\n"
             "Information $\\pi_{\\mathrm{INF}}$ & $10+2^{a}$ & 3--4 & 37 \\\\\n"
             "Model-based $\\pi_{\\mathrm{MB}}$ & 1 & 3 & 3 \\\\\n"
             "Interpolation $\\pi_{\\lambda,i}$ & 2 & 4 & 8 \\\\\n"
             "Sobol $\\pi_{\\mathbf a,i}$ & 7 & 3--5 & 27 \\\\\n"
             "EI $\\pi_{\\mathrm{EI},i}$ & 10 & 3--6 & 37 \\\\\n"
             "At $(2.5,0.045)$ & 3 & 2--3 & 7 \\\\\n"
             "At $(1,0.113)$ & 5 & 2--4 & 15 \\\\\n"
             "\\hline\n"
             "Total & 41 & & 137 \\\\\n"
             "\\hline\n"
             "\\multicolumn{4}{l}{\\footnotesize $^{a}$Archived records of an earlier campaign.}\n"
             "\\end{tabular}\n"
             "\\end{table}\n\n"
             "\\paragraph*{\\textit{Baseline policy}}")])

card(G, 'Campaign order (decision)', grade='A',
     remarks=rk('Code-C15', 'N8'),
     why='The text presents the campaign as five consecutive blocks, the baseline as the first record, and the interpolation '
         'policies as "first tested". The run numbers in the data say otherwise: the baseline, interpolation and '
         'model-based records used for reward transfer were flown in run It19, after the Sobol policies (It17) and EI_01–08 '
         '(It17–18), and they are re-flights of earlier designs. INF_11 and INF_12 come from an earlier campaign. Presenting '
         'by stage is fine, but a referee who asks for the logs will see the order.',
     sources=code('`EXP/legacy_name_map.json` and the metadata of each record. The re-flight of π_MB in It19 '
                  '(mission_design "rt_calibration", identification_iteration "iteration_006") goes through the '
                  '`video_repeats` mode of `transfer_calibration.py`, which re-packages the reference of an earlier '
                  'experiment.'),
     suggestion='(a) Replace "The campaign is organized into five consecutive blocks, introduced below together with the '
                'notation used in the results." by: "The campaign has five stages, presented below in the order of the RT '
                'loop. The flights were not acquired in this order. The baseline, interpolation, and model-based records '
                'used for reward transfer were re-flown after the first Sobol and EI policies, two information records come '
                'from an earlier campaign, and the sequential identification of Section~\\ref{sec:results-inf} is a '
                'post-campaign replay in the order of Fig.~\\ref{fig:adjoint-convergence}."\n(b) The data record is '
                'incomplete: write the actual order in the note and I adapt the sentence. The same records show that EI_01–08 were '
                'flown in two sessions (It17, It18) and that runs It3, It6–It16 and It22 are not in the data, so the table '
                'counts retained flights only; say whether "selected sequentially by EI" holds.\n(c) Keep the present wording.\n'
                'Apply = (a). Keep as is = (c).')

card(G, 'Baseline policy paragraph', grade='B',
     remarks=rk('IIC-3', 'IIC-4', 'IIC-5'),
     why='A controller is not a policy: the baseline policy is the constant reference. The rewards are not normalized by '
         'the baseline cost; only the scores of Eq. (normalized-score) are. That PID feedback is reactive is stated in the '
         'Introduction and in Sec. III-A.',
     edits=[(r"The campaign starts from the built-in cascaded PID controller at the nominal condition $(z^\ast/R,\,v_x^\ast/v_h)=(1.5,0.079)$. This policy is denoted by $\pi_{\mathrm{BL}}$ and is repeated experimentally to quantify run-to-run variability.",
             r"The baseline policy $\pi_{\mathrm{BL}}$ is a constant reference at the nominal condition, tracked by the "
             r"onboard cascaded PID controller. It is flown repeatedly to quantify run-to-run variability."),
            ('and the baseline tracking cost used to normalize the rewards reported later. Since $\\pi_{\\mathrm{BL}}$ reacts only after the vehicle departs from the desired clearance, it also exposes the ground-effect excursion that the subsequent predictive policies are designed to anticipate.',
             r"and the baseline cost $J_{\mathrm{BL}}$ used in the normalized score of "
             r"Eq.~\eqref{eq:normalized-score}.")])

card(G, 'Information phase in II-C: where the replay starts', grade='A',
     remarks=rk('Code-C6', 'GPT-6', 'Cut-C3'),
     why='"Reconstructed initial condition" is not what the code does: every replay starts at x = 1.70 m from the steady '
         'out-of-ground-effect state at the commanded clearance and speed of the record, with no synchronization to the '
         'measured state. The '
         'GPT review asks exactly this. The rest of the paragraph repeats II-A and is shortened.',
     sources=code(L['Code-C6']),
     edits=[('Each trajectory deployed in the physical environment is replayed through the differentiable DT with the same reference and reconstructed initial condition used experimentally. Factual replay identifies the coefficient pair from the accumulated tracking response. The subsequent DT design searches for a safe altitude reference that adds information along the least-observed parameter direction, thereby defining the next experiment. The two operations are repeated sequentially, with each new flight updating both the identified parameters and the information available for the next design.',
             r"Each episode is replayed in the DT with the deployed reference, starting at $x=1.70$~m from the steady "
             r"out-of-ground-effect state at the commanded clearance and speed of the record. Factual replay identifies $A$ and $p$ from the "
             r"accumulated tracking response, and the DT then designs the next experiment.")])

card(G, 'Information phase: the records, the design domains and the update schedule', grade='A',
     flags=['Linked: [[t:Information phase: opening of III-B]]', 'Linked: [[t:Near-wall stage]]'],
     remarks=rk('N8', 'IIC-6', 'IIC-7', 'IIC-8', 'IIC-9', 'IIC-22'),
     why='Three facts differ from the text. Of the twelve information records, ten were designed in this campaign and two '
         '(INF_11, INF_12) are archived means from an earlier campaign at z*/R = 1. The low-clearance domain of the '
         'reference is 0.3R to 1.5R, not 0.5R to 1.5R (INF_09 reaches 0.34R). The model was updated after each batch of '
         'three; the flight-by-flight sequence of Fig. 4 is a post-campaign replay. The first sentence (Cheeseman–Bennett '
         'initialization) is the fourth statement of it, and the 52-word colon sentence is split.',
     sources=code('Design batches: INF_01–03 It1, INF_04–06 It2 ("wide" 0.5–6R), INF_07–09 It4 and INF_10 It5 '
                  '("near_wall" 0.3–1.5R, `informative_policy.py:62-65,368-391`). INF_11: legacy campaign `GE_rg_a`, '
                  '(1, 0.091), v_x = 0.40 m/s; INF_12: (1, 0.102), 0.45 m/s; `raw_repetitions_available: false`. Every record '
                  'of a batch carries the same identification_iteration; E00–E12 is a post-campaign replay '
                  '(`adjoint_identification.py:1,41-45,70-83`).'),
     edits=[('The model is initialized from the Cheeseman-Bennett coefficients, $A=1/16$ and $p=2$. Starting from the baseline record, twelve information-oriented policies $\\pi_{\\mathrm{INF}}^{(n)}$ are added sequentially to the cumulative dataset. The first six policies are designed over the broad admissible clearance range $0.5<z/R<6$. This first stage deliberately explores a wide set of altitude histories: it establishes the global scale and decay of the interaction without assuming in advance that the most useful data must come from the smallest admissible clearance, and it verifies the response of the evolving DT over the complete safe operating range.',
             r"Starting from the baseline record, twelve information-oriented records $\pi_{\mathrm{INF}}^{(n)}$ are added to "
             r"the cumulative dataset. Ten were designed in this campaign in four batches, the last of which kept a single "
             r"policy. Six span the broad range $0.5\leq z/R\leq6$ of the reference, and four the near-wall range "
             r"$0.3\leq z/R\leq1.5$. The other two "
             r"are near-wall records of an earlier campaign at $z^\ast/R=1$ and $v_x^\ast/v_h=0.091$ and $0.102$, of which "
             r"only the mean trajectories are available. The broad stage explores a wide set of clearance histories. It "
             r"establishes the global scale and decay of the interaction without assuming that the most useful data come "
             r"from the smallest admissible clearance, and it tests the evolving DT over the whole admissible range."),
            (r"By the end of the sixth information-oriented episode, new policies in the broad domain still increase the cumulative Fisher information, but their marginal E-optimal contribution has become modest compared with the first information-oriented interaction. This behavior is physically consistent with Eq.~\eqref{eq:fge}: at larger clearances,",
             r"In the post-campaign evaluation of Section~\ref{sec:results-inf}, the broad-domain episodes after the first "
             r"still increase the cumulative Fisher information, but each adds much less than the first did. This agrees "
             r"with Eq.~\eqref{eq:fge}. At larger clearances,"),
            (r"The admissible design domain is therefore restricted to $0.5<z/R<1.5$ for the remaining six policies, defining the near-wall domain. The restriction is an adaptive design decision, not a rejection of the broad-domain data. All preceding episodes",
             r"After the sixth episode, the design domain of the reference is restricted to $0.3\leq z/R\leq1.5$, the "
             r"near-wall domain. "
             r"All preceding episodes"),
            (r"After every flight, the new record is appended to the cumulative dataset and the identification is warm-started from the preceding converged coefficients.",
             r"During the campaign, the model was updated after each batch. In the post-campaign identification of "
             r"Section~\ref{sec:results-inf}, the records are appended one at a time, and each fit is warm-started from the "
             r"preceding estimate.")])

card(G, 'Identification loss: the error, its window and its samples', grade='A',
     remarks=rk('IIC-10', 'Code-fit', 'Code-C6'),
     why='The error e_z is never defined, and the loss is said to use "the positions encountered during the flight". In '
         'the code both errors are clearances relative to the nominal clearance, and only the samples above the obstacle '
         '(2.20 to 3.01 m) enter the fit. That the post-edge response is not fitted matters later, where the DT misses the '
         'undershoot after the trailing edge.',
     sources=code(L['Code-fit'],
                  'The DT reference is the nominal clearance; the recorded Δz is replayed inside the controller '
                  '(`jDT/simulator.py:212-225`; `adjoint_identification.py:715-719`).'),
     edits=[('For physical episode $n$, the experimental record provides the measured altitude-tracking error, the deployed reference policy, and the reconstructed initial condition. The DT replays the same episode with the current model parameters $\\boldsymbol{\\theta}_p$. The experimental and virtual error histories are evaluated at the same $K_n$ spatial positions encountered during the flight and collected in the vectors',
             r"For physical episode $n$, the record provides the deployed reference and the measured clearance error "
             r"$e_{z,n}^{\bullet}(x)=z(x)-z^\ast$. The DT replays the same episode with the current model parameters "
             r"$\boldsymbol{\theta}_p$ and gives the corresponding error $e_{z,n}^{\circ}(x;\boldsymbol{\theta}_p)$. Both are "
             r"evaluated at the $K_n$ samples of the measured record above the obstacle, $2.20\leq x\leq3.01$~m, and "
             r"collected in the vectors")])

card(G, 'Identification: Adam reference, bounds, minimum steps, cold start', grade='B',
     remarks=rk('IIC-24', 'IIC-25', 'Code-C6', 'Code-C10', 'L-Uncited', 'GPT-11'),
     why='Adam is uncited; the admissible set Θ is never given; the 100-step minimum is not stated. A cold start from (0, 0) '
         'on the complete dataset reaches the same coefficients as the warm-started sequence, which answers a question a '
         'referee will ask about local minima. Ljung (already in the bibliography, uncited) goes at the curvature-based '
         'uncertainty.',
     sources=code(L['Code-C10'], '`adjoint_identification.py:120-122,761-766`: P_MIN, P_MAX = 0.0, 6.0; '
                  'A ≥ −0.95·0.5^p, so that f_GE ≥ 0.05 at z = 0.5R. `:133` CONVERGENCE_MIN_ITERATIONS = 100.'),
     extra=bib('Kingma2015'),
     edits=[(r"Adam uses this gradient to update the parameters over successive optimization steps.",
             r"Adam~\cite{Kingma2015} uses this gradient to update the parameters over successive optimization steps."),
            (r"where $\eta$ is the chosen learning rate, $\epsilon$ prevents division by zero, and $\Pi_{\Theta}$ keeps the solution inside the physically admissible set $\Theta$.",
             r"where $\eta$ is the learning rate, $\epsilon$ prevents division by zero, and $\Pi_{\Theta}$ projects onto the "
             r"admissible set $\Theta=\{0\leq p\leq6,\ A\geq-0.95\,(0.5)^{p}\}$, which keeps $f_{\mathrm{GE}}\geq0.05$ for "
             r"$z_i\geq0.5R$."),
            (r"The optimization is considered converged only when all three conditions remain satisfied over a complete monitoring window.",
             r"The optimization is considered converged only when all three conditions remain satisfied over a complete "
             r"monitoring window, after at least 100 steps."),
            (r"while the Adam moments are reset because the cumulative objective has changed.",
             r"while the Adam moments are reset because the cumulative objective has changed. A cold start from "
             r"$(A,p)=(0,0)$ on the complete dataset converges to $(0.120,1.970)$, against $(0.121,1.980)$ with warm "
             r"starts."),
            (r"Local parameter uncertainty is approximated from the curvature of the identification loss.",
             r"Local parameter uncertainty is approximated from the curvature of the identification "
             r"loss~\cite{Ljung1999}.")])

card(G, 'Parameter uncertainty: a curvature indicator, not a covariance (decision)', grade='A',
     flags=['Linked: [[t:Analyses on existing data]]'],
     remarks=rk('R1-1', 'R2-6', 'DA-6', 'GPT-7', 'GPT-10', 'Code-C20'),
     why='Three seats and the GPT review read Eq. (parameter-covariance) as mis-scaled: J_p is a mean over episodes and '
         'samples, so the indicator does not shrink as data are added. Read at face value, the final marginal 2σ intervals '
         'of A and p both include zero, and at z/R = 1 the band on f_GE is wider than the augmentation f_GE − 1. The text '
         'already says it is not a confidence region, but "improved confidence" and "well constrained" remain.',
     suggestion='(a) Call Σ_θ a curvature-based indicator throughout, compare its values between stages only, and drop '
                '"confidence" and "well constrained" (round 2, edit cards).\n(b) In addition, replace it by an uncertainty '
                'that has a scale: a refit of A and p leaving one episode out at a time, or a bootstrap over episodes '
                '(13 refits in the DT, no flights). I can run this from the code for round 2.\n(c) Keep as is.\n'
                'Apply = (a) and (b). For (a) only, say so in the note. Keep as is = (c).')

card(G, 'Two overfull equations', grade='C',
     remarks=[remark('Compile', 'Baseline compile', 'Overfull \\hbox (52.39pt too wide) in paragraph at lines 651--651; '
                     'Overfull \\hbox (20.26pt too wide) in paragraph at lines 717--717.', 'main.log')],
     why='The covariance and the reward equations run into the margin. Both are split over two lines; nothing else changes.',
     edits=[('\\boldsymbol{\\Sigma}_{\\theta}\\simeq\n \\max\\!\\left[J_p(\\widehat{\\boldsymbol{\\theta}}_p),10^{-12}\\right]\n \\mathbf Q\\operatorname{diag}\\!\\left[\n \\max(\\lambda_1,\\lambda_H)^{-1},\n \\max(\\lambda_2,\\lambda_H)^{-1}\n \\right]\\mathbf Q^{\\mathsf T}.',
             "\\begin{split}\n"
             " &\\boldsymbol{\\Sigma}_{\\theta}\\simeq\n"
             " \\max\\!\\left[J_p(\\widehat{\\boldsymbol{\\theta}}_p),10^{-12}\\right]\\mathbf Q\\\\\n"
             " &\\quad\\times\\operatorname{diag}\\!\\left[\n"
             " \\max(\\lambda_1,\\lambda_H)^{-1},\n"
             " \\max(\\lambda_2,\\lambda_H)^{-1}\n"
             " \\right]\\mathbf Q^{\\mathsf T}.\n"
             " \\end{split}"),
            ('J_{\\mathrm{trk}}(\\pi)=\\frac{1}{N_{\\mathcal R}}\n \\sum_{x_k\\in\\Omega_{\\mathcal R}}\n \\left[\\frac{z_k-z_{\\mathrm{BL}}(x_k)}{R}\\right]^2,\n \\qquad\n \\mathcal{R}(\\pi)=1-J_{\\mathrm{trk}}(\\pi).',
             "\\begin{split}\n"
             " J_{\\mathrm{trk}}(\\pi)&=\\frac{1}{N_{\\mathcal R}}\n"
             " \\sum_{x_k\\in\\Omega_{\\mathcal R}}\n"
             " \\left[\\frac{z_k-z_{\\mathrm{BL}}(x_k)}{R}\\right]^2,\\\\\n"
             " \\mathcal{R}(\\pi)&=1-J_{\\mathrm{trk}}(\\pi).\n"
             " \\end{split}"),
            (r"Thus, $A$ and $p$ may retain a strongly elongated and correlated local uncertainty region even when the resulting ground-effect curve is tightly constrained. The quantity",
             r"The quantity")])

card(G, 'Information design as flown: the batch rule behind Eq. (e-optimal-design)', grade='A',
     flags=['Linked: [[t:E-optimal design in II-A]]'],
     remarks=rk('N8', 'GPT-9', 'GPT-8', 'R1-5', 'R1-6', 'IIC-11', 'IIC-28'),
     why='Eq. (e-optimal-design) adds each candidate to the information of past experiments, but the design code never forms '
         'that sum: it selects three policies per batch, ranks by the information of each candidate, filters by novelty '
         'with respect to the measured trajectories, and checks a 0.3R clearance and no actuator limit. The card keeps the '
         'equation as the idealized criterion and states the rule that was flown. This also explains why the broad domain '
         'did not find the low-clearance designs on its own (R1-5). The sentence saying that F_1:N is evaluated during the '
         'design goes, since the matrix was formed only after the campaign.',
     sources=code('`informative_policy.py:312-603`: 68 candidates (64 scrambled Sobol points, seed 17, plus 4 shapes); '
                  'screening |v_z,ref| ≤ 0.5 m/s, |a_z,ref| ≤ 2 m/s², finite rollout to 4.0 m, lowest-rotor clearance ≥ 0.3R. '
                  'Mission 1: top 30% by λ_min of the candidate\'s own F, the half of that pool with the highest GE novelty, '
                  'then the maximum λ_min. Mission 2: λ_min(F_mission1 + F_candidate). Mission 3: maximum post-exit '
                  'novelty (≥ 0.30R) subject to information gates. Fisher averaged over up to 5 sigma-point samples. '
                  '"No accumulated F_{1:N} of past experiments is ever formed."'),
     edits=[('Since spatial residuals can remain correlated, this matrix is used as a comparative design metric rather than as an exact statistical Fisher matrix. During sequential design it is evaluated with the current converged DT. For the post-campaign comparison reported later, every episode and the repeated-baseline counterfactual are reevaluated using the final DT, final parameter scaling, and the same residual variance, so their cumulative values are directly comparable.',
             r"Since spatial residuals can remain correlated, this matrix is a comparative metric rather than an exact "
             r"statistical Fisher matrix. It is evaluated after the campaign, for every episode and for the repeated-baseline "
             r"counterfactual, with the final DT, the final parameter scaling, and the same residual variance, so that the "
             r"cumulative values are directly comparable."),
            ('which selects the safe candidate predicted to increase the Fisher information along its weakest direction. The criterion already favors sensitivities that complement the accumulated dataset. A separate novelty check may nevertheless select a slightly less informative candidate when its predicted response is sufficiently different from the experiments already performed. Candidates that violate state, reference-rate, acceleration, actuator, or clearance constraints are discarded before deployment.',
             r"which is the idealized criterion. The campaign used a batch approximation of it. Each design iteration "
             r"produced three policies from 68 candidates, 64 scrambled Sobol points and four structured shapes. The "
             r"candidates were screened in the DT for reference rate ($|v_z|\leq0.5$~m/s), reference acceleration ($|a_z|\leq2$~m/s$^2$), completion of "
             r"the rollout, and a lowest-rotor clearance of at least $0.3R$. The first policy maximizes $\lambda_{\min}$ of "
             r"its own predicted Fisher matrix among the most novel half of the $30\%$ most informative candidates, where "
             r"novelty is the distance of the predicted response from the measured trajectories. The second maximizes "
             r"$\lambda_{\min}$ of the joint matrix with the first, and the third maximizes the novelty of the predicted "
             r"response after the trailing edge, subject to minimum information levels. The predicted Fisher matrices are "
             r"averaged over up to five sigma-point samples of $\boldsymbol{\theta}_p$. The accumulated information "
             r"$\mathbf F_{1:N}$ of past experiments is not used in the design, where past trajectories enter through the "
             r"novelty filter.")])

card(G, 'Model-based policy: what is computed offline and how it is flown', grade='A',
     remarks=rk('EIC-6', 'R2-8', 'R3-8', 'Code-flight', 'Cut-C5', 'IIC-12', 'IIC-30'),
     why='"Reference governor" names, in control, an online add-on that enforces constraints, and "model predictive control" '
         'a receding-horizon optimizer; neither is what the paper does, and the text needs a sentence to say so. The policy '
         'is a reference correction computed offline. It is not a lookup table onboard either: the ground station '
         'interpolates it at the measured position and sends the corrected setpoint every 20 ms.',
     sources=code(L['Code-flight']),
     edits=[('After identification, $A$ and $p$ are frozen and the specialized performance loop uses the converged DT to improve altitude tracking across the finite obstacle. The control policy is implemented as a spatial reference governor above the unchanged cascaded PID controller, so the computationally expensive prediction and optimization remain offline while the deployed policy is a lightweight lookup table. First the DT produces the model-based policy $\\pi_{\\mathrm{MB}}$; physical rewards around that policy then train the reward-transfer surrogate used by Expected Improvement to design improved policies. The policy is the spatial altitude reference supplied to the governor,',
             r"After identification, $A$ and $p$ are frozen, and the DT is used to improve altitude tracking across the "
             r"obstacle. The policy is a spatial reference correction, computed offline. During the flight, the ground "
             r"station interpolates it at the measured streamwise position and sends the corrected altitude setpoint "
             r"$z_{\pi}$ to the unchanged cascaded PID controller,"),
            (r"The governor modifies only the vertical set point as a function of measured longitudinal position.",
             r"The correction modifies only the vertical setpoint, as a function of the measured streamwise position."),
            (r"This spatial representation is preferred over the time representation as it prevents small DT-experiment timing differences from desynchronizing the anticipatory command from the obstacle.",
             r"A spatial rather than temporal parameterization prevents small timing differences between DT and experiment "
             r"from shifting the anticipatory command relative to the obstacle."),
            (r"The model-based policy is first obtained through model-predictive reference synthesis. The model-based policy $\pi_{\mathrm{MB}}$ is obtained from a finite-horizon",
             r"The model-based policy $\pi_{\mathrm{MB}}$ is obtained offline from a finite-horizon"),
            (r"PID states, and reference governor over the entire prediction interval.",
             r"PID states, and reference correction over the entire prediction interval."),
            (r"The optimized policy is therefore computed before the flight and then executed online as a lightweight interpolation table. In this work, \emph{model predictive control} refers to this model-predictive reference synthesis; a receding-horizon optimizer is not run onboard.",
             r"No optimization runs during the flight.")])

card(G, 'Model-based objective: nodes, mean squares, window and optimizer', grade='B',
     remarks=rk('N7', 'GPT-reg', 'IIC-31', 'IIC-32', 'EIC-7'),
     why='In the code the reference has 81 nodes 25 mm apart (1.09R) over 2.00 to 4.00 m, the penalties are means, not sums, '
         'and the tracking term inside J_MB runs to 4.00 m, while the reward of Eq. (reward) stops at 3.70 m. The equation '
         'now matches, which also makes the weights independent of the grid. The Adam settings were missing. "Enforces '
         'safety" becomes what the term does.',
     sources=code('`next_mission_design/model_based_policy.py:54,64-65,88-112,232-285,304-331`: 81 nodes on 2.00–4.00 m, '
                  'Δz = 0 outside; |Δz| ≤ 3R; amplitude = mean over 81 nodes, curvature = mean over 79 second differences, '
                  'clearance = mean over samples above the obstacle; J_trk over 2.20–4.00 m; Adam 150 iterations, learning '
                  'rate 1e-3, β = (0.9, 0.999), from Δz = 0, no convergence test.'),
     edits=[(r"the reference correction is parameterized at control points separated by one rotor radius, $\Delta x=R$, over the complete crossing and interpolated between consecutive points.",
             r"the reference correction is parameterized at $N_x=81$ nodes spaced by $25$~mm ($1.09R$) over "
             r"$2.00\leq x\leq4.00$~m, linearly interpolated between them, and zero outside this interval."),
            ('J_{\\mathrm{MB}}=&\\;J_{\\mathrm{trk}}\n +0.10\\left\\|\\frac{\\Delta z_{\\pi}}{R}\\right\\|_2^2\n +2.0\\left\\|\\mathbf{D}^2\\frac{\\Delta z_{\\pi}}{R}\\right\\|_2^2 \\notag\\\\\n &+10^5\\Phi_{\\mathrm{clr}}(\\pi),',
             "J_{\\mathrm{MB}}=&\\;J_{\\mathrm{trk}}\n"
             " +\\frac{0.10}{N_x}\\left\\|\\frac{\\Delta z_{\\pi}}{R}\\right\\|_2^2 \\notag\\\\\n"
             " &+\\frac{2.0}{N_x-2}\\left\\|\\mathbf{D}^2\\frac{\\Delta z_{\\pi}}{R}\\right\\|_2^2\n"
             " +10^5\\Phi_{\\mathrm{clr}}(\\pi),"),
            ('where $\\mathbf{D}^2$ is the spatial second-difference operator and $\\Phi_{\\mathrm{clr}}$ is the mean squared violation of the $0.5R$ minimum clearance of the lowest rotor while it is above the obstacle. The amplitude term limits control authority, the curvature term suppresses spatially sharp commands, and the clearance term enforces safety on the tilted rotor geometry rather than only on the vehicle center of mass. The final policy is replayed once more in the DT and rejected if the hard clearance check fails.',
             r"where $J_{\mathrm{trk}}$ is evaluated over $2.20\leq x\leq4.00$~m, $\mathbf{D}^2$ is the second-difference "
             r"operator on the nodes, and $\Phi_{\mathrm{clr}}$ is the mean squared violation of the $0.5R$ minimum "
             r"clearance of the lowest rotor while the vehicle is above the obstacle. The amplitude term limits control "
             r"authority, the curvature term suppresses spatially sharp commands, and the clearance term applies the $0.5R$ "
             r"limit to each tilted rotor rather than only to the center of mass. Adam runs for 150 iterations with "
             r"learning rate $10^{-3}$, starting from $\Delta z_{\pi}=0$. The final policy is replayed once more in the DT "
             r"and rejected if the hard clearance check fails.")])

card(G, 'Reward: the evaluation window, the samples and the DT reward', grade='A',
     remarks=rk('N3', 'IIC-13', 'GPT-reward'),
     why='Eq. (reward) is the paper\'s central metric, and N_R, Ω_R and z_k are undefined. In the code the window is 2.20 to '
         '3.70 m, the samples are those of the repetition-averaged trajectory (about 42 at the nominal condition), and the '
         'DT reward replays the same samples with the final coefficients. Every reward in Secs. III-C and III-D follows '
         'this definition.',
     sources=code('`next_mission_design/expected_improvement_policy.py:69,72,260-274` (RT_REWARD_END_M = 3.70), used in '
                  '`replay_rows`; the plotted reward axes are R = 1 − J (`paper/pp_paper.py:1271-1273`). Recomputed: BL '
                  'R∘ = 0.676, R• = 0.544; MB 0.968, 0.855; EI_09 0.978, 0.952 (match Fig. 14).'),
     edits=[(r"Performance is evaluated against the original mission reference used by the nominal cascaded PID controller. The tracking cost and corresponding reward are",
             r"Performance is measured against the nominal reference $z_{\mathrm{BL}}=z^\ast$. The clearance $z_k$ is taken "
             r"from the repetition-averaged trajectory at the $N_{\mathcal R}$ samples $x_k$ in the window "
             r"$\Omega_{\mathcal R}=[2.20,3.70]$~m ($21.7\leq x/R\leq87.0$), with $N_{\mathcal R}\simeq42$ at the nominal "
             r"condition. DT rewards are evaluated at the same samples by factual replay with the final coefficients. "
             r"The tracking cost and reward are")])

card(G, 'Which model designed the flown π_MB (decision)', grade='A',
     remarks=rk('N7'),
     why='The text says π_MB was optimized with the final identified DT (here and in the Introduction, Sec. II-A and '
         'Sec. III-C). The records say otherwise: the flown π_MB carries identification iteration 006, the generator uses '
         'the coefficients (A, p) = (0.230, 3.136) labeled "historical first-identification model", and the final '
         'coefficients come from a post-campaign replay. Re-optimizing with either set gives nearly the same shape (0.04R '
         'RMS apart), so the results hold; the sentence does not.',
     sources=code('`model_based_policy.py:46-52`: GE_COEFFICIENT_SOURCE = "manual", (A, p) = (0.230416, 3.136230), '
                  '"historical first-identification model ... used to design the original It3 policy"; comments say It6 was '
                  'designed with a "robust envelope" (ROBUST_MB_POLICY = False now). EXP_MB metadata: identification_iteration '
                  '"iteration_006". Re-optimization with the current code: manual set and final set differ by 0.04R RMS '
                  'after amplitude scaling; both are 10–15% larger than the flown reference.'),
     suggestion='(a) Replace "The reported policy is optimized with the single final identified DT; no model-uncertainty '
                'ensemble is used." by: "The flown $\\pi_{\\mathrm{MB}}$ was optimized with the coefficients identified '
                'during the campaign, $(A,p)=(0.230,3.14)$, and was not re-optimized after the final identification; '
                're-optimizing it with the final coefficients changes the reference by $0.04R$ RMS after amplitude scaling. '
                'All DT rewards reported here are recomputed with the final coefficients." Say in the note whether a '
                'model-uncertainty envelope was used; I align the Introduction, Sec. II-A, Sec. III-C and the off-nominal '
                'policies (same iteration 006) in round 2.\n(b) The record is wrong and the final coefficients were used: '
                'say so, and the text stays.\n(c) Re-optimize π_MB with the final model and fly it again (new flights).\n'
                'Apply = (a). Keep as is = (b).')

card(G, 'Performance phase: the Sobol library, the seven policies flown, ten EI policies', grade='A',
     remarks=rk('IIC-14', 'IIC-33', 'N11', 'EIC-3', 'R1-9'),
     why='The library has 2048 points, not 2000. The number of EI policies, ten, is never given, although it is the data '
         'that "a few evaluations" refers to. How the seven Sobol policies were chosen is not in the code; the text of '
         'Sec. III-D says they span different amplitude combinations, which this sentence now repeats. If they were chosen '
         'by hand, say so in the note.',
     sources=code('`expected_improvement_policy.py:58,63,620-640`: 2048 = 2¹¹ scrambled Sobol points, seed 17. EI_01–EI_10 '
                  'at the nominal condition; π_EI★ = EI_09. No code selects ALPHA_01–07; their coefficient vectors look '
                  'hand-designed (ALPHA_04 ≈ 0.44 e_B, ALPHA_05 ≈ 0.36 e_C).'),
     extra=bib('Owen1998'),
     edits=[('A scrambled Sobol library of 2000 coefficient vectors is screened in the DT, and seven admissible, mutually distinct policies $\\pi_{\\mathbf a,i}$ are deployed to train the local GP discrepancy. Subsequent policies $\\pi_{\\mathrm{EI},i}$ are selected sequentially by Expected Improvement; after each flight, the physical reward is appended to the reward-transfer surrogate dataset.',
             r"A scrambled Sobol library~\cite{Owen1998} of $2048$ coefficient vectors is screened in the DT, and seven "
             r"admissible policies $\pi_{\mathbf a,i}$, chosen to span different amplitude combinations, are flown to train "
             r"the GP discrepancy. Ten policies $\pi_{\mathrm{EI},i}$ are then selected by EI and flown, and each physical "
             r"reward is added to the surrogate dataset.")])

card(G, 'Basis functions: defined in Methods, with widths and units', grade='B',
     flags=['Linked: [[t:Local exploration around]]'],
     remarks=rk('IIC-15', 'IIID-3', 'N11', 'GPT-1', 'R1-9', 'R3-10'),
     why='The basis appears only in Results, without widths, and "centered on the model-based reference" leaves open '
         'whether it is a position or a shape. The definition moves here from the code, and a_j becomes a peak amplitude in '
         'rotor radii, which settles the units questioned by the GPT review. The purpose sentences repeat II-A.',
     sources=code('`expected_improvement_policy.py:84-89,204-213`: Gaussian centers 2.50, 2.95, 3.30 m (x/R = 34.8, 54.3, 69.6 '
                  'in the shifted coordinate), σ = 0.25, 0.20, 0.25 m, each multiplied by sin²[π(x − 2.00)/2.00] and '
                  'normalized to unit peak; Δz = Δz_MB + R B a; box −1 ≤ a_j ≤ 1.'),
     edits=[(r"Physical rewards are then used to refine this model-based policy and compensate for the remaining model discrepancy. Reinforcement Twinning uses these measurements to correct the local policy ranking predicted by the DT. A new candidate is written as",
             r"A candidate policy is written as"),
            ('where the smooth basis functions $\\mathbf{b}(x)$ span the control-relevant portions of the mission and $\\mathbf a=[a_A,a_B,a_C]^\\top$ is the bounded vector of policy-modification coefficients. A space-filling library is first evaluated in the DT; the same reference and rotor-clearance checks used for the MB solution define the admissible set $\\mathcal A_{\\mathrm{safe}}$.',
             r"where $\mathbf a=[a_A,a_B,a_C]^\top\in[-1,1]^3$ and $\mathbf{b}(x)$ holds three basis functions. Each is a "
             r"Gaussian centered at $x=2.50$, $2.95$, and $3.30$~m ($x/R\simeq35$, $54$, and $70$ in the shifted coordinate "
             r"of the figures), with standard deviation $0.25$, $0.20$, and $0.25$~m. It is multiplied by "
             r"$\sin^2[\pi(x-x_0)/L]$, with $x_0=L=2.00$~m, and normalized to unit peak, so that $a_j$ is a peak amplitude "
             r"in rotor radii. The reference and rotor-clearance checks used for $\pi_{\mathrm{MB}}$ define the admissible set "
             r"$\mathcal A_{\mathrm{safe}}$."),
            ('In the present work, local corrections are generated from three Gaussian basis functions centered on the model-based reference at $x/R\\simeq35$, $54$, and $70$. The first two centers, denoted by A and B, lie above the obstacle, whereas C acts on the downstream recovery. Each basis has one bounded amplitude, so that $\\mathbf a=[a_A,a_B,a_C]^\\top$ completely specifies the local departure from $\\pi_{\\mathrm{MB}}$, with $a_A,a_B,a_C\\in[-1,1]$.',
             r"The basis centers A and B lie above the obstacle and C downstream of it (Fig.~\ref{fig:sobol}).")])

card(G, 'Surrogate settings as implemented, and the EI candidate set', grade='B',
     remarks=rk('N6', 'GPT-1', 'GPT-2', 'GPT-4', 'IIC-16', 'IIC-34', 'IIC-35', 'IIC-17'),
     why='"Scaled by 0.30R" mixes a length with a dimensionless coefficient; the code uses a length scale of 0.30 in each '
         'a_j. The signal variance is set, not initialized, and no hyperparameter is optimized. "Cleaned" mean trajectories '
         'are the repetition averages. The candidates over which EI is maximized were never stated; the GPT review asks for '
         'them because a fixed library can exclude better policies. Two sentences that repeat II-A go.',
     sources=code('`expected_improvement_policy.py:97,242-246,303-337,918-942,1037-1040`: feature = a/0.30; signal = '
                  'max(var(residual), 0.05²), fixed; noise = 0, jitter 1e-8; ξ = 0; incumbent = best measured reward; '
                  'variance floored at 1e-8; candidates: 2048 Sobol points, 6 axis seeds at ±0.25, the projected historical '
                  'coordinates, 128 Gaussian moves (σ = 0.10) around the four best; admissible if the DT lowest-rotor '
                  'clearance ≥ 0.5R; one maximizer per run.'),
     edits=[('At the nominal operating condition, its input is the three-component vector $\\mathbf a$, with each coordinate scaled by $0.30R$. The signal variance is initialized from the empirical variance of the affine residuals and is bounded below by $0.05^2$. The rewards are computed from the cleaned mean trajectories and are treated as deterministic campaign observations;',
             r"At the nominal operating condition, its input is $\mathbf a$, with a length scale of $0.30$ in each "
             r"coordinate. The signal variance is set to the empirical variance of the affine residuals, with a lower bound "
             r"of $0.05^2$, and no hyperparameter is optimized. The rewards are computed from the repetition-averaged "
             r"trajectories and are treated as deterministic observations;"),
            (r"Two policies with similar DT performance can receive different physical corrections. Its posterior mean and variance are updated after every performance-oriented episode.",
             r"The posterior mean and variance of $\delta$ are updated after every performance-oriented episode."),
            ('with zero improvement assigned to a vanishing posterior variance. The first term exploits candidates with a high predicted physical reward, whereas the second rewards unresolved but potentially useful regions. The model-based policy remains the reference throughout the search; data are used to learn the GP discrepancy that affects physical performance.',
             r"with the posterior variance floored at $10^{-8}$. EI is maximized over the Sobol library, six points at "
             r"$\pm0.25$ on the axes, the coefficients of the policies already flown, and 128 Gaussian perturbations "
             r"($\sigma=0.10$) of the four best, all screened in the DT.")])

card(G, 'Transfer rule: what scales with the local model-based correction', grade='A',
     remarks=rk('N5', 'GPT-1', 'IIC-18', 'IIIE-1'),
     why='Eq. (rt-policy) is additive, so the same coefficients give the same altitude offset at every condition, and the '
         'claim that the correction "is reduced automatically" does not follow. The code does something else: it scales '
         'each coefficient by the ratio of the local amplitudes of the two model-based corrections. The card writes that '
         'rule here and gives its numbers in Sec. III-E. At (1, 0.113) the transferred coefficients leave the box [−1, 1]³.',
     sources=code('`next_mission_design/transfer_calibration.py:200-223,431-439`: a★ = argmin‖b(x)ᵀa − (Δz_EI★ − Δz_MB)/R‖² '
                  '= (−0.664, +0.699, +0.200); m_j(Δz) = [Σ_k b_j(x_k)(Δz(x_k)/R)² / Σ_k b_j(x_k)]^½; s_j = '
                  'm_j(Δz_MB^χ)/m_j(Δz_MB^nom); a_j^tr = s_j a★_j. s = (0.407, 0.527, 0.428) at (2.5, 0.045), '
                  '(1.845, 1.508, 1.604) at (1, 0.113). The flown transferred references match this rule within 0.03R and '
                  '0.10R; with unscaled a★ the deviation would be 0.34R and 0.49R.'),
     edits=[(r"Policy coordinates are defined relative to the local MB deformation. Consequently, a correction learned where the model-based action is large is reduced automatically when the local MB solution requires little intervention, rather than being transferred as a fixed altitude offset.",
             r"To transfer a policy, each coefficient is scaled by the ratio $s_j$ of the root-mean-square amplitude of the "
             r"condition-specific model-based correction to that of the nominal one, both weighted by $b_j$, "
             r"$a_j^{\mathrm{tr}}=s_j a_j^{\star}$, where $\mathbf a^{\star}$ holds the coefficients of "
             r"$\pi_{\mathrm{EI}}^{\star}$. A correction learned where the model-based correction is large is "
             r"therefore reduced where the local model-based correction is small, rather than being transferred as a fixed "
             r"altitude offset."),
            (r"The nominal best correction is then transferred by applying the same three coefficients $\mathbf a=[a_A,a_B,a_C]^\top$ relative to the condition-specific model-based policy. This scaling preserves the learned correction structure without imposing the nominal reference correction as a fixed altitude offset.",
             r"The nominal best correction, $\mathbf a^{\star}=[-0.66,0.70,0.20]^{\mathsf T}$, is then transferred with the "
             r"scaling of Section~\ref{sec:performance-phase}, with $\mathbf s=[0.41,0.53,0.43]^{\mathsf T}$ at "
             r"$(2.5,0.045)$ and $[1.85,1.51,1.60]^{\mathsf T}$ at $(1,0.113)$.")])

card(G, 'Generalization paragraph in II-C', grade='B',
     remarks=rk('IIC-19', 'IIC-20', 'IIC-37'),
     why='Removes the colon, says that the baseline policy is flown (not computed with the DT), and leaves the "not a '
         'converged surrogate" disclaimer to Sec. III-E and the Conclusions, where it already is. The same symbol π_EI★ '
         'names the nominal and the condition-specific best; a distinct symbol, for example π★_EI,χ, is your choice.',
     edits=[(r"Two off-nominal conditions are considered: $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and $(1,0.113)$. For each condition, a baseline policy $\pi_{\mathrm{BL}}$ and a model-based policy $\pi_{\mathrm{MB}}$ are computed with the frozen identified DT.",
             r"Two off-nominal conditions are tested, $(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and $(1,0.113)$. At each, the "
             r"baseline policy $\pi_{\mathrm{BL}}$ is flown, and a model-based policy $\pi_{\mathrm{MB}}$ is computed with "
             r"the frozen DT."),
            (r"These tests distinguish direct transfer of the nominal correction from a local, proof-of-concept extension of the RT search at a new operating condition; they do not constitute convergence of a surrogate over the full velocity-clearance domain.",
             r"These tests separate direct transfer of the nominal correction from a local RT search at a new operating "
             r"condition.")])

# ================================================================ III-A
G = 'III-A. Baseline response'
card(G, 'Number of repetitions: three, not five', grade='A',
     remarks=rk('N1', 'R1-11', 'GPT-15'),
     why='The mean trajectories of π_BL, π_MB and π_EI★ in Figs. 2 and 13 are averages of three flights, not five. The RMS '
         'is computed after aligning the repetitions at the leading-edge crossing and interpolating them on the samples of '
         'the first, which the formula now says.',
     sources=code('`EXP/CLEAN/EXP_BL_reward.json`, `EXP_MB_reward.json`, `EXP_EI_09_reward.json`: number_of_repetitions = 3, '
                  'written by `pp_EXP.py:620-636` from the raw files actually averaged. Alignment and interpolation: '
                  '`pp_EXP.py:268-316`.'),
     edits=[(r"obtained from five repetitions,", r"obtained from three repetitions,"),
            (r"At each streamwise position, this quantity is defined as $\mathrm{RMS}(x)=[N_r^{-1}\sum_{j=1}^{N_r}(z_j(x)-\overline z(x))^2]^{1/2}$, with $N_r=5$.",
             r"After the repetitions are aligned at the leading-edge crossing and interpolated on the samples of the first "
             r"one, this quantity is $\mathrm{RMS}(x)=[N_r^{-1}\sum_{j=1}^{N_r}(z_j(x)-\overline z(x))^2]^{1/2}$, with "
             r"$N_r=3$."),
            (r"over five repetitions.", r"over three repetitions."),
            (r"are obtained by averaging five repetitions of each case,", r"are averages of three repetitions of each case,")])

card(G, 'Baseline response: shorter, with the measured extremes', grade='B',
     remarks=rk('Cut-C14', 'IIIA-1', 'IIIA-3', 'IIIA-4', 'IIIA-5', 'N12'),
     why='The opening repeats the baseline paragraph of II-C, the colon and "markedly" go, and two values follow the data: '
         'the undershoot reaches z/R = 0.41, and the commanded clearance is recovered about 35R after the trailing edge. A '
         'question only you can answer, which a referee will ask: why does the vehicle settle at z/R ≈ 2 over the obstacle '
         'for 2.3 s despite the integral action? One sentence in the note and I add it.',
     sources=code('EXP_BL: maximum 2.56 at x/R = 32; mean 1.96 over the second half of the obstacle; minimum 0.41 at '
                  'x/R = 62.8; within 0.1R of 1.5 from x/R ≈ 91, i.e. ≈ 34R after the trailing edge.'),
     edits=[('The first experimental case employs only the cascaded PID controller available in the original Crazyflie firmware. The most direct target for this baseline crossing is a constant-clearance trajectory at $(z^\\ast/R,\\,v_x^\\ast/v_h)=(1.5,0.079)$. The desired trajectory is therefore the straight horizontal line denoted by $\\pi_{\\mathrm{BL}}$ and reported with a dashed line in Fig.~\\ref{fig:stage0}. This case establishes the performance baseline because the controller acts exclusively through feedback, without any anticipation of the approaching aerodynamic interaction.',
             r"Fig.~\ref{fig:stage0} shows the baseline crossing at the nominal condition, flown with the onboard cascaded "
             r"PID controller alone. The dashed line is the constant reference $\pi_{\mathrm{BL}}$. The controller acts only "
             r"through feedback, without anticipating the aerodynamic interaction."),
            (r"Before reaching the obstacle, the vehicle maintains an almost constant clearance close to the commanded value, supporting satisfactory tracking at this modest forward speed away from the surface interaction. The response changes markedly over the obstacle: the vehicle initially rises to approximately $z/R=2.5$ and subsequently settles around $z/R=2$.",
             r"Before the obstacle, the vehicle holds a nearly constant clearance close to the commanded value. Over the "
             r"obstacle, it first rises to about $z/R=2.5$ and then settles around $z/R=2$."),
            ('producing an undershoot down to approximately $z/R=0.5$. The vehicle then gradually recovers the commanded clearance, which is reached only about $40R$ downstream of the obstacle. Both excursions are substantially larger than the run-to-run dispersion, indicating a repeatable interaction rather than experimental scatter. The baseline experiment consequently provides the reference cost for all subsequent performance comparisons and the first factual record used during the information phase.',
             r"producing an undershoot down to about $z/R=0.4$. The vehicle then recovers the commanded clearance, to within "
             r"$0.1R$, about $35R$ downstream of the trailing edge. Both excursions exceed the run-to-run dispersion, so "
             r"they reflect a repeatable interaction rather than experimental scatter.")])

# ================================================================ III-B
G = 'III-B. Information phase'
card(G, 'Information phase: opening of III-B', grade='B',
     flags=['Linked: [[t:Information phase: the records]]'],
     remarks=rk('Cut-C17', 'IIIB-10', 'N8'),
     why='The two opening paragraphs restate the method of II-C and give the near-wall bound as 0.5R; the code uses 0.3R. '
         'They become one paragraph that introduces the figure. Two sentences further on restate the domain switch a third '
         'time, with the same wrong bound.',
     edits=[('Each information-oriented policy is constructed by fixing a set of longitudinal nodes and allowing the optimizer to modify the local vertical reference at those nodes. Interpolation between consecutive values produces the continuous reference $z_{\\pi}(x)$ deployed through the onboard PID controller. The longitudinal locations remain fixed, while the optimized nodal heights determine which clearances and altitude variations are requested during the crossing. The bounds of the design domain apply to this reference, not to the DT or physical vehicle trajectory, which can depart from it under the closed-loop dynamics.\n\nTwo consecutive design domains are used. The first six policies are generated in the \\emph{broad domain}, with the reference bounded within $0.5<z/R<6$, allowing the optimizer to explore a broad range of vertical excitations. After these six policies, the upper bound is reduced to $z/R=1.5$ for the remaining six episodes, defining the \\emph{near-wall domain}. The purpose of this restriction is to add information near the wall, where the ground-effect response is expected to be strongest and most sensitive to $A$ and $p$. Representative references and physical responses from both domains are reported in Fig.~\\ref{fig:informative-policies}. The broad-domain policies $\\pi_{\\mathrm{INF},1}$ and $\\pi_{\\mathrm{INF},6}$ request markedly different altitude histories across the obstacle, whereas the near-wall policy $\\pi_{\\mathrm{INF},9}$ concentrates the crossing at smaller clearances. The physical curves indicate the clearances actually traversed by the vehicle and are the trajectories used during factual replay and identification.',
             r"Each information-oriented reference is defined by its values at fixed streamwise nodes and interpolated "
             r"between them. The design domain bounds this reference, not the trajectory, which departs from it under the "
             r"closed-loop dynamics. The first six policies are designed in the \emph{broad domain}, $0.5\leq z/R\leq6$, and "
             r"the following ones in the \emph{near-wall domain}, $0.3\leq z/R\leq1.5$, where the ground-effect response is "
             r"strongest and most sensitive to $A$ and $p$. Fig.~\ref{fig:informative-policies} shows representative "
             r"references and trajectories. The broad-domain policies $\pi_{\mathrm{INF},1}$ and $\pi_{\mathrm{INF},6}$ "
             r"request different clearance histories across the obstacle, whereas the near-wall policy "
             r"$\pi_{\mathrm{INF},9}$ keeps the crossing at smaller clearances. These trajectories are the ones used in "
             r"factual replay and identification."),
            (r"The observed clearance coverage and the uncertainty remaining below $z/R=2$ motivate the restriction of the reference domain to $0.5<z/R<1.5$. The earlier records remain in the cumulative replay buffer; only the admissible references for the next designs are changed. This second stage",
             r"The near-wall stage")])

card(G, 'Parameter history: the first identification and the two domains', grade='B',
     remarks=rk('IIIB-1', 'IIIB-11', 'N2'),
     why='"Change substantially" becomes the values after the first identification, and the domains are named rather than '
         'restated with the wrong bound.',
     sources=code('`identification_output/Warm_start/E00/adjoint_results.npz`: A = 0.1036, p = 1.336.'),
     edits=[(r"Both coefficients are initialized with the Cheeseman-Bennett values, $A=1/16$ and $p=2$, and change substantially after the first adjoint identification, performed using only the baseline record in the gray region.",
             r"Both coefficients start from the Cheeseman-Bennett values and change to $A=0.104$ and $p=1.34$ after the "
             r"first identification, which uses only the baseline record (gray region)."),
            (r"The episodes designed with references in the broad domain $0.5<z/R<6$ occupy the olive region, while those using the near-wall domain $0.5<z/R<1.5$ occupy the green region.",
             r"Broad-domain episodes lie in the olive region and near-wall episodes in the green region.")])

card(G, 'Fisher proxy: what the comparison with the repeated baseline shows', grade='B',
     remarks=rk('GPT-8', 'R1-5', 'DA-4', 'IIIB-12'),
     why='The repeated baseline counts the same measured record again and again, so it measures repeated-design information '
         'under independent noise, not new experiments, and "more information" overstates a score computed with the final '
         'model. The comparison stays; its wording says what it is.',
     edits=[(r"The latter repeats the same measured baseline episode at $0.35$~m/s, including its sampling and residual level, for the same number of cumulative interactions.",
             r"The latter counts the measured baseline episode once per cumulative episode, with its sampling and residual "
             r"level, so that it measures repeated-design information under independent noise rather than new "
             r"experiments."),
            (r"The designed episode therefore provides more than one order of magnitude more information along the weakest direction.",
             r"Under the adopted local scaling, the design score of the designed episode is therefore more than ten times "
             r"larger along the least-observed direction.")])

card(G, 'Correlation history, and the value 1.000', grade='B',
     remarks=rk('N2', 'IIIB-2', 'IIIB-3', 'IIIB-13', 'GPT-8'),
     why='The correlation does not decrease over the broad stage: it drops from 0.974 to 0.783 after the first informative '
         'episode, then rises to 0.883. ρ_A,p is defined. The value 1.000 is 0.9998, not a normalization; the GPT review '
         'asks which it is.',
     sources=code('ρ for E00–E12: 0.974, 0.783, 0.829, 0.848, 0.860, 0.857, 0.883, 0.860, 0.872, 0.847, 0.831, 0.822, 0.818. '
                  'λ_min after episode 7: 0.9998; no normalization in `pp_paper.py:587-652`.'),
     edits=[(r"Across the following broad-domain episodes, $\lambda_{\min}(\mathbf F)$ continues to increase, but with a much smaller slope, reaching $1.000$ after the sixth information-oriented policy.",
             r"Over the next five broad-domain episodes, $\lambda_{\min}(\mathbf F)$ rises only from $0.676$ to $1.000$. "
             r"This value is dimensionless and set by the scaling of Section~\ref{sec:information-phase}; it is not a "
             r"normalization."),
            ('The estimated parameter correlation starts at $\\rho_{A,p}=0.974$ for the baseline record and varies non-monotonically as new trajectories are added, reaching $0.883$ after the six broad-domain policies. The reduction supports the conclusion that the designed missions add a new sensitivity direction, but the remaining value is still high.',
             r"The correlation $\rho_{A,p}$ of $A$ and $p$, computed from $\boldsymbol{\Sigma}_{\theta}$, drops from $0.974$ "
             r"for the baseline record to $0.783$ after the first informative episode. It then rises to $0.883$ over the "
             r"remaining broad-domain episodes, as further broad-domain data mainly reinforce the same coupled direction."),
            (r"The parameter correlation decreases further to $\rho_{A,p}=0.818$, although it remains appreciable.",
             r"The correlation then decreases to $\rho_{A,p}=0.818$, which is still high.")])

card(G, 'Broad-domain law: its uncertainty in numbers', grade='B',
     remarks=rk('IIIB-4', 'IIIB-14', 'N12'),
     why='"Substantial local uncertainty" and "already small" become the values of the indicator. A disclaimer that repeats '
         'Sec. II-C goes.',
     sources=code('2σ_f/f after the broad stage (E06): 45% at z/R = 1, 9.9% at 1.5, 3.6% at 2.'),
     edits=[(r"It describes uncertainty in the total thrust factor rather than in the smaller augmentation $f_{\mathrm{GE}}-1$, and it is not an exact confidence interval. The olive",
             r"The olive"),
            (r"but this portion of the curve is still associated with substantial local uncertainty. Above approximately $z/R=2$, the indicator is already small because",
             r"but there the indicator is still $45\%$ at $z/R=1$. Above about $z/R=2$, it is below $4\%$ because")])

card(G, 'Near-wall stage: the λ_min increase and the two archived records', grade='A',
     flags=['Linked: [[t:Information phase: the records]]'],
     remarks=rk('N2', 'R1-5', 'DA-4'),
     why='A third of the increase after the switch comes from the two archived records, which were not designed in this '
         'campaign; a reader must know. The counterfactual at episode 13 counts the baseline 13 times, not 12.',
     sources=code('INF_11 and INF_12 add 0.403 and 0.330 to λ_min, i.e. 0.733 of the 2.242 gained after episode 7. '
                  '0.387 = 13 × 0.02979; twelve copies give 0.357.'),
     edits=[(r"and its cumulative value rises from $1.000$ to $3.242$. Twelve repetitions of the baseline would instead reach only $0.387$.",
             r"and its cumulative value rises from $1.000$ to $3.242$, of which $0.733$ comes from the two archived records. "
             r"Repeating the baseline record over the same 13 cumulative episodes would reach only $0.387$.")])

card(G, 'Why A and p stay correlated', grade='B',
     remarks=rk('GPT-ident', 'R1-8', 'IIIB-15'),
     why='Gives the two-line reason for the coupling, which the GPT review asks for and which also explains why records on '
         'both sides of z = R help. Removes the colon and "safely".',
     edits=[(r"This residual coupling follows from the structure of the selected power law and the range that can be explored safely: coordinated variations of $A$ and $p$ can generate very similar $f_{\mathrm{GE}}(z/R)$ curves.",
             r"This residual coupling follows from the power law and from the limited range of clearance that can be flown. "
             r"The sensitivities $\partial f_{\mathrm{GE}}/\partial A=(R/z)^p$ and "
             r"$\partial f_{\mathrm{GE}}/\partial p=A(R/z)^p\ln(R/z)$ are nearly proportional over a narrow range of "
             r"clearance, and the second vanishes at $z=R$ and changes sign across it. Coordinated variations of $A$ and $p$ "
             r"therefore produce nearly identical $f_{\mathrm{GE}}(z/R)$ curves.")])

card(G, 'Final law: numbers instead of "substantially", and the Crazyflie evidence', grade='B',
     remarks=rk('IIIB-6', 'IIIB-8', 'IIIB-9', 'R2-1', 'L-GE4'),
     why='"Moderately", "substantially" and "most important" become values. The amplitude of about twice 1/16 is what '
         'Carter et al. measured on a Crazyflie 2.0, which supports the result rather than making it a surprise; the '
         'domain seat expects that comparison. The static-law disclaimer is already in Sec. II-B.',
     sources=code('f_GE(1) = 1.218 (E06) and 1.121 (E12); 2σ_f/f from E06 to E12: 45% → 15% at z/R = 1, 9.9% → 4.3% at 1.5.'),
     extra=bib('Sharf2014'),
     edits=[(r"the final model changes only moderately at large clearance but differs substantially from the broad-domain estimate below $z/R=2$. The most important improvement in this region is the contraction of the relative uncertainty.",
             r"the final model is close to the broad-domain estimate above $z/R=2$ and differs from it below, with "
             r"$f_{\mathrm{GE}}=1.121$ instead of $1.218$ at $z/R=1$. In this region, the indicator "
             r"$2\sigma_{f_{\mathrm{GE}}}/f_{\mathrm{GE}}$ falls from $45\%$ to $15\%$ at $z/R=1$ and from $9.9\%$ to "
             r"$4.3\%$ at $z/R=1.5$."),
            ('The final coefficients differ substantially from the Cheeseman-Bennett initialization: the exponent returns close to two, but the identified amplitude is almost twice the classical value. This supports the value of a system-specific information phase when a low-order model is transferred from an isolated hovering rotor to a complete Crazyflie crossing a finite obstacle. It does not imply that the two-parameter law resolves every transient feature; it establishes a more representative static model over the range that can be tested safely.',
             r"The final exponent, $p=1.980$, is close to the Cheeseman-Bennett value $p=2$, whereas the amplitude, "
             r"$A=0.121$, is almost twice $1/16$. A ground effect stronger than the classical prediction has also been "
             r"measured on a tethered Crazyflie~2.0~\cite{Carter2021} and on a small multirotor~\cite{Sharf2014}. This "
             r"supports a system-specific information phase when a low-order model is transferred from an isolated hovering "
             r"rotor to a complete Crazyflie crossing a finite obstacle.")])

card(G, 'Baseline replay and the closing paragraphs of III-B', grade='B',
     remarks=rk('Cut-C6', 'IIIB-16'),
     why='The two closing paragraphs restate the subsection and defend the second stage ("still valuable"). They become two '
         'sentences that say what the replay shows. The colon and "nevertheless" go from the replay description.',
     edits=[(r"The model initialized with Cheeseman-Bennett predicts the qualitative trend: the increased thrust raises the vehicle above the obstacle, and the removal of that contribution produces a loss of altitude downstream. Its magnitude is nevertheless underestimated.",
             r"With the Cheeseman-Bennett coefficients, the DT predicts the rise over the obstacle and the loss of altitude "
             r"downstream, but underestimates both."),
            ('The broad-domain and final replays are already very similar for this baseline case. The near-wall episodes are still valuable because they improve the confidence and the local form of $f_{\\mathrm{GE}}$ where the interaction is strongest, but they produce only a small additional change in the replay of $\\pi_{\\mathrm{BL}}$. This result supplies the control-oriented stopping argument: the model obtained after the broad domain already reproduces the dominant response, and the combined dataset refines the uncertain near-wall portion without materially changing the DT prediction for the baseline mission.',
             r"The broad-domain and final replays of $\pi_{\mathrm{BL}}$ are nearly identical. The model obtained after the "
             r"broad domain therefore already reproduces the dominant baseline response, and the near-wall episodes refine "
             r"$f_{\mathrm{GE}}$ below $z/R=2$ without changing this replay."),
            ('Overall, the information phase replaces a generic ground-effect approximation with a model specialized to the tested vehicle and operating envelope. The broad-domain policies establish the global response, while the near-wall domain adds information and reduces uncertainty close to the wall. Further refinement would demand experiments with a smaller physical safety margin, whereas the objective of RT also requires the identified DT to be used for control improvement. The combination of stable coefficients, limited remaining correlation improvement, reduced near-wall uncertainty, and nearly unchanged baseline replay between the intermediate and final models therefore provides a practical and transparent justification for ending identification and proceeding to the model-based policy.',
             r"The information phase thus replaces the generic Cheeseman-Bennett law with a law identified for the tested "
             r"vehicle and clearance range.")])

# ================================================================ III-C
G = 'III-C. Model-based policy'
card(G, 'Model-based policy in Results: one sentence instead of the method', grade='B',
     flags=['Linked: [[t:Which model designed]]'],
     remarks=rk('Cut-C16', 'IIIC-1', 'IIIC-6'),
     why='The opening repeats Sec. II-C and names the wrong objective (the policy minimizes J_MB, not the tracking cost) and '
         'the wrong label. "With the final DT" is left out until [[t:Which model designed]] is decided.',
     edits=[('Once the information phase is completed, the identified GE parameters are frozen and the resulting DT is used to compute the model-based policy $\\pi_{\\mathrm{MB}}$. The objective is to exploit the DT, now augmented with the final identified ground-effect model, to construct an anticipatory vertical reference for the onboard cascaded PID controller. The reference is parameterized on a dense spatial grid with nodes separated by $\\Delta x\\simeq R$ and linearly interpolated between adjacent nodes. Their vertical coordinates are optimized by minimizing the tracking cost introduced in Section~\\ref{sec:performance-phase}, with respect to the nominal clearance $z^\\ast/R=1.5$ and subject to the prescribed safety constraints.\n\nThe comparison with the baseline policy is reported in Fig.~\\ref{fig:mb-optimum}. The constant reference $\\pi_{\\mathrm{BL}}$, executed through the built-in PID controller, can react to the aerodynamic interaction only after a tracking error has developed. By contrast,',
             r"Fig.~\ref{fig:mb-optimum} compares the baseline policy with the model-based policy $\pi_{\mathrm{MB}}$, "
             r"obtained by minimizing $J_{\mathrm{MB}}$ of Eq.~\eqref{eq:mb-objective}. Unlike the constant reference "
             r"$\pi_{\mathrm{BL}}$,")])

card(G, 'Model-based policy: measured extremes and rewards', grade='B',
     remarks=rk('IIIC-2', 'IIIC-3', 'IIIC-4', 'IIIC-7', 'N3', 'N12'),
     why='"Markedly" and "substantial" become the measured minimum (0.53 against 0.41), the rewards get one precision '
         'throughout (0.855, not 0.85), and "causal information" and "consistent ordering" of two points go.',
     sources=code('Minimum after the trailing edge: MB 0.53, BL 0.41. Rewards: BL 0.676 / 0.544, MB 0.968 / 0.855.'),
     edits=[(r"These anticipatory actions produce a markedly lower experimental trajectory over the obstacle than the baseline response. The dominant overshoot is attenuated and the downstream recovery is faster. A substantial undershoot nevertheless remains after the trailing edge, with a local minimum comparable to that obtained under $\pi_{\mathrm{BL}}$.",
             r"These anticipatory actions lower the measured trajectory over the obstacle, attenuate the overshoot, and "
             r"shorten the downstream recovery. An undershoot nevertheless remains after the trailing edge, to "
             r"$z/R\approx0.5$ against $0.4$ under $\pi_{\mathrm{BL}}$."),
            ('The performance change can be quantified with the same reward definition used throughout the subsequent policy search. The DT reward increases from approximately $\\mathcal R_{\\circ}=0.68$ for $\\pi_{\\mathrm{BL}}$ to $\\mathcal R_{\\circ}=0.97$ for $\\pi_{\\mathrm{MB}}$. The corresponding physical reward increases from approximately $\\mathcal R_{\\bullet}=0.54$ to $\\mathcal R_{\\bullet}=0.85$. Their consistent ordering supports the conclusion that the identified DT contains sufficient causal information to design a policy that improves physical tracking, while the difference in their absolute values quantifies the remaining transfer error.',
             r"With the reward of Eq.~\eqref{eq:reward}, the DT reward increases from $\mathcal R_{\circ}=0.676$ for "
             r"$\pi_{\mathrm{BL}}$ to $0.968$ for $\pi_{\mathrm{MB}}$, and the physical reward from $\mathcal R_{\bullet}=0.544$ "
             r"to $0.855$. Both rewards rank $\pi_{\mathrm{MB}}$ above $\pi_{\mathrm{BL}}$, so the DT is accurate "
             r"enough to design a policy that improves physical tracking, and the gap between the two rewards measures the "
             r"remaining transfer error.")])

card(G, 'The DT misses the post-edge undershoot, which it was not fitted to', grade='B',
     remarks=rk('IIIC-5', 'R2-4', 'Code-fit'),
     why='The colon and "pronounced" go, and one fact is added: the identification loss uses only the samples above the '
         'obstacle, so the DT was never fitted to the response after the trailing edge. That is a simpler explanation than '
         'an unmodeled transient, and the domain seat asks for alternatives to "transient".',
     edits=[(r"This difference is also visible in the trajectory replay.",
             r"The DT prediction $\mathrm{DT}_{\mathrm{MB}}$ in Fig.~\ref{fig:mb-optimum} shows the same gap."),
            (r"The larger discrepancy occurs around the trailing edge: the DT predicts that the reference increase should almost suppress the downstream undershoot, whereas a pronounced loss of clearance remains experimentally.",
             r"The largest difference occurs at the trailing edge. The DT predicts that raising the reference almost "
             r"suppresses the downstream undershoot, whereas the vehicle still descends to $z/R\approx0.5$. The "
             r"identification loss covers only the samples above the obstacle, so the DT is not fitted to this post-edge "
             r"response.")])

card(G, 'Closing paragraph of III-C', grade='B',
     remarks=rk('Cut-C7', 'GPT-14'),
     why='Repeats the model-free argument (Introduction, Sec. II-A, opening of III-D) and claims "safety and data-efficiency '
         'benefits" that no result shows.',
     edits=[('where the static GE model is least representative.\n\nThe model-based policy consequently provides both a performance improvement and a well-informed reference for the next phase. A global model-free search would discard the safety and data-efficiency benefits already supplied by the identified DT. Instead, the performance phase explores the neighborhood of $\\pi_{\\mathrm{MB}}$ and learns the GP discrepancy between the DT and physical rewards. The reward-transfer surrogate retains the useful ranking supplied by the DT while correcting the residual mismatch that prevents the best DT policy from coinciding with the best physical policy.',
             r"where the static GE model is least representative.")])

# ================================================================ III-D
G = 'III-D. Performance phase'
card(G, 'Opening of III-D', grade='B',
     remarks=rk('Cut-C8', 'GPT-14'),
     why='Repeats the purpose stated in Sec. II-C, and says "leading and trailing edges" where Sec. III-C locates the '
         'error at the trailing edge.',
     edits=[('Once the model-based policy has been obtained, the GE parameters are frozen and the campaign proceeds to the performance phase. The purpose of this phase is to learn the GP discrepancy between the DT and physical rewards. The comparison discussed in Section~\\ref{sec:results-mb} revealed that the DT remains optimistic, particularly around the leading and trailing edges of the obstacle, where the static GE correction cannot represent the complete transient aerodynamic response. Rather than increasing the complexity of the physical model, RT accounts for the control-relevant part of this structural error through the reward-transfer surrogate. The resulting search retains the safety and data efficiency of the model-based policy while allowing the best physical policy to depart from the best DT policy.',
             r"The performance phase learns the GP discrepancy between DT and physical rewards. Section~\ref{sec:results-mb} "
             r"showed that the DT is optimistic around the trailing edge, where the static ground-effect law cannot "
             r"represent the complete transient response. The reward-transfer surrogate accounts for the control-relevant "
             r"part of this error without enlarging the model.")])

card(G, 'Interpolation policies: method stated once', grade='B',
     flags=['Linked: [[t:Policies: what the information-policy rewards]]'],
     remarks=rk('IIID-1', 'IIID-2'),
     why='The exclusion of the information-oriented policies is a method decision, now in Sec. II-A. The definition and '
         'purpose of the interpolation policies are given in Sec. II-C.',
     edits=[(r"Only performance-oriented policies are considered at this stage. The information-oriented policies used during identification are excluded because their large altitude excursions were designed to excite the model parameters, not to maintain the nominal clearance $z^{\ast}/R=1.5$. The initial reward-transfer surrogate dataset therefore contains",
             r"The initial reward-transfer surrogate dataset contains"),
            ('Two additional policies are then introduced by applying one and two thirds of the model-based reference correction to the baseline reference. The resulting policies $\\pi_{\\lambda,i}$, with $\\lambda\\in\\{1/3,2/3\\}$, are reported in Fig.~\\ref{fig:intermediate-policies}. Since they lie on the direct interpolation path between the two existing policies, they are expected to produce intermediate rewards. Their main role is consequently to establish the global DT-to-physical reward trend and calibrate the affine component of the reward-transfer surrogate before the GP discrepancy is introduced.',
             r"Fig.~\ref{fig:intermediate-policies} shows the two interpolation policies $\pi_{\lambda,i}$ of "
             r"Section~\ref{sec:performance-phase}, which apply one and two thirds of the model-based correction and "
             r"calibrate the affine part of the surrogate.")])

card(G, 'Local exploration around π_MB, and the Sobol figure', grade='B',
     flags=['Linked: [[t:Basis functions]]'],
     remarks=rk('Cut-C9', 'IIID-11', 'IIID-12', 'N11'),
     why='The first paragraph repeats the model-free argument with "safe", "deliberately", a colon and "substantially". In '
         'the second, the hyphens stand for dashes. The faded curves of Fig. 10 are 256 unscreened samples with '
         '|a_j| ≤ 0.8, not a "safe" library.',
     sources=code('`paper/pp_paper.py:94-95,1365-1371`: 256 Sobol samples with |a_j| ≤ 0.8, not screened.'),
     edits=[('The calibration must subsequently be refined near the region of greatest practical interest, namely the model-based policy. Exploring around $\\pi_{\\mathrm{MB}}$ tests whether small changes to an already safe and effective policy can improve the physical response. This local strategy avoids the experimental cost and risk of an unconstrained model-free search. It also keeps the policy parameterization deliberately compact: a high-dimensional correction could describe more complex shapes, but would require substantially more physical tests before the Gaussian process could resolve their effect on performance.',
             r"The calibration is then refined near $\pi_{\mathrm{MB}}$. Three coefficients keep the number of flights needed "
             r"to train the GP small; a richer correction could describe more shapes but would need more flights."),
            ('A space-filling Sobol sequence is used to generate the faded-blue candidate family reported in Fig.~\\ref{fig:sobol}. The dark-blue dashed references in the same figure identify the small subset selected for physical testing. The subset spans different amplitude combinations and deliberately includes both apparently unfavorable changes-such as increasing the reference above the obstacle or reducing it downstream-and corrections that extend the compensating action already suggested by $\\pi_{\\mathrm{MB}}$.',
             r"Fig.~\ref{fig:sobol} shows representative samples of the Sobol library (faded blue) and the seven policies "
             r"flown (dark-blue dashed). They combine different amplitudes and include changes that look unfavorable, such "
             r"as raising the reference above the obstacle or lowering it downstream, as well as changes that extend the "
             r"correction of $\pi_{\mathrm{MB}}$."),
            (r"\caption{Safe Sobol policy library, basis locations, and experimentally tested local policies $\pi_{\mathbf a,i}$.}",
             r"\caption{Representative unscreened samples of the Sobol library ($|a_j|\leq0.8$), basis locations, and the "
             r"seven Sobol policies $\pi_{\mathbf a,i}$ flown.}")])

card(G, 'Reward pairs after local exploration', grade='B',
     remarks=rk('IIID-4', 'IIID-5', 'IIID-13'),
     why='The 43-word colon sentence repeats the roles of the affine fit and the GP from Sec. II-A, "sufficiently separated" '
         'becomes the measured range, and the last sentence repeats Sec. II-C.',
     sources=code('Physical rewards of ALPHA_01–07: 0.887, 0.932, 0.891, 0.860, 0.854, 0.867, 0.771.'),
     edits=[('Most of the tested Sobol policies instead occupy a narrow neighborhood of $\\pi_{\\mathrm{MB}}$ on the DT-reward axis, while their physical rewards remain sufficiently separated to reveal a policy-dependent GP discrepancy. These measurements improve the local calibration of $\\widehat{\\delta}(\\mathbf a)$: the affine relation continues to describe the overall relation between the DT and physical rewards, whereas the Gaussian process learns how policies with similar DT performance can be ranked differently by the physical environment.',
             r"Most Sobol policies have DT rewards close to that of $\pi_{\mathrm{MB}}$, whereas their physical rewards range "
             r"from $0.771$ to $0.932$, which reveals a policy-dependent GP discrepancy. These measurements calibrate the GP "
             r"discrepancy near $\pi_{\mathrm{MB}}$."),
            ('through Expected Improvement. The reward markers are computed from the cleaned mean trajectories; run-to-run dispersion is assessed in the trajectory comparisons and is not represented as a statistical error bar in the surrogate plots.',
             r"through Expected Improvement.")])

card(G, 'EI search: how many evaluations, what gain, and a near-identical policy', grade='A',
     flags=['Linked: [[t:Analyses on existing data]]'],
     remarks=rk('IIID-6', 'IIID-7', 'IIID-8', 'IIID-14', 'N11', 'R1-2', 'DA-1', 'R2-11'),
     why='"After only a few EI-guided evaluations" is the paper\'s data-efficiency claim; π_EI★ is the ninth of ten EI '
         'policies. "Other high-reward evaluations approach a similar reference shape" is shown by no figure, but the data '
         'support it: EI_05 lies within 0.024 of π_EI★ in every coefficient and reached 0.947, which answers part of the '
         'winner\'s-curse remark. The best Sobol policy had already reached 0.932, which a referee will see in Fig. 11; '
         'saying it first is better.',
     sources=code('EI_05 a = (−0.644, +0.712, +0.176), R• = 0.947; EI_09 a = (−0.664, +0.699, +0.200), R• = 0.952; per-run '
                  'tracking cost (stored metric) −0.191 ± 0.038 and −0.173 ± 0.036 (n = 3). ALPHA_02: R• = 0.932.'),
     edits=[('The acquisition does not seek an immediate reward increase at every iteration: some policies are selected because their GP interpolation uncertainty makes them informative candidates, and their physical reward can therefore remain below the incumbent. Nevertheless, after only a few EI-guided evaluations, the search identifies $\\pi_{\\mathrm{EI}}^{\\star}$.',
             r"EI does not seek a reward increase at every iteration. Some policies are selected for their GP uncertainty, "
             r"and their physical reward can remain below the best reward $\mathcal R_{\bullet}^{+}$ observed so far. The "
             r"ninth of the ten EI-selected policies is $\pi_{\mathrm{EI}}^{\star}$."),
            ('Relative to $\\pi_{\\mathrm{MB}}$, its DT reward increases only from approximately $0.968$ to $0.978$, whereas the physical reward rises from approximately $0.855$ to $0.952$. The marked difference between these two increments is the improvement enabled by the learned GP discrepancy: the DT alone regards the two policies as nearly equivalent, while the physical observations reveal a substantial performance gain. Other high-reward evaluations approach a similar reference shape, supporting a repeatable control strategy rather than proving convergence to a unique optimum.',
             r"Relative to $\pi_{\mathrm{MB}}$, its DT reward increases only from $0.968$ to $0.978$, whereas the physical "
             r"reward rises from $0.855$ to $0.952$. The DT alone ranks the two policies as nearly equivalent, and the "
             r"physical rewards, through the GP discrepancy, reveal the difference. The fifth EI policy, whose coefficients "
             r"differ from those of $\pi_{\mathrm{EI}}^{\star}$ by at most $0.024$, reached $0.947$, so the gain is not tied "
             r"to a single policy. The coefficients of $\pi_{\mathrm{EI}}^{\star}$ lie at least $0.30$ from the faces of the "
             r"box $[-1,1]^3$, which therefore does not bind at the best policy. The best Sobol policy reached $0.932$.")])

card(G, 'Trajectory of π_EI★: what the figure shows', grade='B',
     remarks=rk('IIID-9', 'R2-11', 'N12'),
     why='Four intensifiers in one paragraph, and two claims the figure does not show: the command does not rise earlier '
         'but higher, and the clearance at the trailing edge is about the same. The decisive difference is the minimum '
         'after the edge, 1.11 against 0.53. "Better prepared" goes.',
     sources=code('Post-edge minimum z/R: EI_09 1.11, MB 0.53. a_B = +0.70 (raise near the trailing edge).'),
     edits=[('which slightly reduces the remaining positive tracking excursion. The command then rises earlier and more rapidly near the trailing edge. The vehicle consequently reaches a somewhat larger clearance before leaving the obstacle and is better prepared for the subsequent loss of aerodynamic support. The downstream undershoot is markedly reduced and the recovery toward $z^{\\ast}/R=1.5$ becomes smoother. This reduction of the post-obstacle excursion supplies the dominant reward gain and clearly separates $\\pi_{\\mathrm{EI}}^{\\star}$ from the purely model-based policy;',
             r"which reduces the remaining positive excursion. Near the trailing edge, the command then rises higher, to "
             r"about $z/R=3.1$ against $2.5$ for $\pi_{\mathrm{MB}}$. The downstream minimum rises from $z/R\approx0.5$ to "
             r"$1.1$, and the recovery toward $z^{\ast}/R=1.5$ is smoother. This smaller post-obstacle excursion separates "
             r"$\pi_{\mathrm{EI}}^{\star}$ from $\pi_{\mathrm{MB}}$;")])

card(G, 'Video frames: one flight per case', grade='B',
     remarks=rk('IIID-10'),
     why='One flight per case cannot support repeatability; the repeated flights of Fig. 13 do. The text also mentions '
         'three paths superposed in panel (c), but the caption says (c) shows π_EI★ only: check the panel, and correct the '
         'caption if (c) overlays all three.',
     edits=[(r"The single-run paths reproduce the ordering observed in the mean trajectories, supporting the repeatability of the measured improvement. In particular, the three paths superposed in Fig.~\ref{fig:real-comparison}(c) make the large departure of the baseline policy immediately visible.",
             r"The single-run paths show the same ordering as the mean trajectories.")])

# ================================================================ III-E
G = 'III-E. Generalization'
card(G, 'Generalization: which reward, and the numbers that follow (decision)', grade='A',
     remarks=rk('N4', 'EIC-4', 'R1-3', 'R3-9', 'DA-9'),
     why='Fig. 15 and the text use two different rewards. The figure plots the stored per-run metric (tracking cost to '
         '4.00 m, plus the cost after the edge, plus a peak term), while 0.57 and 0.83 in the text, and Fig. 14, use the '
         'reward of Eq. (reward). The ranking at one condition depends on the choice, so this needs you before the text of '
         'III-E and the Conclusions can be fixed. The condition-aware surrogate itself was trained on the stored metric.',
     sources=code('Scores S• with the reward of Eq. (reward): nominal MB 0.681, EI★ 0.894; (2.5, 0.045) MB 0.622, TR 0.671; '
                  '(1, 0.113) MB 0.740, TR 0.772, EI_01 0.575, EI★ 0.827. With the stored metric (current Fig. 15): nominal '
                  'MB 0.455, EI★ 0.843; (2.5, 0.045) MB 0.539, TR 0.679; (1, 0.113) MB 0.680, TR 0.651, EI_01 0.365, '
                  'EI★ 0.757. At (1, 0.113) MB and TR differ by less than the run-to-run spread (−0.452 ± 0.014, n = 2, '
                  'against −0.492 ± 0.111, n = 3).'),
     suggestion='(1) Use the reward of Eq. (reward) everywhere: I regenerate Fig. 15 with it. The transferred policy then '
                'improves on π_MB at both conditions (0.671 against 0.622, 0.772 against 0.740, the second within the '
                'run-to-run spread); 0.57 and 0.83 stay; the reversal sentences in III-E and the Conclusions go.\n(2) Keep '
                'the stored metric in Fig. 15: I define it next to Eq. (normalized-score), and the text becomes 0.36 and '
                '0.76; the transferred policy improves strongly at (2.5, 0.045) (0.539 to 0.679) and is slightly worse at '
                '(1, 0.113) (0.680 against 0.651, within the spread). Fig. 14 and Fig. 15 then show different scores for '
                'the same nominal policies.\nApply = (1): text and figure in round 2. For (2), write it in the note.')

card(G, 'Opening of III-E', grade='B',
     remarks=rk('Cut-C10'),
     why='The paragraph summarizes III-D, with "clear", "a few", "substantially" and "marginally".',
     edits=[('Up to this point, the reward-transfer surrogate has been calibrated at the single nominal operating condition $(z^\\ast/R,\\,v_x^\\ast/v_h)=(1.5,0.079)$. At this condition, the model-based policy produced a clear improvement over the baseline policy, and only a few additional physical evaluations were required for the GP discrepancy $\\delta$ to capture part of the residual mismatch between the DT and physical rewards. Expected Improvement could consequently identify a policy with substantially better physical performance even though its DT reward was only marginally higher than that of $\\pi_{\\mathrm{MB}}$. The final campaign block investigates whether this policy correction remains useful when both the desired clearance and the forward velocity are changed.',
             r"The final stage tests whether the correction learned at the nominal condition remains useful when both the "
             r"desired clearance and the forward speed change.")])

card(G, 'Off-nominal trajectories: repeated sentences, and a hypothesis stated as fact', grade='B',
     remarks=rk('IIIE-1', 'IIIE-8', 'IIIE-3', 'IIIE-4', 'R2-10'),
     why='The first sentences repeat Sec. II-C. The explanation of the weaker transfer was stated as fact; the card states '
         'the three differences that are measured (shorter time over the obstacle, coefficients outside the box, the least '
         'constrained part of the law), as the domain seat suggests, and lets the reader weigh them. The ranking sentences '
         'wait for [[t:Generalization: which reward]].',
     edits=[('Two additional operating conditions are considered: a low-speed, larger-clearance crossing at $(z^\\ast/R,\\,v_x^\\ast/v_h)=(2.5,0.045)$ and a higher-speed, small-clearance crossing at $(1,0.113)$. The trajectory comparisons are reported in Fig.~\\ref{fig:generalization-trajectories}. At each condition, the built-in PID controller executes the condition-specific baseline policy $\\pi_{\\mathrm{BL}}$, while a new model-based policy is computed using the same frozen parameter vector $\\widehat{\\boldsymbol{\\theta}}_p$ identified at the end of the information phase.',
             r"Fig.~\ref{fig:generalization-trajectories} shows the lower-speed, larger-clearance crossing at "
             r"$(z^\ast/R,\,v_x^\ast/v_h)=(2.5,0.045)$ and the higher-speed, smaller-clearance crossing at $(1,0.113)$."),
            ('This loss is important: the transferred correction was learned from discrepancies measured only at the nominal condition $(1.5,0.079)$, whereas the relative importance of the unmodeled transients changes with velocity, clearance, and the magnitude of the model-based action. Transfer therefore provides an informed initialization, but it does not replace condition-specific learning when the operating condition moves away from the region represented in the reward-transfer surrogate dataset.',
             r"The transferred correction was learned from discrepancies measured only at the nominal condition. At "
             r"$(1,0.113)$, the vehicle spends $1.6$~s over the obstacle instead of $2.3$~s, the transferred coefficients "
             r"leave the box $[-1,1]^3$, and the policies operate at clearances where $f_{\mathrm{GE}}$ is least "
             r"constrained. The discrepancy can therefore differ from the nominal one.")])

card(G, 'Normalized score: definitions, and what it means', grade='B',
     remarks=rk('Cut-C11', 'IIIE-5', 'GPT-12'),
     why='S_e is undefined, and the score does not put missions "on the same improvement scale": it is a fractional '
         'reduction of cost relative to the baseline of each condition.',
     edits=[('A direct comparison of rewards across these missions requires the different baseline difficulty to be removed. The DT and physical quantities are therefore normalized independently by their condition-specific baseline-policy values according to Eq.~\\eqref{eq:normalized-score}. The DT and physical scores are denoted by $\\mathcal S_{\\circ}$ and $\\mathcal S_{\\bullet}$, respectively. By construction, $\\mathcal S_e=0$ for the corresponding baseline policy and a larger value indicates a greater reduction of the tracking cost. This normalization places missions with different velocities and clearances on the same improvement scale and defines the normalized reward-transfer surrogate used across operating conditions.',
             r"Rewards at different conditions are compared through the scores of Eq.~\eqref{eq:normalized-score}, "
             r"$\mathcal S_{\circ}$ for the DT and $\mathcal S_{\bullet}$ for the experiment. Each is the fractional "
             r"reduction of the tracking cost relative to the baseline policy at the same condition, for which it is zero.")])

card(G, 'Condition-aware surrogate: what was implemented', grade='B',
     remarks=rk('IIIE-6', 'N6', 'GPT-13', 'N12', 'Cut-C12'),
     why='The affine term of Eq. (generalized-surrogate) is undefined, and the GP inputs, data and noise are not stated; '
         'the GPT review asks for them before "redirected the search" can be believed. The code uses six standardized '
         'inputs, per-run means with a noise term, and proposes three candidates per round, of which one was flown. '
         'Krause and Ong is the reference for a GP over policy and context.',
     sources=code('`next_mission_design/generalized_policy.py:188-344,452-567`: inputs [β1, β2, β3, projection RMSE, v_x, '
                  'z*/R], β_j = a_j / max(m_j(Δz_MB^χ), 0.05), standardized by the training mean and max(std, (0.25, 0.25, '
                  '0.25, 0.05, 0.10, 0.50)); unit-length Matérn-3/2; scores = per-repetition means of the stored metric; '
                  'affine part by weighted least squares, weights 1/noise², noise = max(SD/|R_BL|, 0.01); kernel diagonal '
                  'noise² + 1e-7; three distinct maximizers per round; only candidate 2 of runs It25 and It26 is in the '
                  'data.'),
     extra=bib('KrauseOng2011'),
     edits=[(r"In this more general formulation, the GP discrepancy depends on both the policy and the operating condition,",
             r"In the condition-aware surrogate, the GP discrepancy depends on both the policy and the operating "
             r"condition~\cite{KrauseOng2011},"),
            ('The vector $\\mathbf a$ contains the three coefficients that modify the condition-specific model-based policy, while $(z^\\ast/R,\\,v_x^\\ast/v_h)$ identifies the operating condition. Additional experiments distributed over the domain of interest would therefore train the normalized reward-transfer surrogate to propose a condition-specific correction instead of reproducing the same transferred policy everywhere. The present experiments provide an initial demonstration of this extension rather than a complete mapping of the velocity-clearance domain.',
             r"Here, $\widehat{\mathcal S}_{\bullet,\mathrm{aff}}$ is the affine fit of $\mathcal S_{\bullet}$ on "
             r"$\mathcal S_{\circ}$. As implemented, $\widehat{\delta}$ takes as standardized inputs the coefficients $a_j$ "
             r"divided by the local amplitude of the model-based correction, the residual of their projection on the basis, "
             r"$v_x^\ast$, and $z^\ast/R$. The scores are means over the flights of each policy. Their standard deviation "
             r"over the flights, divided by the baseline cost and at least $0.01$, weights the affine fit and enters the GP "
             r"as noise. Additional experiments over the "
             r"velocity--clearance domain would train this surrogate to propose a condition-specific correction instead of "
             r"a single transferred one."),
            (r"Two EI-guided physical evaluations are added at $(z^\ast/R,\,v_x^\ast/v_h)=(1,0.113)$.",
             r"Two EI rounds are run at $(z^\ast/R,\,v_x^\ast/v_h)=(1,0.113)$; each proposes three distinct candidates, of "
             r"which one is flown.")])

card(G, 'Closing paragraph of III-E', grade='B',
     flags=['Linked: [[t:Generalization: which reward]]'],
     remarks=rk('Cut-C12', 'IIIE-7', 'GPT-14'),
     why='The fourth "not a converged surrogate" disclaimer is kept in one sentence; "local DT" (the DT is the same frozen '
         'one), "substantially" and "safe and data-efficient reference" go. "When direct transfer fails" depends on the '
         'reward decision and is left out.',
     edits=[('Only two condition-specific EI iterations are used here, so the result is interpreted as a proof-of-concept local extension of the RT workflow rather than as convergence of a general surrogate. At a new operating condition, the local DT first supplies a model-based policy that already improves substantially over the baseline policy. When direct transfer fails to improve that policy, a small number of physical interactions can reveal how the GP discrepancy has changed and redirect the search toward a better condition-specific solution. Repeating this process over the velocity-clearance domain would progressively calibrate $\\widehat{\\delta}(\\mathbf a,z^\\ast/R,v_x^\\ast/v_h)$ and enable the generation of policies tailored to the requested operating condition while retaining the model-based policy as the safe and data-efficient reference.',
             r"With only two EI iterations, this result is a proof of concept rather than a converged surrogate. At a new "
             r"operating condition, the frozen DT first supplies a model-based policy that improves on the baseline policy. "
             r"A few physical episodes can then reveal how the GP discrepancy has changed and redirect the search toward "
             r"a better condition-specific policy.")])

# ================================================================ IV
G = 'IV. Conclusions'
card(G, 'Conclusions: shorter, with numbers and the limits of the DT screening', grade='B', flags=[YOURS,
     'Linked: [[t:Generalization: which reward]]'],
     remarks=rk('Cut-C13', 'CON-1', 'CON-2', 'CON-4', 'EIC-6', 'EIC-7', 'DA-6', 'N12'),
     why='The Conclusions restate Results (434 words) with a 48-word colon sentence, "visual diversity", "well constrained", '
         '"virtual safety" and "few". The three paragraphs here keep every claim, give the numbers, and add the limit a '
         'referee will raise: admissibility was checked only in a DT that underpredicts the undershoot. "Constrained to '
         'z/R ≥ 0.5" was not true of the information phase (references to 0.34R); the lowest measured mean clearance is '
         'used instead. The generalization paragraph waits for the reward decision.',
     sources=code('Lowest measured mean clearance over the obstacle: 0.68R (INF_09). Information design admitted a DT '
                  'lowest-rotor clearance of 0.3R (`informative_policy.py:68`).'),
     edits=[('This work demonstrated Reinforcement Twinning for predictive trajectory control of a micro aerial vehicle crossing a finite obstacle in ground effect. The information phase provided evidence that the designed experiments added more than visual diversity: the cumulative smallest Fisher eigenvalue grew much faster than for repeated baseline experiments, and restricting the design from the broad domain to the near-wall domain restored information gain as the former began to saturate. Although the identified model parameters remained correlated, the resulting ground-effect function was well constrained over the control-relevant clearance range. Parameter decorrelation was therefore not treated as the objective by itself; the relevant outcome was the improved identification of the weakest observable parameter direction and of the aerodynamic correction used by the controller.',
             r"This work demonstrated Reinforcement Twinning for the trajectory control of a micro aerial vehicle crossing a "
             r"finite obstacle in ground effect. In the information phase, the designed experiments raised the smallest "
             r"eigenvalue of the cumulative Fisher-information proxy to $3.242$ over the baseline and twelve "
             r"information-oriented episodes, against $0.387$ for the baseline record repeated over the same episodes. The "
             r"near-wall records, two of them archived, gave most of this increase. The parameters remain correlated ($\rho_{A,p}=0.818$), but the uncertainty indicator "
             r"of $f_{\mathrm{GE}}$ fell to $15\%$ at $z/R=1$ and $4.3\%$ at $z/R=1.5$."),
            ('Model-based optimization remained the backbone of the framework. The identified DT generated an anticipatory model-based policy that improved tracking without replacing the onboard feedback controller and while satisfying the adopted virtual safety constraints. The remaining replay error then motivated the performance phase rather than invalidating the DT. Fractional and Sobol policies calibrated the reward-transfer surrogate, while Expected Improvement directed subsequent physical experiments toward uncertain and potentially better policies. With few additional interactions, the resulting $\\pi_{\\mathrm{EI}}^{\\star}$ outperformed the model-based policy by compensating for response features that the low-order static model could not rank accurately. In this way, the DT restricted the search to a screened, high-performing neighborhood, and physical rewards were used specifically to learn the GP discrepancy within that neighborhood.',
             r"The DT produced a model-based policy that raised the physical reward from $0.544$ to $0.855$, kept "
             r"the onboard feedback controller, and passed the DT clearance checks. Interpolation and Sobol policies then "
             r"calibrated the reward-transfer surrogate, and after nine EI-selected policies the search found a policy with "
             r"physical reward $0.952$, mainly by reducing the post-obstacle undershoot that the static model does not "
             r"predict."),
            ('The conclusions are therefore limited to the tested envelope. The ground-effect model represents an unsteady rotor-surface interaction with a static two-parameter law and cannot reproduce every transient feature. The physical experiments were constrained to $z/R\\geq0.5$, so the results do not support extrapolation toward contact, and generalization was examined at only two additional operating conditions. Future work should extend the campaign across a denser velocity-clearance domain, account explicitly for repeated-measurement uncertainty in the reward-transfer surrogate, and investigate richer unsteady aerodynamic models, moving landing surfaces, and onboard or real-time policy adaptation. Within the present limits, the campaign shows how RT can combine interpretable physics, virtual safety screening, and a targeted data-driven correction to improve control performance without requiring unconstrained model-free exploration.',
             r"The results are limited to a static two-parameter ground-effect law, to the clearances flown (the lowest "
             r"measured mean clearance over the obstacle was $0.68R$), and to two off-nominal conditions. Admissibility was "
             r"checked only in the DT, which underpredicts the trailing-edge undershoot, so the DT screening reduces the "
             r"risk of a policy without bounding it. Future work should cover a denser velocity--clearance domain, include "
             r"repeated-measurement uncertainty in the surrogate, and test unsteady aerodynamic models, moving landing "
             r"surfaces, and onboard or real-time policy adaptation.")])

# ================================================================ Throughout the text (renames, applied after all edits)
G = 'Throughout the text'
card(G, 'Rename: "near-wall" becomes "low-clearance"', grade='B',
     remarks=[remark('T1', 'Writing audit', 'Intro L43 reserves "wall effect" for lateral surfaces, so '
                                       '"near-wall" for a floor contradicts the paper\'s own taxonomy.', 'Section 3.1')],
     why='The Introduction reserves "wall effect" for lateral surfaces, and the obstacle is horizontal. The legends of '
         'Figs. 3, 5 and 6 still say "near wall"; they change when the figures are regenerated.',
     rename={'frm': 'near-wall', 'to': 'low-clearance',
             'subs': [(r'near-wall', 'low-clearance'), (r'near the wall', 'at low clearance'),
                      (r'close to the wall', 'at low clearance'), (r'away from the wall', 'at larger clearance')]})

card(G, 'Rename: "Richardson et al." becomes "Richardson and Pretorius"', grade='C',
     remarks=[remark('L-Richardson', 'Literature check', 'Two authors: write "Richardson and Pretorius", not "Richardson et al.".')],
     why='The cited paper has two authors. The edits of other cards already use both names; this catches the rest.',
     rename={'frm': 'Richardson et al.', 'to': 'Richardson and Pretorius',
             'subs': [(r'Richardson et al\.', 'Richardson and Pretorius')]})

card(G, 'Rename: "Cheeseman-Bennett" with an en dash', grade='C',
     remarks=[remark('P4', 'Writing audit', '"Cheeseman-Bennett" should use an en-dash, `Cheeseman--Bennett`.')],
     why='Two names joined by a dash take an en dash.',
     rename={'frm': 'Cheeseman-Bennett', 'to': 'Cheeseman--Bennett',
             'subs': [(r'(?<!-)Cheeseman-Bennett', 'Cheeseman--Bennett')]})

card(G, 'Rename: the EI exploration margin ξ becomes ζ', grade='C',
     remarks=rk('IIA-15', 'EIC-10'),
     why='The margin ξ and the descriptor bold ξ appear in the same equation. Only the margin changes; it is zero in the '
         'campaign, so deleting it is the other option (say so in the note).',
     rename={'frm': r'\xi (margin)', 'to': r'\zeta',
             'subs': [(r'(?<!\\boldsymbol)\\xi(?![A-Za-z])', r'\zeta')]})

card(G, 'Rename: the subscript "safe" of the admissible sets becomes "adm"', grade='C',
     remarks=rk('GPT-14', 'EIC-7'),
     why='The five admissible sets are defined by checks in the DT, not by a safety guarantee. With this rename and the edits '
         'above, "safe" no longer describes a DT check anywhere in the paper.',
     rename={'frm': r'\mathrm{safe}', 'to': r'\mathrm{adm}',
             'subs': [(r'\\mathrm\{safe\}', r'\mathrm{adm}')]})

# ================================================================ Beyond this round
G = 'Beyond this round'
card(G, 'Analyses on existing data: what the panel asks for that needs no flight', grade='A',
     remarks=rk('R1-2', 'R3-4', 'DA-1', 'R1-4', 'R3-1', 'R1-7', 'R3-2', 'DA-2', 'R3-3', 'DA-3', 'GPT-10', 'GPT-12', 'R2-1', 'R2-4'),
     why='Most objections of the panel can be answered with the logged data and the DT, without flying. Each item below is '
         'a computation I can run from the code for round 2, with a figure or a sentence for the paper.',
     suggestion='(i) Reward noise: the spread of each reward over its flights, a GP with that noise, and the best posterior '
                'mean as EI incumbent (R1-2, R3-4, DA-1, GPT-3). The per-run raw records are missing for the reward of '
                'Eq. (reward); the stored per-run metric exists.\n(ii) Surrogate ablations on the 21 nominal policies: GP '
                'alone, affine alone, affine plus GP, compared by leave-one-out error (R1-4, R3-1).\n(iii) The DT optimum '
                'without the amplitude and curvature penalties, to separate regularization from discrepancy learning '
                '(R1-7, R3-2, DA-2).\n(iv) Model-based policies designed with the Cheeseman–Bennett and the broad-domain '
                'coefficients, scored in the final DT, to show what the information phase is worth for control (R3-3, '
                'DA-3).\n(v) Leave-one-episode-out identification, or a bootstrap over episodes (GPT-10, R1-1).\n(vi) The '
                'identified f_GE against the Crazyflie data of Carter et al. and Kan et al. and the Sanchez-Cuevas model '
                '(R2-1).\n(vii) The thrust reconstructed from the logged PWM, IMU and battery data along each flight, to '
                'test the "transient" explanation (R2-4).\n(viii) The run-to-run uncertainty of the baseline cost, propagated into the '
                'normalized scores of Sec. III-E (GPT-12).\nApply = run all; to choose, list the numbers in the note. Keep '
                'as is = none now; the items are carried over.')

card(G, 'New flights the panel asks for', grade='B',
     remarks=rk('R1-2', 'DA-1', 'R2-4', 'R2-5', 'R3-3', 'EIC-3'),
     why='These need the vehicle. They are listed so that you can plan a session; none is needed for the text changes of '
         'this round.',
     suggestion='(a) Confirmation flights of π_MB and π_EI★, interleaved, five each, to give both rewards a spread and '
                'answer the winner\'s-curse remark (R1-2, DA-1).\n(b) The mission with the obstacle removed, to validate '
                'the nominal DT out of ground effect (R2-4, R2-5).\n(c) A model-based policy designed with the '
                'Cheeseman–Bennett coefficients, flown, to show the control value of the information phase (R3-3).\n(d) '
                'Bayesian optimization of the same three coefficients without the DT prior, with the same budget, as a '
                'comparator (EIC-3); expensive.\nApply = you plan (a) and (b); I carry over (c) and (d). Write another choice '
                'in the note.')

card(G, 'Length: equations to remove or merge (round 2)', grade='B',
     remarks=rk('EIC-1'),
     why='This round removes about 2,000 words of prose. The journal-fit seat also lists equations that a T-CST paper would '
         'not typeset. Removing equations shifts the numbering, so these come in round 2 as edit cards.',
     suggestion='(a) Rigid-body, quaternion and rotor equations (eq_vehicle_trasl to eq_RP_moments) become one sentence '
                'citing Richardson and Pretorius, with Table I kept.\n(b) Adam moments and update (adam-moments, '
                'adjoint-adam) become one sentence with the settings.\n(c) Keep one version each of the Fisher update, the '
                'E-optimal criterion, the surrogate and EI: the generic ones of Sec. II-A or the specialized ones of '
                'Sec. II-C.\n(d) Merge figures: Fig. 2 into Fig. 13, Fig. 10 with Fig. 11, Fig. 12 with Fig. 13 (the '
                'seat\'s list).\nApply = all in round 2. Name the items to keep in the note.')

card(G, 'Bibliography: corrections to existing entries', grade='B',
     remarks=rk('EIC-2', 'L-Mendez', 'GPT-bib', 'L-Uncited', 'L-Taffanel'),
     why='The method paper is now on arXiv, a paragraph of prose sits inside references.bib, and several entries have '
         'wrong or missing fields. These change references.bib only.',
     suggestion='Apply = I make these changes in references.bib:\n'
                '1. Mendez2026: replace the @unpublished entry by the arXiv record (same key): Mendez, Schena, Poletti, '
                'Lecomte, Randino, Van den Berghe, "Reinforcement Twinning via Twin-Calibrated Bayesian Policy Search and '
                'Replay-Driven Identification", arXiv:2611.03540, 2026, doi 10.48550/arXiv.2611.03540.\n'
                '2. Delete the prose paragraph after CheesemanBennett1955.\n'
                '3. CheesemanBennett1955: title "The Effect of the Ground on a Helicopter Rotor in Forward Flight", R&M 3021, '
                'HMSO, London, 1957 (report dated 1955).\n'
                '4. Taffanel2021Lighthouse: @misc with arXiv:2104.11523, doi 10.48550/arXiv.2104.11523, presented at the '
                'ICRA 2021 workshop "Robot Swarms in the Real World"; brace {UAV}.\n'
                '5. Uncited after this round: Chiuso2019, Hjalmarsson2005 (IEEEtran does not print them); delete them or '
                'tell me where to cite them.\n'
                '6. Minor fields: Mockus1975 (booktitle, LNCS 27, doi 10.1007/3-540-07165-2_55), Forrester2007 (no. 2088, '
                'S{\\\'o}bester), Korenhof2021 (Paulan, Sanneke), Wagg2025 (Jason Shepherd, Zack Xuereb Conti), Cai2024 '
                '(vol. 61, no. 4, pp. 1230–1246), Kennedy2001 (full journal name), Matus2020 (no. 1).\n'
                'Keep as is = no change to references.bib.')
