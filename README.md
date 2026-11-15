# TERRA-SPACE — Dhofar / Rocknest starter data package

## What is included

- `data/earth/dhofar_ama18_sem_eds.csv`
  - 12 AMADEE-18 sample IDs and rounded oxide-equivalent wt% values from the published SEM–EDS Table 5.
  - The paper describes these as semiquantitative EDS results on prepared mixed-powder pellets, not high-accuracy whole-rock bulk chemistry.
  - Two poor-quality spectra (4-15 and 8-18) were omitted by the paper authors.
- `data/earth/dhofar_mineral_detection_summary.csv`
  - Qualitative mineral detections reported across the AMADEE-18 sample suite.
  - It intentionally does not invent per-sample abundance values.
- `data/mars/rocknest_apxs_bulk.csv`
  - Rocknest bulk APXS major-element oxide chemistry.
- `data/mars/rocknest_chemin_mineralogy.csv`
  - CheMin mineral abundances for crystalline phases only.
- `data/earth/dhofar_vs_rocknest_preliminary_scores.csv`
  - Preliminary 0–100 profile-similarity scores using seven common oxides.
- `models/soil_similarity.py`
  - Reusable calculation function.

## Preliminary score method

For the seven common oxide components (SiO2, Al2O3, FeO/FeOT, MgO, CaO, Na2O, K2O), each Earth and Mars vector is renormalised to sum to 1 over the shared components. The score is:

`100 * (1 - 0.5 * sum(abs(E_i - M_i)))`

This is a Bray–Curtis-style similarity for compositional profiles.

## Critical limitations

1. Dhofar values are rounded SEM–EDS oxide-equivalent values; Rocknest values are APXS bulk chemistry. The methods and sample scales differ.
2. The Dhofar SEM–EDS results are semiquantitative and are not interchangeable with laboratory XRF whole-rock chemistry.
3. The preliminary score is therefore a **screening indicator only**, not a validated mineralogical similarity score.
4. The score is not an agricultural suitability score. It says nothing by itself about plant growth, water retention, nutrient availability, salinity, perchlorates or toxicity.
5. The score excludes oxides not shared in both datasets and renormalises the shared subset. It must be displayed with that explanation.
6. The Rocknest CheMin mineral abundances are crystalline phases only. The sample also contains a substantial X-ray amorphous component.
7. Dhofar sample coordinates and detailed quantitative XRD results are described as available in the AMADEE-18 supporting-data archive. They have not yet been ingested into this starter package. Do not plot invented sample coordinates.
8. The AMADEE-18 mission also included Hortextreme, a hydroponic microgreens greenhouse experiment. The project gap is specifically soil-as-substrate characterisation / soil-based cultivation, not the absence of all plant-growth work at the site.

## Sources

- Lalla et al. (2020), *Laboratory Analysis of Returned Samples from the AMADEE-18 Mars Analog Mission*, Astrobiology 20(11), 1303–1320. DOI: https://doi.org/10.1089/ast.2019.2038
- Rull et al. (2020), *Raman characterization of terrestrial analogs from the AMADEE-18 astronaut simulated mission using the ExoMars RLS simulator*. DOI: https://doi.org/10.1002/jrs.6023
- Blake et al. (2024), *The Chemistry and Mineralogy (CheMin) X-ray Diffractometer on the MSL Curiosity Rover: A Decade of Mineralogy from Gale Crater, Mars*. https://www.mdpi.com/2075-163X/14/6/568
- Rocknest bulk APXS composition reproduced in Clark et al. (2020), JSC-Rocknest simulant paper. https://ntrs.nasa.gov/api/citations/20205001719/downloads/Clark_JSCRN_Submission_April30-2020.pdf
- AMADEE-18 mission science archive: https://mission.oewf.org/archive/

## Next data-acquisition priorities

1. Download AMADEE-18 supporting files with sample coordinates and per-sample XRD quantitative mineral abundances.
2. Retrieve sample-specific SEM–EDS and Raman detection matrices.
3. Find Dhofar agricultural soil measurements: pH, EC/salinity, texture, CEC, N, P, K, organic carbon and water-retention curves.
4. Select a Mars agricultural reference deliberately. Rocknest is a basaltic aeolian soil reference; Phoenix is a separate northern-plains chemistry/perchlorate reference. Do not merge them into one sample.
5. Build separate mineralogical similarity, major-element profile similarity, and agricultural compatibility assessments.
