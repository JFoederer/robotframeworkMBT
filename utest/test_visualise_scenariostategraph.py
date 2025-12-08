import unittest
from typing import Any

try:
    from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseScenarioGraph(unittest.TestCase):
        def test_scenario_state_graph_init(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 1)
            self.assertEqual(len(stg.networkx.edges), 0)

            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

        def test_scenario_state_graph_ids_empty(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            scenario = ScenarioInfo('test')
            state = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            node_id = stg._get_or_create_id((scenario, state))

            self.assertEqual(node_id, 'node0')

        def test_scenario_state_graph_ids_duplicate_scenario(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            s0 = ScenarioInfo('test')
            s1 = ScenarioInfo('test')
            st0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            st1 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            id0 = stg._get_or_create_id((s0, st0))
            id1 = stg._get_or_create_id((s1, st1))

            self.assertEqual(id0, id1)

        def test_scenario_state_graph_ids_different_scenarios(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            s00 = ScenarioInfo('test0')
            s01 = ScenarioInfo('test0')
            s10 = ScenarioInfo('test1')
            s11 = ScenarioInfo('test1')

            state = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            id00 = stg._get_or_create_id((s00, state))
            id01 = stg._get_or_create_id((s01, state))
            id10 = stg._get_or_create_id((s10, state))
            id11 = stg._get_or_create_id((s11, state))

            self.assertEqual(id00, 'node0')
            self.assertEqual(id01, 'node0')
            self.assertEqual(id00, id01)

            self.assertEqual(id10, 'node1')
            self.assertEqual(id11, 'node1')
            self.assertEqual(id10, id11)

            self.assertNotEqual(id00, id10)
            self.assertNotEqual(id00, id11)
            self.assertNotEqual(id01, id10)
            self.assertNotEqual(id01, id11)

        def test_scenario_state_graph_ids_different_states(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            scenario = ScenarioInfo('test')

            s00 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            s01 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            s10 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            s11 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            id00 = stg._get_or_create_id((scenario, s00))
            id01 = stg._get_or_create_id((scenario, s01))
            id10 = stg._get_or_create_id((scenario, s10))
            id11 = stg._get_or_create_id((scenario, s11))

            self.assertEqual(id00, 'node0')
            self.assertEqual(id01, 'node0')
            self.assertEqual(id00, id01)

            self.assertEqual(id10, 'node1')
            self.assertEqual(id11, 'node1')
            self.assertEqual(id10, id11)

            self.assertNotEqual(id00, id10)
            self.assertNotEqual(id00, id11)
            self.assertNotEqual(id01, id10)
            self.assertNotEqual(id01, id11)

        def test_scenario_state_graph_ids_different_scenario_state(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            s00 = ScenarioInfo('test0')
            s01 = ScenarioInfo('test1')
            s10 = ScenarioInfo('test0')
            s11 = ScenarioInfo('test1')

            st00 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            st01 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            st10 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            st11 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            id00 = stg._get_or_create_id((s00, st00))
            id01 = stg._get_or_create_id((s01, st01))
            id10 = stg._get_or_create_id((s10, st10))
            id11 = stg._get_or_create_id((s11, st11))

            self.assertEqual(id00, 'node0')
            self.assertEqual(id01, 'node1')
            self.assertEqual(id10, 'node2')
            self.assertEqual(id11, 'node3')

            self.assertNotEqual(id00, id01)
            self.assertNotEqual(id00, id10)
            self.assertNotEqual(id00, id11)
            self.assertNotEqual(id01, id10)
            self.assertNotEqual(id01, id11)
            self.assertNotEqual(id10, id11)

        def test_scenario_state_graph_add_new_node(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 1)

            self.assertIn('start', stg.networkx.nodes)
            self.assertNotIn('test', stg.networkx.nodes)

            scenario = ScenarioInfo('test')
            state = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            stg.ids['test'] = (scenario, state)
            stg._add_node('test')

            self.assertEqual(len(stg.networkx.nodes), 2)

            self.assertIn('start', stg.networkx.nodes)
            self.assertIn('test', stg.networkx.nodes)

            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')
            self.assertIn('test', stg.networkx.nodes['test']['label'])
            self.assertIn('prop:', stg.networkx.nodes['test']['label'])
            self.assertIn('value=some_value', stg.networkx.nodes['test']['label'])

        def test_scenario_state_graph_add_existing_node(self):
            info = TraceInfo()
            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 1)
            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

            stg._add_node('start')

            self.assertEqual(len(stg.networkx.nodes), 1)
            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

        def test_scenario_state_graph_update_single(self):
            info = TraceInfo()

            scenario = ScenarioInfo('1')

            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            info.update_trace(scenario, space, 1)

            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 2)
            self.assertEqual(len(stg.networkx.edges), 1)

            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

            self.assertIn('1', stg.networkx.nodes['node0']['label'])
            self.assertIn('prop:', stg.networkx.nodes['node0']['label'])
            self.assertIn('value=some_value', stg.networkx.nodes['node0']['label'])

            self.assertIn(('start', 'node0'), stg.networkx.edges)
            self.assertEqual(stg.networkx.edges[('start', 'node0')]['label'], '')

        def test_scenario_state_graph_update_multi_loop(self):
            info = TraceInfo()

            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space1 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            info.update_trace(scenario1, space1, 1)
            info.update_trace(scenario2, space2, 2)
            info.update_trace(scenario1, space1, 3)

            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 3)
            self.assertEqual(len(stg.networkx.edges), 3)

            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

            self.assertIn('1', stg.networkx.nodes['node0']['label'])
            self.assertIn('2', stg.networkx.nodes['node1']['label'])
            self.assertIn('prop:', stg.networkx.nodes['node0']['label'])
            self.assertIn('prop:', stg.networkx.nodes['node1']['label'])
            self.assertIn('value=some_value', stg.networkx.nodes['node0']['label'])
            self.assertIn('value=another_value', stg.networkx.nodes['node1']['label'])

            self.assertIn(('start', 'node0'), stg.networkx.edges)
            self.assertIn(('node0', 'node1'), stg.networkx.edges)
            self.assertIn(('node1', 'node0'), stg.networkx.edges)

            self.assertEqual(stg.networkx.edges[('start', 'node0')]['label'], '')
            self.assertEqual(stg.networkx.edges[('node0', 'node1')]['label'], '')
            self.assertEqual(stg.networkx.edges[('node1', 'node0')]['label'], '')

        def test_scenario_state_graph_update_self_loop(self):
            info = TraceInfo()

            scenario = ScenarioInfo('1')

            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            info.update_trace(scenario, space, 1)
            info.update_trace(scenario, space, 2)

            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 2)
            self.assertEqual(len(stg.networkx.edges), 2)

            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')

            self.assertIn('1', stg.networkx.nodes['node0']['label'])
            self.assertIn('prop:', stg.networkx.nodes['node0']['label'])
            self.assertIn('value=some_value', stg.networkx.nodes['node0']['label'])

            self.assertIn(('start', 'node0'), stg.networkx.edges)
            self.assertIn(('node0', 'node0'), stg.networkx.edges)

            self.assertEqual(stg.networkx.edges[('start', 'node0')]['label'], '')
            self.assertEqual(stg.networkx.edges[('node0', 'node0')]['label'], '')

        def test_scenario_state_graph_update_backtrack(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "more_value")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "yet_another_value")])

            info.update_trace(scenario0, space0, 1)
            info.update_trace(scenario1, space1, 2)
            info.update_trace(scenario2, space2, 3)
            info.update_trace(scenario1, space1, 2)
            info.update_trace(scenario0, space0, 1)
            info.update_trace(scenario2, space3, 2)
            info.update_trace(scenario1, space4, 3)

            stg = ScenarioStateGraph(info)

            self.assertEqual(len(stg.networkx.nodes), 6)
            self.assertEqual(len(stg.networkx.edges), 5)

        def test_scenario_state_graph_final_trace_normal(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            info.update_trace(scenario0, space0, 1)
            info.update_trace(scenario1, space1, 2)
            info.update_trace(scenario2, space2, 3)

            stg = ScenarioStateGraph(info)

            trace = stg.get_final_trace()

            for node in trace:
                self.assertIn(node, stg.networkx.nodes)

            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), stg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node1', 'node2'])

        def test_scenario_state_graph_final_trace_backtrack(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "more_value")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "yet_another_value")])

            info.update_trace(scenario0, space0, 1)
            info.update_trace(scenario1, space1, 2)
            info.update_trace(scenario2, space2, 3)
            info.update_trace(scenario1, space1, 2)
            info.update_trace(scenario0, space0, 1)
            info.update_trace(scenario2, space3, 2)
            info.update_trace(scenario1, space4, 3)

            stg = ScenarioStateGraph(info)

            trace = stg.get_final_trace()

            for node in trace:
                self.assertIn(node, stg.networkx.nodes)

            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), stg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node3', 'node4'])

if __name__ == '__main__':
    unittest.main()
