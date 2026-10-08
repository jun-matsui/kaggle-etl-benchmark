"""
Definições de especificações de tarefas para o Benchmark de Síntese de Código ETL.
Avalia a capacidade de LLMs converterem fluxos de nós visuais e regras complexas em código Python eficiente.
"""

from typing import Dict, Any, List

BENCHMARK_TASKS: List[Dict[str, Any]] = [
    {
        "id": "etl_01_complex_join_missing_types",
        "title": "Knime Joiner & Missing Value Imputation with Type Coercion",
        "difficulty": "medium",
        "category": "joins_and_imputation",
        "prompt": """You are an expert Data Engineer translating visual ETL logic (Knime / Alteryx) into pure, idiomatic Python using pandas.

Given two input DataFrames:
`df_sales`: with columns ['transaction_id', 'customer_id', 'amount', 'date']
`df_customers`: with columns ['customer_id', 'customer_name', 'tier', 'signup_date']

Requirements:
1. Implement a function `transform_etl(df_sales: pd.DataFrame, df_customers: pd.DataFrame) -> pd.DataFrame`.
2. Perform a LEFT JOIN of `df_sales` with `df_customers` on `customer_id`.
3. For any missing `customer_name`, impute with "Unknown Customer".
4. For missing `tier`, impute with "Standard".
5. Ensure `amount` is converted to float64, replacing invalid/negative amounts with 0.0.
6. Create a column `is_vip` which is True if `tier` in ['Gold', 'Platinum'] and `amount` > 100.0, else False.
7. Return the resulting DataFrame sorted by `transaction_id` in ascending order.
8. Output ONLY executable Python code inside a single ```python code block. Do NOT include markdown explanations outside the code block.""",
        "sample_input": {
            "df_sales": [
                {"transaction_id": 1, "customer_id": "C101", "amount": 150.50, "date": "2026-01-01"},
                {"transaction_id": 2, "customer_id": "C102", "amount": -20.0, "date": "2026-01-02"},
                {"transaction_id": 3, "customer_id": "C999", "amount": 250.0, "date": "2026-01-03"},
                {"transaction_id": 4, "customer_id": "C101", "amount": 80.0, "date": "2026-01-04"}
            ],
            "df_customers": [
                {"customer_id": "C101", "customer_name": "Alice", "tier": "Gold", "signup_date": "2025-01-01"},
                {"customer_id": "C102", "customer_name": "Bob", "tier": None, "signup_date": "2025-05-10"}
            ]
        },
        "expected_columns": ["transaction_id", "customer_id", "amount", "date", "customer_name", "tier", "signup_date", "is_vip"],
        "expected_rows_count": 4,
        "verification_rule": "check_etl_01"
    },
    {
        "id": "etl_02_regex_nested_string_splitter",
        "title": "Knime Regex Extractor & Multi-Column Sanitizer",
        "difficulty": "hard",
        "category": "string_sanitization_regex",
        "prompt": """You are an expert Data Engineer translating Knime Regex Splitter and Cell Replacer nodes into idiomatic Python pandas code.

Given an input DataFrame `df_raw` with column `log_entry` containing raw log strings like:
`"USER:john_doe|ROLE:admin|IP:192.168.1.1|STATUS:200|DURATION:120ms"`
or edge cases like:
`"USER:|ROLE:guest|IP:unknown|STATUS:500"` (missing fields / malformed)

Requirements:
1. Implement `transform_etl(df_raw: pd.DataFrame) -> pd.DataFrame`.
2. Extract the key-value pairs into explicit columns: `username`, `role`, `ip_address`, `status_code`, `duration_ms`.
3. If `username` is empty or missing, set it to "anonymous".
4. Convert `status_code` to integer; if missing or invalid, default to 0.
5. Extract `duration_ms` as an integer (strip 'ms'); if missing or invalid, default to 0.
6. Filter out rows where `role` is "bot" or `ip_address` is "blacklisted".
7. Return only the new structured columns in the exact order: `['username', 'role', 'ip_address', 'status_code', 'duration_ms']`.
8. Output ONLY executable Python code inside a single ```python code block.""",
        "sample_input": {
            "df_raw": [
                {"log_entry": "USER:alice|ROLE:admin|IP:10.0.0.1|STATUS:200|DURATION:45ms"},
                {"log_entry": "USER:|ROLE:guest|IP:192.168.0.5|STATUS:404|DURATION:12ms"},
                {"log_entry": "USER:spambot|ROLE:bot|IP:1.2.3.4|STATUS:200|DURATION:5ms"},
                {"log_entry": "CORRUPTED_LINE_WITHOUT_DELIMITERS"}
            ]
        },
        "expected_columns": ["username", "role", "ip_address", "status_code", "duration_ms"],
        "expected_rows_count": 3,
        "verification_rule": "check_etl_02"
    },
    {
        "id": "etl_03_group_loop_vectorized_aggregation",
        "title": "Knime GroupLoop & Math Formula to Vectorized Cumulative Windows",
        "difficulty": "hard",
        "category": "window_functions_aggregation",
        "prompt": """You are an expert Data Engineer translating Knime GroupLoop, Moving Aggregation, and Math Formula nodes into fast vectorized Python pandas.

Given an input DataFrame `df_metrics` with columns:
['department', 'employee_id', 'month', 'revenue', 'target']

Requirements:
1. Implement `transform_etl(df_metrics: pd.DataFrame) -> pd.DataFrame`.
2. Sort the data chronologically by `department`, `employee_id`, and `month` (format 'YYYY-MM').
3. For each `employee_id`, compute:
   - `cumulative_revenue`: running total of `revenue` over time.
   - `target_achievement_pct`: (`revenue` / `target`) * 100 rounded to 2 decimal places. If `target` <= 0 or NaN, set to 0.0.
   - `rolling_3m_avg_revenue`: 3-month rolling mean of `revenue` per employee (minimum periods = 1), rounded to 2 decimal places.
4. Calculate department-level rank: `dept_rank_in_month` ranking employees within their department by `revenue` descending for that specific month (method='min').
5. Return the complete DataFrame with the original columns plus the 4 new computed columns.
6. Output ONLY executable Python code inside a single ```python code block.""",
        "sample_input": {
            "df_metrics": [
                {"department": "Sales", "employee_id": "E01", "month": "2026-01", "revenue": 1000.0, "target": 800.0},
                {"department": "Sales", "employee_id": "E01", "month": "2026-02", "revenue": 1200.0, "target": 1000.0},
                {"department": "Sales", "employee_id": "E02", "month": "2026-01", "revenue": 1500.0, "target": 1200.0},
                {"department": "Sales", "employee_id": "E02", "month": "2026-02", "revenue": 900.0, "target": 1000.0}
            ]
        },
        "expected_columns": ['department', 'employee_id', 'month', 'revenue', 'target', 'cumulative_revenue', 'target_achievement_pct', 'rolling_3m_avg_revenue', 'dept_rank_in_month'],
        "expected_rows_count": 4,
        "verification_rule": "check_etl_03"
    },
    {
        "id": "etl_04_unpivot_pivoting_matrix_reshaping",
        "title": "Knime Unpivoting & Pivoting with Multi-Level Column Flattening",
        "difficulty": "hard",
        "category": "matrix_reshaping_pivoting",
        "prompt": """You are an expert Data Engineer translating Knime Unpivoting and Pivoting nodes into clean, idiomatic Python pandas code.

Given an input DataFrame `df_wide` representing multi-year monthly metrics with columns:
`['region', 'store_id', '2025_Q1', '2025_Q2', '2026_Q1', '2026_Q2']`

Requirements:
1. Implement `transform_etl(df_wide: pd.DataFrame) -> pd.DataFrame`.
2. Unpivot (melt) the quarter columns so each row represents a single `(region, store_id, quarter_label, value)` tuple.
3. Parse `quarter_label` (e.g. '2025_Q1') into two distinct columns: `year` (integer, e.g. 2025) and `quarter` (string, e.g. 'Q1').
4. Pivot the data so that `year` becomes columns, indexed by `['region', 'store_id', 'quarter']`, with the values being the sum of `value`.
5. Flatten any MultiIndex in columns and reset the index so all columns are standard 1-level columns with clean names: `['region', 'store_id', 'quarter', 'val_2025', 'val_2026']`.
6. Fill any missing/NaN values with 0.0.
7. Sort rows by `region`, `store_id`, and `quarter` in ascending order.
8. Output ONLY executable Python code inside a single ```python code block.""",
        "sample_input": {
            "df_wide": [
                {"region": "North", "store_id": "S1", "2025_Q1": 100.0, "2025_Q2": 150.0, "2026_Q1": 120.0, "2026_Q2": 180.0},
                {"region": "South", "store_id": "S2", "2025_Q1": 200.0, "2025_Q2": 210.0, "2026_Q1": 250.0, "2026_Q2": 300.0}
            ]
        },
        "expected_columns": ["region", "store_id", "quarter", "val_2025", "val_2026"],
        "expected_rows_count": 4,
        "verification_rule": "check_etl_04"
    }
]

