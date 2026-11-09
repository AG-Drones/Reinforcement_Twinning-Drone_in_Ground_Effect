# Independent check of review round 1

> **Status at delivery.** The seven must-fix items were corrected in the cards before delivery; item 7 by neutral wording ("the DT") until the card on which model designed π_MB is decided. Of the should-fix items, 8, 10–14, 17 and 18 were corrected; 9 (how the seven local policies were chosen) and 15 (the table height) are put to you as questions on the cards; 16 was reduced. The minor sentence-length, colon and comma-splice items were corrected. What remains is listed in round1_not_in_cards.md. Line numbers below refer to the proposal before these corrections.

Proposal: `typeset/main_round1_proposal.tex` (cited as `P:line`). Code paths are relative to `code/`. Recounts were run on `EXP/CLEAN`.

**Confirmed against code and data:** table rows (41 policies, 137 flights); three repetitions; INF_11/12 (0.40/0.45 m/s, 1R); domains 0.5–6R and 0.3–1.5R; windows 2.20–3.01 and 2.20–3.70 m (N_R 41–42); Θ; Adam settings; cold start; MB settings (81 nodes, means, J400, 150 × 10⁻³); s_j and a★; basis; EI candidate set; 0.35 s, 4.55R, 50 Hz; 8.5/1.5 mm offsets; EI_05 against EI_09 (0.024, 0.947); every III-A to III-D number; Cheeseman–Bennett expansion; f_GE derivatives. No label or sole citation lost.

## Must fix

1. **No card covers P:846.** "motivate the restriction of the reference domain to $0.5<z/R<1.5$"
   - **Problem.** This contradicts C43, C60 and the code (0.3R; `next_mission_design/informative_policy.py:64-65`). It is also the third statement of the domain switch (see P:606 and P:829).
   - **Fix.** Delete the first two sentences. Keep "This second stage produces trajectories such as π_INF,9 …".

2. **C84 (P:989).** "their standard error, at least $0.01$, weights the affine fit and enters the GP as noise"
   - **Problem.** The code uses the repetition standard deviation divided by |R_BL|, not a standard error: `max(std/|R_BL|, 0.01)` (`next_mission_design/generalized_policy.py:226-229`). The code check's own draft sentence (N6) introduced this error.
   - **Fix.** "their standard deviation over the flights, divided by the baseline cost and floored at 0.01, …"

3. **C42 (P:602).** "starting at $x=1.70$ m from the steady out-of-ground-effect state at the nominal clearance and speed"
   - **Problem.** The replay starts at each record's own commanded clearance and speed, plus the reference offset at 1.70 m (`adjoint_identification.py:623-625,658-666`). INF_11 and INF_12 are at z\*/R = 1 and 0.40/0.45 m/s, and INF_05 starts 1.64R higher. "Nominal" is defined as (1.5, 0.079).
   - **Fix.** "…from the steady out-of-ground-effect state at the record's commanded clearance, speed and initial reference."
   - **Same section.** The old sentence at P:433, "The remaining channels support initialization and replay of the measured operating conditions", now contradicts C42. Only the measured x enters the replay. Rewrite it as "…are kept for trajectory assessment."

4. **C48 against old text at P:713, P:606 and C30 Block 5 (P:372).** C48 says that F₁:N is never formed during design. Three places still say otherwise:
   - P:713: "During sequential design it is evaluated with the current converged DT."
   - P:606: the switch is justified by the cumulative Fisher information ("…therefore restricted"). That information was computed only after the campaign, and the switch was a manual flag (`informative_policy.py:43`).
   - Block 5: "scored by the information they add along the least-observed parameter direction".
   - **Fix.**
     - Delete the P:713 sentence.
     - At P:606, write "The post-campaign evaluation of Section III-B shows that…" and drop "therefore".
     - In Block 5, write "scored by their predicted information on θ_p".

5. **C35 (P:550).** "The DT applies $f_{GE}$ to the thrust at the commanded rotor speed"
   - **Problem.** The code applies it to the thrust at the realized, lagged rotor speed (`jDT/simulator.py:358-363,406`).
   - **Fix.** Write "at the actual rotor speed". The constant-speed argument still holds.

6. **C31 (P:380).** "Positive z is the height of the rotor plane above this surface, which lies 8.5 mm above the center of mass…"
   - **Problem.** "which" attaches to "this surface", so the sentence says the table top lies 8.5 mm above the center of mass.
   - **Fix.** "Positive z is the height above this surface of the rotor plane, which lies…"

7. **C19 (P:72), C70 (P:890) and C86 (P:1009) against C52.** "the identified DT yields / is accurate enough / produced a model-based policy"
   - **Problem.** The flown π_MB used (0.230, 3.136) (`next_mission_design/model_based_policy.py:46-52`), and P:751, "optimized with the single final identified DT", stays wrong in the proposal. The new cards repeat the claim three times.
   - **Fix.** Either apply C52(a) in this round, or write "the DT" in C19, C70 and C86 until C52 is decided.

## Should fix

8. **C53 (P:763), C77 (P:937), C19 and C86: EI count and the campaign table caption (P:575).**
   - **Text.** "Ten policies … are then selected sequentially by EI, and each physical reward is added". "The ninth of the ten EI-selected policies". Caption: "Policies and flights of the campaign".
   - **Metadata:** EI_01–02 are It17_4–5 (among the ALPHA runs), EI_03–08 are It18_1–6, all packaged as `rt_calibration` (`EXP/legacy_name_map.json`, `EXP/EXP_EI_0x_metadata.json`); runs It3, It6–It16 and It22 are absent. So EI was batched (2, 6, 1, 1) and the table counts retained flights only.
   - **Fix:** caption "Policies and retained flights"; "selected by EI in four rounds" if confirmed; add both points to C40.

9. **C53, C39, C75, C76 and C77: "Sobol policies".** "seven admissible policies …, chosen to span different amplitude combinations"
   - **Problem.** No code selects them, and ALPHA_04 and ALPHA_05 are near single-axis vectors (`material/code_check_current.md:451`).
   - **Fix.** Call them "local-exploration policies π_a,i" unless the author confirms that they were drawn from the library.

10. **C35 (P:552).**
    - **Text.** "changes the augmentation by less than 1.3%". With the exact Cheeseman–Bennett relation, f−1 changes by 1.30–1.69% for 1.5 ≥ z/R ≥ 0.5 (thrust by less than 0.5%). Write "by less than 2%", as `literature_scan_round_SER.md:599` proposed.
    - **Undefined symbol.** v_h is used here (II-B) but defined only in II-C (P:565). Write "v_x ≤ 0.5 m/s".

11. **C26 (P:195) and C13 (P:60).** "clearance and actuator constraints checked in the DT" and "state, clearance, and actuation constraints".
    - **Problem.** No actuator check exists in `model_based_policy.py` or `expected_improvement_policy.py`.
    - **Fix.** "reference-amplitude and clearance constraints".

12. **C48 (P:724).**
    - **Fisher averaging.** "The sensitivities are averaged over … sigma-point samples": the code averages the Fisher matrices (`informative_policy.py:430-440`).
    - **"Only through the novelty filter".** "Past experiments enter the design only through the novelty filter" is false, because they also enter through θ̂_p and Σ_θ. Write "the accumulated Fisher information of past experiments is not used; past trajectories enter through the novelty filter".
    - **Sentence length.** The sentence "Each design iteration produced …" has 42 words.

13. **C56 (P:801).**
    - **Undefined symbol.** a★ is used before its definition (P:969). Add "where a★ holds the coefficients of π_EI★".
    - **Wording.** "within the support of b_j" should be "weighted by b_j" (`transfer_calibration.py:212-223`).

14. **Broken antecedents.**
    - **P:908 (after C74).** "therefore" has lost its premise. Delete it.
    - **P:857 (after C63).** "decreases further", although the previous sentence says ρ rose. Write "then decreases".
    - **C19 (P:72).** "…of its onboard controller that both designs…": the controller seems to design the flights. Write "…and its onboard controller; the DT both designs…".

15. **C31: frame and table height.**
    - **x origin.** The x origin is no longer defined, because the deleted sentence was its only definition. Restore it.
    - **Table height.** "0.63 m above the floor" is TABLE_HEIGHT_Z in the Lighthouse frame (`jDT/params.py:54`), and that frame's origin is not documented. The card itself asks the author to confirm it, so keep the number out until he does.

16. **Facts stated twice:** "leave the box [−1,1]³" (C56 P:969 and C82 P:971); "validated by its authors in near-hover flight" (C17, C34); Kan, Lei, Yon and Herz (C08 and C35/C36); Carter (C08, C67); the domain restriction (P:606, P:829, P:846). In II-B, cite and give only the consequence for the model.

17. **C43 (P:604).** "four batches" next to "three policies per iteration" (C48) suggests 12 designs, but 10 were flown. Add "of the last batch only one policy was flown (INF_10)".

18. **C35.** `DelContBernard2017` is cited for "transient development … at the obstacle edges", but its abstract reports no finding (`literature_ge_identification.md:57,99`). Keep only Curtiss1984.

## Minor

- **Sentences over 40 words (new text):** C06 (42), C07 (46), C08 Yon/Herz (45), C19 second and third contributions (47, 41), C35 Kan (42), C51 (41), C54 (51), C82 (41), C85 (42), C86 (45).
- **Colons:** C43 ("in four batches: six…"), C84 ("six standardized inputs: …"); old one at P:631.
- **C86:** "after twelve episodes" against "13 cumulative episodes" (P:855).
- **C20:** roadmap is a comma splice; use semicolons.
- **C04:** edits 1 and 3 rewrite rather than cut, against his rule.
- **C05:** "hazardous missions, from logistics…" makes logistics hazardous.
- **C33:** the script also refuses DT-predicted clearance below 0.5R (`run_next_experiment.py:247-252`); relevant to the 0.3R design screen and to "checked only in the DT".
- **P:244:** "EI is set to zero when σ=0" conflicts with C55's variance floor.
- **C29:** caption uses R̂_•; text uses μ_•.

## Card dependencies

- **C52** ↔ C19, C70, C86, P:195 and P:751 (item 7).
- **C80** ↔ C82 (P:971 ranking), C84 ("means over the flights" is the stored per-run metric, not Eq. (reward)), P:991, P:1000 (0.57 and 0.83 are Eq. (reward) values, while Fig. 15 shows 0.365 and 0.757) and the third paragraph of the Conclusions. As built, III-E mixes the two metrics.
- **C40** ↔ C30 Block 1 ("first episode uses π_BL"), P:597, P:763 ("first tested"), P:908 ("already available"), C18, C53 and C77 (item 8).
- **C74** needs C22: if C22 is unticked, the exclusion of the information-policy rewards disappears.
- **C48** ↔ P:606, P:713 and Block 5 (item 4).
- **C43, C60 and C61** ↔ P:846 (item 1).
- **C42** ↔ P:433.
- **C56** ↔ C82 (duplicate sentence).
- **C54 and C43** need the renames C91 and C87, or "safe" and "near-wall" return.

## Not covered by any card

- **GPT-5:** E[R_•] in Eq. (rt-physical-objective) against the deterministic nominal design rollout; C02's list omits it.
- **GPT-4:** a★'s distance to the faces (0.30) and EI_06/08 within 0.09 of a_B = +1 are not reported.
- **GPT-11, GPT-13, GPT-15 (partly):** floors on f_GE and z; χ_i depending on x only; kernel and pooling of the condition-aware GP; reward spread and record roles in Table II.
- **GPT-12:** uncertainty of J_BL in S.
- **Table I:** omits the products of inertia that the DT uses (`jDT/params.py:169-173`).
- **GE-identification literature:** the gap sentence rests on `literature_ge_identification.md:90`, whose closest works (Lopez-Sanchez 2020, Wilson 2014) are not cited.

## Layout

18 pages, no errors, no overfull boxes, no undefined references or placeholders. Fig. 2 floats two pages after its first mention. Table II uses π_λ,i and π_a,i before the text defines them. Nothing needs action.
