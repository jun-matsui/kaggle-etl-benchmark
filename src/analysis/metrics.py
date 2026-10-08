"""
Generates analytical reports, comparison tables, and charts for DEV.to / Kaggle publications.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from tabulate import tabulate
from src.config import RESULTS_DIR

def load_latest_results() -> Dict[str, Any]:
    """Loads the most recent benchmark JSON results file."""
    json_files = sorted(RESULTS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not json_files:
        raise FileNotFoundError(f"No result JSON files found in {RESULTS_DIR}")
    
    with open(json_files[0], "r", encoding="utf-8") as f:
        return json.load(f)

def generate_markdown_report(data: Dict[str, Any] = None) -> str:
    """Generates a GitHub-flavored Markdown report ready for publication."""
    if data is None:
        data = load_latest_results()
        
    table_rows = []
    for model_name, res in data["results"].items():
        summary = res["summary"]
        table_rows.append([
            f"**{model_name}**",
            f"{summary['accuracy_pct']}% ({summary['tasks_passed']}/{summary['total_tasks']})",
            f"{summary['avg_score']:.2f}",
            f"{summary['avg_api_latency_ms']} ms"
        ])
        
    headers = ["Model", "Accuracy (Passed / Total)", "Avg Score", "Avg API Latency"]
    md_table = tabulate(table_rows, headers=headers, tablefmt="github")
    
    report = f"""# 📊 ETL-to-Python LLM Benchmark Results

### 📈 Official Leaderboard Summary:
{md_table}

### 🔍 Detailed Task-by-Task Breakdown:
"""
    for model_name, res in data["results"].items():
        report += f"\n#### Model: `{model_name}`\n"
        for task_res in res["detailed_tasks"]:
            status = "✅ PASS" if task_res.get("passed") else "❌ FAIL"
            report += f"- **{task_res['task_id']}**: {status} (Sandbox Assertion Time: {task_res.get('duration_ms', 0)} ms)\n"
            if task_res.get("error"):
                report += f"  - *Error Details:* `{task_res['error']}`\n"

    report_path = RESULTS_DIR / "latest_benchmark_summary.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"\n📑 Markdown report successfully generated at: {report_path}")
    print("\n" + report)
    return report

if __name__ == "__main__":
    generate_markdown_report()
