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
from concurrent.futures import ThreadPoolExecutor


def run_command(command, timeout):
    print(f"Starting run for command: {command}")
    try:
        # 使用 subprocess.run 设置超时
        subprocess.run(command, shell=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(
            f"Command '{command}' exceeded the timeout of {timeout} seconds and was terminated."
        )


def run_multiple_times(command, num_times, max_workers=1, timeout=30):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(num_times):
            time.sleep(2)
            executor.submit(run_command, command, timeout)


if __name__ == "__main__":
    command_to_run = "python run_single.py"
    num_runs = 50
    max_workers = 50
    max_timeout = 18000  # 设置最大执行时间为30秒

    run_multiple_times(command_to_run, num_runs, max_workers, max_timeout)
