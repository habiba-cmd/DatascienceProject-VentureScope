# VentureScope — runnable research prototype

## 1. Set up (Windows / Jupyter)

Open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
jupyter notebook VentureScope_Complete.ipynb
```

Change `DATA_DIR` in the first notebook configuration cell to `Path(r"D:\Downloadeds")` if needed. Run the notebook **in order**. It inspects ZIP members and reads the Amazon CSVs with the correct headerless schema.

## 2. Run dashboard

```bash
python -m streamlit run app.py
```

## What is and is not validated

* Four sources are ingested separately. Amazon Reviews train/test is the **Amazon Review Polarity** format (labels 1 and 2); it is not the UCSD Amazon Reviews 2023 corpus. It lacks ASIN/category/date, so cannot be product-joined to the Amazon Products snapshot.
* The Amazon Products file is a sampled snapshot, not a live complete marketplace inventory.
* Olist is historic Brazil; UCI is historic UK; their records are not joined to Amazon rows.
* Review keyword flags are **candidate** complaints, not validated unmet-need labels.
* The sentiment classifiers have genuine held-out evaluation using the provided train/test partitions, but they do not evaluate aspect-level unmet-need detection.
* Market scores are withheld until domain-matched, human-validated customer problem and other evidence is provided. Optional user-entered inputs are explicitly labelled as such.
* Human annotation, inter-annotator agreement, expert/user studies, present-day regional market data and external opportunity-score backtesting **cannot be fabricated** and are not claimed as complete.

## Outputs

`outputs/` contains per-source CSVs, trained sentiment models, text reports, plots, sample annotation worksheet, and manifest. All derived metrics are computed locally from the supplied data; no results are prefilled.

## Running tests

```bash
python -m pytest tests -q
```

## Integrated business-idea assessment (new)
The notebook now includes category shortlist matching, a category-specific competitor profile, an annotation worksheet that is preserved across reruns, genuine annotation evaluation if labels are provided, and chronological historical baseline comparison. The dashboard exposes category suggestions, competitor listings, and annotation status. **Lexical category suggestions require human confirmation.**

### Fastest execution
1. `python -m pip install -r requirements.txt`
2. Open `VentureScope_Complete.ipynb` in Jupyter from this folder and run all cells. `DATA_DIR` defaults to `D:\Downloadeds`.
3. Edit `BUSINESS_IDEA` in the integrated section and confirm `SELECTED_CATEGORY`.
4. `python -m streamlit run app.py`
5. Enter actual human labels in `outputs/customer_problem_annotation.csv`, rerun the annotation evaluation cell, and inspect `outputs/need_classifier_comparison.csv`.

**Research status:** Dataset-dependent experiments and human validation have not been run in this distribution. A complete research claim requires actual annotation, matched contemporary evidence, expert evaluation and retrospective tests; the system never fabricates those.
