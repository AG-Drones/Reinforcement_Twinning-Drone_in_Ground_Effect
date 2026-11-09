# Ground-effect modeling and identification: literature map, verification, and proposed Introduction text

Manuscript: `material/main_lf.tex` (Abstract, Introduction lines 38-64 and GE model lines 527-551 read in full; Sec. II-C and Results lines 640-845 read). Bibliography: `paper/references.bib`. External review: `material/PAPER_REVIEW_V2.md`, lines 527-755. Earlier check: `material/literature_scan_round_SER.md`. Date: 2026-11-04.

**How things were verified.** Metadata come from the CrossRef REST API (`api.crossref.org/works/<DOI>`, read through WebFetch; direct curl is blocked by the proxy), from OpenAlex where CrossRef was rate-limited, from DataCite for arXiv DOIs, and from publisher or library pages where stated. Content (what a paper reports) comes from the abstract at least; for Sanchez-Cuevas et al. 2017 and Carter et al. 2021 the full text was read. Each line below says when content rests on less than an abstract. Rule applied: if a record could not be confirmed with the stated metadata, the paper is not proposed.

**Main points for the author**

1. The current paragraph (line 45) covers the classical model and two multirotor studies only. The literature on *how GE parameters are obtained* splits into test-stand fits (most multirotor work), analytical/image models, CFD, learned models from flight data, and observer-based estimates. None of the works found designs flights to identify GE parameters. That is the gap to state, and it is defensible.
2. Two 2026 Vertical Flight Society papers are directly relevant to the obstacle-edge model and were not in either earlier review. **Yon and Li (2026)** correlate partial-coverage rotor thrust with a circular-segment rotor-ground overlap area, which is essentially your $\chi_i$. **Herz et al. (2026)** fly a quadrotor over a building-like edge and find that full GE develops only after most of the vehicle has crossed it, with the airframe driving the onset. Cite the first at Eq. (corrected-thrust) as support and the second as a limitation.
3. **Lei et al. (2026)** report a *negative* GE region near $h/R\approx1.5$ for their small-spacing quadrotor. Your nominal clearance is $z^\ast/R=1.5$ and your law is monotone and positive. A referee may raise this. Add one sentence at the model paragraph saying that the identified law is an effective model over the tested clearances, not a general quadrotor law.
4. Your identified amplitude ($A=0.121$, about twice $1/16$) is consistent with Carter et al. (Crazyflie 2.0, lift increase more than twice the classical prediction) and Sharf et al. 2014 (stronger GE than theory on a small UAV). Carter et al. also show that the Sanchez-Cuevas multirotor model with $K_b\approx2$ fits Crazyflie data ($R^2=0.956$, $1<z/R<3$, $l/r=3.9$). Plotting that curve next to your identified $f_{\mathrm{GE}}$ would give an external check at no cost.
5. Of the 18 references proposed in PAPER_REVIEW_V2, all exist. One content claim could not be verified: for **Xu et al. 2022** no abstract was accessible. Two claims are only partly supported: **Del Cont Bernard et al. 2017**, whose abstract does not state that dynamic GE "differs" from static, and **Xin et al. 2017**, whose DOI did not resolve through the CrossRef or OpenAlex API but is printed on the publisher page. Minor BibTeX fixes are given in (b).
6. **Hayden 1976** (requested) is confirmed only through secondary sources. It is listed in (a) but not proposed.

---

## (a) Thematic synthesis

Format: **paper**: model; how its parameters were obtained; vehicle and scale; verified DOI. "Bib" means the paper is already in `references.bib`.

### Theme 1. Classical rotor models

- **Cheeseman & Bennett 1955** (Bib; ARC R&M 3021): image-source model, $T_{IGE}/T_{OGE}=1/[1-(R/4z)^2/(1+(V/v_i)^2)]$. Analytical, no fitted coefficient. Helicopter rotor, forward flight. Its hover limit has leading-order expansion $A=1/16$, $p=2$. No DOI (scan on Cranfield AERADE; checked in the earlier round).
- **Hayden 1976**, "The effect of the ground on helicopter hovering power required," Proc. 32nd Annual National Forum of the AHS, Washington, DC, May 1976: empirical hover law $T_{IGE}/T_{OGE}=(0.9926+0.03794\,(2R/z)^2)^{2/3}$ fitted to helicopter test data. Full-scale helicopters. No DOI. **Confirmed only through Kan et al. 2019 (ref. [18] and Eq. 5); primary not accessed. Not proposed.**
- **Curtiss, Sun, Putman & Hanker 1984**, JAHS 29(1):48–55: experiments only, no fitted model. They combined flow visualization with steady and non-steady force/moment tests over advance ratio, height and collective, and found three flow regimes (recirculation, ground vortex, clean wake). Translational acceleration has a significant effect, so time is needed to reach steady state. Model helicopter rotor. DOI 10.4050/JAHS.29.48 (OpenAlex).
- **Curtiss, Erdman & Sun 1985**, "Ground effect aerodynamics": hot-wire inflow measurements in GE used to estimate effective inflow. The benefit fades quickly with advance ratio, a ground vortex forms, and acceleration matters. Isolated model rotor. NASA NTRS 19860063840 lists it as a 1985 conference paper. **It is often cited as Vertica 11(1/2), 1987; that venue was not verified, so it is not proposed.**
- **Yu & Peters 2005**, JAHS 50(3):259–268: nonlinear finite-state inflow model of dynamic GE; analytical (potential flow with mass sources). DOI 10.4050/1.3092862 (CrossRef gives only the start page; the end page is from Kan et al.'s reference list). No abstract in the record; content from the title and the 2004 Forum precursor (DOI 10.4050/vfs-f60-000008), which was checked against formulae derived from flight tests.
- **Leishman 2006**, *Principles of Helicopter Aerodynamics*, 2nd ed., Cambridge Univ. Press, Cambridge Aerospace Series 18, ISBN 0-521-85860-7 (CiNii). Momentum and wake theory. **The online chapter list does not show a GE section title, so the page range was not verified.** Cite it only after checking the GE pages in the book.
- **Pasquali, Gennaretti, Bernardini & Serafini 2023**, Aerosp. Sci. Technol. 140:108414: state-space dynamic-inflow model for a hovering rotor over fixed, inclined, heaving or pitching ground. Its coefficients are identified from a mid-fidelity free-wake solver (generalized mirror images). Rotor scale. DOI 10.1016/j.ast.2023.108414 (OpenAlex).

### Theme 2. Multirotor empirical models (test stand or flight)

- **Powers et al. 2013**, *Experimental Robotics* (STAR 88):289–302: models of a micro quadrotor under relative wind and near ground, ceiling and other robots, used in controllers and for mapping by a swarm. Details are paywalled (abstract only). DOI 10.1007/978-3-319-00065-7_21.
- **Sharf et al. 2014**, ICUAS 2014:1158–1166: validates the classical single-propeller GE ratio on a Draganflyer X8 (four coaxial pairs), using a propeller test stand and flights. GE is stronger than theory predicts. DOI 10.1109/ICUAS.2014.6842370 (CrossRef).
- **Li Danjun, Zhou, Shi & Lu 2015**, Proc. 34th CCC:5647–5652: a quadrotor GE model adapted from Cheeseman's, plus a GE compensator with robust PID altitude control for landing; experiments. The abstract does not say how the parameters were obtained. DOI 10.1109/ChiCC.2015.7260521 (CrossRef).
- **Sanchez-Cuevas, Heredia & Ollero 2017**, Int. J. Aerosp. Eng. 2017:1823056: the classical ratio plus image-rotor terms (adjacent spacing $d$, diagonal $b$) and an empirical body ("fountain") coefficient $K_b\approx2$. Obtained on a test bench measuring thrust, rotor speed and PWM, using PQUAD (1.4 kg, 12 cm rotors) and AMUSE (12 kg). Also covers partial GE and control (Themes 3–4). DOI 10.1155/2017/1823056 (CrossRef; full text read).
- **Conyers, Rutherford & Valavanis 2018**, ICRA 2018:1244–1250: empirical GE evaluation for small rotorcraft. **Abstract not retrievable; content not verified.** DOI 10.1109/ICRA.2018.8461035. **Conyers 2019** (PhD, Univ. of Denver, digitalcommons.du.edu/etd/1570) concludes that the Cheeseman–Bennett model "cannot be applied to today's multirotor UAVs" and develops a parametric multirotor GE model. In his work, ceiling effect follows classical theory. No DOI.
- **He, Kou, Calaf & Leang 2019**, J. Dyn. Syst. Meas. Control 141(7):071013: exponential, per-rotor, quasi-steady model validated experimentally on a quadcopter. Used for feedforward and a nonlinear disturbance observer (about 23% lower tracking error). DOI 10.1115/1.4043221.
- **Wei, Chan, Lee & Kong 2019**, Int. J. Intell. Robot. Appl. 3(3):283–297: total thrust of a mini quadcopter rises linearly near the ground, becoming piecewise linear and then quadratic as rotor spacing grows. Built from "a series of experiments" and validated in flight. DOI 10.1007/s41315-019-00098-z (CrossRef; abstract on eScholarship).
- **Kan et al. 2019** (Bib), RA-L 4(4):3860–3867: forward-flight GE models with speed terms, fitted from rotor-speed data on an AscTec Hummingbird (0.55 kg, $R=0.10$ m) and validated on a Crazyflie 2.0 ($z/R\approx1.5$–5, $V\le2.1$ m/s). DOI 10.1109/LRA.2019.2929993.
- **He & Leang 2020**, AIAA J. 58(12):5318–5331: quasi-steady model without singularity. Two coefficients from blade-element theory and images (pitch, solidity, radius), plus an empirical multirotor thrust-loss term; each component validated by experiments. DOI 10.2514/1.J059223 (CrossRef; abstract via OpenAlex).
- **Matus-Vargas, Rodríguez-Gómez & Martínez-Carranza 2021** (Bib, key `Matus2020`), Intell. Serv. Robot. 14(1):99–118: review. Its abstract could not be retrieved this round; metadata verified earlier. DOI 10.1007/s11370-020-00344-5.
- **Carter, Bouchard & Quinn 2021** (Bib), AIAA J. 59(4):1398–1405: Crazyflie 2.0 tethered to a load cell. Lift rises by up to about 20% near the ground, more than twice the classical prediction. The Sanchez-Cuevas model with $K_b\approx2$ fits ($R^2=0.956$, $1<z/R<3$). Ceiling gives up to about 60%, the wall under 5%. DOI 10.2514/1.J059787 (full text read).
- **Tanabe et al. 2021**, J. Robot. Mechatron. 33(2):339–347: CFD of a variable-pitch quadrotor at constant thrust. Power falls near the ground, rises locally at about one rotor radius because of recirculation, then falls again. Outwash is anisotropic. DOI 10.20965/jrm.2021.p0339.
- **Garofano-Soldado, Sanchez-Cuevas, Heredia & Ollero 2022**, Aerosp. Sci. Technol. 126:107625: thrust model for tilted propellers as a function of distance and tilt, from a test bench plus CFD. Small propellers at low Reynolds number. DOI 10.1016/j.ast.2022.107625 (CrossRef).
- **Garofano-Soldado, González-Morgado, Heredia & Ollero 2024**, RA-L 9(2):1907–1914: two models for a fully actuated hexarotor (radius, inter-rotor distance, height, tilt) from a static test bench, used in control. DOI 10.1109/LRA.2024.3350975 (OpenAlex).
- **Franzetti et al. 2024 JINT** (Bib), 110(3):125: six-axis force/torque stands at about 1000 hPa (terraXcube) and 800 hPa (Denver) for ground, ceiling and wall effects. A dimensionless coefficient and an uncertainty analysis; no fitted model in the abstract. DOI 10.1007/s10846-024-02155-7.
- **Franzetti, Parin, Carminati & Capello 2024 ICUAS**, pp. 405–412: an exponential parametric fit and Gaussian-process regression of test-bed thrust (10×4.7 and 12×5 propellers) near ground and ceiling. DOI 10.1109/ICUAS60882.2024.10557056 (OpenAlex).
- **Wolf et al. 2024**, Exp. Fluids 65(10):152: Shake-The-Box particle tracking of a free-flying quadcopter (about 0.5 m span). In ground effect, power drops, flow recirculates between the rotors, and outward jets form. Flow evidence, no model. DOI 10.1007/s00348-024-03880-3.
- **He & Leang 2025**, Aerosp. Sci. Technol. 156:109748: GE models that include advance ratio and climb velocity, with extensive experimental validation. There is an extra thrust gain at $\mu<0.04$ and $z/R<0.5$. Quadcopter-scale. DOI 10.1016/j.ast.2024.109748 (OpenAlex; abstract from the BUAA portal).
- **Lei et al. 2026**, Phys. Fluids 38(7):075139: experiments plus transient CFD on a small-spacing quadrotor. Thrust is nonmonotonic, with a negative-GE region near $h/R\approx1.5$ caused by fountain flow. DOI 10.1063/5.0337114.

### Theme 3. Partial, finite, edge and dynamic ground effect

- **Sanchez-Cuevas et al. 2017** (as above). Partial GE (one or three rotors over a plate) gives a disturbing moment. A plate under one rotor at $z/R=2$ raised the pitch angle on the bench and in outdoor flight, and PID corrected it poorly. In simulation, PID oscillated near the obstacle. A nonlinear disturbance observer and a map-based feedforward did better; a 15 cm map offset destabilized the feedforward.
- **Del Cont Bernard, Riccardi, Giurato & Lovera 2017**, IFAC-PapersOnLine 50(1):10311–10316: experimental campaign on the *dynamic* GE of a quadrotor, after a static characterization of the same platform (Del Cont Bernard et al., *Adv. Aerosp. GNC* 2018, pp. 351–368, DOI 10.1007/978-3-319-65283-2_19). **The abstract states no specific findings.** DOI 10.1016/j.ifacol.2017.08.1500 (CrossRef).
- **Xin, Li, Chen & Liu 2017**, Acta Aeronaut. Astronaut. Sin. 38(3):120219: free-wake (time-stepping) model for a rotor over *finite* ground, with a "material line" correction for wake filaments that cross the ground. Validated with their own thrust, torque and flapping tests in hover and forward flight. Helicopter rotor. DOI 10.7527/S1000-6893.2016.0221 (**publisher page only**; CrossRef and OpenAlex API calls failed).
- **Prothin, Fernandez Escudero, Doué & Jardin 2019**, Int. J. Micro Air Veh. 11: a MAV rotor near the ground and in a wall-ground corner; a numerical model validated by experiments. DOI 10.1177/1756829319861596.
- **Shi et al. 2019** (Neural Lander), ICRA 2019:9784–9790: a DNN residual force, trained offline on observed flight disturbances, used in a stable nonlinear controller for landing and a cross-table trajectory (GE appears and disappears at the table edges). Intel Aero, about 1.47 kg (earlier round). DOI 10.1109/ICRA.2019.8794351.
- **He, Zhang, Lai, Liu & Wang 2024**, IROS 2024:8169–8174: a parsimonious data-driven GE model in velocity, throttle, platform motion and past states, used in a feedforward controller for landing on a vertically oscillating platform. Flight experiments on fixed and oscillating platforms. DOI 10.1109/IROS58592.2024.10802474 (CrossRef; abstract via Semantic Scholar).
- **Yon & Li 2026**, VFS VLADA Specialists' Conf., San Jose, pp. 1–11: a model rotor at partial ground coverage, measured with a six-axis transducer and time-resolved PIV. A semi-empirical thrust ratio spans out-of-ground to full GE, and thrust correlates with a **circular-segment rotor-ground interaction area**. DOI 10.4050/SM-2026-VLADA-5207 (CrossRef).
- **Herz, Taylor, Clar & McCrink 2026**, VFS 82nd Forum, pp. 1–18: a free-flying quadrotor near a partial boundary (facade or vertiport edge), in still air and wind. Partial GE does not resemble full GE until most of the vehicle has passed over, and the airframe drives the onset. DOI 10.4050/F-0082-2026-0091 (CrossRef).
- Dynamic and history effects are also in Curtiss 1984 (acceleration), Yu & Peters 2005, Pasquali 2023 (moving ground) and He & Leang 2025 (climb velocity).

### Theme 4. GE identified or compensated within control

- **Nonlinear disturbance observer and feedforward:** He et al. 2019 (exponential model plus NDO), Sanchez-Cuevas et al. 2017 (NDO and map-based feedforward).
- **Wei et al. 2019:** a GE model identified from experiments, then MRAC in the altitude loop. In flight it improved altitude tracking over PID (up to 80% shorter rise time in GE).
- **Li Danjun et al. 2015:** a Cheeseman-type quadrotor model, a GE compensator and robust PID for landing.
- **Li Xia, Qi, Wang, Li, Deng, Guo & Quan 2024**, Nonlinear Dyn. 112(17):15349–15375: a compensation-function observer estimates GE forces and moments, and **a GE model is identified from the observer estimates in hovering flights**. Two proximate 450 mm quadrotors with optical positioning. DOI 10.1007/s11071-023-09124-z (CrossRef).
- **Xu et al. 2022**, Aerosp. Sci. Technol. 131:107976: the title claims GE identification plus "intelligent" control. **No abstract was accessible** (CrossRef, OpenAlex and Semantic Scholar have none; ScienceDirect is blocked). Topic tags suggest DNN, adaptive control, EKF and a PID comparison, but this is unverified. DOI 10.1016/j.ast.2022.107976.
- **Learned models:** Shi et al. 2019 (DNN residual), He et al. 2024 (data-driven, history-dependent), Franzetti et al. 2024 ICUAS (GPR on stand data).
- **Yang, Chai, Ji, Wu, Xu & Gao 2025**, arXiv:2506.19424v1 (preprint, no journal version found): extra lift, a leveling external torque, and rotor-drag and mixing changes, from force platforms and real flights. Dynamic inversion with feedforward; 45.3% lower RMSE. DOI 10.48550/arXiv.2506.19424 (DataCite).
- **Grey-box multirotor identification (not GE):** Sun, de Visser & Chu 2019, J. Aircraft 56(2):645–661. Stepwise regression from free flights in a wind tunnel; helicopter-theory models proved inaccurate, and moment residuals fell by about 80%. DOI 10.2514/1.C035135 (OpenAlex). Also NeuroBEM (Bauersfeld et al., RSS 2021, DOI 10.15607/RSS.2021.XVII.042; verified in the earlier round, not GE).
- **GP residual dynamics in MPC (not GE):** Torrente et al. 2021, RA-L 6(2):3769–3776, DOI 10.1109/LRA.2021.3061307.

### Theme 5. System identification and optimal experiment design for flight vehicles

- **Mehra 1974; Goodwin & Payne 1977; Hjalmarsson 2005; Ljung 1999** (all Bib).
- **Franceschini & Macchietto 2008**, Chem. Eng. Sci. 63(19):4846–4872, DOI 10.1016/j.ces.2007.11.034 (verified in the earlier round).
- **Morelli & Klein 2016**, *Aircraft System Identification: Theory and Practice*, 2nd ed., Sunflyte Enterprises, ISBN 978-0-9974306-1-5. Covers the whole identification process including experiment design (MathWorks book page). No DOI.
- **Jategaonkar 2015**, *Flight Vehicle System Identification: A Time-Domain Methodology*, 2nd ed., AIAA Progress in Astronautics and Aeronautics vol. 245, Reston, VA. Chapters on data gathering and on output-error, filter-error and equation-error methods. DOI 10.2514/4.102790 (CrossRef; CiNii; table of contents).
- **Tischler & Remple 2012**, *Aircraft and Rotorcraft System Identification*, AIAA (2nd ed.; frequency domain). DOI 10.2514/4.868207 (OpenAlex).
- **Wilson, Schultz & Murphey 2014**, IEEE T-RO 30(6):1358–1370: optimizes a trajectory to increase the norm of the Fisher information matrix. In simulation the smallest eigenvalue rose by about three orders of magnitude; experiments on a cart with a double pendulum. DOI 10.1109/TRO.2014.2345918.
- **Bähnemann, Burri, Galceran, Siegwart & Nieto 2017**, ICRA 2017:3931–3938: sampling-based planning of maximally informative trajectories for multirotor model and calibration parameters, with EKF belief propagation. Flight-validated; parameter convergence about four times faster. DOI 10.1109/ICRA.2017.7989453 (CrossRef).
- **Lopez-Sanchez, Montoya-Chairez, Perez-Alcocer & Moreno-Valenzuela 2020**, IEEE Access 8:167355–167370: an excitation trajectory optimized under position, velocity and acceleration limits, tracked by PID, and estimated by least squares and gradient methods. Quadrotor rigid-body parameters, no GE. DOI 10.1109/ACCESS.2020.3023643 (CrossRef).
- **Vitale, Genito, Garbarino, Ciniglio & Corraro 2010**, Aeronaut. J. 114(1156):377–385: **GE parameters identified from flight data** of an ultralight aircraft. Equation error in the frequency domain, then time-domain identification, and it works without dedicated maneuvers. DOI 10.1017/S0001924000003833 (OpenAlex; Cambridge page).
- **Holder & Tritschler 2019**, VFS 75th Forum, pp. 1–13: a *designed* flight test (test matrix, not optimal design) of a UH-72A hovering in ground effect over sloped terrain. Required power can exceed the out-of-ground-effect value. DOI 10.4050/F-0075-2019-14735 (CrossRef).
- **Search result for "informative trajectories to identify near-ground aerodynamics":** none found for multirotors. Several phrasings were tried (WebSearch; arXiv; publisher pages). The closest works are Bähnemann 2017 and Lopez-Sanchez 2020 (other parameters), Vitale 2010 (GE from flight data, no designed maneuvers) and Holder 2019 (test matrix). This supports the gap sentence in (c), worded as "to our knowledge".

---

## (b) Verification of the references proposed in PAPER_REVIEW_V2

| # | Key (review) | Exists | Metadata in review BibTeX | Review's content claim | Verdict |
|---|---|---|---|---|---|
| 1 | SanchezCuevas2017 | Yes (CrossRef) | Correct; `pages` holds the article ID (17 pp.) | Multirotor and partial GE linked to control: **supported** (full text) | OK |
| 2 | DelContBernard2017 | Yes (CrossRef, PoliMi IRIS) | Correct (50(1):10311–10316). CrossRef mis-splits the name as given "Davide Del Cont"; the review's form is right | "Direct experimental evidence that dynamic GE differs from static": **partly supported**. The abstract says a dynamic campaign follows a static one but gives no finding | Use the softer wording |
| 3 | Xin2017 | Yes (publisher page) | No BibTeX in review; entry below. 38(3):120219 | Finite (not infinite) ground; theory plus experiment: **supported**. Note that it is a helicopter rotor, not a MAV | Add with care (DOI not resolvable through the APIs) |
| 4 | Prothin2019 | Yes (CrossRef) | Missing article number; CrossRef gives initials only; "Doué" | Ground and corner effect on a MAV rotor: **supported** | Minor fix |
| 5 | Tanabe2021 | Yes | Correct | Recirculation and nonmonotonic power: **supported**, but it is **CFD only** (variable pitch, constant thrust) | OK |
| 6 | Wolf2024 | Yes | Missing issue 10; "Strübing", "Schröder" | Wake merging, recirculation, outward jets in GE: **supported** ("anisotropic outwash" is the review's paraphrase) | Minor fix |
| 7 | Lei2026 | Yes (CrossRef) | Correct | Nonmonotonic thrust, negative GE near $h/R\approx1.5$: **supported** | OK, and important (see main point 3) |
| 8 | Wei2019 | Yes | Correct | GE identification then MRAC, flight comparison with PID: **supported** | OK |
| 9 | Xu2022GroundEffect | Yes | Correct (CrossRef: Guoxi Xu ... Shengping Gong; 131:107976) | "Compares adaptive and neural compensation with PID using experiments": **not verifiable**, no abstract accessible | Do not cite for content until read |
| 10 | He2024 | Yes | Correct | Velocity, throttle, platform motion, history; parsimonious; onboard: **supported** | OK |
| 11 | Yang2025 | Yes (arXiv v1, DataCite) | No BibTeX in review; entry below | Force, torque, rotor drag, mixing: **supported**; no journal version found | Cite as a preprint |
| 12 | Torrente2021 | Yes | "Foehn" should be "F{\"o}hn" | GP residual dynamics in MPC: **supported** (not GE) | Minor fix |
| 13 | Meraglia2021 | Yes | Correct (L-CSS 6:1501–1506, issued 2022; online 2021) | Smoother-based ILC; model from black-box subspace identification; quadrotor experiments: **supported** | OK |
| 14 | KrauseOng2011 | Yes (NeurIPS; ETH record) | Missing pp. 2447–2455 | Payoff modeled as a GP over the joint context-action space: **supported** | Minor fix |
| 15 | Eriksson2019 | Yes (NeurIPS 32 page) | Correct (pages not checked) | Local or trust-region BO (TuRBO): consistent with the title (abstract not read) | OK |
| 16 | Sui2015 | Yes (PMLR 37:997–1005) | No BibTeX in review; entry below | SafeOpt with a safety threshold and guarantees: **supported** | OK |
| 17 | Sui2018 | Yes (PMLR 80:4781–4789) | No BibTeX in review; entry below | Stagewise safe BO: title-level | OK |
| 18 | MendezRT2026 | Yes (DataCite: v1 submitted 2026-11-02, eess.SY) | Correct | The title and authors match the manuscript's `Mendez2026` | Replace the `@unpublished` entry |

**Corrected or missing BibTeX** (only entries that change):

```bibtex
@article{DelContBernard2017,
  author  = {{Del Cont Bernard}, Davide and Riccardi, Fabio and Giurato, Mattia and Lovera, Marco},
  title   = {A Dynamic Analysis of Ground Effect for a Quadrotor Platform},
  journal = {IFAC-PapersOnLine},
  volume  = {50},
  number  = {1},
  pages   = {10311--10316},
  year    = {2017},
  doi     = {10.1016/j.ifacol.2017.08.1500}
}

@article{Xin2017,
  author  = {Xin, Ji and Li, Pan and Chen, Renliang and Liu, Dawei},
  title   = {Theoretical Model and Experiment on Rotor in Finite Ground Effect},
  journal = {Acta Aeronautica et Astronautica Sinica},
  volume  = {38},
  number  = {3},
  pages   = {120219},
  year    = {2017},
  doi     = {10.7527/S1000-6893.2016.0221}
}
% The journal publishes mostly in Chinese; check the PDF and add note = {in Chinese} if so.

@article{Prothin2019,
  author  = {Prothin, S. and {Fernandez Escudero}, C. and Dou{\'e}, N. and Jardin, T.},
  title   = {Aerodynamics of {MAV} Rotors in Ground and Corner Effect},
  journal = {International Journal of Micro Air Vehicles},
  volume  = {11},
  pages   = {1756829319861596},
  year    = {2019},
  doi     = {10.1177/1756829319861596}
}

@article{Wolf2024,
  author  = {Wolf, C. Christian and Schanz, Daniel and Schwarz, Clemens and Heintz, Alexander and Bosbach, Johannes and Str{\"u}bing, Tobias and Schr{\"o}der, Andreas},
  title   = {Volumetric Wake Investigation of a Free-Flying Quadcopter Using {Shake-The-Box} {Lagrangian} Particle Tracking},
  journal = {Experiments in Fluids},
  volume  = {65},
  number  = {10},
  pages   = {152},
  year    = {2024},
  doi     = {10.1007/s00348-024-03880-3}
}

@article{Torrente2021,
  author  = {Torrente, Guillem and Kaufmann, Elia and F{\"o}hn, Philipp and Scaramuzza, Davide},
  title   = {Data-Driven {MPC} for Quadrotors},
  journal = {IEEE Robotics and Automation Letters},
  volume  = {6},
  number  = {2},
  pages   = {3769--3776},
  year    = {2021},
  doi     = {10.1109/LRA.2021.3061307}
}

@inproceedings{KrauseOng2011,
  author    = {Krause, Andreas and Ong, Cheng S.},
  title     = {Contextual {Gaussian} Process Bandit Optimization},
  booktitle = {Advances in Neural Information Processing Systems 24},
  editor    = {Shawe-Taylor, J. and Zemel, R. S. and Bartlett, P. L. and Pereira, F. and Weinberger, K. Q.},
  publisher = {Curran Associates},
  pages     = {2447--2455},
  year      = {2011}
}

@inproceedings{Sui2015,
  author    = {Sui, Yanan and Gotovos, Alkis and Burdick, Joel and Krause, Andreas},
  title     = {Safe Exploration for Optimization with {Gaussian} Processes},
  booktitle = {Proc. 32nd Int. Conf. Mach. Learn. (ICML)},
  series    = {Proceedings of Machine Learning Research},
  volume    = {37},
  pages     = {997--1005},
  year      = {2015}
}

@inproceedings{Sui2018,
  author    = {Sui, Yanan and Zhuang, Vincent and Burdick, Joel and Yue, Yisong},
  title     = {Stagewise Safe {Bayesian} Optimization with {Gaussian} Processes},
  booktitle = {Proc. 35th Int. Conf. Mach. Learn. (ICML)},
  series    = {Proceedings of Machine Learning Research},
  volume    = {80},
  pages     = {4781--4789},
  year      = {2018}
}
```

`Yang2025` is given in (d). The review's `MendezRT2026` entry can replace `Mendez2026` as written.

---

## (c) Proposed replacement for the GE paragraph (line 45)

Three paragraphs, 379 words excluding citations. They replace the paragraph that begins "Ground effect (GE), by contrast, has been investigated since..." and end on the gap. Two follow-up edits are needed:

- Line 47 opens with "These limitations matter in cluttered flight because...". Change it to "Accurate GE prediction matters in cluttered flight because...", since the new text ends on the gap and not on "limitations".
- `Matus2020` is no longer cited in this paragraph but remains at line 43.

```latex
Ground effect (GE) has been studied since the 1950s for helicopter rotors. A surface below the rotor redirects the wake and reduces the induced velocity and power. Cheeseman and Bennett derived the resulting thrust gain of an isolated rotor from its normalized clearance and forward speed~\cite{CheesemanBennett1955}, and rotor experiments showed that the near-ground flow changes regime with advance ratio and also depends on translational acceleration~\cite{Curtiss1984}. In multirotors, rotor-rotor interaction and the flow beneath the central body change this response. Their GE has been described by adding image rotors and an empirical body coefficient to the classical model~\cite{SanchezCuevas2017}, or by exponential, quasi-steady, and Gaussian-process models of measured thrust~\cite{He2019,HeLeang2020,Franzetti2024ICUAS}. On a tethered Crazyflie~2.0, the near-ground lift increase exceeded twice the classical prediction~\cite{Carter2021}, whereas computations and experiments on other quadrotors report a nonmonotonic power or thrust response near one to one and a half rotor radii~\cite{Tanabe2021,Lei2026}.

Flight near obstacles adds two complications. First, the surface may lie under only some rotors. The resulting thrust imbalance produces a moment that a cascaded PID controller rejects poorly~\cite{SanchezCuevas2017}. For a single rotor, partial-coverage thrust has been correlated with the rotor-surface overlap area~\cite{Yon2026}, whereas free-flight tests near a building-like edge found that full GE develops only after most of the vehicle has crossed the edge~\cite{Herz2026}. Second, GE is not static. It varies with forward and climb speed~\cite{Kan2019,HeLeang2025} and with the motion of the surface~\cite{He2024}, and it has been characterized in dynamic as well as static quadrotor tests~\cite{DelContBernard2017}.

Control studies compensate GE online or learn it from data. Adaptive control~\cite{Wei2019} and disturbance observers~\cite{He2019,LiX2024} counter the near-ground force, and Li et al.~\cite{LiX2024} also fitted a GE model to observer estimates from hovering flights. Deep networks trained on flight data~\cite{Shi2019} and richer models that include surface motion and past states~\cite{He2024} or GE torques and rotor drag~\cite{Yang2025} provide feedforward or model-based compensation. None of these studies, to our knowledge, selects flights by their information about the GE parameters. Flight-vehicle system identification, by contrast, designs the inputs to maximize the information on the parameters~\cite{Mehra1974,Morelli2016}, and informative trajectories have been planned for other multirotor parameters~\cite{Bahnemann2017}. Here, a two-parameter clearance law, weighted by the fraction of each rotor disk above the obstacle, is identified from E-optimal flights of the complete closed-loop vehicle crossing a finite obstacle, including the partial coverage at its edges.
```

### Sentence-to-source map

| # | Sentence (opening words) | Source(s) | What in the source supports it |
|---|---|---|---|
| 1 | "Ground effect (GE) has been studied since the 1950s..." | CheesemanBennett1955 (cited in S3) | ARC R&M 3021, dated 1955 |
| 2 | "A surface below the rotor redirects the wake..." | No citation in text (textbook physics). Support if wanted: Carter2021, Tanabe2021, Wolf2024 | Carter: PIV shows a 6% downwash reduction near the ground. Tanabe and Wolf: power demand falls in GE. The CB image model rests on reduced inflow |
| 3 | "Cheeseman and Bennett derived the resulting thrust gain..." | CheesemanBennett1955; Curtiss1984 | CB formula in clearance and $V/v_i$ (scan read in the earlier round). Curtiss abstract: three flow regimes with advance ratio; translational acceleration significant |
| 4 | "In multirotors, rotor-rotor interaction and the flow beneath the central body..." | Supported by the S5 references | Sanchez-Cuevas: interaction terms alone do not reproduce the data, a body term is needed. He & Leang 2020: multirotor configuration and thrust loss. Lei: fountain flow |
| 5 | "Their GE has been described by adding image rotors..." | SanchezCuevas2017; He2019; HeLeang2020; Franzetti2024ICUAS | Eq. 4 with $K_b\approx2$ from the test bench (full text). Exponential model validated by experiments (abstract). BET and image coefficients plus empirical thrust loss (abstract). Exponential fit and GPR on test-bed data (abstract) |
| 6 | "On a tethered Crazyflie 2.0..." | Carter2021; Tanabe2021; Lei2026 | Up to about 20%, "more than twice what classic theory predicts" (full text). Local power rise at about 1R (CFD abstract). Negative GE near $h/R\approx1.5$ (abstract) |
| 7 | "Flight near obstacles adds two complications." | Framing | — |
| 8 | "First, the surface may lie under only some rotors." | SanchezCuevas2017 (S9) | Definition of partial GE |
| 9 | "The resulting thrust imbalance produces a moment..." | SanchezCuevas2017 | Moment $M_{ge1}$; plate under one rotor raised pitch and PID corrected it poorly; simulated PID oscillated near the obstacle (full text) |
| 10 | "For a single rotor, partial-coverage thrust..." | Yon2026; Herz2026 | Circular-segment interaction area correlated with thrust (abstract). Partial GE unlike full GE until most of the vehicle has passed over (abstract) |
| 11 | "Second, GE is not static." | Framing, supported by S12 | — |
| 12 | "It varies with forward and climb speed..." | Kan2019; HeLeang2025; He2024; DelContBernard2017 | Forward-speed dependence (full text, earlier round). Advance ratio and climb velocity (abstract). Platform motion and past states (abstract). Dynamic campaign after a static one (abstract) |
| 13 | "Control studies compensate GE online or learn it from data." | Framing, supported by S14–S15 | — |
| 14 | "Adaptive control and disturbance observers..." | Wei2019; He2019; LiX2024 | MRAC in the altitude loop, tested in flight (abstract). NDO, 23% lower error (abstract). Observer estimates used to identify a GE model in hovering experiments (abstract) |
| 15 | "Deep networks trained on flight data..." | Shi2019; He2024; Yang2025 | DNN residual trained offline on observed disturbance forces (arXiv text). History-dependent data-driven model with feedforward (abstract). Torque and rotor-drag model with feedforward (abstract) |
| 16 | "None of these studies, to our knowledge, selects flights..." | Author's judgment | Based on the abstracts above, the full texts of Sanchez-Cuevas, Carter and Kan, and the searches in Theme 5. No source designs flights by information content about GE parameters |
| 17 | "Flight-vehicle system identification, by contrast..." | Mehra1974; Morelli2016; Bahnemann2017 | Survey of optimal input signals for parameter estimation (Bib). The book covers experiment design (publisher description). Maximally informative multirotor trajectories, validated in flight (abstract) |
| 18 | "Here, a two-parameter clearance law..." | This manuscript | Eqs. (fge) and (corrected-thrust), with $\chi_i$ the overlap fraction; Eq. (rt-e-optimal)/(e-optimal-design); twelve information flights with the unchanged PID loop replayed in the DT |

---

## (d) BibTeX

### New keys used in (c)

Keys used in (c) that are already in the .bib: `CheesemanBennett1955` (apply the title fix from the earlier round), `Carter2021`, `Kan2019`, `Mehra1974`.

```bibtex
@article{Curtiss1984,
  author  = {Curtiss, Jr., H. C. and Sun, Mao and Putman, William F. and Hanker, Edward J.},
  title   = {Rotor Aerodynamics in Ground Effect at Low Advance Ratios},
  journal = {Journal of the American Helicopter Society},
  volume  = {29},
  number  = {1},
  pages   = {48--55},
  year    = {1984},
  doi     = {10.4050/JAHS.29.48}
}

@article{SanchezCuevas2017,
  author  = {Sanchez-Cuevas, Pedro and Heredia, Guillermo and Ollero, Anibal},
  title   = {Characterization of the Aerodynamic Ground Effect and Its Influence in Multirotor Control},
  journal = {International Journal of Aerospace Engineering},
  volume  = {2017},
  pages   = {1823056},
  year    = {2017},
  doi     = {10.1155/2017/1823056}
}

@article{He2019,
  author  = {He, Xiang and Kou, Gordon and Calaf, Marc and Leang, Kam K.},
  title   = {In-Ground-Effect Modeling and Nonlinear-Disturbance Observer for Multirotor Unmanned Aerial Vehicle Control},
  journal = {Journal of Dynamic Systems, Measurement, and Control},
  volume  = {141},
  number  = {7},
  pages   = {071013},
  year    = {2019},
  doi     = {10.1115/1.4043221}
}

@article{HeLeang2020,
  author  = {He, Xiang and Leang, Kam K.},
  title   = {Quasi-Steady In-Ground-Effect Model for Single and Multirotor Aerial Vehicles},
  journal = {AIAA Journal},
  volume  = {58},
  number  = {12},
  pages   = {5318--5331},
  year    = {2020},
  doi     = {10.2514/1.J059223}
}

@inproceedings{Franzetti2024ICUAS,
  author    = {{David Du Mutel de Pierrepont Franzetti}, Iris and Parin, Riccardo and Carminati, Davide and Capello, Elisa},
  title     = {Modelling of Ground and Ceiling Effects for Quadcopters Based on Experimental Data},
  booktitle = {Proc. Int. Conf. Unmanned Aircraft Systems (ICUAS)},
  pages     = {405--412},
  year      = {2024},
  doi       = {10.1109/ICUAS60882.2024.10557056}
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

@inproceedings{Yon2026,
  author    = {Yon, Steven and Li, Sicheng},
  title     = {Experimental Investigation of Half-Ground Effects on Hovering Rotor Aerodynamics},
  booktitle = {Proc. Vertical Lift Aircraft Design and Aeromechanics Specialists' Conf.},
  address   = {San Jose, CA, USA},
  publisher = {Vertical Flight Society},
  pages     = {1--11},
  month     = jan,
  year      = {2026},
  doi       = {10.4050/SM-2026-VLADA-5207}
}

@inproceedings{Herz2026,
  author    = {Herz, Sage and Taylor, Julia and Clar, Lauren and McCrink, Matthew},
  title     = {Effects of Partial Boundaries and Variable Wind Conditions on a Free-Flying Multirotor Platform},
  booktitle = {Proc. Vertical Flight Society 82nd Annual Forum and Technology Display},
  address   = {West Palm Beach, FL, USA},
  pages     = {1--18},
  month     = may,
  year      = {2026},
  doi       = {10.4050/F-0082-2026-0091}
}

@article{HeLeang2025,
  author  = {He, Xiang and Leang, Kam K.},
  title   = {Rotorcraft In-Ground Effect Models in Axial and Forward Flight},
  journal = {Aerospace Science and Technology},
  volume  = {156},
  pages   = {109748},
  year    = {2025},
  doi     = {10.1016/j.ast.2024.109748}
}

@inproceedings{He2024,
  author    = {He, Binglin and Zhang, Heng and Lai, Baisheng and Liu, Song and Wang, Yang},
  title     = {Data-Driven Modeling of Ground Effect for {UAV} Landing on a Vertical Oscillating Platform},
  booktitle = {Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)},
  pages     = {8169--8174},
  year      = {2024},
  doi       = {10.1109/IROS58592.2024.10802474}
}

@article{DelContBernard2017,
  author  = {{Del Cont Bernard}, Davide and Riccardi, Fabio and Giurato, Mattia and Lovera, Marco},
  title   = {A Dynamic Analysis of Ground Effect for a Quadrotor Platform},
  journal = {IFAC-PapersOnLine},
  volume  = {50},
  number  = {1},
  pages   = {10311--10316},
  year    = {2017},
  doi     = {10.1016/j.ifacol.2017.08.1500}
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

@article{LiX2024,
  author  = {Li, Xia and Qi, Guoyuan and Wang, Shuai and Li, Kuo and Deng, Jiahao and Guo, Xitong and Quan, Quan},
  title   = {Stable Hovering of Proximity Quadrotor {UAV} In-Ground Effect via Model Compensation Controller},
  journal = {Nonlinear Dynamics},
  volume  = {112},
  number  = {17},
  pages   = {15349--15375},
  year    = {2024},
  doi     = {10.1007/s11071-023-09124-z}
}

@inproceedings{Shi2019,
  author    = {Shi, Guanya and Shi, Xichen and O'Connell, Michael and Yu, Rose and Azizzadenesheli, Kamyar and Anandkumar, Animashree and Yue, Yisong and Chung, Soon-Jo},
  title     = {Neural Lander: Stable Drone Landing Control Using Learned Dynamics},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {9784--9790},
  year      = {2019},
  doi       = {10.1109/ICRA.2019.8794351}
}

@misc{Yang2025,
  author       = {Yang, Tiankai and Chai, Kaixin and Ji, Jialin and Wu, Yuze and Xu, Chao and Gao, Fei},
  title        = {Ground-Effect-Aware Modeling and Control for Multicopters},
  howpublished = {arXiv:2506.19424},
  year         = {2025},
  doi          = {10.48550/arXiv.2506.19424}
}

@book{Morelli2016,
  author    = {Morelli, Eugene A. and Klein, Vladislav},
  title     = {Aircraft System Identification: Theory and Practice},
  edition   = {2nd},
  publisher = {Sunflyte Enterprises},
  year      = {2016},
  isbn      = {978-0-9974306-1-5}
}

@inproceedings{Bahnemann2017,
  author    = {B{\"a}hnemann, Rik and Burri, Michael and Galceran, Enric and Siegwart, Roland and Nieto, Juan},
  title     = {Sampling-Based Motion Planning for Active Multirotor System Identification},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {3931--3938},
  year      = {2017},
  doi       = {10.1109/ICRA.2017.7989453}
}
```

Notes: the article number of `He2019`, the pages of `Shi2019` and the CrossRef records of `Wei2019` and `Torrente2021` were confirmed in this round or in the earlier one. Sources: `Curtiss1984` and `LiX2024` from CrossRef/OpenAlex; `Morelli2016` from the MathWorks book page (no DOI exists).

### Further recommended additions (8)

| Key | Where to cite (verbatim, at most 15 words) | Suggested use |
|---|---|---|
| Sharf2014 | "the identified amplitude is almost twice the classical value" (Results) | `\cite{Carter2021,Sharf2014}`: small multirotors show a stronger GE than the classical model on load cells and stands |
| Pasquali2023 | "The formulation also omits the transient development and decay of the rotor-surface interaction" (Sec. II-B) | With `DelContBernard2017` and `Curtiss1984`: dynamic-inflow models that capture these transients exist but need more states |
| Xin2017 | "The obstacle considered here occupies only a finite streamwise interval" (Sec. II-B) | With `Yon2026` (overlap-area model, support for $\chi_i$) and `Herz2026` (whole-vehicle edge effect, limitation) |
| Prothin2019 | "A vehicle passing through a narrow tunnel may experience floor, ceiling, and lateral-wall interactions" (line 43) | Ground and corner effect on MAV rotors |
| Vitale2010 | "design and perform trajectories that improve the identification of the unknown parameters" (Sec. II-C) | GE parameters have been identified from aircraft flight data, without designed maneuvers |
| Jategaonkar2015 | "This is the discrete-adjoint formulation of the identification problem" (Sec. II-C) | The loss is an output-error criterion of flight-vehicle identification, minimized here with adjoint gradients |
| Wilson2014 | "which selects the safe candidate predicted to increase the Fisher information along its weakest direction" | Trajectory synthesis that maximizes Fisher information, including its smallest eigenvalue |
| Sun2019 | "Adding states and correction terms may reduce this model discrepancy" (line 56) | Grey-box multirotor identification from flight data, where helicopter-theory terms were inaccurate |

Also cite `Lei2026` at "This model is deliberately low order: ground effect is treated as a static function" (Sec. II-B), as discussed in main point 3.

```bibtex
@inproceedings{Sharf2014,
  author    = {Sharf, I. and Nahon, M. and Harmat, A. and Khan, W. and Michini, M. and Speal, N. and Trentini, M. and Tsadok, T. and Wang, T.},
  title     = {Ground Effect Experiments and Model Validation with {Draganflyer X8} Rotorcraft},
  booktitle = {Proc. Int. Conf. Unmanned Aircraft Systems (ICUAS)},
  address   = {Orlando, FL, USA},
  pages     = {1158--1166},
  year      = {2014},
  doi       = {10.1109/ICUAS.2014.6842370}
}

@article{Pasquali2023,
  author  = {Pasquali, Claudio and Gennaretti, Massimo and Bernardini, Giovanni and Serafini, Jacopo},
  title   = {State-Space Dynamic Inflow Modelling for Hovering Rotors in Fixed- and Moving-Ground Effect},
  journal = {Aerospace Science and Technology},
  volume  = {140},
  pages   = {108414},
  year    = {2023},
  doi     = {10.1016/j.ast.2023.108414}
}

@article{Xin2017,
  author  = {Xin, Ji and Li, Pan and Chen, Renliang and Liu, Dawei},
  title   = {Theoretical Model and Experiment on Rotor in Finite Ground Effect},
  journal = {Acta Aeronautica et Astronautica Sinica},
  volume  = {38},
  number  = {3},
  pages   = {120219},
  year    = {2017},
  doi     = {10.7527/S1000-6893.2016.0221}
}

@article{Prothin2019,
  author  = {Prothin, S. and {Fernandez Escudero}, C. and Dou{\'e}, N. and Jardin, T.},
  title   = {Aerodynamics of {MAV} Rotors in Ground and Corner Effect},
  journal = {International Journal of Micro Air Vehicles},
  volume  = {11},
  pages   = {1756829319861596},
  year    = {2019},
  doi     = {10.1177/1756829319861596}
}

@article{Vitale2010,
  author  = {Vitale, Antonio and Genito, Nicola and Garbarino, Luca and Ciniglio, Umberto and Corraro, Federico},
  title   = {A Hybrid Frequency-Time Domain Technique for Ground Effect Identification},
  journal = {The Aeronautical Journal},
  volume  = {114},
  number  = {1156},
  pages   = {377--385},
  year    = {2010},
  doi     = {10.1017/S0001924000003833}
}

@book{Jategaonkar2015,
  author    = {Jategaonkar, Ravindra V.},
  title     = {Flight Vehicle System Identification: A Time-Domain Methodology},
  edition   = {2nd},
  series    = {Progress in Astronautics and Aeronautics},
  volume    = {245},
  publisher = {American Institute of Aeronautics and Astronautics},
  address   = {Reston, VA, USA},
  year      = {2015},
  doi       = {10.2514/4.102790}
}

@article{Wilson2014,
  author  = {Wilson, Andrew D. and Schultz, Jarvis A. and Murphey, Todd D.},
  title   = {Trajectory Synthesis for {Fisher} Information Maximization},
  journal = {IEEE Transactions on Robotics},
  volume  = {30},
  number  = {6},
  pages   = {1358--1370},
  year    = {2014},
  doi     = {10.1109/TRO.2014.2345918}
}

@article{Sun2019,
  author  = {Sun, Sihao and de Visser, Coen C. and Chu, Qiping},
  title   = {Quadrotor Gray-Box Model Identification from High-Speed Flight Data},
  journal = {Journal of Aircraft},
  volume  = {56},
  number  = {2},
  pages   = {645--661},
  year    = {2019},
  doi     = {10.2514/1.C035135}
}
```

---

## Not proposed, and why

- **Hayden 1976:** primary record not found; metadata and model confirmed only through Kan et al. 2019.
- **Curtiss, Erdman & Sun, "Ground effect aerodynamics":** NTRS lists a 1985 conference paper without a venue. The Vertica 1987 citation was not verified.
- **Nobahari & Sharifi 2014** (Eng. Appl. Artif. Intell., pp. 100–111; online estimation of GE in automatic quadrotor landing with a continuous ant-colony filter): the content was read on an ISC record and is simulation-only. The DOI could not be confirmed (the CrossRef query failed; dblp blocked).
- **Keshavarzian & Daneshjou 2020** (J. Braz. Soc. Mech. Sci. Eng. 42:555; PSO online estimation of GE): simulation-only; DOI not confirmed.
- **Osorio Quero & Martínez-Carranza, IMAV 2025:** CFD-derived multiplier and ESO, simulation-only; conference paper without a DOI.
- **Xu et al. 2022:** exists, but the content is unverified (see (b)).

## Main sources consulted

CrossRef API records for every DOI marked "CrossRef"; OpenAlex (`api.openalex.org/works/doi:...`); DataCite (`api.datacite.org/dois/10.48550/arxiv.2611.03540`, `.../arxiv.2506.19424`); Semantic Scholar (He et al. 2024); arxiv.org/abs/2506.19424, /1811.08027, /1612.05143; Sanchez-Cuevas full text (scispace PDF); Carter full text (par.nsf.gov/servlets/purl/10267925); Kan full text (par.nsf.gov/servlets/purl/10181219); hkxb.buaa.edu.cn (Xin 2017); re.public.polimi.it (Del Cont Bernard); escholarship.org/uc/item/4j32f9fp (Wei); saemobilus.sae.org (Yon & Li; Herz et al.; Holder & Tritschler); idus.us.es (Garofano-Soldado 2022); research.buaa.edu.cn (He & Leang 2025; Li Xia et al. 2024); digitalcommons.du.edu/etd/1570 (Conyers); ntrs.nasa.gov/citations/19860063840 (Curtiss 1985); Cambridge Core (Vitale 2010); CiNii (Leishman; Jategaonkar); mathworks.com book page (Morelli & Klein); proceedings.neurips.cc and research-collection.ethz.ch (Krause & Ong; Eriksson); proceedings.mlr.press (Sui 2015, 2018); doaj.org (Lopez-Sanchez 2020).
