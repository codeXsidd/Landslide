# NER-LDI Terrain-Based Landslide Susceptibility Baseline Model

**Generated**: 2026-08-27T13:01:48.811101+00:00
**Model Version**: 1.0.0-baseline

## 1. Purpose

This is a **baseline static susceptibility model** that estimates relative landslide susceptibility
based solely on terrain morphology. It identifies areas where topographic conditions are similar
to historically recorded landslide locations in Northeast India.

## 2. Data Sources

- **Landslide inventory**: GSI NER landslide inventory (10982 events)
- **Terrain rasters**: SRTM GL1 30m DEM derivatives
- **Terrain coverage**: PARTIAL (24/57 NER cells)

## 3. Training Data Construction

- Total GSI events: 10982
- Events excluded (outside current terrain coverage): 1962
- Positive samples used: 7965
- Negative samples generated: 15930
- Total training rows: 23895

## 4. Positive/Negative Sampling

- **Positive (label=1)**: Historical GSI landslide locations with valid terrain features
- **Negative (label=0)**: Random background points at minimum 0.01° (~1.1 km) from any landslide
- **Ratio**: 2 negatives per positive
- Only points with complete terrain feature extraction (no NoData) are used

## 5. Spatial Split

- **Method**: spatial_grid_block_0.5deg
- Points are assigned to 0.5° grid blocks; entire blocks are allocated to train or test
- This prevents spatial autocorrelation leakage between train and test sets
- Train rows: 18784
- Test rows: 5111

## 6. Features

| Feature | Description |
|---|---|
| elevation | Elevation in meters (SRTM GL1) |
| slope | Slope angle in degrees |
| aspect | Slope aspect in degrees (0-360, N=0) |
| terrain_ruggedness | Terrain Ruggedness Index (TRI) |

## 7. Model Comparison

| Metric | RandomForest | XGBoost |
|---|---|---|
| accuracy | 0.7642 | 0.7574 |
| precision | 0.4678 | 0.4582 |
| recall | 0.8046 | 0.7825 |
| f1 | 0.5917 | 0.5779 |
| roc_auc | 0.8433 | 0.8355 |
| pr_auc | 0.4911 | 0.4779 |
| brier_score | 0.1503 | 0.1543 |

**Selected model**: RandomForest

## 8. Evaluation Metrics (Best Model)

- Accuracy: 0.7642
- Precision: 0.4678
- Recall: 0.8046
- F1: 0.5917
- ROC-AUC: 0.8433
- PR-AUC: 0.4911
- Brier Score: 0.1503

## 9. Limitations

- Terrain coverage is partial (24/57 required SRTM cells downloaded)
- Model trained only on areas where terrain data is available
- Northern NER (Arunachal Pradesh, parts of Assam/Nagaland above 26°N) are not covered
- No rainfall, soil moisture, or land cover features included
- Negative sampling is random background, not confirmed stable sites
- GSI inventory may have spatial reporting bias toward accessible areas

## 10. Why This is a Baseline Susceptibility Model

This model captures **static terrain predisposition** to landslides. It does not
account for dynamic triggering factors (rainfall, seismicity, land-use change).
It provides a spatial prior for where landslides are more likely given terrain alone.

## 11. NOT an Official Emergency Warning

**This model is for research purposes only.** It is NOT:
- An official early warning system
- A replacement for GSI/NDMA/IMD hazard assessments
- Suitable for evacuation decisions without expert review
- Validated against real-time event data

## 12. Why Rainfall is Not Yet Included

The IMERG rainfall data available in this project is a 7-day test extract, not a
multi-year historical rainfall record. Using it as a training feature would:
- Misrepresent temporal rainfall patterns
- Create a model that cannot generalize beyond the test period
- Require antecedent rainfall computation over months/years of data

Rainfall will be incorporated in the dynamic risk model once multi-year IMERG
data is acquired and antecedent rainfall indices are computed.
