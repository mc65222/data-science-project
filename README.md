# Harassment and Bullying in U.S. Public Schools

**Author:** Li Linye  
**Course:** CISC7204  
**Project status:** Completed — descriptive analysis and reproducible documentation

This project uses Python and Jupyter Notebook to investigate harassment and bullying in U.S. public schools using the **2015–16 Civil Rights Data Collection (CRDC)**. It combines data cleaning, consistency checks, descriptive statistics and three visualizations.

## Research Question

How did reported harassment and bullying vary by basis in U.S. public schools in 2015–16, and how did the sex composition of reported students differ across categories?

The analysis considers allegations based on sex, race/color/national origin, disability, sexual orientation and religion. Separate student tables examine sex-, race- and disability-based bullying.

## Dataset Source and Usage Permissions

**Data producer:** U.S. Department of Education, Office for Civil Rights (OCR).

**Collection:** Civil Rights Data Collection, school year 2015–16.

- [Official dataset catalog and Excel downloads](https://catalog.data.gov/dataset/2015-16-harassment-or-bullying-by-basis-category-civil-rights-data-collection)
- [Background and documentation for the 2015–16 CRDC](https://www.ed.gov/laws-and-policy/civil-rights-laws/civil-rights-data-collection-crdc/civil-rights-data/civil-rights-data-collection-crdc-2015-16-school-year)

The official catalog identifies the dataset as **public** and lists a **CC BY** license. The catalog links to [this attribution-license entry](http://www.opendefinition.org/licenses/cc-by) without specifying a version. Reused data and derived visualizations should retain attribution to the original producer.

**Attribution:** U.S. Department of Education, Office for Civil Rights, Civil Rights Data Collection, 2015–16. The figures and cleaned tables in this repository are derived from the seven source workbooks listed below.

The files contain aggregate national and state statistics. No student-level personal information, restricted-use records, passwords or API keys are needed.

### Input Files

Place these seven workbooks in the `dataset/` directory:

```text
Allegations-of-Harassment-or-Bullying.xlsx
Harassment-Bullying-on-basis-of-disability-disciplined.xlsx
Harassment-Bullying-on-basis-of-disability-reported.xlsx
Harassment-Bullying-on-basis-of-race-disciplined.xlsx
Harassment-Bullying-on-basis-of-race-reported.xlsx
Harassment-Bullying-on-basis-of-sex-disciplined.xlsx
Harassment-Bullying-on-basis-of-sex-reported.xlsx
```

The allegations workbook has one `Total` sheet. The six student-count workbooks each contain `Total`, `Male` and `Female` sheets, giving **19 sheets**. Each sheet contains 50 states, the District of Columbia and a separate national total.

## Methods and Tools

| Tool | Purpose |
| --- | --- |
| Python and Jupyter Notebook | Organize the analysis, explanations and outputs |
| pandas | Create tidy tables and calculate summaries |
| NumPy | Perform numerical operations and validation |
| openpyxl | Read the Excel workbooks |
| Matplotlib | Generate labeled, reproducible figures |

The workflow is:

1. Read the original workbooks without modifying them.
2. Validate table titles, school year and key column headers.
3. Select geography rows while excluding titles, footnotes and stray scratch values.
4. Extract allegation counts, student totals, source sex categories and school-reporting coverage into tidy tables.
5. Reject missing, nonnumeric, negative or noninteger counts rather than replacing them with zero.
6. Check that national totals equal the sum of the 50 states and DC, that `Male + Female = Total`, and that allegation categories sum to the allegation total.
7. Calculate national counts and within-category shares, create three figures and export results.

National totals are never added to state rows. Reporting coverage below 85% is flagged for caution. Unrelated or repeated labels in column A are ignored; student-table titles and filenames determine the relevant basis and measure. The malformed race-related allegation heading is normalized to “Race, color, or national origin.”

## Key Findings and Visualizations

### 1. Sex-Based Allegations Were the Largest Category

The national table records **135,192 allegations**. Of these, **55,579 (41.1%)** were sex-based and **30,913 (22.9%)** concerned race, color or national origin.

![Allegation counts by basis, with sex-based allegations the largest category](results/figures/01_allegations_by_basis.png)

These counts represent allegations, not unique students. Percentage shares use the national allegation total as the denominator.

### 2. Reported and Disciplined Counts Describe Different Groups

| Basis | Students reported as harassed or bullied | Students disciplined for harassment or bullying |
| --- | ---: | ---: |
| Sex | 43,705 | 50,191 |
| Race, color, or national origin | 23,491 | 28,677 |
| Disability | 9,320 | 12,234 |

![Separate reported and disciplined student counts for three bullying categories](results/figures/02_reported_and_disciplined.png)

Reported victims and disciplined students are different, unlinked groups. Their ratio cannot establish a case-resolution rate, and the two measures should not be added together.

### 3. Sex Composition Differs Across Reported Categories

Female students account for **63.9%** of sex-based reported students. Male students account for **63.5%** of race-based and **66.9%** of disability-based reported students.

![Male and female shares among reported students within each bullying category](results/figures/03_reported_students_by_sex.png)

Each percentage uses male plus female reported students within that basis as its denominator. These are composition shares, not population risk rates. Labels follow the source's sex categories and do not represent all gender identities.

## Limitations

The principal limitation is that **administrative reports do not measure the true prevalence of bullying**. Underreporting and differences in reporting practices and coverage can affect the counts. National school-reporting coverage in the allegations table is approximately 99.5%, while DC has approximately 48.9% coverage in that table.

The seven workbooks do not provide enrollment denominators, so the analysis cannot compare population risks across states or demographic groups. Categories may overlap, preventing their sum from representing unique victims. One historical school year cannot establish trends, current conditions or causation. Internal consistency checks do not independently verify the accuracy of original school reports.

## How to Reproduce the Analysis

### Requirements

- Python **3.11 or 3.12**; execution was verified with Python 3.11.2.
- The seven Excel workbooks in `dataset/`.
- Analysis dependencies from `requirements.txt`.
- For the notebook interface, `requirements-notebook.txt`, which includes the analysis dependencies and adds JupyterLab and ipykernel.

### Run the Jupyter Notebook — Recommended

Download or clone the repository, open a terminal in its root directory and create a virtual environment:

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

**macOS / Linux:**

```bash
.venv/bin/python -m pip install -r requirements-notebook.txt
.venv/bin/python -m jupyterlab
```

On macOS/Linux, use `python3 -m venv .venv` if the `python` command is unavailable.

Open **[analysis.ipynb](analysis.ipynb)**, select the Python environment containing the dependencies, and **restart the kernel and run all cells in order**. Keep the notebook beside `dataset/`. If Jupyter starts outside the project, set `ROOT` in the notebook's paths cell to the project directory.

The notebook is self-contained and does not require `analysis.py`. Its 17 code cells were executed successfully with a fresh Jupyter kernel. The CSVs and findings matched the original script, and three charts are embedded in the saved notebook.

### Optional Python Script

If `analysis.py` is included, it offers the same analysis from the command line:

```powershell
# Windows, from the repository root
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe analysis.py
```

```bash
# macOS / Linux, from the repository root
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analysis.py
```

Installing dependencies requires internet access unless they are cached. The analysis itself makes no network requests and requires no credentials.

## Repository Structure

```text
data-science-project/
├── README.md
├── analysis.ipynb
├── analysis.py                  # Optional command-line version
├── requirements.txt
├── requirements-notebook.txt
├── dataset/                    # Seven source Excel files
└── results/
    ├── figures/                # Three PNG visualizations
    ├── tables/                 # Cleaned and summary CSVs
    ├── analysis_summary.md
    ├── findings.json
    ├── validation.json
    └── input_audit.json
```

Both versions regenerate `results/`. Expected headline results are **135,192 total allegations**, **55,579 sex-based allegations** and a **41.1% sex-based share**. The cleaned student table contains 936 rows and the allegations table contains 52 rows, including the separate national rows.

See [the analysis report](results/analysis_summary.md), [validation results](results/validation.json) and [input audit](results/input_audit.json) for the findings, checks, workbook hashes and software versions.

## Future Improvements

Investigate reporting completeness, add compatible enrollment denominators and compare additional school years using consistent definitions. Peer feedback can help improve chart explanations and accessibility.

## Related Portfolio

[Portfolio source repository](https://github.com/mc65222/data-science-portfolio)

## AI Assistance

OpenAI Codex assisted with code, notebook conversion, documentation and visual presentation. The notebook records reproducible calculations and outputs; the student is responsible for reviewing and understanding the work and providing the required course AI declaration.
