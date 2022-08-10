from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import not_keyword
from robot.api import logger

class SuiteProcessors:
    @classmethod
    @not_keyword
    def echo(cls, in_suite, coverage='*'):
        return in_suite

    process_test_suite = echo # default processor
