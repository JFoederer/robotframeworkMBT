from robot.api.deco import library

from suiterepeater import SuiteRepeater


@library(auto_keywords=None, listener=True)
class StrictSuiteRepeater(SuiteRepeater):
    """
    Nearly identical to SuiteRepeater as used in other test cases. The difference is that
    this variant is strict in its argument handling and will fail if mandatory arguments
    are missing or unknown arguments are provided.
    """

    def process_test_suite(self, in_suite, *, repeat, bonus_scenario=False):
        return super().process_test_suite(in_suite, repeat=repeat, bonus_scenario=bonus_scenario)
