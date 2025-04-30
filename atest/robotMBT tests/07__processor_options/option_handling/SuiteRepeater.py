import copy

class SuiteRepeater:
    def process_test_suite(self, in_suite, **kwargs):
        n_repeats = int(kwargs['repeat'])
        out_suite = copy.deepcopy(in_suite)
        out_suite.scenarios = n_repeats*out_suite.scenarios
        for i in range(len(out_suite.scenarios)):
            out_suite.scenarios[i] = out_suite.scenarios[i].copy()
            out_suite.scenarios[i].name += f" - Rep {i}"
        return out_suite
