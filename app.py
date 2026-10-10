import json,math,argparse
from statistics import mean

def normalize(text): return ' '.join(text.lower().split())
def evaluate(cases,predictions):
    if not cases: raise ValueError('Empty evaluation set')
    by_id={p['id']:p for p in predictions}
    if len(by_id)!=len(predictions):raise ValueError('Duplicate predictions')
    ids=[c['id'] for c in cases]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate cases')
    if set(by_id)-set(ids):raise ValueError('Unknown prediction IDs')
    rows=[]
    for c in cases:
        p=by_id.get(c['id'])
        if p is None:
            rows.append(dict(id=c['id'],correct=False,citations_valid=False,missing=True,latency_ms=None));continue
        latency=float(p['latency_ms'])
        if latency<0 or not math.isfinite(latency):raise ValueError('Invalid latency')
        cited=set(p.get('citations',[]));allowed=set(c.get('allowed_citations',[]))
        rows.append(dict(id=c['id'],correct=normalize(p['answer']) in {normalize(a) for a in c['answers']},citations_valid=bool(cited) and cited<=allowed,missing=False,latency_ms=latency))
    latencies=sorted(r['latency_ms'] for r in rows if r['latency_ms'] is not None)
    metrics={'accuracy':mean(r['correct'] for r in rows),'citation_validity':mean(r['citations_valid'] for r in rows),'coverage':mean(not r['missing'] for r in rows),'p95_latency_ms':latencies[math.ceil(.95*len(latencies))-1] if latencies else None,'n':len(rows)}
    passed=metrics['accuracy']>=.9 and metrics['citation_validity']>=.95 and metrics['coverage']==1 and metrics['p95_latency_ms']<=1500
    return dict(metrics=metrics,release_gate='pass' if passed else 'fail',rows=rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cases');parser.add_argument('--predictions');parser.add_argument('--enforce',action='store_true');args=parser.parse_args()
    if bool(args.cases)!=bool(args.predictions):parser.error('Supply both input files')
    cases=json.load(open(args.cases)) if args.cases else [dict(id='return',answers=['30 days'],allowed_citations=['policy'])]
    preds=json.load(open(args.predictions)) if args.predictions else [dict(id='return',answer='30 days',citations=['policy'],latency_ms=120)]
    result=evaluate(cases,preds);print(json.dumps(result,indent=2))
    if args.enforce and result['release_gate']!='pass':raise SystemExit(1)
