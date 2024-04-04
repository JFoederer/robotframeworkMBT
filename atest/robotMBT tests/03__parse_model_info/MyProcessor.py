from robot.api.deco import not_keyword

class MyProcessor:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    @not_keyword
    def process_test_suite(self, in_suite):
        self.in_suite = in_suite
        self._fail_on_step_errors()
        msg = "Model info not properly parsed"
        for scenario in in_suite.scenarios:
            assert scenario.steps, msg
            for step in scenario.steps:
                assert step.model_info['IN'] == ['Alfa'], f"{msg} in step {step.keyword}"
                assert step.model_info['OUT'] == ['Beta', 'Gamma delta', 'Epsilon'], f"{msg} in step {step.keyword}"
        return in_suite

    def _fail_on_step_errors(self):
        if self.in_suite.has_error():
            raise Exception("Error(s) detected in at least one step")

    def reported_errors(self):
        return self.in_suite.steps_with_errors()
