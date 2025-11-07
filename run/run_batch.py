import logging
import os
import subprocess
import time

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

task_keys = [
    # "exploration"
    # "crossing",
    "encircling",
    # "shaping",
    # "bridging",
    # "aggregation",
    # "flocking",
    "covering",
]

# llm_model_list = ["gpt-4o-2024-11-20"]
# llm_model_list = ["DMXAPI-HuoShan-DeepSeek-V3"]
# llm_model_list = ["o1-mini"]
llm_model_list = ["o1-mini", "gpt-4o-2024-11-20", "DMXAPI-HuoShan-DeepSeek-V3"]

prompt_type_list = [
    # "default",
    # "simple",
    # "simple_strategy",
    # "narrative",
    "structured_default",
    # "structured_strategy"
]
# prompt_type_list.reverse()


test_modes = [
    # 'cap',
    # 'meta'
    # 'llm2swarm'
    'wo_vlm'
    # 'debug'
    # 'vlm'
    # 'improve'
]

run_modes = [
    # 'rerun',
    # 'continue',
    # 'fail_rerun',
    # 'rerun',
    # 'fail_rerun',
    'analyze',
]
# run_modes = [
#     'analyze',
# ]
MAX_THREADS = 1  # Set the maximum number of threads you want to run concurrently


def run_batch(batch_num, task_name, run_mode, test_mode, task_path):
    print(f"Running batch {batch_num} for task {task_name}...")
    result = subprocess.run(["python", "run/run_code.py", "--exp_batch", str(batch_num), "--task_name", task_name,
                             '--run_mode', run_mode, '--test_mode', test_mode, '--task_path', task_path], )
    if result.returncode != 0:
        print(f"Batch {batch_num} encountered an error.")
    return result.returncode


def run_batches(llm, prompt_type, task_name, run_mode, test_mode):
    batch_numbers = range(1, 2)  # Adjust range as needed
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Submit all batches to the executor and create progress bar
        future_to_batch = {executor.submit(run_batch, batch_num, task_name, run_mode, test_mode,
                                           task_path=f'{llm}/{prompt_type}'): batch_num for
                           batch_num in
                           batch_numbers}
        for future in tqdm(as_completed(future_to_batch), total=len(batch_numbers),
                           desc=f"Running {task_name} batches"):
            batch_num = future_to_batch[future]
            try:
                return_code = future.result()
                if return_code != 0:
                    print(f"Batch {batch_num} encountered an error and stopped.")
                    break
            except Exception as exc:
                print(f"Batch {batch_num} generated an exception: {exc}")


def run_tasks():
    for run_mode in run_modes:
        print(f"Running tasks in {run_mode} mode...")
        for llm_model in llm_model_list:
            for prompt_type in prompt_type_list:
                for task_name in task_keys:
                    print(f"Running task {task_name}...")
                    for test_mode in test_modes:
                        run_batches(llm_model, prompt_type, task_name, run_mode, test_mode)


if __name__ == "__main__":
    run_tasks()
