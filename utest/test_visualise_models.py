import unittest
import networkx as nx
from robotmbt.tracestate import TraceState
from robotmbt.visualise.models import *


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
    Class: TraceInfo
    """

    def test_create_TraceInfo(self):
        ts = TraceState(3)
        candidates = []
        for scenario in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        ti = TraceInfo(trace=ts, state=None)

        self.assertEqual(ti.trace[0].name, 0)
        self.assertEqual(ti.trace[1].name, 1)
        self.assertEqual(ti.trace[2].name, 2)

        # TODO change when state is implemented
        self.assertIsNone(ti.state)

    """
    Class: ScenarioGraph
    """

    def test_scenario_graph_init(self):
        sg = ScenarioGraph()
        self.assertIn('start', sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

    def test_scenario_graph_ids_empty(self):
        sg = ScenarioGraph()
        si = ScenarioInfo('test')
        id = sg._get_or_create_id(si)
        self.assertEqual(id, 'node0')

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
        sg.add_node('test')
        self.assertIn('test', sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes['test']['label'], 'test')

    def test_scenario_graph_add_existing_node(self):
        sg = ScenarioGraph()
        sg.add_node('start')
        self.assertIn('start', sg.networkx.nodes)
        self.assertEqual(len(sg.networkx.nodes), 1)

    def test_scenario_graph_update_visualisation_nodes(self):
        ts = TraceState(3)
        candidates = []
        for scenario in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        ti = TraceInfo(trace=ts, state=None)
        sg = ScenarioGraph()
        sg.update_visualisation(ti)

        self.assertIn('node0', sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes['node0']['label'], 0)
        self.assertIn('node1', sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes['node1']['label'], 1)
        self.assertIn('node2', sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes['node2']['label'], 2)

    def test_scenario_graph_update_visualisation_edges(self):
        ts = TraceState(3)
        candidates = []
        for scenario in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        ti = TraceInfo(trace=ts, state=None)
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
        ti = TraceInfo(trace=ts, state=None)
        sg = ScenarioGraph()
        sg.update_visualisation(ti)

        # expected behaviour: no nodes nor edges are added
        self.assertEqual(len(sg.networkx.nodes), 1)
        self.assertEqual(len(sg.networkx.edges), 0)

    def test_scenario_graph_set_starting_node_new_node(self):
        sg = ScenarioGraph()
        si = ScenarioInfo('test')
        sg.set_starting_node(si)
        id = sg._get_or_create_id(si)
        # node
        self.assertIn(id, sg.networkx.nodes)
        self.assertEqual(sg.networkx.nodes[id]['label'], 'test')

        # edge
        self.assertIn(('start', id), sg.networkx.edges)
        edge_labels = nx.get_edge_attributes(sg.networkx, "label")
        self.assertEqual(edge_labels[('start', id)], '')

    def test_scenario_graph_set_starting_node_existing_node(self):
        sg = ScenarioGraph()
        si = ScenarioInfo('test')
        id = sg._get_or_create_id(si)
        sg.add_node(id)
        self.assertIn(id, sg.networkx.nodes)

        sg.set_starting_node(si)
        self.assertIn(('start', id), sg.networkx.edges)
        edge_labels = nx.get_edge_attributes(sg.networkx, "label")
        self.assertEqual(edge_labels[('start', id)], '')

    def test_scenario_graph_set_end_node(self):
        sg = ScenarioGraph()
        si = ScenarioInfo('test')
        id = sg._get_or_create_id(si)
        sg.set_ending_node(si)
        self.assertEqual(sg.end_node, id)


if __name__ == '__main__':
    unittest.main()
