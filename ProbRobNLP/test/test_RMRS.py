import pytest
from ProbRobNLP.RMRS import *


def test_transitive_colsure():
    eq = [('x1', 'x2'), ('x2', 'x3'), ('x4', 'x5')]
    mat, var = build_matrix(eq)
    assert (all([e in eq for e in matrix_to_eq(mat, var)]))
    eq2 = [('x1', 'x2'), ('x2', 'x3'), ('x4', 'x5'), ('x1', 'x3')]
    assert (all([e in eq2 for e in tr(eq)]))


def test_op():
    cat = RMRS(['h1', 'x2'], {}, [EPS('h1', Pred('cat', ['x2']))], set(), set())
    every = RMRS(['h2', 'x3'], {'spec': ['h2', 'x3']}, [EPS('h3', Pred('every', ['x3']))], set(), set())

    every_cat = op(cat, every, 'spec')

    every_cat2 = RMRS(['h2', 'x3'], hole={}, rels=[EPS('h1', Pred('cat', ['x2'])), EPS('h3', Pred('every', ['x3']))],
                      hcons=set(), equalities=[('h1', 'h2'), ('x2', 'x3')])

    assert(every_cat == every_cat2)