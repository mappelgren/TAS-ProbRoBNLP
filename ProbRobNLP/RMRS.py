from collections import namedtuple
import numpy as np


class RMRS:

    def __init__(self, hook, hole, rels, hcons, equalities):
        self.hook = hook
        self.hole = hole
        self.rels = rels
        self.hcons = hcons
        self.equalities = equalities

    def __eq__(self, other):
        return self == other

class Pred:

    def __init__(self, name, args):
        self.name = name
        self.args = args

class EPS:

    def __init__(self, handle, pred):
        self.handle = handle
        self.pred = pred


def build_matrix(eq):
    var = set()
    for a, b in eq:
        var |= {a, b}

    var = sorted(list(var))

    matrix = np.zeros((len(var), len(var)))

    for i, a in enumerate(var):
        for j, b in enumerate(var):
            if (a, b) in eq or (b, a) in eq:
                matrix[i ,j] = 1
    return matrix, var


def matrix_to_eq(mat, var):
    for i, a in enumerate(var):
        for j, b in enumerate(var):
            if mat[i ,j] == 1 and a != b and j > i:
                yield (a, b)


def tr(eq):
    mat, var = build_matrix(eq)

    mat = tr_helper(mat, var)

    return list(matrix_to_eq(mat, var))


def tr_helper(mat, var):
    updated = False
    for i in range(len(var)):
        for j in range(len(var)):
            if mat[i, j] == 1:
                continue
            else:
                for k in range(len(var)):
                    if mat[i, k] == 1 and mat[k, j] == 1:
                        mat[i, j] = 1
                        updated = True
    if updated:
        return tr_helper(mat, var)
    else:
        return mat


hnum = 0


def get_hnum():
    global hnum
    h = f'h{hnum}'
    hnum += 1
    return h


xnum = 0


def get_x():
    global xnum
    x = f'x{xnum}'
    xnum += 1
    return x


def op(a1, a2, label):
    hook = a2.hook

    slots = {key: a1.hole.get(key, {}) | a2.hole.get(key, {}) for key in a1.hole.keys() | a2.hole.keys() if
             key != label}

    new_rels = a1.rels + a2.rels
    equalities = tr(a1.equalities | a2.equalities | {(a1.hook[0], a2.hole[label][0]), (a1.hook[1], a2.hole[label][1])})
    hcons = a1.hcons | a2.hcons

    return RMRS(hook, slots, new_rels, hcons, equalities)

