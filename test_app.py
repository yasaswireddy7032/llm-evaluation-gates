import unittest
from app import *

class EvaluationTests(unittest.TestCase):
    def setUp(self):self.c=[dict(id='a',answers=['yes'],allowed_citations=['x'])]
    def test_missing_fails(self):self.assertEqual(evaluate(self.c,[])['release_gate'],'fail')
    def test_fabricated_citation(self):self.assertFalse(evaluate(self.c,[dict(id='a',answer='yes',citations=['fake'],latency_ms=1)])['rows'][0]['citations_valid'])
    def test_normalization(self):self.assertEqual(evaluate(self.c,[dict(id='a',answer=' YES ',citations=['x'],latency_ms=1)])['release_gate'],'pass')
    def test_invalid_latency(self):
        with self.assertRaises(ValueError):evaluate(self.c,[dict(id='a',answer='yes',latency_ms=float('nan'))])
    def test_duplicate_case(self):
        with self.assertRaises(ValueError):evaluate(self.c*2,[])

if __name__ == '__main__': unittest.main()
