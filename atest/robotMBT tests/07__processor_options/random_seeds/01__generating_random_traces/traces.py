from robot.api.deco import keyword


class traces:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def reset_traces(self):
        self.traces = {}

    @keyword("Trace '${trace}', scenario number ${test_id} is executed")
    def add_test(self, trace, test_id: str):
        """*model info*
        :IN:  None
        :OUT: None
        """
        if trace in self.traces:
            self.traces[trace] += test_id
        else:
            self.traces[trace] = test_id

    def get_all_traces(self):
        return self.traces.values()
