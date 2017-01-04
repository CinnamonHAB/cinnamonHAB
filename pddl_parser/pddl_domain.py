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
    parameters = []
    subexpressions = []

    def __init__(self, expression_type, predicate, parameters, subexpressions):
        self.expression_type = expression_type
        self.predicate = predicate
        self.parameters = parameters
        self.subexpressions = subexpressions

    def __repr__(self):
        ret = "("
        if self.expression_type == ExpressionType(""):
            ret += self.predicate
            for param in self.parameters:
                ret += " ?"
                ret += param
        elif self.expression_type == ExpressionType("forall"):
            ret += "forall ("
            for param in self.parameters:
                ret += " ?"
                ret += param
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


class Predicate:
    name = ""
    objects = []

    def __init__(self, name, objects):
        self.name = name
        self.objects = objects

    def __repr__(self):
        ret = "("
        ret += self.name
        for obj in self.objects:
            ret += " ?"
            ret += obj
        ret += ")\n"
        return ret


class Action:
    name = ""
    parameters = []
    precondition = None  # Expression
    effect = None  # Expression

    def __init__(self, name, parameters, precondition, effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def __repr__(self):
        ret = "(:action "
        ret += self.name
        ret += "\n:parameters("
        for param in self.parameters:
            ret += " ?"
            ret += param
        ret += ")\n:precondition"
        ret += repr(self.precondition)
        ret += ":effect"
        ret += repr(self.effect)
        ret += ")\n"
        return ret


class Domain:
    domain_name = ""
    predicates = []
    actions = []
    _file = None

    def __init__(self):
        self.domain_name = ""
        self.predicates = []
        self.actions = []

    def __repr__(self):
        ret = "(define (domain "
        ret += self.domain_name
        ret += ")\n(:predicates\n"
        for pred in self.predicates:
            ret += repr(pred)
        ret += ")\n"
        for act in self.actions:
            ret += repr(act)
        ret += ")\n"
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

    def _parse_domain_name(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        token4 = self._get_token()
        if token1 != "(" or token2 != "domain" or token4 != ")":
            return -1
        self.domain_name = token3
        return 0

    def _parse_parameters(self):
        parameters = []
        while True:
            token = self._get_token()
            if token == "?":
                continue
            if token == ")":
                return parameters
            if not token:
                return parameters
            parameters.append(token)

    def _parse_predicate(self):
        token = self._get_token()
        if token != "(":
            return None
        name = self._get_token()
        if not name:
            return None
        objects = self._parse_parameters()
        return Predicate(name, objects)

    def _parse_predicates(self):
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "predicates":
            return -1
        while True:
            predicate = self._parse_predicate()
            if not predicate:
                break
            self.predicates.append(predicate)
        return 0

    def _parse_expression(self):
        token1 = self._get_token()
        if token1 != "(":
            return None
        token2 = self._get_token()
        predicate = ""
        subexpressions = []
        parameters = []
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
                parameters = self._parse_parameters()
                subexpression = self._parse_expression()
                subexpressions.append(subexpression)
                token4 = self._get_token()
                if token4 != ")":
                    return None
            return Expression(expression_type, predicate, parameters, subexpressions)
        except ValueError:  # It's not any of and, or, not, forall, when.
            expression_type = ExpressionType("")
            predicate = token2
            parameters = self._parse_parameters()
            return Expression(expression_type, predicate, parameters, subexpressions)

    def _parse_action(self):
        # Action name.
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        name = self._get_token()
        if token1 != "(" or token2 != ":" or token3 != "action" or not name:
            return None
        # Parameters.
        token1 = self._get_token()
        token2 = self._get_token()
        token3 = self._get_token()
        if token1 != ":" or token2 != "parameters" or token3 != "(":
            return None
        parameters = self._parse_parameters()
        # Precondition.
        token1 = self._get_token()
        token2 = self._get_token()
        if token1 != ":" or token2 != "precondition":
            return None
        precondition = self._parse_expression()
        # Effect.)
        token1 = self._get_token()
        token2 = self._get_token()
        if token1 != ":" or token2 != "effect":
            return None
        effect = self._parse_expression()
        # Return
        token1 = self._get_token()
        if token1 != ")":
            return None
        return Action(name, parameters, precondition, effect)

    def parse(self, filename):
        self._file = open(filename, "rb")
        if self._parse_start() != 0:
            print("Beginning is incorrect.")
            return
        if self._parse_domain_name() != 0:
            print("Domain name given incorrectly.")
            return
        if self._parse_predicates() != 0:
            print("Predicates given incorrectly.")
        while True:
            action = self._parse_action()
            if not action:
                return
            self.actions.append(action)
