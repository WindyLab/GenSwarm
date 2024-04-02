CODE_REVIEW_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You are a critic, and you need to check whether the given function meets certain constraints.

## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```

## These are the existing functions that you can directly call:
```python
{other_functions}
```

## This is the constraint that the function should satisfy:
{constraints}

## These are the functions that need to be checked:
```python
{functions}
```

## The output TEXT format is as follows:
 
**Reasoning**: if satisfied, why? For each function, you need to provide a reason. If not satisfied, how to improve it?
**Satisfaction**: True/False.Choose one of them.
**Modified function**:
```python
put the modified function here
```

## Notes:
Your output should satisfy the following notes:
- Check whether the function meets the constraints.
- Provide a reason for each function.
- If the function does not meet the constraints, provide a modified function.
- If the function meets the constraints, don't provide a modified function. 
- The output should strictly adhere to the specified format.
- In your answer, you can only use one True or False in a condition, and it's not allowed to be used elsewhere.
- The modified function section should be filled in only when the function does not meet the constraints.Otherwise, it should be empty.
- The modified function is not allowed to change the function name.
- The modified function absolutely must be complete and executable. You must provide a function that can be run directly, with absolutely no unfinished parts in the code.
""".strip()

HIGH_LEVEL_FUNCTION_REVIEW: str = """
## Background:
{task_des}
## Role setting:
- You are a critic, You should now check if there are any bugs in the functions written by other agents or if there have been any incorrect calls.

## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the existing functions that you can directly call:
```python
{other_functions}
```

## These are the functions that need to be checked:
```python
{function_content}
```

## The output TEXT format is as follows:

**Reasoning**: think step by step, whether the to be checked function has any bugs or incorrect calls.
**Modified function**:(if the function has bugs or incorrect calls else it should not appear,only output the Reasoning part)
```python
import ... (import the necessary modules,if any)
def {function_name}(...):
    # put the modified function here
```

## Notes:
Your output should satisfy the following notes:
- Carefully check if there are any bugs in this function, or if there are any logical inconsistencies.
- Check if the call to each sub-function is correct.
- Check that all defined variables are used.
- Strictly adhere to the specified format.
- The modified function section should be filled in only when the function has bugs or incorrect calls. Otherwise, this section should not appear.
- If the function needs to be rewritten, please ensure that the rewritten function name is {function_name}.
- If you need to rewrite a function, please output the complete and correct function, and only modify the parts that are incorrect.
- You should carefully consider and ensure that your revised version is correct.
- If there is an error in this function, please provide the erroneous line of code in the "reasoning" section, along with suggestions for how it could be corrected.
- If the function outputs velocity, then this velocity must be normalized.
- If the revised function name is run_loop,here is some special notes:
    - The run_loop function is the main function that the ser calls to run the entire task. It is the entry point for the entire task.
    - The run_loop function should contain all the necessary logic to complete the task.
    - Calling time.sleep or any other method to limit frequency is not allowed, as the underlying API has determined a set frequency.
    - The while loop should be used to ensure that the function is called continuously and that the robot can update its observation data in real time.If the function is not implemented in other functions,the run_loop function should be used to achieve this.
    - The while loop must be endless, and the function must be able to run continuously.
""".strip()
