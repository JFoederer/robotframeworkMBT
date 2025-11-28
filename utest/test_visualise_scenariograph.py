import unittest
import networkx as nx
from robotmbt.tracestate import TraceState

try:
    from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
    from robotmbt.visualise.models import TraceInfo, ScenarioInfo, ModelSpace

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseScenarioGraph(unittest.TestCase):
        def test_scenario_graph_init(self):
            sg = ScenarioGraph()
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_scenario_graph_ids_empty(self):
            sg = ScenarioGraph()
            si = ScenarioInfo('test')
            node_id = sg._get_or_create_id(si)
            self.assertEqual(node_id, 'node0')

        def test_scenario_graph_ids_duplicate_scenario(self):
            sg = ScenarioGraph()
            si = ScenarioInfo('test')
            id0 = sg._get_or_create_id(si)
            id1 = sg._get_or_create_id(si)
            self.assertEqual(id0, id1)

        def test_scenario_graph_ids_different_scenarios(self):
            sg = ScenarioGraph()
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
            sg = ScenarioGraph()
            sg.ids['test'] = ScenarioInfo('test')
            sg._add_node('test')
            self.assertIn('test', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['test']['label'], 'test')

        def test_scenario_graph_add_existing_node(self):
            sg = ScenarioGraph()
            sg._add_node('start')
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(len(sg.networkx.nodes), 1)

        def test_scenario_graph_update_visualisation_nodes(self):
            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
            ti = TraceInfo.from_trace_state(ts, ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)

            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertIn('node0', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['node0']['label'], str(0))
            self.assertIn('node1', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['node1']['label'], str(1))
            self.assertIn('node2', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['node2']['label'], str(2))

        def test_scenario_graph_update_visualisation_edges(self):
            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
            ti = TraceInfo.from_trace_state(ts, ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)

            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', 'node0')], '')
            self.assertEqual(edge_labels[('node0', 'node1')], '')
            self.assertEqual(edge_labels[('node1', 'node2')], '')

        def test_scenario_graph_update_visualisation_single_node(self):
            ts = TraceState(1)
            ts.confirm_full_scenario(0, 'one', {})
            self.assertEqual(ts.get_trace(), ['one'])
            ti = TraceInfo.from_trace_state(ts, ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)

            # expected behaviour: no nodes nor edges are added
            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertEqual(len(sg.networkx.edges), 0)

        def test_scenario_graph_get_final_trace(self):
            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
            ti = TraceInfo.from_trace_state(ts, ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)
            sg.set_final_trace(ti)
            trace = sg.get_final_trace()
            # confirm they are proper ids
            for node in trace:
                self.assertIn(node, sg.networkx.nodes)
            # confirm the edges exist
            for i in range(0, len(trace) - 1):
                self.assertIn((trace[i], trace[i + 1]), sg.networkx.edges)

if __name__ == '__main__':
    unittest.main()
