# csi-data-pipeline-assessment
Data Analytics Engineering Intern Assessment
# Data Engineering Assessment: Enterprise Market Research Pipeline

Welcome to the Viva Data Engineering Intern Assessment! 

Thank you for taking the time to demonstrate your skills. This assessment is designed to reflect the exact types of data challenges our Market Research and Statistics unit handles every day.

## 📊 Context
You have been provided with a synthetic, enterprise-scale dataset (`data/raw_csi_database.xlsx`). This file mimics a raw export from a survey platform for a Customer Satisfaction Index (CSI) tracking study of telecommunication service centers. 

Because of how survey platforms handle complex routing and multi-response questions, the dataset is extremely wide (nearly 300 columns) and contains a mix of system metadata, nested logic, and messy strings.

## 🎯 The Objective
Your goal is to build a robust Python/Pandas data pipeline that dynamically cleans, normalizes, and reshapes this wide survey export into a clean, relational database structure suitable for BI reporting.

**⚠️ CRITICAL RULE:** You are dealing with hundreds of columns that may change order or slightly alter their names next quarter. **Hardcoding column names, manual list slicing (e.g., `df.iloc[:, 15:30]`), or repeating the same block of code multiple times will result in a failed assessment.** Your code must be dynamic and modular.

## 🛠️ Required Pipeline Steps

Please complete your work in `src/pipeline_template.py` (or a Jupyter Notebook if you prefer) and ensure it executes the following steps:

### 1. System Noise Cleanup
The raw export contains system-generated metadata columns (e.g., columns starting with an underscore `_` like `_status`, `_submitted_by`, or specific system tags like `Label`).
* **Task:** Programmatically identify and drop all system metadata columns. 

### 2. Text Normalization
Certain behavioral columns contain messy survey routing logic embedded within the answers. 
* **Task:** Clean column `A8. Հաճախ եք այցելում այս սպասարկման կենտրոն:` so that it only contains the core categorical answer (e.g., `1 Այո` or `2 Ոչ`), stripping out the parentheses and routing text (e.g., `(Անցնել հարց 9.2-ին)`).

### 3. Modular Wide-to-Long Transformation (Unpivoting)
This is the core of the assessment. You will notice multiple distinct "question blocks" that span dozens of columns. For example:
* The **`S3`** block (Visit Purposes).
* The **`4.5_`** block (Nested Complaint Details).

* **Task:** Write a single, generalized Python function (e.g., `unpivot_survey_block(df, prefix)`) capable of taking a column prefix string, isolating those specific columns, melting them from wide to long format, and dropping unselected responses (where the value is `0` or `NaN`). 
* *Bonus:* Have your function clean the resulting header strings so the final `Value` column contains only the specific answer text, not the entire "4.5_1 Միանալ/..." path.

### 4. Data Modeling & Export
* **Task:** Use your reusable function to generate two separate, clean, long-format DataFrames:
    1.  `clean_visit_purposes.csv` (Derived from the `S3` block)
    2.  `clean_complaint_details.csv` (Derived from the `4.5_` block)
* Ensure both tables retain core respondent identifiers (e.g., `ID`, `S1` Operator, `10.5` Age Group) so they can be joined later. Output them to the `output/` directory.

## 🏆 Evaluation Criteria
We will be reviewing your submission based on:
1. **Dynamic Logic:** Use of regular expressions (`re`), Pandas string methods, or `filter()` to handle columns dynamically.
2. **Modularity (DRY Principle):** Building reusable functions rather than copying and pasting `.melt()` logic.
3. **Code Quality:** Readability, clear variable naming, and appropriate comments/docstrings.
4. **Data Tidy-ness:** Proper handling of `NaN` values and clean final relational mapping.

## 🚀 Submission Instructions
1. **Fork** this repository to your personal GitHub account.
2. Complete your code in the `src/` folder.
3. Commit your code and the generated CSV files in the `output/` folder.
4. Reply to our email with the link to your forked repository. Include a brief note explaining how long the task took and any specific design choices you made.

Good luck! We look forward to seeing your approach to the problem.
