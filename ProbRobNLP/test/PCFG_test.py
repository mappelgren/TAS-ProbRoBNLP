import pytest
from ProbRobNLP.PCFG import *



def test_terminal_eq():
    t1 = Terminal('a')
    t2 = Terminal('b')
    t3 = Terminal('a')

    assert(t1 == t3)
    assert(t2 != t1)
    assert(t3 != t2)


def test_non_terminal_eq():
    n1 = NonTerminal('VB')
    n2 = NonTerminal('NN')
    n3 = NonTerminal('VB')

    assert(n1 == n3)
    assert(n1 != n2)
    assert(n3 != n2)


def test_rule_eq():
    a1 = Terminal('a')
    b = Terminal('b')
    a2 = Terminal('a')

    vb1 = NonTerminal('VB')
    nn = NonTerminal('NN')
    vb2 = NonTerminal('VB')

    r1 = Rule(vb1, [a1, b], 0.5)
    r2 = Rule(vb2, [a2, b], 0.5)
    r3 = Rule(vb1, [a1, b], 1.0)
    r4 = Rule(nn, [a1, b], 0.5)
    r5 = Rule(vb1, [a1, a2], 0.5)

    assert(r1 == r2)
    assert(r1 != r3)
    assert(r1 != r4)
    assert(r1 != r5)




@pytest.fixture
def word_grammar_setup():

    put = Terminal('put')
    a = Terminal('a')
    cup = Terminal('cup')
    on = Terminal('on')
    the = Terminal('the')
    table = Terminal('table')

    VB = NonTerminal('VB')
    DT = NonTerminal('DT')
    IN = NonTerminal('IN')
    NN = NonTerminal('NN')
    NP = NonTerminal('NP')
    S = NonTerminal('S')
    NPP = NonTerminal("NPP")
    PP = NonTerminal('PP')

    rules1 = [Rule(VB, [put], 1.0),
               Rule(DT, [a], 0.1),
               Rule(NN, [cup], 0.5),
               Rule(DT, [the], 0.7),
               Rule(IN, [on], 1),
               Rule(NN, [table], 0.5),
               Rule(S, [put, NPP], 1.0),
               Rule(NPP, [NP, IN, NP], 1.0),
               Rule(NP, [DT, NN], 1.0)]

    return (rules1, S)


@pytest.fixture
def a_terminals():

    a = Terminal('a')
    b = Terminal('b')
    A = NonTerminal('A')
    B = NonTerminal('B')
    S = NonTerminal('S')

    return a, b, A, B, S


@pytest.fixture
def ASB_grammar(a_terminals):

    a, b, A, B, S = a_terminals

    rules = [Rule(S, [A, S, B], 1),
                Rule(A, [a, A, S], 0.3),
                Rule(A, [a], 0.2),
                Rule(A, [], 0.5),
                Rule(B, [S, B, S], 0.1),
                Rule(B, [A], 0.6),
                Rule(B, [b, b], 0.3)]

    return (rules, S)


@pytest.fixture
def aab_grammar(a_terminals):
    a, b, A, B, S = a_terminals

    rules = [Rule(S, [A, B, B], 0.7),
             Rule(S, [B, B], 0.3),
             Rule(B, [b], 1),
             Rule(A, [a], 1)]

    NR0 = NonTerminal('NR0')

    rules2 = [Rule(NR0, [A, B], 1),
              Rule(S, [NR0, B], 0.7),
              Rule(S, [B, B], 0.3),
              Rule(B, [b], 1),
              Rule(A, [a], 1)]

    return (rules, S), (rules2, S)


def test_ba_grammar(a_terminals):
    a, b, A, B, S = a_terminals

    rules = [Rule(S, [B, A], 1), Rule(A, [a], 0.7), Rule(A, [], 0.3), Rule(B, [b], 1)]

    rules2 = [Rule(S, [B, A], 0.7), Rule(S, [b], 0.3), Rule(B, [b], 1.0), Rule(A, [a], 1.0)]

    g1 = (rules, S)
    g2 = (rules2, S)

    cnf_g1 = to_cnf(g1)

    assert(grammar_eq(cnf_g1, g2))


def test_grammar_eq(aab_grammar):
    g1, g2 = aab_grammar

    assert(grammar_eq(g1, g1))
    assert(not(grammar_eq(g1, g2)))


def test_aab(aab_grammar):
    g1, g2 = aab_grammar

    cnf_g1 = to_cnf(g1)

    assert(grammar_eq(g2, cnf_g1))


def test_parse(word_grammar_setup):
    rules, s  = word_grammar_setup
    pcfg3 = PCFG(rules, s)
    final_cell, full_trace = pcfg3.parse("put a cup on the table")

    assert(any([s == trace.T for trace in final_cell]))
# g5 = [rules5, S]
# print("grammar5 start")
# display_grammar(g5)
# print("grammar5 end")
# display_grammar(to_cnf(g5))