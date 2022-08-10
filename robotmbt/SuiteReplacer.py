from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import keyword
from robot.api import logger
import robot.running.model as rmodel

from .SuiteProcessors import SuiteProcessors

class SuiteReplacer:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, processor='process_test_suite', processor_lib=None,):
        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None
        self.robot_suite = None
        suite_processor = SuiteProcessors if processor_lib is None \
                                          else getattr(Robot.get_library_instance(processor_lib))
        self.suite_processor = getattr(suite_processor, processor)

    @keyword(name="Treat this test suite Model-based")
    def treat_model_based(self):
        """
        Iterate through the suite and if all keywords also have a modelling variant (prefix 'model')
        then replace the contents with a generated trace.
        """
        self.robot_suite = self.current_suite

        logger.info(f"Analysing Robot test suite '{self.robot_suite.name}' for model-based execution.")
        master_suite = self.__process_robot_suite(self.robot_suite, parent=None)

        modelbased_suite = self.suite_processor(master_suite)
        self.__clearTestSuite(self.robot_suite)
        self.__generateRobotSuite(modelbased_suite, self.robot_suite)

    def __process_robot_suite(self, in_suite, parent):
        logger.debug(f"processing test suite: {in_suite.name}")
        out_suite = Suite(in_suite.name, parent)
        out_suite.filename = in_suite.source
        
        if in_suite.setup:
            logger.debug(f"    with setup: {in_suite.setup.name}")
            self.prev_gherkin_kw = None
            step_info = self.__process_step(in_suite.setup, parent=out_suite)
            if step_info.gherkin_kw != 'given':
                step_info.model_info['error'] = "Setup must be a 'given' step"
            out_suite.setup = step_info
        for st in in_suite.suites:
            out_suite.suites.append(self.__process_robot_suite(st, parent=out_suite))
        for tc in in_suite.tests:
            scenario = Scenario(tc.name, parent=out_suite)
            prev_gherkin_kw = None
            logger.debug(f"  test case: {tc.name}")
            if tc.setup:
                logger.debug(f"    with setup: {tc.setup.name}")
                self.prev_gherkin_kw = None
                step_info = self.__process_step(tc.setup, parent=scenario)
                if step_info.gherkin_kw != 'given':
                    step_info.model_info['error'] = "Setup must be a 'given' step"
                scenario.setup = step_info
            logger.debug('    ' + '\n    '.join([st.name + " " + " ".join([str(s) for s in st.args]) for st in tc.body]))
            self.prev_gherkin_kw = None
            for step_def in tc.body:
                step_info = self.__process_step(step_def, parent=scenario)
                scenario.steps.append(step_info)

            out_suite.scenarios.append(scenario)
        return out_suite

    def __process_step(self, step_def, parent):
        step = Step(step_def.name, parent)
        self.prev_gherkin_kw = step.step_kw if str(step.step_kw).lower() in ['given','when','then', 'none'] else self.prev_gherkin_kw
        step.gherkin_kw = step.step_kw if str(step.step_kw).lower() in ['given','when','then'] else self.prev_gherkin_kw
        if step_def.args:
            step.args = step_def.args
        try:
            step.model_info = Robot.run_keyword('model ' + step.bare_kw, *step_def.args)
        except Exception as ex:
            step.model_info['error']=str(ex)
        return step

    def __clearTestSuite(self, suite):
        suite.tests.clear()
        suite.suites.clear()

    def __generateRobotSuite(self, suite_model, target_suite):
        for subsuite in suite_model.suites:
            new_suite = target_suite.suites.create(name=subsuite.name)
            new_suite.resource = target_suite.resource
            if subsuite.setup:
                new_suite.setup = rmodel.Keyword(name=subsuite.setup.keyword, args=subsuite.setup.args, type='setup')
            self.__generateRobotSuite(subsuite, new_suite)
        for tc in suite_model.scenarios:
            new_tc = target_suite.tests.create(name=tc.name)
            if tc.setup:
                new_tc.setup= rmodel.Keyword(name=tc.setup.keyword, args=tc.setup.args, type='setup')
            for step in tc.steps:
                new_tc.body.create_keyword(name=step.keyword, args=step.args)

    def _start_suite(self, suite, result):
        self.current_suite = suite

    def _end_suite(self, suite, result):
        if suite == self.robot_suite:
            self.robot_suite = None

class Suite:
    def __init__(self, name, parent=None):
        self.name = name
        self.filename = ''
        self.parent = parent
        self.suites = []
        self.scenarios = []
        self.setup = None # Can be a single step or None

class Scenario:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.setup = None # Can be a single step or None
        self.steps = []

class Step:
    def __init__(self, name, parent):
        self.keyword = name      # first cell of the Robot line, including step_kw, excluding args
        self.parent = parent     # Parent scenario for easy searching and processing
        self.gherkin_kw = None   # given, when, then or None for non-bdd keywords
        self.args = ()           # Comes directly from Robot
        self.model_info = dict(IN=[], OUT=[]) # Can optionally contain an additional error field
                                 # IN and OUT are lists of Pyhton evaluatable expressions. The
                                 # vocab.attribute form can be used to express relations between
                                 # properties from the domain vocabulaire.

    @property
    def step_kw(self):
        first_word = self.keyword.split()[0].lower()
        return first_word if first_word in ['given','when','then','and','but'] else None

    @property
    def bare_kw(self):
        """The keyword without its Gherkin keyword. I.e., as it is known in Robot framework."""
        return self.keyword.replace(self.step_kw, '', 1).strip() if self.step_kw else self.keyword
