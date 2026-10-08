"""
Benchmark runner using the Google GenAI SDK.
Evaluates models such as gemini-3.8-flash and gemini-2.5-pro across ETL synthesis tasks.
"""

import os
import sys
import json
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from typing import List, Dict, Any
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, RESULTS_DIR
from src.tasks.task_specs import BENCHMARK_TASKS
from src.tasks.validators import execute_and_evaluate

def run_gemini_benchmark(models: List[str] = None) -> Dict[str, Any]:
    """
    Executes the benchmark test battery across specified Gemini models.
    """
    if models is None:
        models = [
            "gemini-3.8-flash",
            "gemini-2.5-pro"
        ]
        
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY was not found in the .env file!")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    benchmark_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models_evaluated": models,
        "tasks_count": len(BENCHMARK_TASKS),
        "results": {}
    }
    
    for model_name in models:
        print(f"\n🚀 Evaluating model: {model_name}...")
        model_records = []
        
        for task in BENCHMARK_TASKS:
            print(f"  📌 Running task: {task['id']} ({task['title']})...")
            start_api_time = time.time()
            try:
                # Official Google GenAI SDK call
                response = client.models.generate_content(
                    model=model_name,
                    contents=task["prompt"],
                    config=types.GenerateContentConfig(
                        temperature=0.0, # Zero-shot deterministic code generation
                    )
                )
                raw_text = response.text or ""
                api_duration_ms = round((time.time() - start_api_time) * 1000, 2)
                
                # Execute and evaluate generated code
                eval_result = execute_and_evaluate(task, raw_text)
                eval_result["api_duration_ms"] = api_duration_ms
                eval_result["raw_response_length"] = len(raw_text)
                
                status_icon = "✅" if eval_result["passed"] else "❌"
                print(f"    {status_icon} Score: {eval_result['score']} | API Latency: {api_duration_ms}ms | Validation: {eval_result.get('message') or eval_result.get('error')}")
                model_records.append(eval_result)
                
            except Exception as e:
                print(f"    ⚠️ Error calling model {model_name}: {e}")
                model_records.append({
                    "task_id": task["id"],
                    "passed": False,
                    "score": 0.0,
                    "error": f"API Error: {str(e)}",
                    "api_duration_ms": round((time.time() - start_api_time) * 1000, 2)
                })
                
        # Calculate summary metrics
        passed_count = sum(1 for r in model_records if r.get("passed"))
        avg_score = sum(r.get("score", 0.0) for r in model_records) / len(BENCHMARK_TASKS)
        avg_latency = sum(r.get("api_duration_ms", 0) for r in model_records) / len(BENCHMARK_TASKS)
        
        benchmark_results["results"][model_name] = {
            "summary": {
                "tasks_passed": passed_count,
                "total_tasks": len(BENCHMARK_TASKS),
                "accuracy_pct": round((passed_count / len(BENCHMARK_TASKS)) * 100, 2),
                "avg_score": round(avg_score, 3),
                "avg_api_latency_ms": round(avg_latency, 2)
            },
            "detailed_tasks": model_records
        }

    # Save results to JSON
    output_file = RESULTS_DIR / f"gemini_benchmark_results_{int(time.time())}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2, ensure_ascii=False)
        
    print(f"\n✨ Benchmark completed! Results saved to: {output_file}")
    return benchmark_results

if __name__ == "__main__":
    run_gemini_benchmark()
