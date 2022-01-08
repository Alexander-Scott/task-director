import logging
import subprocess
from enum import IntEnum

from task_sharding_client.task_runner import TaskRunner

logger = logging.getLogger(__name__)


class BazelExitCodes(IntEnum):
    # Exit codes common to all commands:
    SUCCESS = 0
    COMMAND_LINE_PROBLEM = 2
    BUILD_TERMINATED_ORDERLY_SHUTDOWN = 8
    EXTERNAL_ENVIRONMENT_FAILURE = 32
    OOM_FAILURE = 33
    LOCAL_ENVIRONMENTAL_ISSUE = 36
    UNHANDLED_EXCEPTION = 37

    # Exit codes for bazel build, bazel test:
    BUILD_FAILED = 1
    BUILD_OK_TESTS_FAILED = 3
    BUILD_OK_NO_TESTS_FOUND = 4

    # Exit codes for bazel query:
    PARTIAL_SUCCESS = 3
    COMMAND_FAILURE = 7


class BazelTask(TaskRunner):
    def run(self, step_id: str):
        logger.info("Starting build task")

        target = self._schema["steps"][int(step_id)]["task"]
        proc = subprocess.Popen(["bazel", "test", target], cwd=self._config.workspace_path)
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()

        if exit_code != BazelExitCodes.SUCCESS:
            logger.error("Build failure: " + str(stderr))
            return False

        logger.info("Finished build task")
        return True
