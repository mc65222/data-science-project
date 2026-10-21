"""Reproducible descriptive analysis of the supplied 2015-16 CRDC workbooks.

Run: python analysis.py
All paths default to this script's directory, independent of the working directory.
Original Excel workbooks are opened read-only and never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save figures without requiring a desktop display.
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import openpyxl
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://catalog.data.gov/dataset/2015-16-harassment-or-bullying-by-basis-category-civil-rights-data-collection"
BASES = ("sex", "race", "disability")
BASIS_LABELS = {
    "sex": "Sex",
    "race": "Race, color, or national origin",
    "disability": "Disability",
    "sexual_orientation": "Sexual orientation",
    "religion": "Religion",
}
REGIONS = set("Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|District of Columbia|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming".split("|"))


def require(condition: bool, message: str) -> None:
    """Do not continue with misleading results if an input assumption fails."""
    if not condition:
        raise ValueError(message)


def count(value: object, context: str) -> int:
    """Require a nonnegative integer; blanks/suppression codes are not zero."""
    try:
        numeric = float(str(value).replace(",", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing or nonnumeric count at {context}: {value!r}") from exc
    require(np.isfinite(numeric) and numeric >= 0 and numeric.is_integer(),
            f"Invalid count at {context}: {value!r}")
    return int(numeric)


def coverage(value: object, context: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing reporting coverage at {context}") from exc
    require(np.isfinite(result) and 0 <= result <= 100,
            f"Coverage must be between 0 and 100 at {context}")
    return result


def read_inputs(dataset_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Flatten relevant columns from 19 sheets into two tidy data tables."""
    student_records, allegation_records, audit = [], [], []
    specifications = [("Allegations-of-Harassment-or-Bullying.xlsx", None, "allegations")]
    specifications += [
        (f"Harassment-Bullying-on-basis-of-{basis}-{measure}.xlsx", basis, measure)
        for basis in BASES for measure in ("reported", "disciplined")
    ]
    for filename, basis, measure in specifications:
        path = dataset_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required workbook is missing: {path}")
        with warnings.catch_warnings():
            # Excel metadata extensions are irrelevant when reading cell values.
            warnings.filterwarnings("ignore", message="Unknown extension is not supported")
            workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
            try:
                sheets = ("Total",) if basis is None else ("Total", "Male", "Female")
                require(set(sheets).issubset(workbook.sheetnames), f"Unexpected sheets in {filename}")
                for sheet_name in sheets:
                    rows = list(workbook[sheet_name].values)
                    title = str(rows[1][1])
                    require("2015-16" in title and "harass" in title.lower() and "bull" in title.lower(),
                            f"Unexpected table title: {filename}/{sheet_name}")
                    if basis is not None:
                        require(f"basis of {basis}" in title.lower(), f"Basis mismatch in {filename}")
                        title_word = "disciplined" if measure == "disciplined" else "reported"
                        require(title_word in title.lower(), f"Measure mismatch in {filename}")
                    require(str(rows[3][1]).strip() == "State", f"State header missing in {filename}")
                    expected_header = "Total number of allegations" if basis is None else "Total Students"
                    require(str(rows[3][2]).strip() == expected_header, f"Count header changed in {filename}")
                    # Select by the explicit geography column. This excludes titles,
                    # footnotes and stray numeric scratch cells after the data block.
                    data_rows = [(i, row) for i, row in enumerate(rows, 1)
                                 if len(row) > 1 and row[1] in REGIONS | {"United States"}]
                    names = [row[1] for _, row in data_rows]
                    require(len(names) == 52 and set(names) == REGIONS | {"United States"},
                            f"Expected 50 states, DC and US exactly once: {filename}/{sheet_name}")
                    coverage_index = 9 if basis is None else 24
                    school_index = 8 if basis is None else 23
                    for row_number, row in data_rows:
                        context = f"{filename}/{sheet_name}/row {row_number}"
                        common = {
                            "school_year": "2015-16", "state": row[1],
                            "is_national": row[1] == "United States",
                            "number_of_schools": count(row[school_index], context),
                            "reporting_coverage_pct": coverage(row[coverage_index], context),
                            "source_file": filename, "source_sheet": sheet_name,
                            "source_row": row_number,
                        }
                        common["coverage_below_85_pct"] = common["reporting_coverage_pct"] < 85
                        if basis is None:
                            record = {**common, "total_allegations": count(row[2], context)}
                            for col, category in enumerate(("sex", "race", "disability", "sexual_orientation", "religion"), 3):
                                record[category] = count(row[col], context)
                            require(sum(record[k] for k in BASIS_LABELS) == record["total_allegations"],
                                    f"Allegation categories do not reconcile: {context}")
                            allegation_records.append(record)
                        else:
                            student_records.append({**common, "basis": basis, "measure": measure,
                                                    "sex": sheet_name, "student_count": count(row[2], context)})
                    audit.append({"file": filename, "sheet": sheet_name, "title": title,
                                  "geography_rows": len(data_rows),
                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            finally:
                workbook.close()
    return pd.DataFrame(student_records), pd.DataFrame(allegation_records), audit


def validate(students: pd.DataFrame, allegations: pd.DataFrame) -> dict:
    """Reconcile national totals and sex subtotals without double counting."""
    for keys, group in students.groupby(["basis", "measure", "sex"]):
        national = int(group.loc[group.is_national, "student_count"].iloc[0])
        require(national == int(group.loc[~group.is_national, "student_count"].sum()),
                f"National/state reconciliation failed: {keys}")
    for (basis, measure, state), group in students.groupby(["basis", "measure", "state"]):
        by_sex = group.set_index("sex").student_count
        require(int(by_sex["Total"]) == int(by_sex["Male"] + by_sex["Female"]),
                f"Male + Female does not equal Total: {basis}/{measure}/{state}")
    for column in ["total_allegations", *BASIS_LABELS]:
        require(int(allegations.loc[allegations.is_national, column].iloc[0]) ==
                int(allegations.loc[~allegations.is_national, column].sum()),
                f"Allegation national/state reconciliation failed: {column}")
    return {
        "status": "passed", "workbooks": 7, "sheets": 19,
        "student_table_rows": len(students), "allegation_table_rows": len(allegations),
        "checks": ["52 unique geographies per sheet", "nonnegative integer counts",
                   "coverage within 0-100", "national equals sum of 50 states and DC",
                   "Male + Female equals Total", "allegation categories sum to total"],
    }


def style() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.titlepad": 20,
                         "figure.facecolor": "#f8fafc", "axes.facecolor": "#f8fafc",
                         "text.color": "#172b42", "axes.labelcolor": "#172b42",
                         "savefig.facecolor": "#f8fafc"})


def save_figure(fig: plt.Figure, path: Path, footnote: str) -> None:
    fig.text(0.03, 0.025, footnote, fontsize=9, color="#46566b")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight", metadata={"Software": "CISC7204 CRDC analysis"})
    plt.close(fig)


def generate_outputs(students: pd.DataFrame, allegations: pd.DataFrame, audit: list[dict],
                     validation: dict, output: Path) -> None:
    figures, tables = output / "figures", output / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    students.to_csv(tables / "students_clean.csv", index=False)
    allegations.to_csv(tables / "allegations_clean.csv", index=False)

    us = allegations.loc[allegations.is_national].iloc[0]
    categories = pd.DataFrame([{"basis": k, "label": v, "allegations": int(us[k]),
                                "share_pct": float(us[k] / us.total_allegations * 100)}
                               for k, v in BASIS_LABELS.items()]).sort_values("allegations", ascending=False)
    categories.to_csv(tables / "national_allegations.csv", index=False)
    national = students.loc[students.is_national].copy()
    totals = national.loc[national.sex == "Total"].pivot(index="basis", columns="measure", values="student_count").reindex(BASES)
    totals.to_csv(tables / "national_student_counts.csv")
    sex_counts = national.loc[(national.measure == "reported") & (national.sex != "Total")].pivot(index="basis", columns="sex", values="student_count").reindex(BASES)
    sex_shares = sex_counts.div(sex_counts.sum(axis=1), axis=0) * 100
    sex_shares.to_csv(tables / "reported_sex_shares_pct.csv", float_format="%.6f")
    students.loc[(~students.is_national) & (students.sex == "Total") & students.coverage_below_85_pct,
                 ["state", "basis", "measure", "reporting_coverage_pct"]].to_csv(tables / "low_coverage_student_tables.csv", index=False)

    style()
    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars = ax.barh(categories.label, categories.allegations, color=["#126d82", "#257f91", "#438fa0", "#65a4af", "#8bbdc3"])
    ax.invert_yaxis()
    ax.bar_label(bars, labels=[f"{r.allegations:,}  ({r.share_pct:.1f}%)" for r in categories.itertuples()], padding=7, fontsize=10)
    ax.set_xlim(0, categories.allegations.max() * 1.35)
    ax.set_xlabel("Number of allegations reported to responsible school employees")
    ax.set_title("Sex-based allegations were the largest category\nUnited States public schools | 2015-16")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.15)
    save_figure(fig, figures / "01_allegations_by_basis.png",
                "Source: U.S. Department of Education, OCR, CRDC 2015-16.\nCounts are allegations, not unique students; shares use 135,192 total allegations.")

    fig, ax = plt.subplots(figsize=(11, 7))
    x = np.arange(len(BASES))
    first = ax.bar(x - .2, totals.reported, .38, color="#126d82", label="Reported as harassed or bullied")
    second = ax.bar(x + .2, totals.disciplined, .38, color="#d48242", label="Disciplined for harassment or bullying")
    for bars in (first, second):
        ax.bar_label(bars, labels=[f"{v.get_height():,.0f}" for v in bars], padding=4, fontsize=10)
    ax.set_xticks(x, ["Sex", "Race, color, or\nnational origin", "Disability"])
    ax.set_ylim(0, totals.to_numpy().max() * 1.3)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}"))
    ax.set_ylabel("Number of students within each separate measure")
    ax.set_title("Reported and disciplined counts describe different groups\nUnited States public schools | 2015-16")
    ax.legend(frameon=False, fontsize=10)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.15)
    save_figure(fig, figures / "02_reported_and_disciplined.png",
                "Source: U.S. Department of Education, OCR, CRDC 2015-16.\nThese are unlinked student counts, not a discipline rate; do not sum across bases.")

    fig, ax = plt.subplots(figsize=(11, 6))
    male = sex_shares.Male.to_numpy()
    female = sex_shares.Female.to_numpy()
    positions = np.arange(3)
    ax.barh(positions, male, color="#126d82", label="Male (source category)")
    ax.barh(positions, female, left=male, color="#d48242", label="Female (source category)")
    for i, basis in enumerate(BASES):
        ax.text(male[i]/2, i, f"{male[i]:.1f}%\n(n={int(sex_counts.loc[basis, 'Male']):,})", ha="center", va="center", color="white", weight="bold")
        ax.text(male[i]+female[i]/2, i, f"{female[i]:.1f}%\n(n={int(sex_counts.loc[basis, 'Female']):,})", ha="center", va="center", color="#172b42", weight="bold")
    ax.set_yticks(positions, ["Sex", "Race, color, or\nnational origin", "Disability"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of reported students within each basis (%)")
    ax.set_title("Sex composition differs across reported bullying categories\nUnited States public schools | 2015-16")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.16), ncol=2, frameon=False)
    save_figure(fig, figures / "03_reported_students_by_sex.png",
                "Source: U.S. Department of Education, OCR, CRDC 2015-16.\nDenominator: Male + Female within each basis; these shares are not population risk rates.")

    findings = {
        "school_year": "2015-16", "total_allegations": int(us.total_allegations),
        "sex_based_allegations": int(us.sex), "sex_based_allegations_share_pct": float(us.sex / us.total_allegations * 100),
        "female_share_of_sex_based_reported_students_pct": float(sex_shares.loc["sex", "Female"]),
        "national_student_counts": {basis: {key: int(totals.loc[basis, key]) for key in ("reported", "disciplined")} for basis in BASES},
        "national_allegations_school_reporting_coverage_pct": float(us.reporting_coverage_pct),
        "source_url": SOURCE_URL,
    }
    (output / "findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    (output / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    audit_document = {"python": platform.python_version(),
                      "packages": {name: importlib.metadata.version(name) for name in ("numpy", "pandas", "matplotlib", "openpyxl")},
                      "tables": audit}
    (output / "input_audit.json").write_text(json.dumps(audit_document, indent=2), encoding="utf-8")
    summary = f"""# Analysis results: harassment and bullying, 2015-16

Research question: How did reported harassment and bullying vary by basis, and how did the sex composition of reported students differ?

## Findings

- The national table contains **{int(us.total_allegations):,} allegations**. Sex-based allegations account for **{int(us.sex):,} ({us.sex / us.total_allegations * 100:.1f}%)**, the largest category.
- Reported student counts are **{int(totals.loc['sex', 'reported']):,}** for sex-based, **{int(totals.loc['race', 'reported']):,}** for race/color/national-origin-based, and **{int(totals.loc['disability', 'reported']):,}** for disability-based bullying. Categories must not be added to estimate unique students.
- Female students make up **{sex_shares.loc['sex', 'Female']:.1f}%** of sex-based reported students. Male students make up **{sex_shares.loc['race', 'Male']:.1f}%** of race-based and **{sex_shares.loc['disability', 'Male']:.1f}%** of disability-based reported students. These are within-category shares, not risk estimates.

## Visual evidence

![Allegations by basis](figures/01_allegations_by_basis.png)

![Separate reported and disciplined student counts](figures/02_reported_and_disciplined.png)

![Sex composition of reported students](figures/03_reported_students_by_sex.png)

## Interpretation and limitations

This is descriptive analysis of historical administrative reports. Reporting practices, coverage, school size and underreporting can affect counts. Enrollment denominators are not included, so this analysis cannot measure prevalence, compare population risks or infer causation. Reported victims and disciplined students are different, unlinked groups; their ratio is not a case-resolution rate. People may occur in more than one basis category. Sex categories reproduce the source's Male and Female sheets and do not represent all gender identities.

The national allegations table reports {us.reporting_coverage_pct:.1f}% of schools reporting. District of Columbia coverage is below 85% in that table and is flagged in the cleaned data. National source totals are retained rather than replacing missing reports with zero.

## Reproducibility

Validation passed for all 19 sheets: 50 states, DC and a separate national row; nonnegative integer counts; national/state reconciliation; Male + Female = Total; and allegation-category reconciliation. See `validation.json`, `input_audit.json` and `tables/` for evidence. Checks validate internal consistency, not the accuracy of the original school reports.

Data source: [U.S. Department of Education, Office for Civil Rights, CRDC 2015-16]({SOURCE_URL}). Figures and tables were derived from the seven supplied Excel files without modifying them.
"""
    (output / "analysis_summary.md").write_text(summary, encoding="utf-8")
    print(summary.split("## Visual evidence")[0])
    print(f"Validation passed. Figures, tables and reports saved to: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "dataset")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    students, allegations, audit = read_inputs(args.data_dir.resolve())
    validation = validate(students, allegations)
    generate_outputs(students, allegations, audit, validation, args.output_dir.resolve())


if __name__ == "__main__":
    main()
