import copy

from ProbRobNLP import probrob

reference_id = 0
variable_id = 0


def get_variable():
    global variable_id
    x = f'X{variable_id}'
    variable_id += 1
    return Variable(x)


def reset_variable():
    global variable_id
    variable_id = 0


def get_reference():
    global reference_id
    x = f'x{reference_id}'
    reference_id += 1
    return Constant(x)


def reset_reference():
    global reference_id
    reference_id = 0


event_id = 0


def get_event():
    global event_id
    x = f'e{event_id}'
    event_id += 1
    return Constant(x)

def reset_event():
    global event_id
    event_id = 0


event_variable_id = 0
def get_event_variable():
    global event_variable_id
    x = f'e{event_variable_id}'
    event_variable_id += 1
    return Variable(x)

def reset_event_variable():
    global event_variable_id
    event_variable_id = 0


class DefiniteClause:

    def __init__(self, head, body):
        self.head = head
        self.body = list(body)

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

    def __eq__(self, other):
        return self.head == other.head and len(self.body) == len(other.body) and all([b in other.body for b in self.body])


def _body_recursion(atoms, stack, substitution):
    if len(stack) == 0:
        return [substitution]
    else:
        next_body = stack.pop()
        next_body = next_body.substitution(substitution)

        candidates = [atom for atom in atoms if atom.pred == next_body.pred]

        output = []
        for candidate in candidates:

            substitution_candidate = copy.deepcopy(substitution)

            if all([isinstance(b_term, Variable) or b_term == c_term for c_term, b_term in
                    zip(candidate.terms, next_body.terms)]):
                substitution_candidate.update(
                    {b: a for a, b in zip(candidate.terms, next_body.terms) if isinstance(b, Variable)})

                output += _body_recursion(atoms, copy.deepcopy(stack), substitution_candidate)

        return output


class Term:

    def __init__(self, name, features=None):
        self.name = name
        self.features = [{'proper_noun': False, 'pronoun': False, 'dobj': False, 'iobj': False}] if features is None else features

    def __repr__(self):
        return self.name

    def __eq__(self, other):

        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def is_event(self):
        return self.name[0] in ['e', 'E']

    def update_features(self, new_features):
        f = self.features[-1]
        if 'words' in new_features:
            new_words = new_features['words']
            new_positions = new_features['positions']
            old_words = f['words'] if 'words' in f else []
            old_positions = f['positions'] if 'positions' in f else []
            words = new_words + old_words
            positions = new_positions + old_positions

            positions, words = zip(*sorted(zip(positions, words)))

            words = list(words)
            positions = list(positions)

            f['words'] = words
            f['positions'] = positions

        for key, value in new_features.items():
            if key in ['words', 'positions']:
                continue
            elif key in f:
                if isinstance(value, bool):
                    f[key] = f[key] or value
                elif f[key] != value:
                    raise ValueError(f'{key} does not match between feature sets: {f[key]} and {value}')
            else:
                f[key] = value

    def get_feature(self, keyword):
        if keyword == 'words':
            return ' '.join(self.features[-1][keyword])
        return self.features[-1][keyword]

class Variable(Term):
    pass


class Constant(Term):
    pass


class Predicate:

    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name and self.arity == other.arity

    def __hash__(self):
        return hash(str(self))

class Atom:

    def __init__(self, pred, terms, fp=False):
        assert (len(terms) == pred.arity)
        self.pred = pred
        self.terms = terms
        self.fp = fp

    @property
    def name(self):
        return self.pred.name

    def __repr__(self):
        return f"{self.pred.name}({', '.join(map(str, self.terms))})"

    def is_ground(self):
        return all([isinstance(t, Constant) for t in self.terms])

    def substitution(self, theta):
        new_terms = [theta[t] if t in theta else t for t in self.terms]
        return Atom(self.pred, new_terms)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.pred == other.pred
                and all([t1 == t2 for t1, t2, in zip(self.terms, other.terms)]))

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


class DRSish:

    def __init__(self, ref, log, role=None, holes=None, fills=None):
        self.ref = ref
        self.log = log
        self.role = role
        self.holes = holes if holes is not None else {}
        self.fills = fills if fills is not None else {}

    def __repr__(self):
        return str(self.ref) + str(self.log) + ' h: ' + str(self.holes) + ' f: ' + str(self.fills)

    def __eq__(self, other):
        a = len(self.ref) == len(other.ref)
        b = all([r in other.ref for r in self.ref])
        c = len(self.log) == len(other.log)
        d = all([l in other.log for l in self.log])
        return a and b and c and d

    def __add__(self, other):
        ref = list(set(self.ref + other.ref))
        log = self.log + other.log
        self.holes.update(other.holes)
        self.fills.update(other.fills)
        gaps_to_fill = [h for h in self.fills.keys() if h in self.holes]

        # print('gaps to fill')
        # print(gaps_to_fill)

        drs = DRSish(ref, log, holes=self.holes, fills=self.fills)
        for g in gaps_to_fill:
            drs.replace_reference(drs.holes[g], drs.fills[g])
        # print(self.holes)
        return drs

    def get_predicates(self, reference):
        assert (reference in self.ref)

        for l in self.log:
            if reference in l.refs:
                yield l

    def get_first_predicates(self, reference):
        assert (reference in self.ref)

        for l in self.log:
            if l.fp:
                if reference == l.terms[1]:
                    yield l
            elif reference == l.terms[0]:
                yield l

    def unify(self, other):

        new_ref = []
        log = copy.deepcopy(self.log)
        assert (len(other.ref) == 1)
        for ref in self.ref:

            if isinstance(ref, str) and '<' in ref:

                hole = ref.split('<')[1].strip('>')
                if hole == other.role:
                    new_ref.append(other.ref[0])
                    new_log = []
                    for formula in log:
                        if ref in formula.refs:
                            refs = [other.ref[0] if r == ref else r for r in formula.refs]
                            new_log.append(sem(formula.name, refs))
                        else:
                            new_log.append(formula)
                    log = new_log
            else:
                new_ref.append(ref)
        new_ref = [r for r in new_ref if isinstance(r, str)]
        return DRSish(new_ref, log + other.log, self.role)

    def join_on_reference(self, other):
        assert (len(self.ref) == len(other.ref))

        sref = self.ref
        oref = other.ref
        result = self + other

        # sref.update_features(oref.features)

        for s, o in zip(sref, oref):
            result.replace_reference(o, s)
        return result

    def fill_gap(self, other, dep):
        if dep in self.holes:
            var, extra = self.holes.pop(dep)
            result = self + other
            # hole.update_features(other.ref[0].features)

            result.replace_reference(var, other.ref[0])

            if extra is not None:
                extra_dep, extra_var = extra

                replacement, _ = result.holes.pop(extra_dep)
                result.replace_reference(replacement, extra_var)



        else:
            self.fills[dep] = other.ref[0]
            result = self + other
        return result

    def replace_reference(self, hole, antecedent):
        if not isinstance(hole, Atom) and not isinstance(antecedent, Atom):
            hole.update_features(antecedent.features[-1])
        new_ref = [r for r in self.ref if r != hole] + ([antecedent] if antecedent not in self.ref else [])
        log = copy.deepcopy(self.log)
        new_log = []
        for l in log:
            if hole in l.terms:
                refs = [r if r != hole else antecedent for r in l.terms]
                new_log.append(Atom(l.pred, refs, l.fp))
            else:
                new_log.append(l)
        self.update_holes(hole, antecedent)
        self.ref = new_ref
        self.log = list(set(new_log))

    def update_holes(self, old, new):
        new_holes = {}
        for dep, (var, extra) in self.holes.items():
            if extra is not None:
                extra_dep, extra_var = extra
                if extra_var == old:
                    extra_var = new
                extra = (extra_dep, extra_var)
            if var == old:
                var = new
            new_holes[dep] = (var, extra)
        self.holes = new_holes

    def to_PRS(self):
        order = self.order_prs()
        entities = {entity.name: entity for entity in self._to_PRS()}
        for name in order:
            yield entities[name]

    def remove_predicate(self, p):
        self.log = [l for l in self.log if p != l]

    def remove_reference(self, ref):
        self.ref = [r for r in self.ref if r != ref]

    def _to_PRS(self):
        types = {'tray': 'Tray', 'cup': 'Cup', 'bowl': 'Bowl', 'bucket': 'Bucket',
                 'chair': 'DiningChair', 'filled_cup': 'FilledCup',
                 'plate': 'Plate', 'table': 'Table', 'robot': 'Robot', 'camera': 'Camera', 'peg': 'HexagonalPegBase',
                 'gear': 'HexagonalGear', 'cube': 'Cube', 'toy_cube': 'ToyCube', 'cylinder': 'Cylinder',
                 'rope link': 'RopeLink',
                 'rope bucket': 'RopeBucket', 'conveyor belt': 'CircularConveyorBelt'}

        two_place = {'on': probrob.OnConstraint, 'in': probrob.OnConstraint,
                     'left_of': lambda x: probrob.OfConstraint('left', x)}

        colour_dict = {'red': '"0.1"', 'blue': '"0.2"', 'green': '"0.3"', 'grey': '"0.4"', 'orange': '"0.5"',
                       'purple': '"0.7"', 'pink': '"0.6"', 'black': '"0"', 'white': '"1"'}

        special_names = {'centre': probrob.Vector3D(0, 0, 0)}

        # for l in self.log:
        #     if l.name in special_names:
        #         self.remove_predicate(l)
        #         self.replace_reference(l.refs[0], l.name)
        #         self.remove_reference(l.name)

        for ref in [r for r in self.ref if isinstance(r, Constant) and 'e' not in r.name]:

            atoms = list(self.get_first_predicates(ref))
            # print(ref, atoms)
            constraints = []
            type_ = None
            for pred in atoms:
                if pred.name in types:
                    type_ = types[pred.name]
                elif pred.name in two_place:
                    if pred.fp:
                        term = pred.terms[2]
                    else:
                        term = pred.terms[1]
                    constraints.append(two_place[pred.name](term))
                elif pred.name in colour_dict:
                    constraints.append(probrob.PropConstraint('color', f'"{pred.name}"'))

            if type_ is not None:
                yield probrob.Entity(type_, ref, constraints)
            else:
                print(f'Warning: {ref} identified as type None')

    def order_prs(self):
        constraints = []
        for entity in self._to_PRS():
            for constraint in entity.constraints:
                try:
                    r = constraint.referent
                    if isinstance(r, Constant):
                        constraints.append((r, entity.name))
                except AttributeError:
                    pass

        constraint_dict = {}
        for entity in self._to_PRS():
            c = [d for (d, i) in constraints if i == entity.name and d in self.ref]
            constraint_dict[entity.name] = c

        order = []
        i = 0
        while len(constraint_dict) > 0 and i < 20:

            new_dict = {}
            for name, cons in constraint_dict.items():
                if cons == [] or all([x in order for x in cons]):
                    order.append(name)
                else:
                    new_dict[name] = cons
            constraint_dict = new_dict
            i += 1
        return order

    def draw(self):
        prs_lines = self.to_PRS()
        imp = probrob.Import('model', '*')
        scene = probrob.WorldModel(prs_lines, [imp])
        return scene

    def test_reference_matches(self, reference, constraints):

        preds = [c.name for c in self.get_first_predicates(reference)]
        # print('reference', reference, 'preds', preds, 'constraints', constraints)
        # print(all([c.name in preds for c in constraints]))
        return all([c.name in preds for c in constraints])

    def replace_specials(self):

        list_of_specials = {
            'centre': Atom(Predicate('Vector3D'), [0, 0, 0]),
            'left': Atom(Predicate('left', [])),
        }


class sem:
    def __init__(self, name, refs):
        self.name = name
        self.refs = refs

    def __repr__(self):
        return f'{str(self.name)}({", ".join(map(str, self.refs))})'

    def __eq__(self, other):
        return self.name == other.name and self.refs == other.refs

    def __hash__(self):
        # hash(custom_object)
        return hash((self.name, ' '.join(map(str, self.refs))))
