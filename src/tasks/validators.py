"""
Sandboxed validation engine for executing and verifying Python code synthesized by LLMs.
"""

import re
import traceback
import time
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

def extract_python_code(raw_response: str) -> str:
    """Extracts python code blocks from markdown."""
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    matches = re.findall(pattern, raw_response, re.DOTALL)
    if matches:
        return matches[0].strip()
    return raw_response.strip()

def validate_task_01(func) -> Tuple[bool, str]:
    """Validates ETL Task 01: Left Join + Missing Value Imputation + VIP Logic."""
    df_sales = pd.DataFrame([
        {"transaction_id": 1, "customer_id": "C101", "amount": 150.50, "date": "2026-01-01"},
        {"transaction_id": 2, "customer_id": "C102", "amount": -20.0, "date": "2026-01-02"},
        {"transaction_id": 3, "customer_id": "C999", "amount": 250.0, "date": "2026-01-03"},
        {"transaction_id": 4, "customer_id": "C101", "amount": 80.0, "date": "2026-01-04"}
    ])
    df_customers = pd.DataFrame([
        {"customer_id": "C101", "customer_name": "Alice", "tier": "Gold", "signup_date": "2025-01-01"},
        {"customer_id": "C102", "customer_name": "Bob", "tier": None, "signup_date": "2025-05-10"}
    ])

    res = func(df_sales.copy(), df_customers.copy())
    
    if not isinstance(res, pd.DataFrame):
        return False, "Return value is not a pandas DataFrame."
    
    # 1. Total rows must be 4 (Left Join)
    if len(res) != 4:
        return False, f"Expected 4 rows in Left Join, got {len(res)}"
    
    # 2. Missing customer name imputation
    c999_row = res[res['customer_id'] == 'C999']
    if c999_row.empty or c999_row['customer_name'].values[0] != "Unknown Customer":
        return False, f"Imputation failed for unmapped customer C999: {c999_row['customer_name'].values if not c999_row.empty else 'N/A'}"
    
    # 3. Missing tier imputation
    c102_row = res[res['customer_id'] == 'C102']
    if c102_row.empty or c102_row['tier'].values[0] != "Standard":
        return False, f"Default tier imputation failed for C102: {c102_row['tier'].values if not c102_row.empty else 'N/A'}"
    
    # 4. Negative / invalid amounts coerced to 0.0
    if c102_row['amount'].values[0] != 0.0:
        return False, f"Negative value handling failed: {c102_row['amount'].values[0]}"
        
    # 5. VIP logic: Alice with 150.50 and Gold is True; Alice with 80.0 is False.
    row1 = res[res['transaction_id'] == 1]
    row4 = res[res['transaction_id'] == 4]
    if not bool(row1['is_vip'].values[0]):
        return False, "is_vip boolean logic failed for transaction 1 (expected True)"
    if bool(row4['is_vip'].values[0]):
        return False, "is_vip boolean logic failed for transaction 4 (expected False)"
        
    return True, "All ETL 01 tests passed successfully!"

def validate_task_02(func) -> Tuple[bool, str]:
    """Validates ETL Task 02: Regex Key-Value Extraction + Sanitization + Filtering."""
    df_raw = pd.DataFrame([
        {"log_entry": "USER:alice|ROLE:admin|IP:10.0.0.1|STATUS:200|DURATION:45ms"},
        {"log_entry": "USER:|ROLE:guest|IP:192.168.0.5|STATUS:404|DURATION:12ms"},
        {"log_entry": "USER:spambot|ROLE:bot|IP:1.2.3.4|STATUS:200|DURATION:5ms"},
        {"log_entry": "CORRUPTED_LINE_WITHOUT_DELIMITERS"}
    ])
    
    res = func(df_raw.copy())
    if not isinstance(res, pd.DataFrame):
        return False, "Return value is not a pandas DataFrame."
    
    # Spambot must be filtered (role: bot), corrupted line preserved with defaults -> 3 rows expected
    if len(res) != 3:
        return False, f"Expected 3 rows after filtering 'bot' (preserving corrupted row), got {len(res)}"
        
    # Check fallback for anonymous user
    guest_row = res[res['role'] == 'guest']
    if guest_row.empty or guest_row['username'].values[0] != "anonymous":
        return False, "Fallback to 'anonymous' username failed."
        
    # Check integer typing for duration and status
    if not np.issubdtype(res['status_code'].dtype, np.integer):
        return False, f"Column status_code must have integer dtype, got {res['status_code'].dtype}"
        
    if not np.issubdtype(res['duration_ms'].dtype, np.integer):
        return False, f"Column duration_ms must have integer dtype, got {res['duration_ms'].dtype}"
        
    return True, "All ETL 02 tests passed successfully!"

def validate_task_03(func) -> Tuple[bool, str]:
    """Validates ETL Task 03: Vectorized Cumulative Windows & Department Ranks."""
    df_metrics = pd.DataFrame([
        {"department": "Sales", "employee_id": "E01", "month": "2026-01", "revenue": 1000.0, "target": 800.0},
        {"department": "Sales", "employee_id": "E01", "month": "2026-02", "revenue": 1200.0, "target": 1000.0},
        {"department": "Sales", "employee_id": "E02", "month": "2026-01", "revenue": 1500.0, "target": 1200.0},
        {"department": "Sales", "employee_id": "E02", "month": "2026-02", "revenue": 900.0, "target": 1000.0}
    ])
    
    res = func(df_metrics.copy())
    if not isinstance(res, pd.DataFrame):
        return False, "Return value is not a pandas DataFrame."
        
    e01_m2 = res[(res['employee_id'] == 'E01') & (res['month'] == '2026-02')]
    if e01_m2.empty:
        return False, "Row E01 for month 2026-02 missing in result."
        
    # Cumulative revenue for E01 in Feb must be 2200.0
    cum_rev = e01_m2['cumulative_revenue'].values[0]
    if not np.isclose(cum_rev, 2200.0):
        return False, f"Expected cumulative revenue 2200.0, got {cum_rev}"
        
    # Target achievement percentage for E01 in Feb: 120.0
    achieve = e01_m2['target_achievement_pct'].values[0]
    if not np.isclose(achieve, 120.0, atol=0.1):
        return False, f"Expected target achievement 120.0%, got {achieve}"
        
    return True, "All ETL 03 tests passed successfully!"

def validate_task_04(func) -> Tuple[bool, str]:
    """Validates ETL Task 04: Unpivot, Pivot & Single-Level Column Flattening."""
    df_wide = pd.DataFrame([
        {"region": "North", "store_id": "S1", "2025_Q1": 100.0, "2025_Q2": 150.0, "2026_Q1": 120.0, "2026_Q2": 180.0},
        {"region": "South", "store_id": "S2", "2025_Q1": 200.0, "2025_Q2": 210.0, "2026_Q1": 250.0, "2026_Q2": 300.0}
    ])
    
    res = func(df_wide.copy())
    if not isinstance(res, pd.DataFrame):
        return False, "Return value is not a pandas DataFrame."
        
    if isinstance(res.columns, pd.MultiIndex):
        return False, "Columns still contain MultiIndex rather than single-level headers."
        
    expected_cols = ["region", "store_id", "quarter", "val_2025", "val_2026"]
    if list(res.columns) != expected_cols:
        return False, f"Expected columns {expected_cols}, got {list(res.columns)}"
        
    if len(res) != 4:
        return False, f"Expected 4 rows in total reshaped output, got {len(res)}"
        
    s1_q1 = res[(res['store_id'] == 'S1') & (res['quarter'] == 'Q1')]
    if s1_q1.empty:
        return False, "Row S1 Q1 missing in reshaped output."
        
    if not np.isclose(s1_q1['val_2025'].values[0], 100.0) or not np.isclose(s1_q1['val_2026'].values[0], 120.0):
        return False, f"Incorrect values in S1 Q1: 2025={s1_q1['val_2025'].values[0]}, 2026={s1_q1['val_2026'].values[0]}"
        
    return True, "All ETL 04 tests passed successfully!"

VALIDATOR_REGISTRY = {
    "check_etl_01": validate_task_01,
    "check_etl_02": validate_task_02,
    "check_etl_03": validate_task_03,
    "check_etl_04": validate_task_04,
}

def execute_and_evaluate(task: Dict[str, Any], raw_llm_response: str) -> Dict[str, Any]:
    """
    Executes model-generated code in an isolated scope and evaluates correctness.
    """
    clean_code = extract_python_code(raw_llm_response)
    start_time = time.time()
    
    local_scope = {"pd": pd, "np": np, "re": re}
    try:
        exec(clean_code, local_scope, local_scope)
        
        if "transform_etl" not in local_scope or not callable(local_scope["transform_etl"]):
            return {
                "task_id": task["id"],
                "passed": False,
                "score": 0.0,
                "error": "Function `transform_etl` was not found or is not callable.",
                "duration_ms": round((time.time() - start_time) * 1000, 2),
                "extracted_code": clean_code
            }
            
        validator_fn = VALIDATOR_REGISTRY.get(task["verification_rule"])
        if not validator_fn:
            return {
                "task_id": task["id"],
                "passed": False,
                "score": 0.0,
                "error": f"Validator {task['verification_rule']} not found in registry.",
                "duration_ms": round((time.time() - start_time) * 1000, 2),
                "extracted_code": clean_code
            }
            
        passed, msg = validator_fn(local_scope["transform_etl"])
        return {
            "task_id": task["id"],
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "message": msg,
            "error": None if passed else msg,
            "duration_ms": round((time.time() - start_time) * 1000, 2),
            "extracted_code": clean_code
        }
        
    except Exception as e:
        return {
            "task_id": task["id"],
            "passed": False,
            "score": 0.0,
            "error": f"Execution Error ({type(e).__name__}): {str(e)}\n{traceback.format_exc()}",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
            "extracted_code": clean_code
        }
