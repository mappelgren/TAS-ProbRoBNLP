from collections import defaultdict, namedtuple
from itertools import product

TraceCell = namedtuple('TraceCell', ['T', 'text', 'p'])


class NonTerminal:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Terminal:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class PCFG:

    def __init__(self, rules: list = None, start_symbol: NonTerminal = None):

        rules, start_symbol = to_cnf([rules, start_symbol])

        self.lexicon = defaultdict(list)
        self.rules = []
        for rule in rules:
            if isinstance(rule.RHS[0], Terminal):
                self.lexicon[rule.RHS[0].name].append((rule.LHS, rule.p))
            else:
                self.rules.append(rule)

        self.start_symbol = start_symbol

    def parse(self, sentence):

        words = sentence.split()

        trace = defaultdict(list)
        n = len(words) + 1

        for i in range(1, n):
            word = words[i - 1]
            trace[(i - 1, i)] = [TraceCell(term, word, p) for (term, p) in self.lexicon[word]]

        print(trace)
        for j in range(2, n):
            for i in range(j - 1, -1, -1):
                for k in range(i + 1, j):
                    for c1, c2 in product(trace[(i, k)], trace[(k, j)]):

                        for c3, p in self.use_rules(c1.T, c2.T):
                            trace[(i, j)].append(TraceCell(c3, f"{c1[1]} {c2[1]}", p * c1.p * c2.p))

        return trace[(0, n - 1)], trace

    def use_rules(self, c1, c2):
        for rule in self.rules:
            left, right = rule.RHS
            parent = rule.LHS

            if left == c1 and right == c2:
                yield parent, rule.p  # f"{sem[app_order[0]]}({sem[app_order[1]]})")

    def __eq__(self, other):

        r1, s1 = self.rules, self.start_symbol
        r2, s2 = other.rules, other.start_symbol

        s_eq = s1 == s2

        len_r_eq = len(r1) == len(r2)

        all_r_eq = all([r in r2 for r in r1])

        return s_eq and len_r_eq and all_r_eq

    def display(self):
        rules, s = self.rules, self.start_symbol

        grammar = defaultdict(list)

        for rule in rules:
            grammar[rule.LHS].append((rule.RHS, rule.p))

        lines = []
        for key, value in grammar.items():
            lines.append(f"{key} <- {' | '.join([' '.join([str(a) for a in t]) + f' ({p})' for t, p in value])}")
        return '\n'.join(lines)

    def __repr__(self):
        return self.display()

    def print(self):
        print(self.display)

class Rule:

    def __init__(self, LHS, RHS, p=1):
        self.LHS = LHS
        self.RHS = RHS
        self.p = p

    def __repr__(self):
        return f"{self.LHS} <- {' '.join([str(t) for t in self.RHS])} ({self.p})"

    def __eq__(self, other):
        return (self.LHS == other.LHS and all([r1 == r2 for r1, r2 in zip(self.RHS, other.RHS)])
                and len(self.RHS) == len(other.RHS) and self.p == other.p
                )


def normalise_rule(grammar, lhs):
    rules, s = grammar

    to_normalise = [r for r in rules if r.LHS == lhs]
    p_norm = sum([r.p for r in to_normalise])
    if p_norm == 1:
        return grammar
    else:
        new_rules = [Rule(r.LHS, r.RHS, r.p / p_norm) for r in to_normalise]

    rules = [r for r in rules if r not in to_normalise] + new_rules
    return (rules, s)


def to_cnf(grammar):
    added_rule_nr = 0

    rule_variable_name = 'NR'

    rules, s = grammar
    start = s

    for rule in rules:
        lhs = rule.LHS
        rhs = rule.RHS
        if start in rhs:
            s0 = NonTerminal(start.name + "0")
            rules.insert(0, Rule(s0, [start]))
            start = s0

    change = True

    while change:
        change = False
        for rule in rules:
            lhs = rule.LHS
            rhs = rule.RHS
            if rhs == []:
                #                 if lhs == start:
                #                     continue
                change = True
                new_rules = []
                for rule2 in rules:
                    if rule != rule2:
                        if lhs in rule2.RHS:
                            p = rule.p * rule2.p
                            p2 = (1 - rule.p) * rule2.p
                            new_rules.append(Rule(rule2.LHS, [t for t in rule2.RHS if t != lhs], p))
                            rule2 = Rule(rule2.LHS, rule2.RHS, p2)
                        new_rules.append(rule2)

                rules, s = normalise_rule((new_rules, s), lhs)

            if len(rhs) == 1 and lhs == rhs[0]:
                change = True
                new_rules = [r for r in rules if r != rule]
                rules = new_rules
                rules, s = normalise_rule((rules, s), rule.LHS)

    change = True

    guf = []

    while change:
        change = False
        to_remove = []
        for rule in rules:
            lhs = rule.LHS
            rhs = rule.RHS

            if len(rhs) == 1 and isinstance(rhs[0], NonTerminal):

                to_remove.append(rule)
            else:
                guf.append(rule)

        for rule in to_remove:
            change = True
            lhs = rule.LHS
            rhs = rule.RHS[0]

            rhsides = [(r.RHS, r.p) for r in rules if r.LHS == rhs]

            for (r, p) in rhsides:
                guf.append(Rule(lhs, r, rule.p * p))

        removals = [r.LHS for r in guf if r.RHS[0] == r.LHS and len(r.RHS) == 1]
        guf = [r for r in guf if not (r.RHS[0] == r.LHS and len(r.RHS) == 1)]

        for l in removals:
            guf, s = normalise_rule((guf, s), l)

        rules = guf
        guf = []

    rules, start = remove_non_reachable_state([rules, start])

    new_terminal_rules = {}

    new_rules = []
    for rule in rules:
        lhs = rule.LHS
        rhs = rule.RHS

        if len(rhs) > 1 and any([isinstance(t, Terminal) for t in rhs]):
            new_rhs = []
            for t in rhs:
                if isinstance(t, Terminal):
                    if t not in new_terminal_rules:
                        l = NonTerminal(rule_variable_name + str(added_rule_nr))
                        added_rule_nr += 1
                        r = Rule(l, [t], 1)
                        new_rules.append(r)
                        new_terminal_rules[t] = l

                    new_rhs.append(new_terminal_rules[t])
                else:
                    new_rhs.append(t)
            new_rules.append(Rule(lhs, new_rhs, rule.p))
        else:
            new_rules.append(rule)

    rules = new_rules
    new_rules = []
    change = True
    while change:
        change = False
        for rule in rules:
            if len(rule.RHS) > 2:
                change = True

                l = NonTerminal(rule_variable_name + str(added_rule_nr))
                added_rule_nr += 1

                lhs = rule.LHS
                rhs1 = rule.RHS[:2]
                rhs2 = [l] + rule.RHS[2:]

                new_rules.append(Rule(l, rhs1, 1))
                new_rules.append(Rule(lhs, rhs2, rule.p))

            else:
                new_rules.append(rule)

        rules = new_rules
        new_rules = []

    return [rules, start]


def reachable_states(grammar):
    rules, s = grammar

    reached_states = []

    search(rules, s, reached_states)

    return reached_states


def search(rules, s, reached_states):
    reached_states.append(s)

    relevant_rules = [r for r in rules if r.LHS == s]

    for r in relevant_rules:
        nodes = next_nodes(r, reached_states)

        for node in nodes:
            search(rules, node, reached_states)


def next_nodes(rule, reached_states):
    return [t for t in rule.RHS if isinstance(t, NonTerminal) and t not in reached_states]


def remove_non_reachable_state(g):
    rs = reachable_states(g)

    rules, s = g
    rules = [r for r in rules if r.LHS in rs]

    return (rules, s)




def grammar_eq(g1, g2):

    r1, s1 = g1
    r2, s2 = g2

    s_eq = s1 == s2

    len_r_eq = len(r1) == len(r2)

    all_r_eq = all([r in r2 for r in r1])

    return s_eq and len_r_eq and all_r_eq
