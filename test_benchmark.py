import unittest
from benchmark import compare,interval
class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.c=[dict(id='a',slice='retrieval',answers=['yes'],allowed_citations=['doc'])]
        self.p=[dict(id='a',answer='yes',citations=['doc'],latency_ms=100,cost_usd=.001)]
    def test_identity(self):self.assertEqual(compare(self.c,self.p,self.p)['paired_accuracy_delta'],0)
    def test_missing_rejected(self):
        with self.assertRaises(ValueError):compare(self.c,self.p,[])
    def test_regression(self):
        bad=[dict(self.p[0],answer='no')];self.assertEqual(compare(self.c,self.p,bad)['release_gate'],'fail')
    def test_cost_gate(self):self.assertIn('cost budget exceeded',compare(self.c,self.p,[dict(self.p[0],cost_usd=.1)])['failures'])
    def test_refusal(self):
        c=[dict(self.c[0],should_abstain=True)];p=[dict(self.p[0],abstained=True,citations=[])];self.assertEqual(compare(c,p,p)['candidate']['accuracy'],1)
    def test_bootstrap_reproducible(self):self.assertEqual(interval([0,1,-1]),interval([0,1,-1]))
    def test_dataset_fingerprint(self):self.assertEqual(len(compare(self.c,self.p,self.p)['dataset_sha256']),64)
if __name__=='__main__':unittest.main()
