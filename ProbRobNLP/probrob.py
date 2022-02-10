

class Vector3D:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def toDRS(self):
        return

class Distribution:
    distribution_name = ""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.distribution_name}({self.x}, {self.y})"


class Normal(Distribution):
    distribution_name = "Normal"


# class Discrete(Distribution):

#     distribution_name = "Discrete"

class math_expr:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.x} {self.name} {self.y}"


class Max(math_expr):
    name = "max"

    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return f"{self.name}({self.numbers})"


class Min(math_expr):
    name = "min"

    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return f"{self.name}({self.numbers})"


class Abs(math_expr):
    name = "abs"

    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return f"{self.name}({self.numbers})"


class Plus(math_expr):
    name = "+"


class Minus(math_expr):
    name = "-"


class Times(math_expr):
    name = "*"


class DistanceFrom(math_expr):
    name = "distance from"

    def __init__(self, vector1, vector2):
        self.vector1 = vector1
        self.vector2 = vector2

    def __repr__(self):
        return f"distance from {self.vector1} to {self.vector2}"


class RelativeTo():

    def __init__(self, vector1, vector2):
        self.vector1 = vector1
        self.vector2 = vector2

    def __repr__(self):
        return f"{self.vector1} relative to {self.vector2}"


class BooleanExpr():
    name = ""

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def __repr__(self):
        return f"{self.expr1} {self.name} {self.expr2}"


class NotBool(BooleanExpr):
    name = "not"

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"not {self.expr}"


class AndBool(BooleanExpr):
    name = "and"

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def __repr__(self):
        return f"{self.expr1} and {self.expr2}"


class OrBool(BooleanExpr):
    name = "or"

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def __repr__(self):
        return f"{self.expr1} or {self.expr2}"


class EQ(BooleanExpr):
    name = "=="


class NEQ(BooleanExpr):
    name = "!="


class LT(BooleanExpr):
    name = "<"


class GT(BooleanExpr):
    name = ">"


class GEQ(BooleanExpr):
    name = ">="


class LEQ(BooleanExpr):
    name = "<="


class IsIn(BooleanExpr):
    name = "is in"


class CuboidRegion:

    def __init__(self, vector1, vector2, vector3):
        self.vector1 = vector1
        self.vector2 = vector2
        self.vector3 = vector3

    def __repr__(self):
        return f"CuboidRegion({self.vector1}, {self.vector2}, {self.vector3})"


class RectangleRegion:

    def __init__(self, number1, number2, vector1, vector2):
        self.number1 = number1
        self.number2 = number2
        self.vector1 = vector1
        self.vector2 = vector2

    def __repr__(self):
        return f"Rectangle3DRegion({self.number1}, {self.number2}, {self.vector1}, {self.vector2})"


class HalfspaceRegion:

    def __init__(self, vector1, vector2, number=None):
        self.vector1 = vector1
        self.vector2 = vector2
        self.number = number

    def __repr__(self):
        number = f", {self.number}" if self.number is not None else ""
        return f"HalfspaceRegion({self.vector1}, {self.vector2}{number})"


class PropConstraint:

    def __init__(self, prop, value):
        self.prop = prop
        self.value = value

    def __repr__(self):
        return f"with {self.prop} {self.value}"


class posConstraint:

    def __init__(self, prop, values):
        self.prop = prop
        self.values = values

    def __repr__(self):
        return f"with {self.prop} {self.value}"


class AtConstraint:

    def __init__(self, vector):
        self.vector = vector

    def __repr__(self):
        return f"at {self.vector}"


class BeyondConstraint:
    def __init__(self, beyond, by, from_):
        self.beyond = beyond
        self.by = by
        self.from_ = from_

    def __repr__(self):
        return f"beyond {self.beyond} by {self.by} from {self.from_}"


class InConstraint:
    def __init__(self, region):
        self.region = region

    def __repr__(self):
        return f"in {self.region}"


class OfConstraint:
    def __init__(self, direction, referent, by=None):
        self.direction = direction
        self.referent = referent
        self.by = by

    def __repr__(self):
        by_expr = f" by {self.by}" if self.by is not None else ""
        return f"{self.direction} of {self.referent}" + by_expr


class OnConstraint:
    def __init__(self, referent, completely=False):
        self.referent = referent
        self.completely = completely

    def __repr__(self):
        completely = "completely " if self.completely else ""
        return completely + f"on {self.referent}"


class AlignedWithConstraint:
    def __init__(self, referent, axis):
        self.referent = referent
        self.axis = axis

    def __repr__(self):
        return f"aligned with {self.referent} on {self.axis}"


class PropReference:

    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop

    def __repr__(self):
        return f"{self.obj}.{self.prop}"

class SideSpec:

    def __init__(self, obj, side):
        self.obj = obj
        self.side = side

    def __repr__(self):
        return f"({self.side} {self.obj})"

class Side:
    def __init__(self, side):
        self.side = side

    def __repr__(self):
        return " ".join(self.side)

class FacingConstraint:
    def __init__(self, vector):
        self.direction = vector

    def __repr__(self):
        return f"facing {self.direction}"


class FacingTowardConstraint:
    def __init__(self, referent):
        self.direction = referent

    def __repr__(self):
        return f"facing toward {self.direction}"


class Requirement:
    def __init__(self, boolean):
        self.boolean = boolean

    def __repr__(self):
        return f"require {self.boolean}"


class Entity:

    def __init__(self, type_, name, constraints=None):
        if constraints is None:
            constraints = []
        self.type = type_
        self.name = name
        self.constraints = constraints

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def __repr__(self):
        constraint_repr = " " + ', '.join([con.__repr__() for con in self.constraints])

        return f"{self.name} = {self.type}" + constraint_repr


class Import:

    def __init__(self, module, things):
        self.module = module
        self.things = things

    def __repr__(self):
        return f"from {self.module} import {self.things}"


class WorldModel:

    def __init__(self, entities, imports):
        self.imports = imports
        #         self.entities = [Entity(type_, name, constraints) for name, (type_, constraints) in entities.items()]
        self.entities = entities

    def __repr__(self):
        return "\n".join([str(i) for i in self.imports] + [str(e) for e in self.entities])