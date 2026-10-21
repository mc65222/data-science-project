# Harassment and Bullying in U.S. Public Schools

**A reproducible data science project using the 2015–16 Civil Rights Data Collection (CRDC).**

Status: **local analysis completed**. GitHub repositories, public website publication and peer review remain to be completed by the student.

## 1. Problem and research question

How did reported harassment and bullying vary by basis in U.S. public schools in 2015–16, and how did the sex composition of reported students differ across categories?

The aim is to communicate patterns in historical administrative records through clear, reproducible descriptive analysis. This project does not predict individual behavior or estimate the causal effect of school policies.

## 2. Dataset source and usage permissions

- **Producer:** U.S. Department of Education, Office for Civil Rights (OCR).
- **Collection:** Civil Rights Data Collection, school year **2015–16**. This is the observation period, not 2026.
- **Official catalog and download links:** [2015–16 Harassment or Bullying by Basis Category](https://catalog.data.gov/dataset/2015-16-harassment-or-bullying-by-basis-category-civil-rights-data-collection).
- **Collection background:** [2015–16 CRDC](https://www.ed.gov/laws-and-policy/civil-rights-laws/civil-rights-data-collection-crdc/civil-rights-data/civil-rights-data-collection-crdc-2015-16-school-year).
- **Use permission:** the official catalog marks the dataset as public and identifies its license as **CC BY**, linking to [the attribution license entry](http://www.opendefinition.org/licenses/cc-by). Retain source attribution with reused data and figures. The catalog does not specify a CC BY version; this project does not invent one.
- **Attribution:** U.S. Department of Education, Office for Civil Rights, Civil Rights Data Collection, 2015–16. Figures and cleaned tables in this project are derived from the seven supplied Excel workbooks.
- **Privacy:** the inputs are state and national aggregate tables. The analysis does not use student names, personal records, passwords or API keys. Do not add restricted-use CRDC records or identifiable student data to this repository.

The seven supplied files must be present under `dataset/`:

```text
Allegations-of-Harassment-or-Bullying.xlsx
Harassment-Bullying-on-basis-of-disability-disciplined.xlsx
Harassment-Bullying-on-basis-of-disability-reported.xlsx
Harassment-Bullying-on-basis-of-race-disciplined.xlsx
Harassment-Bullying-on-basis-of-race-reported.xlsx
Harassment-Bullying-on-basis-of-sex-disciplined.xlsx
Harassment-Bullying-on-basis-of-sex-reported.xlsx
```

The first file has a `Total` sheet. Each of the other six has `Total`, `Male` and `Female` sheets: **19 sheets in total**. Each analyzed sheet contains 50 states, the District of Columbia, and a separate United States total. The national row is never added to the state rows.

## 3. Methods and tools

**Tools:** Python, pandas, NumPy, openpyxl and Matplotlib. See [requirements.txt](requirements.txt) for the exact tested package versions.

1. Read the original workbooks in read-only mode.
2. Validate the title, school year, geography header and count header.
3. Identify data rows using state names in column B; exclude decorative headings, notes and stray numeric cells below the tables.
4. Extract allegation counts, student totals, source sex categories, school counts and reporting coverage into tidy tables. Detailed race/ethnicity, IDEA, Section 504 and English-learner breakdowns are outside this project's analysis scope and are not extracted.
5. Reject blank, nonnumeric, negative or noninteger count values. Missing values and suppression symbols are **not** replaced with zero. There were no missing count values in the extracted fields of the supplied files.
6. Reconcile national totals against the sum of states and DC, and check `Male + Female = Total` in each student table. Check that the five allegation categories sum to the allegation total.
7. Calculate national allegation shares and within-basis male/female shares among reported students; create three labeled figures.
8. Save cleaned CSVs, findings, validation results, input SHA-256 hashes, software versions and a written report.

**Source-table issues handled explicitly:** column A contains unrelated or repeated labels in some workbooks and is ignored. The race-related allegations header contains duplicated wording; it is normalized to “Race, color, or national origin” in the output schema. Workbook B2 titles and filenames identify each student table's basis and measure. Source files are preserved unchanged. Original school-reporting coverage is retained; values below 85% are flagged for caution. In the allegations table, District of Columbia has approximately 48.9% coverage. These coverage percentages describe schools reporting, not the proportion of students experiencing bullying.

## 4. Key findings and visualizations

### A. Distribution of allegations

The national table contains **135,192 allegations**. Sex-based allegations are the largest category: **55,579 (41.1%)**. Race/color/national-origin allegations account for **30,913 (22.9%)**. These are allegations, not counts of unique students.

![Horizontal bar chart of five allegation categories, with sex-based allegations the largest at 55,579](results/figures/01_allegations_by_basis.png)

### B. Two different student measures

| Basis of harassment or bullying | Students reported as harassed or bullied | Students disciplined for harassment or bullying |
| --- | ---: | ---: |
| Sex | 43,705 | 50,191 |
| Race, color, or national origin | 23,491 | 28,677 |
| Disability | 9,320 | 12,234 |

![Grouped bar chart showing reported and disciplined student counts as separate measures](results/figures/02_reported_and_disciplined.png)

**Interpretation:** reported victims and disciplined students are different groups and are not linked to individual incidents in these aggregate files. More disciplined students than reported victims does not imply a processing rate above 100%. Do not calculate a “discipline success rate” from this comparison or add the groups together.

### C. Sex composition of reported students

Female students account for **63.9%** of sex-based reported students. Male students account for **63.5%** of race-based and **66.9%** of disability-based reported students.

![Stacked bar chart showing the male and female shares within each reported-student category](results/figures/03_reported_students_by_sex.png)

**Denominator:** male plus female reported students within each basis. These shares are not population risk rates. Labels reproduce the source's sex categories and do not represent all gender identities.

The [generated analysis report](results/analysis_summary.md) and [findings JSON](results/findings.json) are regenerated by the script. README and portfolio prose are curated documents: review them if the input data changes.

## 5. Limitations and next improvements

The principal limitation is that **counts of administrative reports do not measure the true prevalence of bullying**. Underreporting and differences in reporting practice and coverage may affect the results. The allegations table reports 99.5% of schools reporting nationally, with lower coverage in some jurisdictions.

Enrollment denominators are absent from these seven workbooks, so this project cannot compare population risks across states or demographic groups. The files describe one historical school year and cannot establish trends, current conditions or causation. Students may be counted in more than one basis category; the three bases must not be summed to estimate distinct victims. The validation checks establish internal consistency, not the accuracy of the original reports.

Next steps: obtain compatible enrollment denominators, investigate reporting completeness, and compare multiple school years using consistent definitions. Add a real classmate's feedback and record an actual improvement before submission.

## 6. Reproduce the analysis

Use **Python 3.11 or 3.12**. The project was run successfully with Python 3.11.2 and the pinned packages in `requirements.txt`. No API keys, accounts or network requests are needed by the analysis once dependencies and the seven workbooks are present.

### Jupyter Notebook (recommended for reading and submission)

Open [analysis.ipynb](analysis.ipynb) for a self-contained notebook with explanatory Markdown, validation output, tables and three embedded figures. It does not import or require `analysis.py`. Both entry points implement the same analysis; the notebook was executed from a fresh Jupyter kernel, and its CSVs and findings matched the script outputs.

Keep `analysis.ipynb` in the project root beside `dataset/`. In Windows PowerShell:

```powershell
cd "C:\Users\Administrator\Desktop\CISC7204\data-science-portfolio"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

Open `analysis.ipynb`, select the environment containing these dependencies, and restart the kernel and run all cells in order. In VS Code, open the notebook with the Jupyter extension and select the same Python environment. The saved notebook already contains outputs for viewing on GitHub. The working directory must contain `dataset/`, or be one directory below the project; otherwise set `ROOT` in the paths cell explicitly.

`requirements.txt` pins analysis libraries. [requirements-notebook.txt](requirements-notebook.txt) includes those pins and adds the Jupyter interface and kernel; interface versions are not pinned. The `.py` script remains available as an optional command-line alternative below. Running either entry point regenerates `results/`.

### Windows PowerShell

```powershell
cd "C:\Users\Administrator\Desktop\CISC7204\data-science-portfolio"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe analysis.py
```

Virtual-environment activation is unnecessary. If `python` is unavailable but the Python launcher is installed, use `py -3.11 -m venv .venv` for the first Python command. Dependency installation requires internet access unless the packages are cached.

### macOS / Linux

From the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analysis.py
```

### Optional input/output locations

```bash
python analysis.py --data-dir /path/to/dataset --output-dir /path/to/results
```

Defaults are relative to the location of `analysis.py`, so the script also works when called from another working directory. A missing workbook or failed consistency check produces an explicit error. Fix the input problem rather than bypassing validation.

### Output files

```text
results/
  figures/
    01_allegations_by_basis.png
    02_reported_and_disciplined.png
    03_reported_students_by_sex.png
  tables/
    students_clean.csv                 # 936 rows: 18 sheets x 52 geographies
    allegations_clean.csv              # 52 rows: US + 50 states + DC
    national_allegations.csv
    national_student_counts.csv
    reported_sex_shares_pct.csv
    low_coverage_student_tables.csv
  analysis_summary.md
  findings.json
  validation.json
  input_audit.json
```

Expected headline results: 135,192 total allegations; 55,579 sex-based allegations; 41.1% sex-based share. `validation.json` should have `"status": "passed"`. `input_audit.json` records package versions and workbook hashes. Figure styles can vary slightly between operating systems; CSV counts should match.

## 7. Portfolio files and the two-repository requirement

This local folder contains both the project analysis and the portfolio source for convenience. The assignment still calls for **two separate public GitHub repositories**. Before uploading, verify the repository names against your original Moodle page, whose pasted formatting is ambiguous about a leading period.

| Destination | Files to upload |
| --- | --- |
| Project repository (`data-science-project`, subject to the exact course naming requirement) | `analysis.ipynb`, `requirements.txt`, `requirements-notebook.txt`, `README.md`, `.gitignore`, `dataset/` and `results/`; optionally retain `analysis.py` as the equivalent command-line version |
| Portfolio repository (`data-science-portfolio`, subject to the exact course naming requirement) | `index.md`, `_config.yml`, `_layouts/`, `assets/`, and `results/figures/` |

Create the portfolio repository with its own short README. Both repositories need the figure files if you keep the supplied relative image paths. The project repository does not need website template files.

Before publishing, replace **YOUR_FULL_NAME** and **YOUR_GITHUB_USERNAME** in `index.md`, including the project repository URL. Update that URL if the course requires a different repository name. The introduction is a neutral coursework description; customize it to reflect your actual experience.

In the portfolio repository, enable **Settings → Pages → Deploy from a branch → main → / (root) → Save**. The included `index.md` uses a local Jekyll layout from `_layouts/default.html`; `_config.yml` enables that layout. There is no competing `index.html` entry file. Open the actual URL shown by GitHub Pages and test all images and the project link. A typical URL is `https://YOUR_GITHUB_USERNAME.github.io/data-science-portfolio/`, but use the actual URL provided by GitHub.

See [the Chinese completion guide](GUIDE_ZH.md) for remaining submission steps. No repository has been created and no files have been uploaded by the assistant.

## 8. Peer review and AI declaration

Ask a real classmate to identify the research question, main finding and limitation. Record their feedback, make one improvement and commit it with a descriptive message. Do not claim this step was completed before it happens.

AI assistance was used to draft the Python analysis, documentation and portfolio source. The student must review the code, understand the findings and customize the submission. Record the tool as **OpenAI Codex (desktop app)**; use the exact model name visible in your session if your course requires it, rather than guessing. Do not copy the assignment's Gemini/Poe example unless those were actually used. Keep your student ID in the course forum if required; it does not need to be published on the public website.
