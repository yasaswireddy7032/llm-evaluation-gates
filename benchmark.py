"""Paired experiment comparison with bootstrap intervals and slice-level regressions."""
import argparse,hashlib,json,math,random,statistics
from app import normalize

def interval(values,seed=42,repetitions=2000):
    if not values:raise ValueError('Cannot bootstrap empty sample')
    rng=random.Random(seed);n=len(values)
    samples=sorted(statistics.mean(rng.choices(values,k=n)) for _ in range(repetitions))
    return [samples[int(.025*repetitions)],samples[min(repetitions-1,int(.975*repetitions))]]

def score(case,pred):
    latency=float(pred['latency_ms']);cost=float(pred['cost_usd'])
    if not math.isfinite(latency) or latency<0 or not math.isfinite(cost) or cost<0:raise ValueError('Nonnegative finite latency and cost required')
    citations=set(pred.get('citations',[]));allowed=set(case.get('allowed_citations',[]))
    refused=pred.get('abstained',False)
    should_refuse=case.get('should_abstain',False)
    correct=refused if should_refuse else (not refused and normalize(pred['answer']) in {normalize(x) for x in case['answers']})
    grounded=(not citations) if should_refuse else (bool(citations) and citations<=allowed)
    return dict(correct=int(correct),grounded=int(grounded),latency=latency,cost=cost)

def compare(cases,baseline,candidate):
    if not cases:raise ValueError('Cases required')
    ids=[c['id'] for c in cases]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate case IDs')
    def index(rows):
        out={r['id']:r for r in rows}
        if len(out)!=len(rows) or set(out)!=set(ids):raise ValueError('Exactly one prediction required for each case')
        return out
    a=index(baseline);b=index(candidate);rows=[]
    for case in cases:
        rows.append({'id':case['id'],'slice':case['slice'],'baseline':score(case,a[case['id']]),'candidate':score(case,b[case['id']])})
    differences=[r['candidate']['correct']-r['baseline']['correct'] for r in rows]
    slices={}
    for group in sorted({r['slice'] for r in rows}):
        part=[r for r in rows if r['slice']==group]
        slices[group]={'n':len(part),'baseline_accuracy':statistics.mean(r['baseline']['correct'] for r in part),'candidate_accuracy':statistics.mean(r['candidate']['correct'] for r in part)}
    def metrics(key):
        latencies=sorted(r[key]['latency'] for r in rows)
        return {'accuracy':statistics.mean(r[key]['correct'] for r in rows),'citation_rule_pass_rate':statistics.mean(r[key]['grounded'] for r in rows),'p95_latency_ms':latencies[math.ceil(.95*len(rows))-1],'mean_cost_usd':statistics.mean(r[key]['cost'] for r in rows)}
    ma,mb=metrics('baseline'),metrics('candidate');failures=[]
    if mb['accuracy']<ma['accuracy']:failures.append('aggregate accuracy regression')
    if mb['citation_rule_pass_rate']<.95:failures.append('citation rule below 95%')
    if mb['p95_latency_ms']>1500:failures.append('latency budget exceeded')
    if mb['mean_cost_usd']>.01:failures.append('cost budget exceeded')
    for group,values in slices.items():
        if values['candidate_accuracy']<values['baseline_accuracy']:failures.append(f'slice regression: {group}')
    return {'dataset_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),'n':len(rows),'baseline':ma,'candidate':mb,'paired_accuracy_delta':statistics.mean(differences),'bootstrap_95_interval':interval(differences),'slices':slices,'release_gate':'fail' if failures else 'pass','failures':failures,'method':'paired percentile bootstrap; illustrative small synthetic benchmark, not significance proof'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',default='cases.json');p.add_argument('--baseline',default='baseline.json');p.add_argument('--candidate',default='candidate.json');p.add_argument('--enforce',action='store_true');a=p.parse_args()
    result=compare(json.load(open(a.cases)),json.load(open(a.baseline)),json.load(open(a.candidate)));print(json.dumps(result,indent=2))
    if a.enforce and result['release_gate']=='fail':raise SystemExit(1)
