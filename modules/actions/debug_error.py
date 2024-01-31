import re

from modules.actions.action import Action
from modules.utils import parse_code

PROMPT_TEMPLATE = """
NOTICE
Translation: Based on the information below, you need to determine which file needs to be rewritten.
If the test file detects bugs in the source file, the source file should be rewritten.
If there are issues with the test file itself, the test file needs to be rewritten. Only one file can be rewritten.

Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the test case or script and triple quotes.
The message is as follows:
{context}
---
## role:...
## file to rewrite:...
## code:
```python ... ``` 
"""


class DebugError(Action):
    name: str = "DebugError"

    async def run(self, context):
        if "PASS" in context:
            return None, "the original code works fine, no need to debug"

        file_name = re.search("File To Rewrite:\s*(.+\\.py)", context, re.IGNORECASE).group(1)

        self._logger.info(f"Debug and rewrite {file_name}")

        prompt = PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)

        code = parse_code(text=rsp)

        return file_name, code
