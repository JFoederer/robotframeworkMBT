import unittest

try:
    import networkx as nx
    from robotmbt.visualise.graphs.stategraph import StateGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseAbstractGraph(unittest.TestCase):
        def test_abstract_graph_add_edge_labels_for_state_graph_self_loop(self):
            """
            Testing the case where on an edge "scenario2" occurs twice
            Without the "(rep x)" present
            """
            info = TraceInfo()

            scenario1 = ScenarioInfo('scenario1')
            scenario2 = ScenarioInfo('scenario2')
            scenario3 = ScenarioInfo('scenario3')

            space1 = StateInfo._create_state_with_prop(
                "prop", [("value", "some_value")])

            info.update_trace(scenario1, space1, 1)
            info.update_trace(scenario2, space1, 2)
            info.update_trace(scenario3, space1, 3)
            info.update_trace(scenario2, space1, 4)

            sg = StateGraph(info)
            labels = nx.get_edge_attributes(sg.networkx, 'label')
            self.assertEqual(labels[('node0', 'node0')],
                             'scenario2\nscenario3')

if __name__ == '__main__':
    unittest.main()
