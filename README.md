# Precision Data Analysis (Minitab-style Statistical Tool)

Python-based statistical analysis tool designed to evaluate **measurement precision and variation** using structured datasets stored in JSON format. The project implements statistical calculations commonly used in quality control and engineering analysis, similar to workflows typically performed in software such as **Minitab**.

The purpose of this program is to process experimental measurement data and calculate key statistical indicators that help determine **data consistency, reliability, and precision**. By analyzing repeated measurements, the system helps identify variability in measurement systems and supports the validation of experimental or production data.

This project was developed as a simplified Python implementation of statistical techniques used in **engineering measurement analysis**, allowing users to load datasets, perform calculations, and observe statistical results without the need for specialized statistical software.

---

# Purpose of the Project

In engineering and manufacturing environments, it is important to evaluate whether measurements taken during experiments or production are **consistent and reliable**. Tools like **Minitab** are commonly used for this purpose because they provide statistical analysis for quality control and measurement validation.

This project replicates part of that workflow using Python by:

* Importing measurement data from structured files
* Performing statistical calculations on repeated measurements
* Evaluating measurement precision and variability
* Producing numerical results useful for analysis and interpretation

The goal is to demonstrate how statistical analysis commonly performed in specialized software can be implemented programmatically using Python.

---

# Key Features

* Reads experimental measurement datasets from **JSON files**
* Performs statistical analysis on repeated measurements
* Evaluates **precision and variation** in datasets
* Provides numerical outputs useful for engineering analysis
* Demonstrates how statistical tools can be implemented in Python

---

# Statistical Concepts Used

The program applies several basic statistical methods commonly used in data analysis and quality control.

## Mean (Average)

The mean represents the average value of a dataset and is used as the central reference point for the measurements.

Used to determine the typical value of repeated measurements.

## Standard Deviation

Standard deviation measures how much the values in a dataset vary from the mean.

A lower standard deviation indicates that the measurements are more consistent.

## Variance

Variance represents the spread of the dataset and is the square of the standard deviation.

It helps quantify the degree of variability present in measurement results.

## Precision Evaluation

Precision refers to how closely repeated measurements agree with each other.
By analyzing variation in repeated measurements, the program helps determine whether a measurement process is stable or inconsistent.

---

# Data Processing Workflow

The program follows a simple workflow to process datasets:

1. **Load dataset**

   * Reads JSON files containing measurement values.

2. **Parse measurement data**

   * Extracts numeric values from the dataset.

3. **Perform statistical calculations**

   * Calculates mean, variance, and standard deviation.

4. **Analyze measurement precision**

   * Evaluates the variability of the dataset.

5. **Display results**

   * Outputs calculated statistics for interpretation.

---

# Technologies Used

* **Python**
* JSON data processing
* Basic statistical functions
* Standard Python libraries for numerical operations

---

# Project Structure

```
precision-data-analysis
│
├── main.py
├── precision_analysis.py
├── datos_act1.json
├── datos_sixs.json
└── README.md
```

### File Description

**main.py**

Main execution file.
Loads datasets and runs the statistical analysis functions.

**precision_analysis.py**

Contains the core statistical functions used to analyze the datasets.

**datos_act1.json**

Dataset containing measurement values used for statistical analysis.

**datos_sixs.json**

Additional dataset used to compare measurement precision.

---

# Example Use Case

This type of analysis can be useful in situations such as:

* Evaluating **measurement reliability** in laboratory experiments
* Checking **consistency of repeated measurements**
* Supporting **quality control processes** in engineering projects
* Learning how statistical analysis can be implemented programmatically

---

# How to Run

Clone the repository:

```
git clone https://github.com/yourusername/precision-data-analysis.git
```

Navigate to the project directory:

```
cd precision-data-analysis
```

Run the program:

```
python main.py
```

---

# Educational Context

This project was developed as an educational exercise to demonstrate how statistical analysis used in engineering and quality control environments can be implemented using Python. The implementation mirrors some of the conceptual analysis workflows that are typically performed in statistical software such as **Minitab**, but in a simplified and programmable form.
