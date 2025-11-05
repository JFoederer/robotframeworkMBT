import unittest
from robotmbt.tracestate import TraceState
from robotmbt.visualise.models import *


class TestVisualiseModels(unittest.TestCase):
    def test_create_TraceInfo(self):
        ts = TraceState(3)
        candidates = []
        for scenario in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        ti = TraceInfo(trace=ts, state=None)

        self.assertEqual(0, ti.trace[0].name)
        self.assertEqual(1, ti.trace[1].name)
        self.assertEqual(2, ti.trace[2].name)

        # TODO change when state is implemented
        self.assertIsNone(ti.state)
