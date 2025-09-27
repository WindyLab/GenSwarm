"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime
from pathlib import Path


def run_command(index, command, timeout):
    try:
        print(f"[{index}] Running: {command}")
        subprocess.run(command, shell=True, timeout=timeout)
        return f"[✓] {index} SUCCESS | {command}"
    except subprocess.TimeoutExpired:
        return f"[⏱] {index} TIMEOUT | {command}"
    except Exception as e:
        return f"[✗] {index} ERROR | {command} | {str(e)}"


def run_all(llm_list, prompt_list, task_list, repeat_count=1, max_workers=1, timeout=1800, log_path="run_log.txt"):
    commands = []
    index = 0

    for llm in llm_list:
        for prompt in prompt_list:
            for task in task_list:
                for repeat in range(repeat_count):
                    cmd = (
                        f"python run/run_single.py "
                        f"--task_name {task} "
                        f"--prompt_type {prompt} "
                        f"--llm_name {llm} "
                    )
                    commands.append((index, cmd))
                    index += 1

    results = []
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "w") as log_file:
        log_file.write(f"=== Run started at {datetime.now()} ===\n\n")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for idx, cmd in commands:
                future = executor.submit(run_command, idx, cmd, timeout)
                futures.append(future)
                time.sleep(2)  # 👉 每提交一个任务，暂停 2 秒
            for future in tqdm(as_completed(futures), total=len(futures), desc="Executing Tasks"):
                result = future.result()
                results.append(result)
                log_file.write(result + "\n")

        # ✅ 统计结果
        success_count = sum("SUCCESS" in r for r in results)
        timeout_count = sum("TIMEOUT" in r for r in results)
        error_count = sum("ERROR" in r for r in results)
        total = len(results)

        summary = (
            f"\n=== Execution Summary ===\n"
            f"Total Tasks: {total}\n"
            f"✓ Success:   {success_count}\n"
            f"⏱ Timeout:   {timeout_count}\n"
            f"✗ Error:     {error_count}\n"
        )
        print(summary)
        log_file.write(summary)


if __name__ == "__main__":
    llm_model_list = ["DMXAPI-HuoShan-DeepSeek-V3"]
    prompt_type_list = [
        "default",
        # "compound",
        # "simple",
        # "simple_strategy",
        # "narrative",
        # "structured_default",
        # "structured_strategy"
    ]
    task_list = [
        # "shaping",
        # "encircling",
        # "covering",
        "crossing"
        # "exploration"
    ]
    repeat_each = 50  # 每种组合重复几次
    max_concurrent = 50
    per_task_timeout = 1800
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S:%f]")
    log_file_path = f"logs/run_log_{timestamp}.txt"

    run_all(
        llm_list=llm_model_list,
        prompt_list=prompt_type_list,
        task_list=task_list,
        repeat_count=repeat_each,
        max_workers=max_concurrent,
        timeout=per_task_timeout,
        log_path=log_file_path,
    )
