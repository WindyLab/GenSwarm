ANALYZE_PROMPT_TEMPLATE: str = """
## Role setting
You are a robot with the ability to move and perceive.

## These are the basic Robot APIs:
```python
{robot_api}
```

## These are the environment description:
{env_des}

## User requirements: 
{instruction}

## Task description:
You need to analyze user's command. Consider what functions are needed to meet the user's requirements.
The generated result should be in the following fields:
1. Keyword: what are the key words in the requirements?
2. Definition: Professional explanations about the keywords?
3. User Requirement Description: Detailed description of the task the user hopes to automate.
4. Functional Requirements: List the functions expected to be developed based on your analysis and available resources. For each function, briefly describe its purpose and expected outcome. These functions should be decoupled from each other.

## The output TEXT format is as follows:
1. Keyword: <Keyword>
2. Definition: <Definition>
3. User Requirement: <User Requirement>
4. Functional Requirements: <Functional Requirements>
""".strip()