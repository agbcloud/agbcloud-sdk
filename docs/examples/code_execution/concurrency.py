"""
AGB Concurrent Code Execution Example

This example demonstrates how to execute multiple code snippets in parallel using threading.
Concurrent execution is essential for high-throughput applications like data processing pipelines.
"""

import concurrent.futures
import json
import os
import time
from typing import Callable, List

from agb import AGB
from agb.session_params import CreateSessionParams


class ConcurrentAGBProcessor:
    def __init__(self, api_key: str, max_workers: int = 3):
        self.max_workers = max_workers
        self.agb = AGB(api_key=api_key)

    def process_tasks_concurrently(self, tasks: List[dict], processor: Callable):
        """Process multiple tasks concurrently"""
        results = []
        start_time = time.time()

        print(
            f"🚀 Starting processing of {len(tasks)} tasks with {self.max_workers} workers..."
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._process_single_task, task, processor): task
                for task in tasks
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(
                        {"task_id": task.get("id"), "success": True, "result": result}
                    )
                    print(f"✅ Task {task.get('id')} completed")
                except Exception as e:
                    results.append(
                        {"task_id": task.get("id"), "success": False, "error": str(e)}
                    )
                    print(f"❌ Task {task.get('id')} failed: {e}")

        duration = time.time() - start_time
        print(f"🏁 All tasks finished in {duration:.2f} seconds")
        return results

    def _process_single_task(self, task: dict, processor: Callable):
        """Process a single task with its own session"""
        # Create a dedicated session for this task
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)

        if not result.success:
            raise Exception(f"Failed to create session: {result.error_message}")

        session = result.session
        try:
            return processor(session, task)
        finally:
            self.agb.delete(session)


def data_processing_task(session, task):
    """The actual logic to run in the cloud"""
    data = task["data"]
    operation = task["operation"]

    # Simulate some heavy computation
    code = f"""
import json
import time

# Simulate work
time.sleep(1)

data = {json.dumps(data)}
result = []

for item in data:
    if '{operation}' == 'double':
        result.append(item * 2)
    elif '{operation}' == 'square':
        result.append(item ** 2)
    else:
        result.append(item)

print(json.dumps(result))
"""
    code_result = session.code.run(code, "python")

    if code_result.success:
        # Parse the last line of output as JSON result
        # First try to get from results
        if code_result.results and len(code_result.results) > 0:
            for result in code_result.results:
                if result.text and result.text.strip():
                    output_lines = result.text.strip().split("\n")
                    # Find the last line that looks like JSON
                    for line in reversed(output_lines):
                        line = line.strip()
                        if line.startswith("[") or line.startswith("{"):
                            try:
                                return json.loads(line)
                            except json.JSONDecodeError:
                                continue

        # Fallback to stdout logs
        if code_result.logs and code_result.logs.stdout:
            for line in reversed(code_result.logs.stdout):
                line = line.strip()
                if line.startswith("[") or line.startswith("{"):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue

        raise Exception("No valid JSON output found in code execution results")
    else:
        raise Exception(code_result.error_message)


def main():
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable is not set")
        return

    processor = ConcurrentAGBProcessor(api_key=api_key, max_workers=3)

    # Define a batch of tasks
    tasks = [
        {"id": 1, "data": [1, 2, 3, 4], "operation": "double"},
        {"id": 2, "data": [2, 4, 6, 8], "operation": "square"},
        {"id": 3, "data": [10, 20, 30], "operation": "double"},
        {"id": 4, "data": [5, 5, 5, 5], "operation": "square"},
    ]

    results = processor.process_tasks_concurrently(tasks, data_processing_task)

    print("\n--- Final Results ---")
    for res in results:
        status = "Success" if res["success"] else "Failed"
        output = res["result"] if res["success"] else res["error"]
        print(f"Task {res['task_id']}: {status} -> {output}")


if __name__ == "__main__":
    main()
