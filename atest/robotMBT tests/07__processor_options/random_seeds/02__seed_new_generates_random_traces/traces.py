from robot.api.deco import keyword

class traces:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def init_trace_variables(self):
        self.traces = {1:[], 2:[]}

    @keyword("Trace ${n} test number ${m} is executed")
    def add_test(self, trace:int, test_id:int):
        """*model info*
        :IN:  None
        :OUT: None
        """
        self.traces[trace].append(test_id)

    def get_trace(self, trace:int):
        return self.traces[trace]
