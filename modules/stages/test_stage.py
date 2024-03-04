import difflib

from modules.stages.stage import Stage, StageResult
from modules.actions import WriteCode, RunCode
from modules.utils import read_file
from modules.prompt.const import WORKSPACE_ROOT
from modules.framework.workflow_context import FileStatus, FileInfo
from modules.utils.common import BugSource


class TestStage(Stage):
    def __init__(self, action: WriteCode):
        super(TestStage, self).__init__()
        self._action = action
        self._run_code = RunCode()
        self._old_test_code = ""
        self._differ = difflib.Differ()
            
    def _run(self) -> StageResult:
        code_files = self._context.code_files
        files_to_check = ["core.py", "run.py"]
        for file_to_check in files_to_check:
            codefile_name = file_to_check
            testfile_name = "test_" + file_to_check
            if testfile_name not in code_files:
                self._logger.debug("test file not exist: %s", testfile_name)
                code = read_file(WORKSPACE_ROOT, codefile_name)
                prompt = WRITE_TEST_PROMPT_TEMPLATE.format(code_to_test=code)
                code_files[testfile_name] = FileInfo()
                break
            elif code_files[codefile_name].status != FileStatus.TESTED_PASS:
                self._logger.debug("rewrite test file for %s", codefile_name)
                test_code = read_file(WORKSPACE_ROOT, testfile_name)
                prompt = REWRITE_TEST_PROMPT_TEMPLATE.format(
                    test_code=test_code,
                    error_message=code_files[testfile_name].message)
                code_files[testfile_name].version += 1
                break

        new_code = self._action.run(prompt=prompt, filename=testfile_name)
        diff = self._differ.compare(new_code.splitlines(), self._old_test_code.splitlines())
        self._old_test_code = new_code

        self._logger.error(code_files[testfile_name].version)
        
        code_info = {
            "file_name": codefile_name,
            "test_file_name": testfile_name
        }
        error, keys = self._run_code.run(code_info=str(code_info))
        if BugSource.CODE in keys:
            code_files[codefile_name].message = error
        elif BugSource.TEST_CODE in keys:
            code_files[testfile_name].message = error
        else:
            code_files[codefile_name].status = FileStatus.TESTED_PASS
        return StageResult(keys=keys)
