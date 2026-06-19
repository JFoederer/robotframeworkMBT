from robot.api import logger
from robot.api.deco import library
from robot.libraries.BuiltIn import BuiltIn


@library(scope='SUITE', listener='SELF')
class TagListener:
    ROBOT_LISTENER_PRIORITY = -1  # Set lower priority to make sure tags are already set by robotmbt
    TRACE_TAG = 'mbt trace extension'

    def __init__(self):
        self.test_count = 0

    def end_test(self, tc, result):
        self.test_count += 1
        if self.test_count % 2:
            if self.TRACE_TAG in result.tags:
                result.status = 'FAIL'
                result.message = f"Unexpected test tag '{self.TRACE_TAG}'"
        else:
            if self.TRACE_TAG not in result.tags:
                result.status = 'FAIL'
                result.message = f"Test tag '{self.TRACE_TAG}' missing"

        if 'my tag' not in result.tags:
            result.status = 'FAIL'
            result.message = "Test tag 'my tag' missing"
        BuiltIn().set_suite_variable('${confirmed_passes}', BuiltIn().get_variable_value('${confirmed_passes}') + 1)
        logger.info("PASS confirmed by listener")
