import unittest

try:
    from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseScenarioGraph(unittest.TestCase):
        def test_scenario_graph_init(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertEqual(len(sg.networkx.edges), 0)

            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_scenario_graph_ids_empty(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            s = ScenarioInfo('test')

            node_id = sg._get_or_create_id(s)

            self.assertEqual(node_id, 'node0')

        def test_scenario_graph_ids_duplicate_scenario(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            s0 = ScenarioInfo('test')
            s1 = ScenarioInfo('test')

            id0 = sg._get_or_create_id(s0)
            id1 = sg._get_or_create_id(s1)

            self.assertEqual(id0, id1)

        def test_scenario_graph_ids_different_scenarios(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            si00 = ScenarioInfo('test0')
            si01 = ScenarioInfo('test0')
            si10 = ScenarioInfo('test1')
            si11 = ScenarioInfo('test1')

            id00 = sg._get_or_create_id(si00)
            id01 = sg._get_or_create_id(si01)
            id10 = sg._get_or_create_id(si10)
            id11 = sg._get_or_create_id(si11)

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

        def test_scenario_graph_add_new_node(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            sg.ids['test'] = ScenarioInfo('test')
            sg._add_node('test')

            self.assertEqual(len(sg.networkx.nodes), 2)

            self.assertIn('start', sg.networkx.nodes)
            self.assertIn('test', sg.networkx.nodes)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['test']['label'], 'test')

        def test_scenario_graph_add_existing_node(self):
            info = TraceInfo()
            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

            sg._add_node('start')

            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_scenario_graph_update_nodes(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 3)

            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.nodes), 4)

            self.assertIn('start', sg.networkx.nodes)
            self.assertIn('node0', sg.networkx.nodes)
            self.assertIn('node1', sg.networkx.nodes)
            self.assertIn('node2', sg.networkx.nodes)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['node0']['label'], '0')
            self.assertEqual(sg.networkx.nodes['node1']['label'], '1')
            self.assertEqual(sg.networkx.nodes['node2']['label'], '2')

        def test_scenario_graph_update_edges(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 3)

            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.edges), 3)

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)

            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '')
            self.assertEqual(sg.networkx.edges[('node0', 'node1')]['label'], '')
            self.assertEqual(sg.networkx.edges[('node1', 'node2')]['label'], '')

        def test_scenario_graph_update_single_node(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('test')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)

            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertEqual(len(sg.networkx.edges), 1)

            self.assertIn('start', sg.networkx.nodes)
            self.assertIn('node0', sg.networkx.nodes)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['node0']['label'], 'test')

            self.assertIn(('start', 'node0'), sg.networkx.edges)

            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '')

        def test_scenario_graph_update_backtrack(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')
            scenario3 = ScenarioInfo('3')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 3)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario3, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 3)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 4)

            sg = ScenarioGraph(info)

            self.assertEqual(len(sg.networkx.nodes), 5)
            self.assertEqual(len(sg.networkx.edges), 5)

        def test_scenario_graph_final_trace_normal(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 3)

            sg = ScenarioGraph(info)

            trace = sg.get_final_trace()

            # confirm they are proper ids
            for node in trace:
                self.assertIn(node, sg.networkx.nodes)

            # confirm the edges exist
            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), sg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node1', 'node2'])

        def test_scenario_graph_final_trace_backtrack(self):
            info = TraceInfo()

            scenario0 = ScenarioInfo('0')
            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')

            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 3)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario0, StateInfo(ModelSpace()), 1)
            info.update_trace(scenario2, StateInfo(ModelSpace()), 2)
            info.update_trace(scenario1, StateInfo(ModelSpace()), 3)

            sg = ScenarioGraph(info)

            trace = sg.get_final_trace()

            # confirm they are proper ids
            for node in trace:
                self.assertIn(node, sg.networkx.nodes)

            # confirm the edges exist
            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), sg.networkx.edges)

            self.assertEqual(trace, ['start', 'node0', 'node2', 'node1'])

if __name__ == '__main__':
    unittest.main()
