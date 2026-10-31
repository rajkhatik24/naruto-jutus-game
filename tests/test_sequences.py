from src.sequence_engine import SequenceEngine
from src.temporal import TemporalFilter
J=[{'id':'chidori','signs':['ox','hare','monkey']}]
def test_activation():
    e=SequenceEngine(J)
    assert e.accept('ox',0).status=='progress'
    assert e.accept('hare',1).status=='progress'
    assert e.accept('monkey',2).jutsu['id']=='chidori'
    assert e.signs==[]
def test_wrong_order():
    e=SequenceEngine(J)
    assert e.accept('monkey',0).status=='incorrect'
    assert e.accept('ox',1).status=='progress'
    assert e.accept('monkey',2).status=='incorrect'
def test_timeout():
    e=SequenceEngine(J,timeout=2)
    e.accept('ox',0)
    assert e.expire(3)
    assert not e.signs
def test_recover():
    e=SequenceEngine(J)
    e.accept('ox',0);e.accept('ox',1)
    assert e.signs==['ox']
def test_neutral_debounce():
    f=TemporalFilter(3,2)
    assert [f.feed('ox') for _ in range(3)] == [None,None,'ox']
    assert [f.feed('hare') for _ in range(4)] == [None]*4
    f.feed(None);f.feed(None)
    assert [f.feed('hare') for _ in range(3)] == [None,None,'hare']
def test_shared_prefix():
    e=SequenceEngine(J+[{'id':'longer','signs':['ox','hare','monkey','rat']}])
    e.accept('ox',0);e.accept('hare',1)
    assert e.accept('monkey',2).status=='progress'
    assert e.accept('rat',3).jutsu['id']=='longer'
