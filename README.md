# ⚡ Kaggle Benchmarking Challenge: ETL-to-Python Code Synthesis

[![Kaggle Challenge](https://img.shields.io/badge/DEV.to-Kaggle%20Challenge-blue?logo=dev.to)](https://dev.to/challenges/kaggle-2026-09-23)
[![Kaggle Benchmarks](https://img.shields.io/badge/Kaggle-Benchmarks-20BEFF?logo=kaggle)](https://www.kaggle.com/benchmarks)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Official Submission for the [Kaggle Benchmarking Challenge](https://dev.to/challenges/kaggle-2026-09-23) on DEV Community.**  
> *Tag:* `#kagglechallenge` | *Author:* [@angelo_junmatsui_a565bbd](https://dev.to/angelo_junmatsui_a565bbd)

---

## 🎯 1. Overview & Motivation

Enterprise data engineering teams frequently grapple with migrating legacy, visual workflows (**Knime**, **Alteryx**, **SSIS**) or complex business pseudocode into high-performance, idiomatic Python (`pandas` / `polars`).

While general LLM benchmarks evaluate synthetic puzzles or basic algorithmic routines, real-world data pipelines break due to subtle edge cases:
- Handling relational keys with unmapped null values and strict type coercions.
- Parsing semi-structured log streams with missing delimiters without throwing unhandled exceptions.
- Replacing memory-intensive iterative loops with native vectorized window transformations.
- Reshaping multi-quarter matrices and flattening composite MultiIndex column hierarchies.

This project delivers an automated, reproducible benchmark suite designed for the **Kaggle Benchmarks platform** (`@kbench.task()`), putting generated code through rigorous, sandboxed assertions with sub-millisecond execution verification.

---

## 🔬 2. Benchmark Task Suite

The benchmark contains 4 structured, realistic data pipeline challenges:

| Task ID | Name | Core Knime Nodes Simulated | Key Evaluation Criteria |
| :--- | :--- | :--- | :--- |
| **`etl_01`** | **Joiner & Imputation** | `Joiner`, `Missing Value`, `Rule Engine` | Left Join n-to-1, missing customer imputation, negative number sanitization, and boolean flag logic (`is_vip`). |
| **`etl_02`** | **Regex Log Sanitizer** | `Regex Extractor`, `Row Filter` | Key-value regex parsing, safe default fallback for corrupted non-delimited lines, and bot-exclusion filtering. |
| **`etl_03`** | **Vectorized Window Calc** | `GroupLoop`, `Moving Aggregation` | Cumulative revenue (`.cumsum()`), target achievement %, 3-month rolling averages, and intra-department dense ranking without iterative `for` loops. |
| **`etl_04`** | **Matrix Reshaping** | `Unpivoting`, `Pivoting`, `Column Rename` | Melting multi-quarter wide columns, parsing temporal labels, pivoting, and flattening MultiIndex headers to single-level snake_case schemas. |

---

## 📊 3. Official Benchmark Results & Leaderboard

Tested under zero-shot deterministic parameters (`temperature = 0.0`):

| Model | Accuracy (Passed / Total) | Avg Score | Avg API Latency | Sandbox Assertion Latency |
| :--- | :---: | :---: | :---: | :---: |
| 🥇 **`gemini-3.8-flash`** | **100.0% (4/4)** | **1.00** | **14.89 s** | **~13.4 ms** |
| 🥈 **`gemini-2.5-pro`** | **100.0% (4/4)** | **1.00** | **33.78 s** | **~16.0 ms** |

### 🔍 Key Engineering Insights
1. **The Corrupted Row Trap (`etl_02`):** `gemini-3.8-flash` successfully parsed corrupted input strings using fallback extraction without losing data rows. Conversely, `gemini-2.5-pro` aggressively dropped unparsed rows during post-processing, failing data-preservation assertions.
2. **True Vectorization vs Iterative Loops (`etl_03`):** Both frontier models avoided slow `df.iterrows()` antipatterns and synthesized idiomatic, vectorized group operations.
3. **Throughput Advantage:** `gemini-3.8-flash` executed **2.45x faster** than `gemini-2.5-pro` while maintaining 100% accuracy across all test fixtures.

---

## 🏗️ 4. Architecture & Repository Structure

```
├── .env.example                  # Template for API credentials
├── requirements.txt              # Project dependencies
├── README.md                     # Main documentation & challenge overview
├── docs/
│   └── dev_article_draft.md      # Publication-ready DEV.to submission draft
├── src/
│   ├── config.py                 # Environment and path configurations
│   ├── tasks/
│   │   ├── task_specs.py         # Benchmark task definitions, prompts & fixtures
│   │   └── validators.py         # Sandboxed evaluation runner & DataFrame assertions
│   ├── runners/
│   │   └── gemini_runner.py      # Automated benchmark harness via Google GenAI SDK
│   ├── utils/
│   │   └── publish_dev.py        # Automated publishing to DEV.to via REST API
│   └── analysis/
│       └── metrics.py            # Results aggregator & Markdown report generator
├── kaggle/
│   └── benchmark_task_notebook.py# Official task evaluation script for Kaggle Benchmarks (@kbench.task)
└── results/                      # Raw JSON telemetry and benchmark logs
```

---

## 🚀 5. Getting Started (Quickstart)

### Prerequisites
- Python 3.10+
- A Google Gemini API key or Kaggle account

### 1. Clone & Setup Environment
```bash
git clone https://github.com/jun-matsui/kaggle-etl-benchmark.git
cd kaggle-etl-benchmark

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your-gemini-api-key"
DEVCommunity_user="@your_handle"
DEVCommunity_API_Keys="your-dev-api-key"
GITHUB_KEY="your-github-token"
```

### 3. Run Benchmark Suite
```bash
# Execute evaluation across all tasks
python -m src.runners.gemini_runner

# Generate latest summary reports
python -m src.analysis.metrics
```

---

## 🌐 6. Kaggle Benchmarks Integration

To reproduce or run this evaluation on **Kaggle**:
1. Open [Kaggle Benchmarks](https://www.kaggle.com/benchmarks).
2. Click **"+ Create"** to create a new task notebook.
3. Copy and paste the task logic from [`kaggle/benchmark_task_notebook.py`](file:///g:/PastaRede/Projetos/Dev.to/challenges/Kaggle%20Benchmarking%20Challenge/kaggle/benchmark_task_notebook.py).
4. Run the notebook to register the task and publish it to the community leaderboard.

---

## 📜 7. License

Distributed under the MIT License. See `LICENSE` for more information.
