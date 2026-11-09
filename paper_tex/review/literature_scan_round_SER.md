# Literature scan: "Experimental Reinforcement Twinning for Predictive Control of a Micro Aerial Vehicle in Ground Effect"

Scope: `paper/main.tex` (904 lines) and `paper/references.bib` (200 lines plus one stray line), both read in full. Target: IEEE journal, IEEEtran, American English. Date of check: 2026-10-28.

How things were verified. Metadata comes from the CrossRef REST API, read through WebFetch (`api.crossref.org/works/<DOI>`). Direct curl to CrossRef was blocked by the proxy. arXiv DOIs come from DataCite. Where CrossRef was incomplete, the publisher, repository or author page was used, and the source is named in each case. Content claims (what a paper reports) were read from full texts where these were open: Kan et al. (NSF PAR), Carter et al. (NSF PAR), Taffanel et al. (arXiv), Richardson and Pretorius (MATEC PDF), COM(2026) 81 (EUR-Lex), and the Cheeseman and Bennett R&M 3021 scan (Cranfield AERADE).

Note on output: IEEEtran.bst v1.14 ignores the `doi` field. The current `main.bbl` prints no DOIs, even for entries that have one. If the target journal wants DOIs in the reference list, the authors need a DOI-aware style or a `url`/`note` workaround. The `doi` fields below are still worth keeping.

---

## (a) Problems in existing entries

Summary by key. "OK" means the metadata matched the authoritative record.

| Key | Status | Problem |
|---|---|---|
| Matus2020 | Minor | Year 2021 and vol. 14 are **correct**: online 24 Jan 2021, print Mar 2021, vol. 14, no. 1, pp. 99–118. The DOI carries "2020" only because it was registered then. Issue number is missing. The key name is misleading but harmless. |
| Cai2024 | Fix | Missing vol. 61, no. 4, pp. 1230–1246. |
| Franzetti2024 | Fix (robustness) | The name is in fact right. The first author's family name is "David Du Mutel de Pierrepont Franzetti" and the given name is "Iris" (Springer record; author's PoliTo thesis: "Iris David Du Mutel de Pierrepont Franzetti"). CrossRef and OpenAlex truncate it to "...Franze", so automated tools will garble it. Brace the compound surname so BibTeX does not split "de" into a von part. |
| Taffanel2021Lighthouse | Fix, and fix the manuscript text | Never formally published. It exists only as arXiv:2104.11523v1 (23 Apr 2021), presented as a poster at the ICRA 2021 Workshop "Robot Swarms in the Real World" (Bitcraze blog, May 2021). The DOI is missing. **The numbers quoted in the manuscript do not match the paper** (see below). The title prints "uav" in lowercase. |
| PolettiRT2025 | Content fix | No journal version found: arXiv v2 (18 Jun 2026), no journal-ref. The entry is acceptable as a preprint. **However, it is a simulation-only study** (longitudinal ascent and hover of a modeled flapping-wing MAV). It does not support "experimental flapping-wing flight" in the Introduction. |
| Richardson2025 | Minor fix, and fix the manuscript text | Authors (Luke Richardson, Arnold Pretorius, University of Cape Town), vol. 417, art. 04007, 2025 and DOI are **correct**. Official title: "...for a Crazyflie2.1 quadcopter". Venue: 2025 RAPDASA-RobMech-PRASA-AMI Conference (26th RAPDASA), Pretoria. Content mismatches are listed below. |
| Kan2019 | Metadata OK; **content misused** | See (c). |
| EuropeanCommission2026 | Exists; figures match; wording fix | See (d). Add the document type. |
| CheesemanBennett1955 | Fix | The title omits "the": it is "The Effect of **the** Ground on a Helicopter Rotor in Forward Flight", R. & M. No. 3021. The report is dated Sept. 1955 and was published by HMSO, London, in 1957. The report covers **forward flight**, so describing it as a hover model is incomplete. |
| Kennedy2001 | Minor | The journal's full name is "Journal of the Royal Statistical Society: Series B (Statistical Methodology)". |
| Forrester2007 | Minor | Missing no. 2088; journal full name; "S{\'o}bester". It is cited for Expected Improvement, but it is a multi-fidelity co-kriging paper, so it fits better at the reward-transfer sentence. |
| Mockus1975 | Fix | Incomplete booktitle. Missing editor (G. I. Marchuk), series (LNCS vol. 27) and DOI 10.1007/3-540-07165-2_55. "Bayesian" prints in lowercase. |
| Feldbaum1960 | Minor | The paper is "Dual control theory. I", Automation and Remote Control vol. 21, no. 9, pp. 874–880. That is the translation of Avtomatika i Telemekhanika 21(9):1240–1249, 1960 (Russian original confirmed on Math-Net.Ru). The 874–880 English pagination, and the 1961 date of the translated issue, are confirmed only by secondary sources (Wikipedia). No DOI exists. |
| Filatov2000 | OK | |
| Mesbah2018 | OK | |
| MPCReview2021 | Minor | Missing no. 5–6. A manufacturing-oriented review is an odd sole MPC citation for an IEEE robotics/control readership. Consider adding a quadrotor MPC reference (Torrente et al. 2021, see the alternates). |
| Korenhof2021 | **Fix (author names wrong)** | "Paul" should be **Paulan** Korenhof, and "Sanne" should be **Sanneke** Kloppenburg. Missing no. 4. |
| Wagg2025 | **Fix (author names wrong)** | "Jonathan" should be **Jason** Shepherd, and "Zachary" should be **Zack** Xuereb Conti (CrossRef and Cambridge article page). |
| SchenaRT2023 | OK (metadata) | Vol. 82, art. 102421, Oct. 2024. The key says 2023 but the entry is right. Content: all three test cases are simulated (wind turbine, flapping-wing MAV in gusts, cryogenic tank). This is consistent with the manuscript except for the "experimental flapping-wing flight" clause. |
| Mendez2026 | Note | Unpublished, so it cannot be verified. The Introduction and Sec. II lean heavily on it. IEEE referees cannot assess an unavailable manuscript, so post a preprint (e.g., arXiv) and cite that. "Bayesian" prints in lowercase. |
| Rasmussen2006 | OK | Add address (Cambridge, MA, USA). |
| BitcrazeControllers | OK | The URL resolves ("Controllers in the Crazyflie"). "crazyflie" prints in lowercase, so brace it. |
| Uncited: Mehra1974, Goodwin1977, Ljung1999, Hjalmarsson2005, Chiuso2019 | Cite or delete | IEEEtran prints only cited entries, so they are harmless but untidy. **Recommended: cite them.** Mehra1974 and Goodwin1977 go at the E-optimal design (with addition R10 below). Ljung1999 goes at the Hessian-based covariance, Eq. (parameter-covariance): "Around the minimum, the curvature of the loss provides the covariance approximation". Hjalmarsson2005 goes at the claim "the function is thus more identifiable than its particular parameterization", which is application-oriented experiment design. Chiuso2019 can be dropped. Metadata fixes: Goodwin1977 add New York and Math. Sci. Eng. vol. 136; Hjalmarsson2005 author is "H{\aa}kan"; Chiuso2019 add no. 1; Ljung1999 add Upper Saddle River, NJ. Mehra1974 is OK. |
| **Stray text** | Delete | Line 201 of `references.bib` is a paragraph of manuscript prose ("The nominal DT described above ...") after the last entry. BibTeX skips it, but delete it. Any "@" typed there later would break the bibliography. |

### Content and citation-accuracy issues in the manuscript (existing references)

1. **Taffanel2021Lighthouse misquoted (Sec. II-B).** The manuscript says the system provides "sub-centimetre-level absolute accuracy" and that Taffanel et al. "reported an average positioning error of approximately 0.5–1 cm and an RMS position jitter between 0.5 and 1 mm". What the paper actually reports:
   - In Results, the mean and median Euclidean error is 2–4 cm in all cases, with flight outliers up to about 5 cm.
   - The Conclusion says "about 1 cm in the average case". The paper is internally inconsistent here.
   - Jitter is the RMS of consecutive-sample distances in the **stationary** test: LH2 0.3 mm (crossing beam) and 0.7 mm (EKF); LH1 0.6 mm and 3.9 mm.
   - "0.5–1 cm" appears nowhere, and sub-centimeter accuracy is not supported.

   Suggested text: *"For Lighthouse~V2, Taffanel et al.~\cite{Taffanel2021Lighthouse} reported mean Euclidean errors in the low-centimeter range, with in-flight outliers up to about 5~cm, and a stationary jitter of 0.3--0.7~mm depending on the estimator."* Also state which Lighthouse version and estimator the campaign used, and use "centimeter/millimeter" (American English).
2. **PolettiRT2025 (Introduction).** The clause "...and experimental flapping-wing flight~\cite{SchenaRT2023,PolettiRT2025}" is wrong. Neither paper is experimental, and the clause contradicts the paper's own claim to be "the first experimental demonstration". Suggested: *"...cryogenic thermal management~\cite{SchenaRT2023}, and hybrid control of flapping-wing ascent and hover in simulation~\cite{PolettiRT2025}."*
3. **Richardson2025 (Table I and Sec. II-B).**
   - Richardson and Pretorius list m = 0.032 kg (not 0.03242 kg) and give no rotor radius.
   - They scale rotor speed by V(t)/**3.7 V**, the measured voltage at hover load with a full battery. The manuscript uses V_ref = **4.20 V**. Unless the authors re-identified the PWM-to-speed map at 4.2 V, this is an inconsistency with the inherited propulsion model.
   - Their inertia tensor has off-diagonal terms (0.83, 0.72, 1.80 × 10⁻⁶ kg m²), which the manuscript omits.
   - The caption "Baseline DT parameters adopted from Richardson et al." therefore overstates the case. Split the table into parameters inherited from Richardson and parameters measured here.
   - Validation was a 230-s flight with position steps near hover: RMSE x 2.32 cm, y 2.17 cm, z 1.73 cm. There was no forward-flight test, so "validated ... for low speed free flight" should read "validated in near-hover step maneuvers".
   - Two authors: write "Richardson and Pretorius", not "Richardson et al.".
4. **CheesemanBennett1955 (Intro and Sec. II-B).** The report is titled and derived for forward flight. In the form used by Kan et al., T_IGE/T_OGE = 1/[1 − (R/4z)²/(1 + (V/v_i)²)]. The manuscript's "for an isolated rotor in hovering" should read "the hover limit of the Cheeseman–Bennett model". The values A = 1/16 and p = 2 are the **leading-order expansion** of 1/[1 − (R/4z)²], not an exact rearrangement. The two agree within 0.1% at z/R = 1.5, but at z/R = 0.5 the exact value is 1.33 versus 1.25. Suggested: *"...whose leading-order expansion gives A = 1/16 and p = 2."*
5. **Carter2021 is under-used.** Carter et al. measured a tethered **Crazyflie 2.0** on a load cell. They found a near-ground lift increase of up to about 20%, more than twice the classical prediction. This directly supports the Results statement "The classical Cheeseman--Bennett initialization captures the sign of the effect but does not reproduce" the magnitude. Suggested addition there: *"This is consistent with load-cell measurements on a Crazyflie~2.0, in which the near-ground lift increase exceeded twice the classical prediction~\cite{Carter2021}."* The manuscript's claim that wall effect is much weaker than floor or ceiling effect is confirmed: under 5% lift loss, only within millimeters, against about 20% for the ground and about 60% for the ceiling.

### Corrected BibTeX entries (complete)

```bibtex
@article{Matus2020,
  author  = {Matus-Vargas, Antonio and Rodriguez-Gomez, Gustavo and Martinez-Carranza, Jose},
  title   = {Ground Effect on Rotorcraft Unmanned Aerial Vehicles: A Review},
  journal = {Intelligent Service Robotics},
  volume  = {14},
  number  = {1},
  pages   = {99--118},
  year    = {2021},
  doi     = {10.1007/s11370-020-00344-5}
}

@article{Cai2024,
  author  = {Cai, Jielong and Gunasekaran, Sidaard},
  title   = {Propeller Ceiling Effect in Forward Flight},
  journal = {Journal of Aircraft},
  volume  = {61},
  number  = {4},
  pages   = {1230--1246},
  year    = {2024},
  doi     = {10.2514/1.C037779}
}

@article{Franzetti2024,
  author  = {{David Du Mutel de Pierrepont Franzetti}, Iris and Parin, Riccardo and Capello, Elisa and Rutherford, Matthew J. and Valavanis, Kimon P.},
  title   = {Ground, Ceiling and Wall Effect Evaluation of Small Quadcopters in Pressure-Controlled Environments},
  journal = {Journal of Intelligent \& Robotic Systems},
  volume  = {110},
  number  = {3},
  pages   = {125},
  year    = {2024},
  doi     = {10.1007/s10846-024-02155-7}
}

@misc{Taffanel2021Lighthouse,
  author       = {Taffanel, Arnaud and Rousselot, Barbara and Danielsson, Jonas and McGuire, Kimberly and Richardsson, Kristoffer and Eliasson, Marcus and Antonsson, Tobias and H{\"o}nig, Wolfgang},
  title        = {Lighthouse Positioning System: Dataset, Accuracy, and Precision for {UAV} Research},
  howpublished = {arXiv:2104.11523},
  note         = {Presented at the ICRA 2021 Workshop on Robot Swarms in the Real World},
  year         = {2021},
  doi          = {10.48550/arXiv.2104.11523}
}

@article{PolettiRT2025,
  author  = {Poletti, Romain and Schena, Lorenzo and Koloszar, Lilla and Degroote, Joris and Mendez, Miguel Alfonso},
  title   = {{Reinforcement Twinning} for Hybrid Control of Flapping-Wing Drones},
  journal = {arXiv preprint arXiv:2505.18201},
  year    = {2025},
  doi     = {10.48550/arXiv.2505.18201}
}

@inproceedings{Richardson2025,
  author    = {Richardson, Luke and Pretorius, Arnold},
  title     = {Development of a High-Fidelity Simulation Environment for a {Crazyflie2.1} Quadcopter},
  booktitle = {Proc. 2025 RAPDASA-RobMech-PRASA-AMI Conf.},
  series    = {MATEC Web of Conferences},
  volume    = {417},
  pages     = {04007},
  address   = {Pretoria, South Africa},
  year      = {2025},
  doi       = {10.1051/matecconf/202541704007}
}

@techreport{EuropeanCommission2026,
  author      = {{European Commission}},
  title       = {Action Plan on Drone and Counter Drone Security},
  institution = {European Commission},
  type        = {Communication from the Commission to the European Parliament and the Council},
  number      = {COM(2026) 81 final},
  address     = {Brussels, Belgium},
  month       = feb,
  year        = {2026},
  url         = {https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52026DC0081}
}

@techreport{CheesemanBennett1955,
  author      = {Cheeseman, I. C. and Bennett, W. E.},
  title       = {The Effect of the Ground on a Helicopter Rotor in Forward Flight},
  institution = {Aeronautical Research Council},
  address     = {London, U.K.},
  type        = {R\&M},
  number      = {3021},
  year        = {1955},
  note        = {Published by HMSO, London, 1957}
}

@article{Kennedy2001,
  author  = {Kennedy, Marc C. and O'Hagan, Anthony},
  title   = {{Bayesian} Calibration of Computer Models},
  journal = {Journal of the Royal Statistical Society: Series B (Statistical Methodology)},
  volume  = {63},
  number  = {3},
  pages   = {425--464},
  year    = {2001},
  doi     = {10.1111/1467-9868.00294}
}

@article{Forrester2007,
  author  = {Forrester, Alexander I. J. and S{\'o}bester, Andr{\'a}s and Keane, Andy J.},
  title   = {Multi-Fidelity Optimization via Surrogate Modelling},
  journal = {Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences},
  volume  = {463},
  number  = {2088},
  pages   = {3251--3269},
  year    = {2007},
  doi     = {10.1098/rspa.2007.1900}
}

@inproceedings{Mockus1975,
  author    = {Mo{\v{c}}kus, J.},
  title     = {On {Bayesian} Methods for Seeking the Extremum},
  booktitle = {Optimization Techniques {IFIP} Technical Conference, Novosibirsk, July 1--7, 1974},
  editor    = {Marchuk, G. I.},
  series    = {Lecture Notes in Computer Science},
  volume    = {27},
  publisher = {Springer},
  address   = {Berlin, Heidelberg, Germany},
  pages     = {400--404},
  year      = {1975},
  doi       = {10.1007/3-540-07165-2_55}
}

@article{Feldbaum1960,
  author  = {Feldbaum, A. A.},
  title   = {Dual Control Theory. {I}},
  journal = {Automation and Remote Control},
  volume  = {21},
  number  = {9},
  pages   = {874--880},
  year    = {1960},
  note    = {Translated from \emph{Avtomatika i Telemekhanika}, vol. 21, no. 9, pp. 1240--1249, 1960}
}

@article{MPCReview2021,
  author  = {Schwenzer, Max and Ay, Muzaffer and Bergs, Thomas and Abel, Dirk},
  title   = {Review on Model Predictive Control: An Engineering Perspective},
  journal = {The International Journal of Advanced Manufacturing Technology},
  volume  = {117},
  number  = {5--6},
  pages   = {1327--1349},
  year    = {2021},
  doi     = {10.1007/s00170-021-07682-3}
}

@article{Korenhof2021,
  author  = {Korenhof, Paulan and Blok, Vincent and Kloppenburg, Sanneke},
  title   = {Steering Representations---Towards a Critical Understanding of Digital Twins},
  journal = {Philosophy \& Technology},
  volume  = {34},
  number  = {4},
  pages   = {1751--1773},
  year    = {2021},
  doi     = {10.1007/s13347-021-00484-1}
}

@article{Wagg2025,
  author  = {Wagg, David J. and Burr, Christopher and Shepherd, Jason and {Xuereb Conti}, Zack and Enzer, Mark and Niederer, Steven},
  title   = {The Philosophical Foundations of Digital Twinning},
  journal = {Data-Centric Engineering},
  volume  = {6},
  pages   = {e12},
  year    = {2025},
  doi     = {10.1017/dce.2025.4}
}

@article{SchenaRT2023,
  author  = {Schena, Lorenzo and Marques, Pedro A. and Poletti, Romain and Ahizi, Samuel and Van den Berghe, Jan and Mendez, Miguel A.},
  title   = {{Reinforcement Twinning}: From Digital Twins to Model-Based Reinforcement Learning},
  journal = {Journal of Computational Science},
  volume  = {82},
  pages   = {102421},
  year    = {2024},
  doi     = {10.1016/j.jocs.2024.102421}
}

@unpublished{Mendez2026,
  author = {Mendez, Miguel A. and Schena, Lorenzo and Poletti, Romain and Lecomte, Y. and Randino, S. and Van den Berghe, Jan},
  title  = {{Reinforcement Twinning} via Twin-Calibrated {Bayesian} Policy Search and Replay-Driven Identification},
  note   = {Manuscript submitted to Proceedings of the Royal Society A},
  year   = {2026}
}

@misc{BitcrazeControllers,
  author       = {{Bitcraze AB}},
  title        = {Controllers in the {Crazyflie}},
  howpublished = {Crazyflie firmware documentation},
  url          = {https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/functional-areas/sensor-to-control/controllers/},
  note         = {Accessed: Oct. 23, 2026}
}

@book{Goodwin1977,
  author    = {Goodwin, Graham C. and Payne, Robert L.},
  title     = {Dynamic System Identification: Experiment Design and Data Analysis},
  series    = {Mathematics in Science and Engineering},
  volume    = {136},
  publisher = {Academic Press},
  address   = {New York, NY, USA},
  year      = {1977}
}

@book{Ljung1999,
  author    = {Ljung, Lennart},
  title     = {System Identification: Theory for the User},
  edition   = {2nd},
  publisher = {Prentice Hall},
  address   = {Upper Saddle River, NJ, USA},
  year      = {1999}
}

@article{Hjalmarsson2005,
  author  = {Hjalmarsson, H{\aa}kan},
  title   = {From Experiment Design to Closed-Loop Control},
  journal = {Automatica},
  volume  = {41},
  number  = {3},
  pages   = {393--438},
  year    = {2005},
  doi     = {10.1016/j.automatica.2004.11.021}
}

@article{Chiuso2019,
  author  = {Chiuso, Alessandro and Pillonetto, Gianluigi},
  title   = {System Identification: A Machine Learning Perspective},
  journal = {Annual Review of Control, Robotics, and Autonomous Systems},
  volume  = {2},
  number  = {1},
  pages   = {281--304},
  year    = {2019},
  doi     = {10.1146/annurev-control-053018-023744}
}
```

Unchanged and verified: Kan2019, Carter2021 (vol. 59, no. 4, pp. 1398–1405, 2021, Crazyflie 2.0), Filatov2000, Mesbah2018, Mehra1974, Rasmussen2006, BitcrazeFirmware.

---

## (b) Proposed additions (15, by priority)

Every entry below was verified against CrossRef (or DataCite, or the publisher where stated). Proposed sentences use the paper's macros and style. Keys are suggestions.

### E1. Kennedy and O'Hagan 2000 (Essential)
```bibtex
@article{Kennedy2000,
  author  = {Kennedy, Marc C. and O'Hagan, Anthony},
  title   = {Predicting the Output from a Complex Computer Code When Fast Approximations Are Available},
  journal = {Biometrika},
  volume  = {87},
  number  = {1},
  pages   = {1--13},
  year    = {2000},
  doi     = {10.1093/biomet/87.1.1}
}
```
CrossRef lists only "M. Kennedy". The second author is confirmed on O'Hagan's publication page.

**Why:** The affine-plus-GP reward transfer, R• = γ0 + γ1 R∘ + δ, is the autoregressive multi-fidelity model introduced here. A referee will expect it named and credited, not presented as new.
**Where:** "An affine relation captures the global calibration between the two, while a Gaussian process" (Introduction). Also cite at Eq. (rt-surrogate).
**Proposed:** *"This structure is the autoregressive multi-fidelity model of Kennedy and O'Hagan~\cite{Kennedy2000}, in which the high-fidelity response is a scaled low-fidelity response plus an independent Gaussian-process discrepancy~\cite{Kennedy2001,Forrester2007}."*

### E2. Marco et al. 2017 (Essential)
```bibtex
@inproceedings{Marco2017,
  author    = {Marco, Alonso and Berkenkamp, Felix and Hennig, Philipp and Schoellig, Angela P. and Krause, Andreas and Schaal, Stefan and Trimpe, Sebastian},
  title     = {Virtual vs. Real: Trading Off Simulations and Physical Experiments in Reinforcement Learning with {Bayesian} Optimization},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  address   = {Singapore},
  pages     = {1557--1563},
  year      = {2017},
  doi       = {10.1109/ICRA.2017.7989186}
}
```
**Why:** This is the closest prior work on combining simulator and hardware returns inside Bayesian policy search. Without it, the "DT-to-experiment reward transfer" novelty claim is exposed.
**Where:** "Bayesian RT therefore learns how control performance transfers from the virtual to the physical environment."
**Proposed:** *"Related Bayesian optimization schemes treat simulations and physical experiments as two information sources of different cost and accuracy~\cite{Marco2017}; here, the virtual source is a physics-based twin identified from the same flights."*

### E3. Schoellig, Mueller and D'Andrea 2012 (Essential)
```bibtex
@article{Schoellig2012,
  author  = {Schoellig, Angela P. and Mueller, Fabian L. and D'Andrea, Raffaello},
  title   = {Optimization-Based Iterative Learning for Precise Quadrocopter Trajectory Tracking},
  journal = {Autonomous Robots},
  volume  = {33},
  number  = {1--2},
  pages   = {103--127},
  year    = {2012},
  doi     = {10.1007/s10514-012-9283-2}
}
```
**Why:** The paper learns a feedforward correction over repeated trials around a nominal model, under constraints. That is exactly what a referee will compare with quadrotor ILC, so the difference has to be stated: scalar-reward Bayesian search plus twin identification, versus error-signal learning.
**Where:** "The reference is stored as a function of longitudinal position and transferred to the vehicle"
**Proposed:** *"This resembles iterative learning control, which refines a feedforward correction over repeated quadrotor flights~\cite{Schoellig2012,Mueller2012}; RT differs in that the correction is optimized in an identified twin and refined through a learned reward transfer."*

### E4. Garone, Di Cairano and Kolmanovsky 2017 (Essential)
```bibtex
@article{Garone2017,
  author  = {Garone, Emanuele and Di Cairano, Stefano and Kolmanovsky, Ilya},
  title   = {Reference and Command Governors for Systems with Constraints: A Survey on Theory and Applications},
  journal = {Automatica},
  volume  = {75},
  pages   = {306--328},
  year    = {2017},
  doi     = {10.1016/j.automatica.2016.08.013}
}
```
**Why:** In control, "reference governor" names an online add-on that modifies the reference to enforce constraints. The policy here is an offline-optimized, position-scheduled reference. Either cite and qualify the term, or rename it (e.g., "spatial reference correction").
**Where:** "The policy is the spatial altitude reference supplied to a reference governor," (Sec. II-C). Also "compact feedforward correction or reference governor" (Introduction).
**Proposed:** *"Unlike a classical reference or command governor, which modifies the reference online to enforce constraints~\cite{Garone2017}, the present governor is a position-scheduled correction optimized offline and screened for constraint satisfaction in the DT."*

### E5. Jones, Schonlau and Welch 1998 (Essential)
```bibtex
@article{Jones1998,
  author  = {Jones, Donald R. and Schonlau, Matthias and Welch, William J.},
  title   = {Efficient Global Optimization of Expensive Black-Box Functions},
  journal = {Journal of Global Optimization},
  volume  = {13},
  number  = {4},
  pages   = {455--492},
  year    = {1998},
  doi     = {10.1023/A:1008306431147}
}
```
**Why:** It is the standard source for the closed-form Expected Improvement used in Eqs. (rt-expected-improvement) and (ei). Mockus1975 and Forrester2007 alone are not the usual attribution for that formula.
**Where:** "Expected Improvement balances the predicted physical return against the uncertainty of the surrogate"
**Proposed:** Change the citation to `\cite{Mockus1975,Jones1998}`, and in Sec. II-A add: *"Equation~\eqref{eq:rt-expected-improvement} is the closed-form Expected Improvement of the efficient global optimization algorithm~\cite{Jones1998}."*

### E6. Sanchez-Cuevas, Heredia and Ollero 2017 (Essential)
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
```
`pages` holds the article number (17 pp.).

**Why:** It is the standard multirotor ground-effect characterization. It shows multirotor ground effect differs from the single-rotor case, and it measures *partial* ground effect, with only some rotors above the surface. That is the physical basis for the rotor-overlap weighting χ_i. Carter et al. fit its model to Crazyflie data.
**Where:** "four nearby rotors interact with one another and with the central body" (Introduction). Also "defined as the fraction of the $i_{th}$ rotor disk that overlaps the obstacle" (Sec. II-B).
**Proposed:** *"At MAV scale, however, four nearby rotors interact with one another and with the central body, so multirotor ground effect differs from the single-rotor case, including when only some rotors are above the surface~\cite{SanchezCuevas2017}."*

### R7. Mueller, Schoellig and D'Andrea 2012 (Recommended)
```bibtex
@inproceedings{Mueller2012,
  author    = {Mueller, Fabian L. and Schoellig, Angela P. and D'Andrea, Raffaello},
  title     = {Iterative Learning of Feed-Forward Corrections for High-Performance Tracking},
  booktitle = {Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)},
  address   = {Vilamoura, Portugal},
  pages     = {3276--3281},
  year      = {2012},
  doi       = {10.1109/IROS.2012.6385647}
}
```
**Why:** It learns corrections to the *reference* sent to an unchanged quadrotor feedback controller. That is the nearest structural analog to the paper's policy class, except that its correction is time-indexed.
**Where:** "This spatial representation is preferred over the time representation" (Sec. II-C).
**Proposed:** *"Quadrotor iterative learning schemes index the learned reference or input correction in time~\cite{Mueller2012,Schoellig2012}; a position-indexed reference instead keeps the anticipatory command locked to the obstacle edges."*

### R8. Shi et al. 2019, Neural Lander (Recommended)
```bibtex
@inproceedings{Shi2019,
  author    = {Shi, Guanya and Shi, Xichen and O'Connell, Michael and Yu, Rose and Azizzadenesheli, Kamyar and Anandkumar, Animashree and Yue, Yisong and Chung, Soon-Jo},
  title     = {Neural Lander: Stable Drone Landing Control Using Learned Dynamics},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {9784--9790},
  year      = {2019},
  doi       = {10.1109/ICRA.2019.8794351}
}
```
**Why:** It is the reference point for learned ground-effect compensation. Its cross-table trajectory, where ground effect appears and vanishes at a table edge, is the closest learning-based analog to the finite-obstacle crossing. It used an Intel Aero (1.47 kg), and its learned residual takes velocity as an input.
**Where:** "it treats ground effect as a static function of the instantaneous rotor clearance" (Sec. II-B).
**Proposed:** *"Learned residual models can capture richer near-ground dynamics, including the transition across a table edge~\cite{Shi2019}, but they require dedicated training data and offer less physical interpretability than a two-parameter law."*

### R9. Berkenkamp, Schoellig and Krause 2016 (Recommended)
```bibtex
@inproceedings{Berkenkamp2016,
  author    = {Berkenkamp, Felix and Schoellig, Angela P. and Krause, Andreas},
  title     = {Safe Controller Optimization for Quadrotors with {Gaussian} Processes},
  booktitle = {Proc. IEEE Int. Conf. Robot. Autom. (ICRA)},
  pages     = {491--496},
  year      = {2016},
  doi       = {10.1109/ICRA.2016.7487170}
}
```
**Why:** It is the canonical safe GP Bayesian optimization of quadrotor controllers on hardware. It is the model-free baseline against which the "DT-screened neighborhood" safety argument should be positioned.
**Where:** "In contrast with a fully model-free search, however, exploration begins from an improved physics-based solution"
**Proposed:** *"Gaussian-process Bayesian optimization has tuned quadrotor controllers directly on hardware, with safety enforced through a performance threshold~\cite{Berkenkamp2016}; here, the DT supplies both the starting policy and the safety screening."*

### R10. Franceschini and Macchietto 2008 (Recommended)
```bibtex
@article{Franceschini2008,
  author  = {Franceschini, Gaia and Macchietto, Sandro},
  title   = {Model-Based Design of Experiments for Parameter Precision: State of the Art},
  journal = {Chemical Engineering Science},
  volume  = {63},
  number  = {19},
  pages   = {4846--4872},
  year    = {2008},
  doi     = {10.1016/j.ces.2007.11.034}
}
```
**Why:** The E-optimal, Fisher-based sequential design currently has no citation at all. This review, together with the already-present Mehra1974 and Goodwin1977, covers nonlinear dynamic models. Pukelsheim 2006 is an alternate.
**Where:** "is selected with an E-optimal criterion," (Sec. II-A).
**Proposed:** *"E-optimality is one of the classical criteria of model-based experiment design for dynamic systems~\cite{Mehra1974,Goodwin1977,Franceschini2008}; maximizing $\lambda_{\min}$ shortens the longest axis of the parameter confidence ellipsoid."*

### R11. Kingma and Ba 2015, Adam (Recommended)
```bibtex
@inproceedings{Kingma2015,
  author    = {Kingma, Diederik P. and Ba, Jimmy},
  title     = {Adam: A Method for Stochastic Optimization},
  booktitle = {Proc. 3rd Int. Conf. Learn. Represent. (ICLR)},
  address   = {San Diego, CA, USA},
  year      = {2015},
  doi       = {10.48550/arXiv.1412.6980}
}
```
ICLR 2015 has no proceedings DOI; the DOI given is the arXiv one (DataCite).

**Why:** Adam's update equations are reproduced in Eqs. (adam-moments) and (adjoint-adam) with no citation.
**Where:** "Adam uses this gradient to update the parameters over successive optimization steps."
**Proposed:** *"The Adam optimizer~\cite{Kingma2015} uses this gradient to update the parameters over successive optimization steps."*

### R12. Bradbury et al. 2018, JAX (Recommended)
```bibtex
@misc{Bradbury2018,
  author       = {Bradbury, James and Frostig, Roy and Hawkins, Peter and Johnson, Matthew James and Katariya, Yash and Leary, Chris and Maclaurin, Dougal and Necula, George and Paszke, Adam and Vander{P}las, Jake and Wanderman-{M}ilne, Skye and Zhang, Qiao},
  title        = {{JAX}: Composable Transformations of {Python}+{NumPy} Programs},
  howpublished = {GitHub repository},
  url          = {https://github.com/jax-ml/jax},
  note         = {Version [insert version used]},
  year         = {2018}
}
```
This is the developers' recommended citation (JAX README). Software, no DOI.

**Why:** The discrete-adjoint identification and the policy gradients rest on JAX reverse-mode autodiff. Citing it, with its version, supports reproducibility.
**Where:** "implemented as a differentiable physics-based simulator using the JAX library in Python"
**Proposed:** *"...using the JAX library~\cite{Bradbury2018}, whose reverse-mode automatic differentiation provides the discrete-adjoint gradients used for identification and policy optimization."*

### R13. Powers et al. 2013 (Recommended)
```bibtex
@incollection{Powers2013,
  author    = {Powers, Caitlin and Mellinger, Daniel and Kushleyev, Aleksandr and Kothmann, Bruce and Kumar, Vijay},
  title     = {Influence of Aerodynamics and Proximity Effects in Quadrotor Flight},
  booktitle = {Experimental Robotics: The 13th International Symposium on Experimental Robotics},
  editor    = {Desai, Jaydev P. and Dudek, Gregory and Khatib, Oussama and Kumar, Vijay},
  series    = {Springer Tracts in Advanced Robotics},
  volume    = {88},
  publisher = {Springer},
  address   = {Cham, Switzerland},
  pages     = {289--302},
  year      = {2013},
  doi       = {10.1007/978-3-319-00065-7_21}
}
```
Metadata is from CrossRef and the Springer book page. The content claim comes from Kan et al.'s summary; the chapter itself was paywalled.

**Why:** It is the early quadrotor proximity-effect study, reporting that ground influence extends to larger clearances than classical models predict. It supports the motivation for identifying A and p rather than fixing them.
**Where:** "describe the effect for an isolated rotor hovering above an extended plane" (Introduction).
**Proposed:** *"Quadrotor experiments, however, showed a stronger and more extended ground influence than such classical models predict~\cite{Powers2013,Carter2021}."*

### R14. He, Kou, Calaf and Leang 2019 (Recommended)
```bibtex
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
```
**Why:** It is the model-based control counterpart: a ground-effect model combined with a disturbance observer for multirotor control near the ground. It is needed so that "PID is reactive" is not set against an unstated alternative.
**Where:** "but they are reactive: an unmodeled aerodynamic force must first produce an error" (Introduction).
**Proposed:** *"Ground-effect models have been combined with nonlinear disturbance observers to improve multirotor control near the ground~\cite{He2019}; the present work instead anticipates the interaction through a reference designed with an identified twin."*

### O15. Owen 1998 (Optional)
```bibtex
@article{Owen1998,
  author  = {Owen, Art B.},
  title   = {Scrambling {Sobol'} and {Niederreiter--Xing} Points},
  journal = {Journal of Complexity},
  volume  = {14},
  number  = {4},
  pages   = {466--489},
  year    = {1998},
  doi     = {10.1006/jcom.1998.0487}
}
```
**Why:** It is the method citation for the scrambled Sobol library. Pair it with Sobol 1967 if a slot is free (see the alternates).
**Where:** "A scrambled Sobol library of 2000 coefficient vectors is screened in the DT"
**Proposed:** *"A scrambled Sobol library~\cite{Sobol1967,Owen1998} of 2000 coefficient vectors is screened in the DT,"*

### Verified alternates (not proposed unless a slot is freed)

All DOIs were confirmed on CrossRef unless noted.
- Sobol', USSR Comput. Math. Math. Phys., 7(4):86–112, 1967. DOI 10.1016/0041-5553(67)90144-9.
- Conyers, Rutherford, Valavanis, "An Empirical Evaluation of Ground Effect for Small-Scale Rotorcraft," ICRA 2018, pp. 1244–1250. DOI 10.1109/ICRA.2018.8461035. Their ceiling-effect paper: ICUAS 2018, pp. 243–249, DOI 10.1109/ICUAS.2018.8453469.
- David Du Mutel de Pierrepont Franzetti et al., "Modelling of Ground and Ceiling Effects for Quadcopters Based on Experimental Data," ICUAS 2024, pp. 405–412. DOI 10.1109/ICUAS60882.2024.10557056. This is a companion to Franzetti2024.
- Cutler, Walsh, How, "Real-World Reinforcement Learning via Multifidelity Simulators," IEEE T-RO 31(3):655–671, 2015. DOI 10.1109/TRO.2015.2419431. Multi-fidelity simulator chain, demonstrated on an RC car.
- Calandra, Seyfarth, Peters, Deisenroth, Ann. Math. Artif. Intell. 76(1–2):5–23, 2016. DOI 10.1007/s10472-015-9463-9. Bayesian-optimization gait learning on hardware.
- Rai, Antonova, Meier, Atkeson, JMLR 20(49):1–24, 2019 (no DOI). Simulation-informed kernels for hardware Bayesian optimization.
- Torrente, Kaufmann, Foehn, Scaramuzza, "Data-Driven MPC for Quadrotors," IEEE RA-L 6(2):3769–3776, 2021. DOI 10.1109/LRA.2021.3061307. GP-augmented MPC; addresses high-speed drag, not ground effect.
- Zhang et al., "Gain-Scheduling Tracking Control for Quadrotors Under Ground Effects via NTSMC-sLPV," IEEE TAES 61(2):1958–1970. DOI 10.1109/TAES.2024.3462919 (verified via OpenAlex). An IEEE-journal example of control under ground effect.
- Wei, Chan, Lee, Kong, Int. J. Intell. Robot. Appl. 3(3):283–297, 2019. DOI 10.1007/s41315-019-00098-z. MRAC versus PID for a mini quadcopter in ground effect.
- Giernacki et al., "Crazyflie 2.0 Quadrotor as a Platform for Research and Education in Robotics and Control Engineering," MMAR 2017, pp. 37–42. DOI 10.1109/MMAR.2017.8046794.
- Bauersfeld et al., "NeuroBEM," RSS XVII, 2021. DOI 10.15607/RSS.2021.XVII.042. Not a ground-effect paper.
- O'Connell et al., "Neural-Fly," Sci. Robot. 7(66):eabm6597, 2022. DOI 10.1126/scirobotics.abm6597. Wind, not ground effect.
- Pukelsheim, *Optimal Design of Experiments*, SIAM, 2006. DOI 10.1137/1.9780898719109.
- Bristow, Tharayil, Alleyne, "A Survey of Iterative Learning Control," IEEE Control Syst. Mag. 26(3):96–114, 2006. DOI 10.1109/MCS.2006.1636313. Authors confirmed at Missouri S&T Scholars' Mine.

---

## (c) Kan2019: what Kan et al. actually report

**Plainly: Kan et al. did use a Crazyflie, but a Crazyflie 2.0, not the Crazyflie 2.1+ flown here, and only to validate models fitted on a much larger vehicle. Their "altitude dominates speed" conclusion comes from that larger vehicle, and they never say the speed influence is negligible. The manuscript's two citations of Kan2019 also contradict each other.**

- **Vehicles.** Models were fitted and evaluated on an **AscTec Hummingbird** (0.551 kg, R = 0.10 m), flown at 0–8 m/s and 0.05–0.5 m altitude. A **Bitcraze Crazyflie 2.0** (0.032 kg, R = 0.023 m) was used *only to validate* the proposed models. It flew at V ∈ {0, 0.52, 1.05, 1.57, 2.10} m/s and z ∈ {35, 46, 58, 69, 92, 115} mm, which is z/R ≈ 1.5–5. Thrust was inferred from rotor RPM on the Hummingbird and from consumed motor power via manufacturer curves on the Crazyflie. No finite obstacle is described.
- **Findings.**
  - Hover and helicopter models do not fully describe quadrotor forward flight.
  - On the Hummingbird, the measured T_IGE/T_h ratio decreases with V and rises again near V/v_h ≈ 1.4.
  - Within *low-to-medium* speeds, ground effect depends "much more strongly" on altitude than on forward speed. This is drawn from Hummingbird data (their Fig. 4).
  - Their proposed low-speed models still contain speed terms.
  - The Crazyflie data validated only the low/medium-speed variants. The authors state that the high-speed variants could not be validated on the Crazyflie.
  - The authors do **not** use the word "negligible", and they do not measure energy efficiency directly.
- **What is wrong in the manuscript.**
  - Sec. II-B, "experiments conducted on the same MAV showed negligible influence", is inaccurate on three counts: it is not the same vehicle (2.0 versus 2.1+), the Crazyflie was a validation set only, and "negligible" overstates "much weaker than altitude".
  - The Introduction says velocity "changes the response". That is true mainly at medium-to-high advance ratios, and as written it contradicts the Sec. II-B justification.
- **Why the omission is still defensible.** For the 32.4 g vehicle with R = 23 mm, v_h ≈ 4.4 m/s. The campaign's 0.20–0.50 m/s is therefore V/v_h ≈ 0.05–0.11. That lies inside Kan's Crazyflie range (V/v_h ≤ about 0.48) and well below the Hummingbird's "practically constant OGE thrust" range (V/v_h < 0.7). The forward-flight term of the Cheeseman–Bennett model, 1/[1 − (R/4z)²/(1 + (V/v_i)²)], reduces the ground-effect increment by under 1.3% at 0.5 m/s, 0.6% at 0.35 m/s and 0.2% at 0.2 m/s.

**Replace in the Introduction:** *"Kan et al.~\cite{Kan2019} showed that hover-based models do not fully describe small quadrotors in forward flight, because the near-ground thrust ratio varies with speed, although clearance dominates at low-to-medium speeds."*

**Replace in Sec. II-B** (sentence beginning "The forward flight speed $v_x$ effect is not taken into account"): *"The forward speed $v_x$ is not included. For small quadrotors at low-to-medium speed, Kan et al.~\cite{Kan2019} found a much stronger dependence of ground effect on clearance than on speed, and they validated their low-speed models on a Crazyflie~2.0 up to 2.1~m/s. Here, $v_x\leq0.5$~m/s gives $v_x/v_h\lesssim0.11$, for which the forward-flight term of the Cheeseman--Bennett model changes the thrust increment by less than 2\%~\cite{CheesemanBennett1955}."*

---

## (d) European Commission figures

**Plainly: the document exists and contains both figures. The manuscript reports them correctly, but calls the document an "outlook" and slightly over-specifies the geographic scope. The Communication gives no source for the forecast.**

- **Document.** COM(2026) 81 final, Brussels, 11 Feb 2026, "Action Plan on Drone and Counter Drone Security", a Communication from the Commission to the European Parliament and the Council. The CELEX number 52026DC0081 resolves on EUR-Lex.
- **Text (Introduction of the Communication).** It reads "From a European industrial perspective, the commercial airborne drone market segment alone is forecast to be worth around EUR 14.5 billion by 2030 and potentially exceed EUR 50 billion by 2033." The sentence has **no footnote or source** for the forecast.
- **What the manuscript gets right and wrong.**
  - The figures match: about EUR 14.5 billion by 2030 and more than EUR 50 billion by 2033.
  - The document is a security action plan, not an "outlook".
  - The scope is framed "from a European industrial perspective"; the text does not explicitly say these figures cover the EU market.
  - Because no primary market study is cited, a referee may ask for one.
- **Suggested wording:** *"In its 2026 Action Plan on Drone and Counter Drone Security, the European Commission cites forecasts of about EUR~14.5 billion by 2030 for the commercial airborne-drone segment, potentially exceeding EUR~50 billion by 2033~\cite{EuropeanCommission2026}."* Use the corrected `@techreport` in (a).

---

## Incidental (non-literature) items noticed while reading

- Line 149: `\label{eq:rt-model-objective}` should be `\eqref{...}`. As written it duplicates a label.
- Line 401: `\mathbf{F}*{B}` should be `\mathbf{F}_{B}`.
- Line 427: in the quaternion kinematics, "$\dot{\mathbf q} + \frac12$..." should use "=".
- Line 644: leftover Italian note "(eq da rivedere togliendo scientific region)".
- Line 707: typo "sepastinguish".
- Line 79: typo "repsect".
- Line 710: a stray `\fi`.
- Line 796: the caption says $\pi_{k,i}$ but the text uses $\pi_{\lambda,i}$.
- Line 824: "It20" is not defined.
- Lines 381 and elsewhere: "centimetre" should be "centimeter" for American English.

---

## Sources consulted (main)
- CrossRef REST API records for every DOI listed above (api.crossref.org/works/...); DataCite for the arXiv DOIs.
- Kan et al. 2019 full text: https://par.nsf.gov/servlets/purl/10181219
- Carter et al. 2021 full text: https://par.nsf.gov/servlets/purl/10267925
- Taffanel et al. 2021: https://arxiv.org/abs/2104.11523 ; https://ar5iv.labs.arxiv.org/html/2104.11523 ; workshop poster: https://www.bitcraze.io/2021/05/lighthouse-positioning-accuracy/
- Poletti et al.: https://arxiv.org/abs/2505.18201v2 ; Schena et al. preprint: https://arxiv.org/abs/2311.03628v4
- Richardson and Pretorius: https://www.matec-conferences.org/articles/matecconf/abs/2025/11/matecconf_rapdasa2025_04007/matecconf_rapdasa2025_04007.html (and the PDF)
- COM(2026) 81: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:52026DC0081
- Cheeseman and Bennett R&M 3021: https://aerade.cranfield.ac.uk/handle/1826.2/3590 (scan: https://reports.aerade.cranfield.ac.uk/bitstream/1826.2/3590/1/arc-rm-3021.pdf)
- Feldbaum original: https://mathnet.ru/eng/at12624 ; translation pagination: https://en.wikipedia.org/wiki/Dual_control_theory
- Wagg et al. author names: https://www.cambridge.org/core/product/7C2E25F20DDB7EF7DDD560363DE9E171 ; https://eprints.whiterose.ac.uk/223865
- Franzetti name: https://iris.polito.it/retrieve/handle/11583/3004030/939557 ; https://iris.polito.it/handle/11583/2993441
- Mockus book: https://link.springer.com/10.1007/3-540-07165-2 ; Powers book: https://link.springer.com/978-3-319-00064-0
- Marco et al.: https://research-collection.ethz.ch/handle/20.500.11850/226691 ; Cutler et al.: https://dspace.mit.edu/handle/1721.1/104936 ; Rai et al.: https://jmlr.org/papers/v20/18-196.html
- Kennedy and O'Hagan 2000 authorship: https://tonyohagan.co.uk/academic/abs/techrep9.html ; JAX citation: https://raw.githubusercontent.com/jax-ml/jax/HEAD/README.md ; Adam: https://arxiv.org/abs/1412.6980
- Bristow et al.: https://scholarsmine.mst.edu/mec_aereng_facwork/1328 ; Goodwin and Payne: https://ci.nii.ac.jp/ncid/BA00315049
- Wei et al.: https://escholarship.org/uc/item/4j32f9fp ; Zhang et al. TAES: https://api.openalex.org/works/doi:10.1109%2FTAES.2024.3462919
