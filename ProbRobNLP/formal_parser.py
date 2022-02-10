from sly import Lexer, Parser
from .probrob import *


class PRSLexer(Lexer):

    tokens = {
        ID, IMPORT, REQUIRE, CLASS,

        WITH, TOP, BOTTOM, FRONT, BACK, LEFT, RIGHT,
        # distribution
        NORMAL, DISCRETE, VECTOR3D,

        # LOGIC
        AND, OR, NOT, TRUE, FALSE,

        # MATH
        NUMBER, DOUBLEEQ, NEQ, LEQ, GEQ, GT, LT, EQ,
        MAX, MIN, PLUS, TIMES, ABS, MINUS,
        RELATIVE, BEYOND, COMPLETELY,
        FACING, LBRACKET, RBRACKET,
        TOWARD, NOT,
        CUBOID, RECTANGLE,
        HALFSPACE, DISTANCE, ALIGNED,
        TO, AT, BY, FROM, IN, IS, OF, ON, X, Y, Z, COMMA, POINT, QUOTE, AHEAD, BELOW, ABOVE ,BEHIND
    }

    literals = {'+', '-', '(', ')', '*', '.', '"', ',', ':'}

    # names
    ignore = ' \t"'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    ID['import'] = IMPORT
    ID['require'] = REQUIRE
    ID['class'] = CLASS
    ID['with'] = WITH
    ID['top'] = TOP
    ID['bottom'] = BOTTOM
    ID['front'] = FRONT
    ID['back'] = BACK
    ID['left'] = LEFT
    ID['right'] = RIGHT
    ID['Normal'] = NORMAL
    ID['Discrete'] = DISCRETE
    ID['Vector3D'] = VECTOR3D
    ID['and'] = AND
    ID['or'] = OR
    ID['True'] = TRUE
    ID['False'] = FALSE
    ID['max'] = MAX
    ID['min'] = MIN
    ID['abs'] = ABS
    ID['relative'] = RELATIVE
    ID['beyond'] = BEYOND
    ID['ahead'] = AHEAD
    ID['below'] = BELOW
    ID['above'] = ABOVE
    ID['behind'] = BEHIND
    ID['completely'] = COMPLETELY
    ID['facing'] = FACING
    ID['toward'] = TOWARD
    ID['CuboidRegion'] = CUBOID
    ID['Rectangle3DRegion'] = RECTANGLE
    ID['HalfspaceRegion'] = HALFSPACE
    ID['distance'] = DISTANCE
    ID['aligned'] = ALIGNED
    ID['not'] = NOT
    ID['to'] = TO
    ID['at'] = AT
    ID['by'] = BY
    ID['from'] = FROM
    ID['in'] = IN
    ID['is'] = IS
    ID['of'] = OF
    ID['on'] = ON
    ID['x'] = X
    ID['y'] = Y
    ID['z'] = Z

    @_(r'\"?\d+(\.\d+)?\"?')
    def NUMBER(self, t):
        t.value = t.value.strip('"')
        t.value = float(t.value)
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    DOUBLEEQ = r"=="
    NEQ = r"!="
    LEQ = r"<="
    GEQ = r'>='
    GT = r'>'
    LT = r'<'
    EQ = r"="

    #     PLUS = r'\+'
    #     TIMES = r'\*'

    #     MINUS = r'-'
    #     COMMA = r','
    #     LBRACKET = r'\('
    #     RBRACKET = r'\)'

    #     POINT = r'\.'
    #     QUOTE = r'"'
    ignore_comment = r'\#.*'


class PRSParser(Parser):
    # Get the token list from the lexer (required)
    tokens = PRSLexer.tokens
    literals = PRSLexer.literals

    @_('scenarioop')
    def scenario(self, p):
        imports = [f for t, f in p.scenarioop if t == "import"]
        entities = [e for t, e in p.scenarioop if t == "statement"]
        return WorldModel(entities, imports)

    @_('statement')
    def scenarioinstance(self, p):
        return ('statement', p.statement)

    @_('FROM ID IMPORT "*"')
    def scenarioinstance(self, p):
        return ('import', Import(p.ID, "*"))

    @_('scenarioinstance')
    def scenarioop(self, p):
        return [p.scenarioinstance]

    @_('scenarioinstance scenarioop')
    def scenarioop(self, p):
        if p.scenarioinstance is None:
            return p.scenarioop
        else:
            return [p.scenarioinstance] + p.scenarioop

    #     @_('region')
    #     def scenario(self, p):
    #         return p.region

    #     @_('vector')
    #     def scenario(self, p):
    #         return p.vector

    #     @_('distribution')
    #     def scenario(self, p):
    #         return p.distribution

    #     @_('scalarplus')
    #     def scenario(self, p):
    #         return p.scalarplus

    ### statement

    @_('ID EQ value')
    def statement(self, p):
        type_, constraints = p.value
        return Entity(type_, p.ID, constraints)

    #         return {p.ID: p.value}

    @_('instance')
    def statement(self, p):
        return p.instance

    #     @_('classDef')
    #     def statement(self, p):
    #         return p.classDef

    @_('REQUIRE boolean')
    def statement(self, p):
        return Requirement(p.boolean)

    ### value
    ## value ::= boolean | scalar | vector | instance | property

    @_('boolean')
    def value(self, p):
        return p.boolean

    @_('scalar')
    def value(self, p):
        return p.scalar

    @_('vector')
    def value(self, p):
        return p.vector

    @_('instance')
    def value(self, p):
        return p.instance

    #### Instance
    ## instance ::= classname (specif ier,)∗
    @_('ID specifierop')
    def instance(self, p):
        return p.ID, p.specifierop

    @_('specifier')
    def specifierop(self, p):
        return [p.specifier]

    @_('specifier "," specifierop')
    def specifierop(self, p):
        return [p.specifier] + p.specifierop

    @_('ID')
    def instance(self, p):
        return (p.ID, [])

    ### specifier
    # specifier ::= with property value | posSpec | orientationSpec

    @_('WITH property_ value')
    def specifier(self, p):
        return PropConstraint(p.property_, p.value)

    @_('ID')
    def property_(self, p):
        return p.ID

    @_('ID "." ID')
    def property_(self, p):
        return PropReference(p.ID0, p.ID1)

    @_('sidespec "." ID')
    def property_(self, p):
        return PropReference(p.sidespec, p.ID)

    @_('sidespec "." axis')
    def property_(self, p):
        return PropReference(p.sidespec, p.axis)

    @_('ID "." axis')
    def property_(self, p):
        return PropReference(p.ID, p.axis)

    @_("'(' locsop ')' ID")
    def property_(self, p):
        return PropReference(p.ID, p.locsop)

    @_("posSpec")
    def specifier(self, p):
        return p.posSpec

    @_("orientationSpec")
    def specifier(self, p):
        return p.orientationSpec

    #### posSpec
    #     posSpec ::= at vector
    # | beyond (vector | instance) by (number | vector) from (vector | objectname)
    # | in region
    # | (lef t | right | ahead | . . . ) of (vector | objectname)
    # | (completely)? on (vector | objectname)
    # | aligned with(vector | objectname) on (x | y | z)

    @_('AT vector')
    def posSpec(self, p):
        return AtConstraint(p.vector)

    @_('IN region')
    def posSpec(self, p):
        return InConstraint(p.region)

    @_('BEYOND vorobj BY byop FROM vorobj')
    def posSpec(self, p):
        return BeyondConstraint(p.vorobj0, p.byop, p.vorobj1)

    @_('locsop OF vorobj')
    def posSpec(self, p):
        return OfConstraint(p.locsop, p.vorobj)

    @_('locsop OF vorobj BY scalar')
    def posSpec(self, p):
        return OfConstraint(p.locsop, p.vorobj, by=p.scalar)

    @_('ON vorobj')
    def posSpec(self, p):
        return OnConstraint(p.vorobj)

    @_('COMPLETELY ON vorobj')
    def posSpec(self, p):
        return OnConstraint(p.vorobj, completely=True)

    @_('ALIGNED WITH vorobj ON axis')
    def posSpec(self, p):
        return AlignedWithConstraint(p.vorobj, p.axis)

    @_('ALIGNED WITH vorobj BY axis')
    def posSpec(self, p):
        return AlignedWithConstraint(p.vorobj, p.axis)

    #### sidespec
    @_('"(" locsop ID ")"')
    def sidespec(self, p):
        return SideSpec(p.ID, p.locsop)

    ##### orientationSpec
    #     orientationSpec ::= facing vector
    #         | facing toward (vector | objectname)

    @_("FACING vector")
    def orientationSpec(self, p):
        return FacingConstraint(p.vector)

    @_("FACING TOWARD vorobj")
    def orientationSpec(self, p):
        return FacingTowardConstraint(p.vorobj)

    ### classDef



    @_('X')
    def axis(self, p):
        return p.X

    @_('Y')
    def axis(self, p):
        return p.Y

    @_('Z')
    def axis(self, p):
        return p.Z

    @_('vector')
    def vorobj(self, p):
        return p.vector

    @_('property_')
    def vorobj(self, p):
        return p.property_

    @_('vorobj "-" vorobj')
    def vorobj(self, p):
        return Minus(p.vorobj0, p.vorobj1)

    @_('vorobj "+" vorobj')
    def vorobj(self, p):
        return Plus(p.vorobj0, p.vorobj1)

    @_('sidespec')
    def vorobj(self, p):
        return p.sidespec

    @_('NUMBER')
    def byop(self, p):
        return p.NUMBER

    @_('vector')
    def byop(self, p):
        return p.vector

    ####

    @_("TOP")
    def locspec(self, p):
        return p.TOP

    @_("BOTTOM")
    def locspec(self, p):
        return p.BOTTOM

    @_("FRONT")
    def locspec(self, p):
        return p.FRONT

    @_("BACK")
    def locspec(self, p):
        return p.BACK

    @_("LEFT")
    def locspec(self, p):
        return p.LEFT

    @_("RIGHT")
    def locspec(self, p):
        return p.RIGHT

    @_("AHEAD")
    def locspec(self, p):
        return p.AHEAD

    @_("BEHIND")
    def locspec(self, p):
        return p.BEHIND

    @_("ABOVE")
    def locspec(self, p):
        return p.ABOVE

    @_("BELOW")
    def locspec(self, p):
        return p.BELOW

    @_("locspec")
    def locsop(self, p):
        return Side([p.locspec])

    @_("locspec locspec")
    def locsop(self, p):
        return Side([p.locspec0, p.locspec1])

    ### boolean
    ## boolean ::= True | False | boolOp
    @_('TRUE')
    def boolean(self, p):
        return p.TRUE

    @_('FALSE')
    def boolean(self, p):
        return p.FALSE

    @_('boolop')
    def boolean(self, p):
        return p.boolop

    ### boolop
    ##  boolOp ::= not boolean
    ##      | boolean (and | or) boolean
    ##      | scalar (== | != | < | > | >= | <=) scalar
    ##      | (vector | objectname) is in region

    @_('NOT boolean')
    def boolop(self, p):
        return NotBool(p.boolean)

    @_('boolean AND boolean')
    def boolop(self, p):
        return AndBool(p.boolean0, p.boolean1)

    @_('boolean OR boolean')
    def boolop(self, p):
        return OrBool(p.boolean0, p.boolean1)

    @_('scalar DOUBLEEQ scalar')
    def boolop(self, p):
        return EQ(p.scalar0, p.scalar1)

    @_('scalar NEQ scalar')
    def boolop(self, p):
        return NEQ(p.scalar0, p.scalar1)

    @_('scalar LT scalar')
    def boolop(self, p):
        return LT(p.scalar0, p.scalar1)

    @_('scalar GT scalar')
    def boolop(self, p):
        return GT(p.scalar0, p.scalar1)

    @_('scalar GEQ scalar')
    def boolop(self, p):
        return GEQ(p.scalar0, p.scalar1)

    @_('scalar LEQ scalar')
    def boolop(self, p):
        return LEQ(p.scalar0, p.scalar1)

    @_('vector IS IN region')
    def boolop(self, p):
        return IsIn(p.vector, p.region)

    @_('ID IS IN region')
    def boolop(self, p):
        return IsIn(p.ID, p.region)

    ### REGION
    # region ::= CuboidRegion(vector,vector,vector)
    #        | Rectangle3DRegion(number,number,vector,vector)
    #        | HalfspaceRegion(vector,vector,(number)?)
    @_('CUBOID "(" vector "," vector "," vector ")"')
    def region(self, p):
        return CuboidRegion(p.vector0, p.vector1, p.vector2)

    @_('RECTANGLE "(" NUMBER "," NUMBER "," vector "," vector ")"')
    def region(self, p):
        return RectangleRegion(p.NUMBER0, p.NUMBER1, p.vector0, p.vector1)

    @_('HALFSPACE "(" vector "," vector  ")"')
    def region(self, p):
        return HalfspaceRegion(p.vector0, p.vector1)

    @_('HALFSPACE "(" vector "," vector "," NUMBER ")"')
    def region(self, p):
        return HalfspaceRegion(p.vector0, p.vector1, p.NUMBER)

    ### SCALAR

    @_('property_')
    def scalar(self, p):
        return p.property_

    @_('NUMBER')
    def scalar(self, p):
        return p.NUMBER

    @_('distribution')
    def scalar(self, p):
        return p.distribution

    @_('scalarop')
    def scalar(self, p):
        return p.scalarop

    ### SCALAROP
    @_('scalar')
    def scalarplus(self, p):
        return [p.scalar]

    @_('scalarplus scalar')
    def scalarplus(self, p):
        return p.scalarplus + [p.scalar]

    @_('MAX "(" scalarplus ")"')
    def scalarop(self, p):
        return Max(p.scalarplus)

    @_('MIN "(" scalarplus ")"')
    def scalarop(self, p):
        return Min(p.scalarplus)

    @_('"-" scalar')
    def scalarop(self, p):
        return - p.scalar

    @_('scalar "-" scalar')
    def scalarop(self, p):
        return Minus(p.scalar0, p.scalar1)

    @_('ABS "(" scalar ")"')
    def scalarop(self, p):
        return Abs(p.scalar)

    @_('scalar "+" scalar')
    def scalarop(self, p):
        return Plus(p.scalar0, p.scalar1)

    @_('scalar "*" scalar')
    def scalarop(self, p):
        return Times(p.scalar0, p.scalar1)

    @_('DISTANCE FROM vector TO vector')
    def scalarop(self, p):
        return DistanceFrom(p.vector0, p.vector1)

    ### VECTOR3D
    @_('VECTOR3D "(" scalar "," scalar "," scalar ")"')
    def vector(self, p):
        return Vector3D(p.scalar0, p.scalar1, p.scalar2)

    @_('vectorop')
    def vector(self, p):
        return p.vectorop

    ### VECTOR OP
    @_('vector RELATIVE TO vector')
    def vectorop(self, p):
        return RelativeTo(p.vector0, p.vector1)

    ### DISTRIBTUION
    @_('"(" scalar "," scalar ")"')
    def distribution(self, p):
        return Distribution(p.scalar0, p.scalar1)

    @_('NORMAL "(" scalar "," scalar ")"')
    def distribution(self, p):
        return Normal(p.scalar0, p.scalar1)

def parse_file(file_name):
    with open(file_name, "r") as f:
        text = f.read()
    lexer = PRSLexer()
    parser = PRSParser()
    result = parser.parse(lexer.tokenize(text))
    return result