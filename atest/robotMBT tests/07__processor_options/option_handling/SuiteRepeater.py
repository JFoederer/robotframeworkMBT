import copy

class SuiteRepeater:
    """
    Given a test suite, repeats all scenarios 'repeat' times (default=1)
    Setting bonus_scenario=${True} repeats 1 additional time
    sub-suites are ignored
    """
    def process_test_suite(self, in_suite, repeat=1, **kwargs):
        n_repeats = int(repeat)
        if kwargs.get('bonus_scenario', False):
            n_repeats +=1
        out_suite = copy.deepcopy(in_suite)
        out_suite.scenarios = n_repeats*out_suite.scenarios
        for i in range(len(out_suite.scenarios)):
            out_suite.scenarios[i] = out_suite.scenarios[i].copy()
            if i:
                out_suite.scenarios[i].name += f" (rep {i})"
        return out_suite

    def mandatory_repeat_argument(self, in_suite, *, repeat, bonus_scenario=False):
        return self.process_test_suite(in_suite, repeat=repeat, bonus_scenario=bonus_scenario)
