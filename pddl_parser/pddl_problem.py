from enum import Enum


class ExpressionType(Enum):
    CUSTOM = ""
    AND = "and"
    OR = "or"
    NOT = "not"
    WHEN = "when"
    FORALL = "forall"


class Expression:
    expression_type = ExpressionType("")
    predicate = ""
    objects = []
    subexpressions = []

    def __init__(self, expression_type, predicate, objects, subexpressions):
        self.expression_type = expression_type
        self.predicate = predicate
        self.objects = objects
        self.subexpressions = subexpressions

    def __repr__(self):
        ret = "("
        if self.expression_type == ExpressionType(""):
            ret += self.predicate
            for obj in self.objects:
                ret += " "
                ret += obj
        elif self.expression_type == ExpressionType("forall"):
            ret += "forall ("
            for obj in self.objects:
                ret += " "
                ret += obj
            ret += ")"
            for subexpr in self.subexpressions:
                ret += " "
                ret += repr(subexpr)
        else:
            ret += self.expression_type.value
            for subexpr in self.subexpressions:
                ret += " "
                ret += repr(subexpr)
        ret += ")\n"
        return ret


class Problem:
    problem_name = ""
    domain_name = ""
    objects = []
    init_expressions = []
    goal_expression = None
    _file = None

    def __init__(self):
        self.problem_name = ""
        self.domain_name = ""
        self.objects = []
        self.init_expressions = []
        self.goal_expression = None

    def __repr__(self):
        ret = "(define (problem "
        ret += self.problem_name
        ret += ")\n(:domain "
        ret += self.domain_name
        ret += ")\n(:objects "
        for obj in self.objects:
            ret += " "
            ret += obj
        ret += ")\n(:init\n"
        for expr in self.init_expressions:
            ret += repr(expr)
        ret += ")\n(:goal\n"
        ret += repr(self.goal_expression)
        ret += ")\n)"
        return ret

    def _get_token(self):
        token = ""
        # Consume space and the first char of token.
        while True:
            c = self._file.read(1).decode("ascii")
            if not c:
                return None
            elif c.isspace():
                continue
            else:
                token += c
                break
        # If the token is any of ()?: then we return it.
        if token == "(" or token == ")" or token == "?" or token == ":":
            return token.lower()
        # Consume rest of the token's chars.
        while True:
            c = self._file.read(1).decode("ascii")
            if not c:
                return token.lower()
            elif c == "(" or c == ")" or c == "?" or c == ":":
                self._file.seek(-1, 1)  # Seek one byte back.
                return token.lower()
            elif not c.isspace():
                token += c
                continue
            elif c.isspace():
                return token.lower()

    def _parse_start(self):
        token1 = self._get_token()
        token2 = self._get_token()
        if token1 != "(" or token2 != "define":
            return -1
        return 0

    def _parse_problem_name(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        token4 = self._get_token()
        if token1 != "(" or token2 != "problem" or token4 != ")":
            return -1
        self.problem_name = token3
        return 0

    def _parse_domain_name(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        token4 = self._get_token()
        token5 = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "domain" or token5 != ")":
            return -1
        self.domain_name = token4
        return 0

    def _parse_object_list(self):
        objects = []
        while True:
            token = self._get_token()
            if token == ")":
                return objects
            if not token:
                return None
            objects.append(token)

    def _parse_objects(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "objects":
            return -1
        objects = self._parse_object_list()
        if not objects:
            return -1
        self.objects = objects
        return 0

    def _parse_expression(self):
        token1 = self._get_token()
        if token1 != "(":
            return None
        token2 = self._get_token()
        predicate = ""
        subexpressions = []
        objects = []
        try:
            expression_type = ExpressionType(token2)
            if expression_type == ExpressionType("and") or expression_type == ExpressionType("or"):
                while True:
                    subexpression = self._parse_expression()
                    if not subexpression:
                        break
                    subexpressions.append(subexpression)
            elif expression_type == ExpressionType("not"):
                subexpression = self._parse_expression()
                if not subexpression:
                    return None
                subexpressions.append(subexpression)
                token3 = self._get_token()
                if token3 != ")":
                    return None
            elif expression_type == ExpressionType("when"):
                subexpression1 = self._parse_expression()
                subexpression2 = self._parse_expression()
                if not subexpression1 or not subexpression2:
                    return None
                subexpressions.append(subexpression1)
                subexpressions.append(subexpression2)
                token3 = self._get_token()
                if token3 != ")":
                    return None
            elif expression_type == ExpressionType("forall"):
                token3 = self._get_token()
                if token3 != "(":
                    return None
                objects = self._parse_objects()
                subexpression = self._parse_expression()
                subexpressions.append(subexpression)
                token4 = self._get_token()
                if token4 != ")":
                    return None
            return Expression(expression_type, predicate, objects, subexpressions)
        except ValueError:  # It's not any of and, or, not, forall, when.
            expression_type = ExpressionType("")
            predicate = token2
            objects = self._parse_object_list()
            return Expression(expression_type, predicate, objects, subexpressions)

    def _parse_init(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "init":
            return -1
        while True:
            expression = self._parse_expression()
            if not expression:
                return 0
            self.init_expressions.append(expression)

    def _parse_goal(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "goal":
            return -1
        expression = self._parse_expression()
        if not expression:
            return -1
        self.goal_expression = expression
        return 0

    def parse(self, filename):
        self._file = open(filename, "rb")
        if self._parse_start() != 0:
            print("Beginning is incorrect.")
            return
        if self._parse_problem_name() != 0:
            print("Problem name given incorrectly.")
            return
        if self._parse_domain_name() != 0:
            print("Domain name given incorrectly.")
        if self._parse_objects() != 0:
            print("Objects given incorrectly.")
        if self._parse_init() != 0:
            print("Init given incorrectly.")
        if self._parse_goal() != 0:
            print("Goal given incorrectly.")
