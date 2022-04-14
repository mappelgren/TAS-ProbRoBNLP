import copy


class DefiniteClause:

    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __repr__(self):
        return f"{self.head} <- {', '.join(map(str, self.body))}"

    def substitution(self, theta):
        new_head = self.head.substitution(theta)
        new_body = [atom.substitution(theta) for atom in self.body]

        return DefiniteClause(new_head, new_body)

    def is_ground(self):
        return self.head.is_ground() and all([atom.is_ground() for atom in self.body])

    def get_possible_substitutions(self, atoms):
        body = copy.deepcopy(self.body)
        outputs = _body_recursion(atoms, body, {})
        # print(outputs)
        return outputs

    def get_consequences(self, atoms):
        for substitution in self.get_possible_substitutions(atoms):
            # print(substitution)
            update = self.substitution(substitution).head
            # print(update)
            yield update


def _body_recursion(atoms, stack, substitution):
    # print('body_recursion w', atoms, stack, substitution)
    if len(stack) == 0:
        # print('returning', substitution)
        return [substitution]
    else:
        next_body = stack.pop()
        next_body = next_body.substitution(substitution)
        # print('next body:', next_body)
        candidates = [atom for atom in atoms if atom.pred == next_body.pred]
        # print('candidates', candidates)
        output = []
        for candidate in candidates:
            # print('processing', candidate)
            substitution_candidate = copy.deepcopy(substitution)
            # print('terms', list(zip(candidate.terms, next_body.terms)))
            # print([isinstance(b_term, Variable) or b_term == c_term for c_term, b_term in zip(candidate.terms, next_body.terms)])
            if all([isinstance(b_term, Variable) or b_term == c_term for c_term, b_term in
                    zip(candidate.terms, next_body.terms)]):
                substitution_candidate.update(
                    {b: a for a, b in zip(candidate.terms, next_body.terms) if isinstance(b, Variable)})
                # print('substitution candidate', substitution_candidate)
                output += _body_recursion(atoms, copy.deepcopy(stack), substitution_candidate)

        # print('output', output)
        return output



class Variable:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):

        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Constant:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Predicate:

    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name and self.arity == other.arity


class Atom:

    def __init__(self, pred, terms):
        assert (len(terms) == pred.arity)
        self.pred = pred
        self.terms = terms

    def __repr__(self):
        return f"{self.pred.name}({', '.join(map(str, self.terms))})"

    def is_ground(self):
        return all([isinstance(t, Constant) for t in self.terms])

    def substitution(self, theta):
        new_terms = [theta[t] if t in theta else t for t in self.terms]
        return Atom(self.pred, new_terms)

    def __eq__(self, other):
        return self.pred == other.pred and self.terms == other.terms

    def __hash__(self):
        return hash(str(self.pred) + ','.join(map(str, self.terms)))

    @classmethod
    def from_string(cls, pred_name, pred_arity, terms):
        pred = Predicate(pred_name, pred_arity)
        terms = [Variable(t) if t.isupper() else Constant(t) for t in terms]
        return Atom(pred, terms)


def cn(rules, ground_atoms):
    out = list(ground_atoms)
    for rule in rules:
        if isinstance(rule, Atom) and rule.is_ground():
            out.append(rule)
        elif isinstance(rule, DefiniteClause):
            out += rule.get_consequences(ground_atoms)
    return set(out)


def consequences(rules):
    c0 = set()
    c1 = cn(rules, c0)
    while len(c1 - c0) > 0:
        c0 = c1
        c1 = cn(rules, c0)
    return c1