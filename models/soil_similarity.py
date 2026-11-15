"""Exploratory Earth-Mars major-oxide profile comparison.

This is a screening metric only. It is not a mineralogical match score or
plant-growth suitability score. See README for method limitations.
"""
import numpy as np
import pandas as pd

COMMON_OXIDES = ["SiO2", "Al2O3", "FeO", "MgO", "CaO", "Na2O", "K2O"]

ROCKNEST_APXS = {
    "SiO2": 42.97,
    "Al2O3": 9.37,
    "FeO": 19.18,  # total iron expressed as FeO (FeOT)
    "MgO": 8.69,
    "CaO": 7.26,
    "Na2O": 2.70,
    "K2O": 0.49,
}

def bray_curtis_profile_similarity(earth_values, mars_values=ROCKNEST_APXS):
    """Return 0-100 similarity after normalising the shared oxide subset."""
    e = np.array([float(earth_values[k]) for k in COMMON_OXIDES], dtype=float)
    m = np.array([float(mars_values[k]) for k in COMMON_OXIDES], dtype=float)
    if np.any(e < 0) or np.any(m < 0) or e.sum() == 0 or m.sum() == 0:
        raise ValueError("Oxide values must be non-negative and have a positive sum.")
    e /= e.sum()
    m /= m.sum()
    return float(100 * (1 - 0.5 * np.abs(e - m).sum()))

def score_dhofar_samples(csv_path):
    df = pd.read_csv(csv_path)
    rows = []
    for _, r in df.iterrows():
        vals = {
            "SiO2": r["SiO2_wt_pct"], "Al2O3": r["Al2O3_wt_pct"],
            "FeO": r["FeO_wt_pct"], "MgO": r["MgO_wt_pct"],
            "CaO": r["CaO_wt_pct"], "Na2O": r["Na2O_wt_pct"],
            "K2O": r["K2O_wt_pct"],
        }
        rows.append({
            "sample_id": r["sample_id"],
            "major_oxide_profile_similarity_score": round(
                bray_curtis_profile_similarity(vals), 2
            )
        })
    return pd.DataFrame(rows).sort_values(
        "major_oxide_profile_similarity_score", ascending=False
    )
