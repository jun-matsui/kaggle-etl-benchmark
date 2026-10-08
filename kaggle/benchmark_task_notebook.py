"""
Kaggle Benchmarking Challenge - Kaggle Task Definition
Este script pode ser colado diretamente em um Notebook do Kaggle com o SDK kbench.
"""

# No Kaggle Notebook, instale o SDK oficial:
# !pip install -q kaggle-benchmarks

import re
import traceback
import pandas as pd
import numpy as np

# Se executado no Kaggle, descomente a importação do kbench:
# import kbench

# @kbench.task(
#     name="etl_knime_to_python_code_synthesis",
#     version="1.0.0",
#     description="Evaluates LLM capability in converting visual ETL pipeline logic into idiomatic, vectorized Python pandas code."
# )
def evaluate_etl_knime_benchmark(model_output: str, task_id: str = "etl_01") -> float:
    """
    Função de avaliação oficial para o Kaggle Benchmarks.
    Recebe a resposta do modelo (código) e retorna a pontuação de 0.0 a 1.0.
    """
    code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", model_output, re.DOTALL)
    clean_code = code_match.group(1).strip() if code_match else model_output.strip()
    
    local_scope = {"pd": pd, "np": np, "re": re}
    try:
        exec(clean_code, local_scope, local_scope)
        if "transform_etl" not in local_scope or not callable(local_scope["transform_etl"]):
            return 0.0
            
        transform_fn = local_scope["transform_etl"]
        
        if task_id == "etl_01":
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
            res = transform_fn(df_sales.copy(), df_customers.copy())
            assert len(res) == 4
            assert res[res['customer_id'] == 'C999']['customer_name'].values[0] == "Unknown Customer"
            assert res[res['customer_id'] == 'C102']['tier'].values[0] == "Standard"
            assert res[res['customer_id'] == 'C102']['amount'].values[0] == 0.0
            assert bool(res[res['transaction_id'] == 1]['is_vip'].values[0]) is True
            assert bool(res[res['transaction_id'] == 4]['is_vip'].values[0]) is False
            return 1.0

        elif task_id == "etl_02":
            df_raw = pd.DataFrame([
                {"log_entry": "USER:alice|ROLE:admin|IP:10.0.0.1|STATUS:200|DURATION:45ms"},
                {"log_entry": "USER:|ROLE:guest|IP:192.168.0.5|STATUS:404|DURATION:12ms"},
                {"log_entry": "USER:spambot|ROLE:bot|IP:1.2.3.4|STATUS:200|DURATION:5ms"},
                {"log_entry": "CORRUPTED_LINE_WITHOUT_DELIMITERS"}
            ])
            res = transform_fn(df_raw.copy())
            assert len(res) == 3
            assert res[res['role'] == 'guest']['username'].values[0] == "anonymous"
            return 1.0

        elif task_id == "etl_03":
            df_metrics = pd.DataFrame([
                {"department": "Sales", "employee_id": "E01", "month": "2026-01", "revenue": 1000.0, "target": 800.0},
                {"department": "Sales", "employee_id": "E01", "month": "2026-02", "revenue": 1200.0, "target": 1000.0},
                {"department": "Sales", "employee_id": "E02", "month": "2026-01", "revenue": 1500.0, "target": 1200.0},
                {"department": "Sales", "employee_id": "E02", "month": "2026-02", "revenue": 900.0, "target": 1000.0}
            ])
            res = transform_fn(df_metrics.copy())
            e01_m2 = res[(res['employee_id'] == 'E01') & (res['month'] == '2026-02')]
            assert np.isclose(e01_m2['cumulative_revenue'].values[0], 2200.0)
            assert np.isclose(e01_m2['target_achievement_pct'].values[0], 120.0, atol=0.1)
            return 1.0

        elif task_id == "etl_04":
            df_wide = pd.DataFrame([
                {"region": "North", "store_id": "S1", "2025_Q1": 100.0, "2025_Q2": 150.0, "2026_Q1": 120.0, "2026_Q2": 180.0},
                {"region": "South", "store_id": "S2", "2025_Q1": 200.0, "2025_Q2": 210.0, "2026_Q1": 250.0, "2026_Q2": 300.0}
            ])
            res = transform_fn(df_wide.copy())
            assert not isinstance(res.columns, pd.MultiIndex)
            assert list(res.columns) == ["region", "store_id", "quarter", "val_2025", "val_2026"]
            assert len(res) == 4
            return 1.0

        return 0.0
    except Exception:
        return 0.0

