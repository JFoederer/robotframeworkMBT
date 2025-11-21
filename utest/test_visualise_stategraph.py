import unittest
import networkx as nx
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
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')


if __name__ == '__main__':
    unittest.main()
