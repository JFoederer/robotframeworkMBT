import unittest


try:
    from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseScenarioDeltaValueGraph(unittest.TestCase):
        def test_scenario_delta_value_graph_init(self):
            info = TraceInfo()
            stg = ScenarioDeltaValueGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 1)
            self.assertEqual(len(stg.networkx.edges), 0)

            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

        def test_scenario_delta_value_graph_ids_empty(self):
            info = TraceInfo()
            stg = ScenarioDeltaValueGraph(info)

            scenario = ScenarioInfo('test')

            node_id = stg._get_or_create_id((scenario, set({'x': '1'}.items())))

            self.assertEqual(node_id, 'node0')

        def test_scenario_delta_value_graph_ids_duplicate_scenario(self):
            info = TraceInfo()
            stg = ScenarioDeltaValueGraph(info)

            s0 = ScenarioInfo('test')
            s1 = ScenarioInfo('test')

            id0 = stg._get_or_create_id((s0, set({'x': '1'}.items())))
            id1 = stg._get_or_create_id((s1, set({'x': '1'}.items())))

            self.assertEqual(id0, id1)

        def test_scenario_delta_value_graph_merge_same_scenario_update(self):
            info = TraceInfo()
            sti = StateInfo._create_state_with_prop("prop", [("x", "1")])
            info.update_trace(ScenarioInfo("incr x"), sti, 1)
            info.update_trace(ScenarioInfo("set y"), StateInfo._create_state_with_prop("prop", [("y", "True")]), 2)
            info.update_trace(ScenarioInfo("incr x"), sti, 1)
            info.update_trace(ScenarioInfo("incr x"), StateInfo._create_state_with_prop("prop", [("x", "2")]), 2)
            info.update_trace(ScenarioInfo("set y"), StateInfo._create_state_with_prop("prop", [("y", "True")]), 3)
            sdvg = ScenarioDeltaValueGraph(info)
            self.assertEqual(len(sdvg.networkx.nodes), 4)

    # TODO add more tests
