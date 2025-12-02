import unittest

try:
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseModels(unittest.TestCase):
        """
        Contains tests for robotmbt/visualise/models.py
        """

        """
        Class: ScenarioInfo
        """

        def test_scenarioInfo_str(self):
            si = ScenarioInfo('test')
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 'test')

        def test_scenarioInfo_Scenario(self):
            s = Scenario('test')
            s.src_id = 0
            si = ScenarioInfo(s)
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 0)

        """
        Class: StateInfo
        """

        def test_stateInfo_empty(self):
            s = StateInfo(ModelSpace())
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_empty(self):
            space = ModelSpace()
            space.props['prop1'] = ModelSpace()
            s = StateInfo(space)
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_val(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            space.props['prop1'] = prop1
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))

        def test_stateInfo_prop_val_empty(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            prop2 = ModelSpace()
            space.props['prop1'] = prop1
            space.props['prop2'] = prop2
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))
            self.assertFalse('prop2:' in str(s))

        """
        Class: TraceInfo
        """

        def test_traceInfo(self):
            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
            ti = TraceInfo.from_trace_state(trace=ts, state=ModelSpace())

            self.assertEqual(ti.trace[0].name, str(0))
            self.assertEqual(ti.trace[1].name, str(1))
            self.assertEqual(ti.trace[2].name, str(2))

            self.assertEqual(str(ti.state), '')

if __name__ == '__main__':
    unittest.main()
