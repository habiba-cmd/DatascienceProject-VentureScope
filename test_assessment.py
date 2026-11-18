from src.assessment import market_score,founder_invariance_test,readiness,sensitivity

def test_insufficient_evidence():
    d={'market_demand':80,'customer_problem':None,'competition':60,'product_fit':None,'accessibility':None}
    c={k:1 for k in d}
    assert market_score(d,c)['score'] is None

def test_full_evidence():
    d={k:60 for k in ['market_demand','customer_problem','competition','product_fit','accessibility']}
    c={k:1 for k in d}
    assert abs(market_score(d,c)['score']-60)<1e-9
    assert founder_invariance_test(d,c)
    assert sensitivity(d,c,n=100)['draws']==100
