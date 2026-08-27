# NER-SAGE Architecture Rules

These rules apply to ALL agents working on the NER-SAGE project.
They are non-negotiable and must be followed in every component.

---

## Data Integrity

1. **Never invent real-time data.**
   - All observations must come from a real source or be explicitly marked `is_simulated: true`.
   - Synthetic data used in demos must be labelled at every layer (API response, UI, logs).

2. **Missing data does not automatically reduce risk.**
   - An unknown satellite observation does not make the area safer.
   - The uncertainty engine must treat missing inputs as UNKNOWN, not as LOW.

3. **Conflicting evidence must always be surfaced.**
   - When evidence sources disagree, the system must return `evidence_status: "CONFLICTING"`.
   - Silent averaging of conflicting signals is forbidden.

4. **Every data item must carry provenance.**
   - Required fields: `source`, `timestamp`, `location`, `evidence_type`, `freshness`, `reliability`, `is_simulated`.
   - No data item may enter the evidence store without these fields.

---

## Prediction Model

5. **ML probability and confidence are always separate fields.**
   - `risk_score` (0–1): probability of landslide
   - `confidence` (0–1): trust in the risk score
   - These MUST be displayed together. Displaying risk without confidence is forbidden.

6. **Calibrated probabilities are required.**
   - Raw XGBoost/RF output must be calibrated before display.
   - Use isotonic regression or Platt scaling.

7. **The ML risk model is a component, not the complete product.**
   - The pipeline must continue through uncertainty → evidence → verification → consequence → simulation → decision.

---

## Evidence and Verification

8. **Citizen reports are additional evidence, not ground truth.**
   - Every citizen report must pass: metadata validation → location validation → timestamp validation → duplicate detection → CV analysis → reliability scoring.
   - Verified reliability score must accompany any report used in the decision pipeline.

9. **Stale evidence must be flagged.**
   - Satellite observations older than 7 days: `freshness: "LOW"`.
   - Ground reports older than 24 hours: `freshness: "MEDIUM"`.

---

## Decision Engine

10. **Every recommendation must have an explanation.**
    - Required: `reason`, `supporting_evidence`, `unknown_evidence`, `consequence_if_wrong`.

11. **ALL critical actions require authorized human approval.**
    - Evacuations, road closures, resource pre-positioning: human approval required.
    - The system may RECOMMEND but never DISPATCH autonomously.

12. **Decision value is not the same as uncertainty reduction.**
    - A piece of evidence is valuable if it reduces uncertainty about a HIGH-CONSEQUENCE decision.
    - Formula: `DecisionValue = (UncertaintyReduction × DecisionImportance × Reliability) / AcquisitionCost`

---

## Database

13. **Use MongoDB for operational documents.**
    - Evidence, risk predictions, citizen reports, audit logs, simulations.

14. **Use Neo4j exclusively for graph connectivity.**
    - Road networks, village isolation, hospital accessibility, cascading failures.
    - Never duplicate graph queries in MongoDB.

15. **Use Redis only for cache and temporary state.**
    - Redis is NOT the permanent evidence store.
    - All Redis data must have a TTL.

16. **Use Qdrant only for vector retrieval (RAG).**
    - Do not store operational documents in Qdrant.

17. **Never store large binary files in MongoDB.**
    - Images, DEMs, satellite rasters, videos → MinIO object storage.
    - MongoDB stores only the MinIO object key/URL.

---

## Code Architecture

18. **Business logic belongs in backend services.**
    - Never put core decision logic inside API route handlers.
    - Never put core decision logic inside UI components.

19. **Write tests for every decision-engine component.**
    - Evidence engine: unit tests for reliability, freshness, contradiction, unknowns.
    - Decision engine: unit tests for prioritization, action scoring.
    - Graph engine: tests for isolation, connectivity, alternate routes.

20. **Keep model versions and prediction timestamps.**
    - Every `risk_predictions` document must include `model_version` and `created_at`.
    - Every simulation must store `scenario_type`, `input_changes`, `baseline_state`, `simulated_state`.

---

## AI Responsibility

21. **NER-SAGE is a research and decision-support prototype.**
    - It is NOT an official emergency warning authority.
    - AI-generated text must never be presented as an official government warning.

22. **LLM (Groq) is for explanation, not calculation.**
    - The LLM must never independently calculate risk probabilities.
    - It receives structured state and generates grounded explanations from retrieved SOPs.

23. **GenAI responses must include source attribution.**
    - Every RAG-generated explanation must display source document name, version, and jurisdiction.

---

## NER Region Constants

- Bounding box: lon [88.0, 97.4], lat [21.9, 29.5]
- Coordinate system: WGS84 (EPSG:4326)
- Risk thresholds: HIGH ≥ 0.75, MEDIUM 0.50–0.74, LOW < 0.50
- Confidence thresholds: HIGH ≥ 0.80, MEDIUM 0.60–0.79, LOW < 0.60
- Satellite freshness: HIGH < 2 days, MEDIUM 2–7 days, LOW > 7 days
