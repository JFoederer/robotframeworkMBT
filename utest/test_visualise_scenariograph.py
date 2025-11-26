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
            si0 = ScenarioInfo('test0')
            si1 = ScenarioInfo('test1')
            id0 = sg._get_or_create_id(si0)
            id1 = sg._get_or_create_id(si1)
            self.assertEqual(id0, 'node0')
            self.assertEqual(id1, 'node1')

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
            ti = TraceInfo.from_trace_state(trace=ts, state=ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)

            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)

            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
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

        def test_scenario_graph_set_starting_node_new_node(self):
            sg = ScenarioGraph()
            si = ScenarioInfo('test')
            sg._set_starting_node(si)
            node_id = sg._get_or_create_id(si)
            # node
            self.assertIn(node_id, sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes[node_id]['label'], 'test')

            # edge
            self.assertIn(('start', node_id), sg.networkx.edges)
            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', node_id)], '')

        def test_scenario_graph_set_starting_node_existing_node(self):
            sg = ScenarioGraph()
            si = ScenarioInfo('test')
            node_id = sg._get_or_create_id(si)
            sg._add_node(node_id)
            self.assertIn(node_id, sg.networkx.nodes)

            sg._set_starting_node(si)
            self.assertIn(('start', node_id), sg.networkx.edges)
            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', node_id)], '')

        def test_scenario_graph_set_end_node(self):
            sg = ScenarioGraph()
            si = ScenarioInfo('test')
            node_id = sg._get_or_create_id(si)
            sg._set_ending_node(si)
            self.assertEqual(sg.end_node, node_id)

        def test_scenario_graph_set_final_trace(self):
            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
            ti = TraceInfo.from_trace_state(trace=ts, state=ModelSpace())
            sg = ScenarioGraph()
            sg.update_visualisation(ti)
            sg.set_final_trace(ti)
            # test start node
            self.assertIn(('start', 'node0'), sg.networkx.edges)
            # test end node
            self.assertEqual(sg.end_node, 'node2')

if __name__ == '__main__':
    unittest.main()
