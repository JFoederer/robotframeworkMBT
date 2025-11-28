import unittest
import networkx as nx
from robotmbt.tracestate import TraceState

try:
    from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
    from robotmbt.visualise.models import TraceInfo, ScenarioInfo, ModelSpace, StateInfo

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseScenarioGraph(unittest.TestCase):
        def test_scenario_state_graph_init(self):
            stg = ScenarioStateGraph()

            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(stg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(len(stg.networkx.nodes), 1)
            self.assertEqual(len(stg.networkx.edges), 0)

        def test_scenario_state_graph_ids_empty(self):
            stg = ScenarioStateGraph()

            si = ScenarioInfo('test')
            node_id = stg._get_or_create_id(si, StateInfo(ModelSpace()))

            self.assertEqual(node_id, 'node0')

        def test_scenario_state_graph_ids_duplicate_scenario(self):
            stg = ScenarioStateGraph()

            si = ScenarioInfo('test')
            sti = StateInfo(ModelSpace())

            id0 = stg._get_or_create_id(si, sti)
            id1 = stg._get_or_create_id(si, sti)

            self.assertEqual(id0, id1)

        def test_scenario_state_graph_ids_different_scenarios(self):
            stg = ScenarioStateGraph()

            si0 = ScenarioInfo('test0')
            si1 = ScenarioInfo('test1')
            sti = StateInfo(ModelSpace())

            id0 = stg._get_or_create_id(si0, sti)
            id1 = stg._get_or_create_id(si1, sti)

            self.assertEqual(id0, 'node0')
            self.assertEqual(id1, 'node1')

        def test_scenario_state_graph_ids_different_states(self):
            stg = ScenarioStateGraph()

            si = ScenarioInfo('test0')
            sti0 = StateInfo(ModelSpace("state0"))
            sti1 = StateInfo(ModelSpace("state1"))

            id0 = stg._get_or_create_id(si, sti0)
            id1 = stg._get_or_create_id(si, sti1)

            self.assertEqual(id0, 'node0')
            self.assertEqual(id1, 'node1')

        def test_scenario_state_graph_add_new_node(self):
            stg = ScenarioStateGraph()

            self.assertIn('start', stg.networkx.nodes)
            self.assertNotIn('test', stg.networkx.nodes)
            self.assertEqual(len(stg.networkx.nodes), 1)

            stg.ids['test'] = (ScenarioInfo('test'), StateInfo(ModelSpace()))
            stg._add_node('test')

            self.assertIn('start', stg.networkx.nodes)
            self.assertIn('test', stg.networkx.nodes)
            self.assertEqual(len(stg.networkx.nodes), 2)
            self.assertEqual(stg.networkx.nodes['test']['label'],
                             ScenarioStateGraph._gen_label(ScenarioInfo('test'), StateInfo(ModelSpace())))

        def test_scenario_state_graph_add_existing_node(self):
            stg = ScenarioStateGraph()
            stg._add_node('start')
            self.assertIn('start', stg.networkx.nodes)
            self.assertEqual(len(stg.networkx.nodes), 1)

        def test_scenario_state_graph_update_visualisation_nodes(self):
            stg = ScenarioStateGraph()

            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
                ti = TraceInfo.from_trace_state(ts, ModelSpace())
                stg.update_visualisation(ti)

            self.assertIn('node0', stg.networkx.nodes)
            self.assertIn('node1', stg.networkx.nodes)
            self.assertIn('node2', stg.networkx.nodes)

            self.assertEqual(stg.networkx.nodes['node0']['label'],
                             ScenarioStateGraph._gen_label(ScenarioInfo(str(0)), StateInfo(ModelSpace())))
            self.assertEqual(stg.networkx.nodes['node1']['label'],
                             ScenarioStateGraph._gen_label(ScenarioInfo(str(1)), StateInfo(ModelSpace())))
            self.assertEqual(stg.networkx.nodes['node2']['label'],
                             ScenarioStateGraph._gen_label(ScenarioInfo(str(2)), StateInfo(ModelSpace())))

        def test_scenario_state_graph_update_visualisation_edges(self):
            stg = ScenarioStateGraph()

            ts = TraceState(3)
            candidates = []
            for scenario in range(3):
                candidates.append(ts.next_candidate())
                ts.confirm_full_scenario(candidates[-1], str(scenario), {})
                ti = TraceInfo.from_trace_state(trace=ts, state=ModelSpace())
                stg.update_visualisation(ti)

            self.assertIn(('node0', 'node1'), stg.networkx.edges)
            self.assertIn(('node1', 'node2'), stg.networkx.edges)

            edge_labels = nx.get_edge_attributes(stg.networkx, "label")
            self.assertEqual(edge_labels[('node0', 'node1')], '')
            self.assertEqual(edge_labels[('node1', 'node2')], '')

        def test_scenario_state_graph_update_visualisation_single_node(self):
            stg = ScenarioStateGraph()

            ti = TraceInfo([ScenarioInfo('one')], ModelSpace())
            stg.update_visualisation(ti)

            # expected behaviour: only start and added node and their edge
            self.assertEqual(len(stg.networkx.nodes), 2)
            self.assertEqual(len(stg.networkx.edges), 1)

        # TODO: improve existing tests and add tests for set_final_trace/get_final_trace, _gen_label

if __name__ == '__main__':
    unittest.main()
