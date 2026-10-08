# 📊 ETL-to-Python LLM Benchmark Results

### 📈 Official Leaderboard Summary:
| Model                | Accuracy (Passed / Total)   |   Avg Score | Avg API Latency   |
|----------------------|-----------------------------|-------------|-------------------|
| **gemini-3.8-flash** | 100.0% (4/4)                |           1 | 14899.62 ms       |
| **gemini-2.5-pro**   | 100.0% (4/4)                |           1 | 33785.72 ms       |

### 🔍 Detailed Task-by-Task Breakdown:

#### Model: `gemini-3.8-flash`
- **etl_01_complex_join_missing_types**: ✅ PASS (Sandbox Assertion Time: 16.0 ms)
- **etl_02_regex_nested_string_splitter**: ✅ PASS (Sandbox Assertion Time: 0.0 ms)
- **etl_03_group_loop_vectorized_aggregation**: ✅ PASS (Sandbox Assertion Time: 12.98 ms)
- **etl_04_unpivot_pivoting_matrix_reshaping**: ✅ PASS (Sandbox Assertion Time: 24.85 ms)

#### Model: `gemini-2.5-pro`
- **etl_01_complex_join_missing_types**: ✅ PASS (Sandbox Assertion Time: 16.0 ms)
- **etl_02_regex_nested_string_splitter**: ✅ PASS (Sandbox Assertion Time: 12.22 ms)
- **etl_03_group_loop_vectorized_aggregation**: ✅ PASS (Sandbox Assertion Time: 14.05 ms)
- **etl_04_unpivot_pivoting_matrix_reshaping**: ✅ PASS (Sandbox Assertion Time: 21.75 ms)
