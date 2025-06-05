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

import os
import pickle
import sys
import json
import time

from global_skill import allocate_run
import rospy
import numpy as np


def main():
    result = allocate_run()
    print(result)
    # 将返回值（字典）保存为 JSON 文件
    with open("allocate_result.pkl", "wb") as f:
        pickle.dump(result, f)
    print(result)


if __name__ == "__main__":
    print(sys.argv)
    rospy.init_node("allocate_run_node", anonymous=True)
    time.sleep(3)
    main()
