import unittest

try:
    from robotmbt.visualise.graphs.stategraph import StateGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseStateGraph(unittest.TestCase):
        def test_state_graph_init(self):
            sg = StateGraph()

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertEqual(len(sg.networkx.edges), 0)

            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_state_graph_ids_empty(self):
            sg = StateGraph()

            si = StateInfo(ModelSpace())

            node_id = sg._get_or_create_id(si)

            self.assertEqual(node_id, 'node0')

        def test_state_graph_ids_duplicate_state(self):
            sg = StateGraph()

            s0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            s1 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            id0 = sg._get_or_create_id(s0)
            id1 = sg._get_or_create_id(s1)

            self.assertEqual(id0, id1)

        def test_state_graph_ids_different_states(self):
            sg = StateGraph()

            s00 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            s01 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            s10 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            s11 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            id00 = sg._get_or_create_id(s00)
            id01 = sg._get_or_create_id(s01)
            id10 = sg._get_or_create_id(s10)
            id11 = sg._get_or_create_id(s11)

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

        def test_state_graph_add_new_node(self):
            sg = StateGraph()

            self.assertEqual(len(sg.networkx.nodes), 1)

            self.assertIn('start', sg.networkx.nodes)
            self.assertNotIn('test', sg.networkx.nodes)

            sg.ids['test'] = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            sg._add_node('test')

            self.assertEqual(len(sg.networkx.nodes), 2)

            self.assertIn('start', sg.networkx.nodes)
            self.assertIn('test', sg.networkx.nodes)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertIn('prop:', sg.networkx.nodes['test']['label'])
            self.assertIn('value=some_value', sg.networkx.nodes['test']['label'])

        def test_state_graph_add_existing_node(self):
            sg = StateGraph()

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

            sg._add_node('start')

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_state_graph_update_single(self):
            sg = StateGraph()

            scenario = ScenarioInfo('1')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            sg.update_visualisation(TraceInfo([scenario], space))

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

            self.assertIn('prop:', sg.networkx.nodes['node0']['label'])
            self.assertIn('value=some_value', sg.networkx.nodes['node0']['label'])

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '1')

        def test_state_graph_update_multi(self):
            sg = StateGraph()

            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')
            scenario3 = ScenarioInfo('3')

            space1 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            ti1 = TraceInfo([scenario1], space1)
            ti2 = TraceInfo([scenario1, scenario2], space2)
            ti3 = TraceInfo([scenario1, scenario2, scenario3], space3)

            sg.update_visualisation(ti1)
            sg.update_visualisation(ti2)
            sg.update_visualisation(ti3)

            self.assertEqual(len(sg.networkx.nodes), 4)
            self.assertEqual(len(sg.networkx.edges), 3)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertIn('prop:', sg.networkx.nodes['node0']['label'])
            self.assertIn('prop:', sg.networkx.nodes['node1']['label'])
            self.assertIn('prop:', sg.networkx.nodes['node2']['label'])
            self.assertIn('value=some_value', sg.networkx.nodes['node0']['label'])
            self.assertIn('value=other_value', sg.networkx.nodes['node1']['label'])
            self.assertIn('value=another_value', sg.networkx.nodes['node2']['label'])

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)

            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '1')
            self.assertEqual(sg.networkx.edges[('node0', 'node1')]['label'], '2')
            self.assertEqual(sg.networkx.edges[('node1', 'node2')]['label'], '3')

        def test_state_graph_update_multi_loop(self):
            sg = StateGraph()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])

            ti1 = TraceInfo([scenario0], space0)
            ti2 = TraceInfo([scenario0, scenario1], space1)
            ti3 = TraceInfo([scenario0, scenario1, scenario2], space0)

            sg.update_visualisation(ti1)
            sg.update_visualisation(ti2)
            sg.update_visualisation(ti3)

            self.assertEqual(len(sg.networkx.nodes), 3)
            self.assertEqual(len(sg.networkx.edges), 3)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertIn('prop:', sg.networkx.nodes['node0']['label'])
            self.assertIn('prop:', sg.networkx.nodes['node1']['label'])
            self.assertIn('value=some_value', sg.networkx.nodes['node0']['label'])
            self.assertIn('value=other_value', sg.networkx.nodes['node1']['label'])

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node0'), sg.networkx.edges)

            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '0')
            self.assertEqual(sg.networkx.edges[('node0', 'node1')]['label'], '1')
            self.assertEqual(sg.networkx.edges[('node1', 'node0')]['label'], '2')

        def test_state_graph_update_self_loop(self):
            sg = StateGraph()

            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])

            ti1 = TraceInfo([scenario1], space)
            ti2 = TraceInfo([scenario1, scenario2], space)

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertEqual(len(sg.networkx.edges), 0)

            sg.update_visualisation(ti1)

            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertEqual(len(sg.networkx.edges), 1)

            sg.update_visualisation(ti2)

            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertEqual(len(sg.networkx.edges), 2)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertIn('prop:', sg.networkx.nodes['node0']['label'])
            self.assertIn('value=some_value', sg.networkx.nodes['node0']['label'])

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node0'), sg.networkx.edges)

            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '1')
            self.assertEqual(sg.networkx.edges[('node0', 'node0')]['label'], '2')

        def test_state_graph_update_backtrack(self):
            sg = StateGraph()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "more_value")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "yet_another_value")])

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertEqual(len(sg.networkx.edges), 0)

            sg.update_visualisation(TraceInfo([scenario0], space0))

            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertEqual(len(sg.networkx.edges), 1)

            sg.update_visualisation(TraceInfo([scenario0, scenario1], space1))

            self.assertEqual(len(sg.networkx.nodes), 3)
            self.assertEqual(len(sg.networkx.edges), 2)

            sg.update_visualisation(TraceInfo([scenario0, scenario1, scenario2], space2))

            self.assertEqual(len(sg.networkx.nodes), 4)
            self.assertEqual(len(sg.networkx.edges), 3)

            sg.update_visualisation(TraceInfo([scenario0, scenario1], space1))

            self.assertEqual(len(sg.networkx.nodes), 4)
            self.assertEqual(len(sg.networkx.edges), 3)

            sg.update_visualisation(TraceInfo([scenario0], space0))

            self.assertEqual(len(sg.networkx.nodes), 4)
            self.assertEqual(len(sg.networkx.edges), 3)

            sg.update_visualisation(TraceInfo([scenario0, scenario2], space3))

            self.assertEqual(len(sg.networkx.nodes), 5)
            self.assertEqual(len(sg.networkx.edges), 4)

            sg.update_visualisation(TraceInfo([scenario0, scenario2, scenario1], space4))

            self.assertEqual(len(sg.networkx.nodes), 6)
            self.assertEqual(len(sg.networkx.edges), 5)

        def test_state_graph_final_trace_normal(self):
            sg = StateGraph()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])

            sg.update_visualisation(TraceInfo([scenario0], space0))
            sg.update_visualisation(TraceInfo([scenario0, scenario1], space1))
            sg.update_visualisation(TraceInfo([scenario0, scenario1, scenario2], space2))

            sg.set_final_trace(TraceInfo([scenario0, scenario1, scenario2], space2))

            trace = sg.get_final_trace()

            for node in trace:
                self.assertIn(node, sg.networkx.nodes)

            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), sg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node1', 'node2'])

        def test_state_graph_final_trace_backtrack(self):
            sg = StateGraph()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            space0 = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            space1 = StateInfo._create_state_with_prop("prop", [("value", "other_value")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "another_value")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "more_value")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "yet_another_value")])

            sg.update_visualisation(TraceInfo([scenario0], space0))
            sg.update_visualisation(TraceInfo([scenario0, scenario1], space1))
            sg.update_visualisation(TraceInfo([scenario0, scenario1, scenario2], space2))
            sg.update_visualisation(TraceInfo([scenario0, scenario1], space1))
            sg.update_visualisation(TraceInfo([scenario0], space0))
            sg.update_visualisation(TraceInfo([scenario0, scenario2], space3))
            sg.update_visualisation(TraceInfo([scenario0, scenario2, scenario1], space4))

            sg.set_final_trace(TraceInfo([scenario0, scenario2, scenario1], space4))

            trace = sg.get_final_trace()

            for node in trace:
                self.assertIn(node, sg.networkx.nodes)

            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), sg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node3', 'node4'])

if __name__ == '__main__':
    unittest.main()
