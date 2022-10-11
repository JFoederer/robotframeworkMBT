from robot.api.deco import library, not_keyword

@library
class MyProcessor:
    @not_keyword
    def process_test_suite(self, in_suite):
        msg = "Model info not properly parsed"
        for scenario in in_suite.scenarios:
            assert scenario.steps, msg
            for step in scenario.steps:
                assert step.model_info['IN'] == ['Alfa'], f"{msg} in step {step.keyword}"
                assert step.model_info['OUT'] == ['Beta', 'Gamma delta', 'Epsilon'], f"{msg} in step {step.keyword}"
        return in_suite
