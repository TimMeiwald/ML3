from collections import deque
from functools import lru_cache as cache
from enum import IntEnum


class Rules(IntEnum):
    _ROOT = 0
    _TERMINAL = 1
    _SEQUENCE = 2
    _ORDERED_CHOICE = 3
    _NOT_PREDICATE = 4
    _AND_PREDICATE = 5
    _OPTIONAL = 6
    _ZERO_OR_MORE = 7
    _ONE_OR_MORE = 8
    _SUBEXPRESSION = 10
    _VAR_NAME = 11
    _test = 12
    # Following enum values are all autogenerated from grammar file
    Alphabet_Upper = 20
    Alphabet_Lower = 21
    Num = 22
    Spaces = 23
    Specials = 24
    ASCII = 25
    rm_whitespace = 26
    space_seperator = 27
    terminator = 28
    indent = 29
    indentation = 30
    operator_assignment = 31
    multiuse_seperator = 32
    int = 33
    typedef_int = 34
    type_int = 35
    typedef = 36
    variable = 37
    variable_assignment = 38
    variable_modification = 39
    sym_add = 40
    sym_subtract = 41
    sym_modulo = 42
    sym_division = 43
    sym_multiplication = 44
    sym_power = 45
    sym_open_bracket = 46
    sym_close_bracket = 47
    add = 48
    subtract = 49
    modulo = 50
    division = 51
    multiplication = 52
    power = 53
    subexpression = 54
    maths_argument = 55
    maths = 56
    special_instructions = 57
    syscall_def = 58
    syscall = 59
    grammar = 60



class Node():
    """Core data type"""

    def __init__(self, type: int, content: str = ""):
        """Constructor

        Args:
            type (int): int that corresponds to Rules IntEnum telling you what type of Node it is.
            content (str, optional): Content of Node. Defaults to "".
        """
        self.type = type
        self.content = content
        self.children = deque()
        self.parent = None

    def appender(self, node_deque):
        if (isinstance(node_deque, tuple)):
            print("Tuple apparently: ", node_deque)
            raise Exception
        if (node_deque is None):
            return None
        elif (not isinstance(node_deque, deque)):
            self.children.append(node_deque)
        else:
            for child in node_deque:
                self.appender(child)

    def __equals(self, __o: object) -> bool:
        if (__o is None):
            return False
        if (self.content == __o.content and self.type.name == __o.type.name):
            # By name of type as opposed to value because the value can change between
            # parser versions as the enum is autogenerated
            return True
        else:
            return False

    def __eq__(self, __o: object) -> bool:
        """Two Nodes are considered equal if they and all their subchildren have identical types and contents in order"""
        return self.__subtree_equals(__o)

    def __subtree_equals(self, __o: object) -> bool:
        if (self.__equals(__o) is False):
            return False
        else:
            count = 0
            for index, child in enumerate(self.children):
                try:
                    bool = child.__subtree_equals(__o.children[index])
                    count += bool
                except IndexError:
                    return False
            if (count != len(self.children)):
                return False
            else:
                return True

    def pretty_print(self):
        self._pretty_print(self)

    def _pretty_print(self, node, indent=0):
        indent_str = "  "
        if (node is not None):
            print(indent_str * indent +
                  f"Node: {node.type.name}, '{node.content}'")
            for child in node.children:
                self._pretty_print(child, indent + 1)


class Parser():

    def __init__(self):
        self.src = ""

    def _set_src(self, src: str):
        self.src = src
        # Ensures all caches are cleared on resetting the src
        # Resets state completely
        for rule in Rules:
            # Less than 20 is core parser stuff, greater than 20 is inherited
            # class stuff
            if (rule > 0 and rule < 20):
                func = getattr(self, rule.name)
                func.cache_clear()

    def caller(self, position, func, arg=None):
        """Calls generated functions, ensures converted to node not nested deques,
        Useful for testing or calling specific subterminals"""
        return self._VAR_NAME(position, (func, arg))

    def parse(self, src, func, *, arg=None):
        """Pass in the src and the function from the Grammar_Parser class you defined in the Grammar file
        and it will parse it and return the position at which halting stopped, whether the parse succeeded
        and the AST."""
        self._set_src(src)
        position, bool, node = self._VAR_NAME(0, (func, arg))
        if(node is not None):
            pass_two = Parser_Pass_Two()
            pass_two.parse(node)
            return position, bool, node
        else:
            return position, bool, None

    @cache
    def _token(self, position):
        if (position >= len(self.src)):
            return False
        return self.src[position]

    @cache
    def _TERMINAL(self, position: int, arg: str):
        #assert type(position) == int
        #assert type(Arg) == str
        if(arg == ""):
            node = Node(Rules._TERMINAL, None)
            return position, True, node
        token = self._token(position)
        if (token == arg):
            position += 1
            if (token == "\\"):
                token = self._token(position)
                if (token == "n"):
                    position += 1
                    token = "\\n"
                elif (token == "r"):
                    position += 1
                    token = "\\r"
                elif (token == "t"):
                    position += 1
                    token = "\\t"
                else:
                    token = "\\"
            node = Node(Rules._TERMINAL, token)
            return position, True, node
        else:
            # Don't generate anything other than terminal and var on run, means
            # no rationalizer
            return position, False, None

    @cache
    def _VAR_NAME(self, position: int, args):
        """True if called function evaluates to true else false, Is used to call other functions."""
        # where func is a grammar rule
        temp_position = position
        func, args = args
        position, bool, node = func(position, args)
        if (bool):
            key = func.__name__
            var_node = Node(Rules[key], None)
            if (node is not None):
                var_node.appender(node)
                return position, True, var_node
            else:
                return position, True, None
        else:
            position = temp_position
            return position, False, None

    @cache
    def _ORDERED_CHOICE(self, position: int, args):
        """True if one expression matches, then updates position, else false, no positional update"""
        LHS_func, LHS_arg = args[0]
        RHS_func, RHS_arg = args[1]
        temp_position = position
        position, bool, node = LHS_func(position, LHS_arg)
        if (bool):
            return position, True, node
        position = temp_position
        position, bool, node = RHS_func(position, RHS_arg)
        if (bool):
            return position, True, node
        position = temp_position
        return position, False, None

    @cache
    def _SEQUENCE(self, position: int, args):
        """True if all expressions match, then updates position, else false, no positional update"""
        temp_position = position
        LHS_func, LHS_arg = args[0]
        RHS_func, RHS_arg = args[1]
        position, bool, lnode = LHS_func(position, LHS_arg)
        if (bool):
            position, bool, rnode = RHS_func(position, RHS_arg)
            if (bool):
                node = deque()
                node.append(lnode)
                node.append(rnode)
                return position, True, node
            else:
                position = temp_position
                return position, False, None
        else:
            position = temp_position
            return position, False, None

    @cache
    def _ZERO_OR_MORE(self, position: int, args):
        """Always True, increments position each time the expression matches else continues without doing anything"""
        func, arg = args
        zero_nodes = deque()
        while (True):
            temp_position = position
            position, bool, term_node = func(temp_position, arg)
            if (bool):
                zero_nodes.append(term_node)
                continue
            else:
                position = temp_position
                break
        if (len(zero_nodes) == 0):
            return position, True, None
        else:
            return position, True, zero_nodes

    @cache
    def _ONE_OR_MORE(self, position: int, args):
        """Always True, increments position each time the expression matches else continues without doing anything"""
        func, arg = args
        one_nodes = deque()
        while (True):
            temp_position = position
            position, bool, term_node = func(temp_position, arg)
            if (bool):
                one_nodes.append(term_node)
                continue
            else:
                position = temp_position
                break
        if (len(one_nodes) == 0):
            return position, False, None
        else:
            return position, True, one_nodes

    @cache
    def _OPTIONAL(self, position: int, args):
        """Always True, increments position if option matches otherwise continues without doing anything"""
        func, arg = args
        temp_position = position
        position, bool, node = func(temp_position, arg)
        if (bool):
            return position, True, node
        else:
            position = temp_position
            return position, True, None

    @cache
    def _AND_PREDICATE(self, position: int, args):
        """True if the function results in True, never increments position"""
        func, arg = args
        temp_position = position
        position, bool, node = func(position, arg)
        if (bool):
            position = temp_position
            return position, True, None
        else:
            position = temp_position
            return position, False, None

    @cache
    def _NOT_PREDICATE(self, position: int, args):
        """True if the function results in False, never increments position"""
        position, bool, node = self._AND_PREDICATE(position, args)
        return position, not bool, None

    @cache
    def _SUBEXPRESSION(self, position: int, args):
        """Subexpression is any expression inside a pair of () brackets
        SUBEXPR essentially does nothing but allows for order of precedent
        more importantly order of precedence is very restricted because it made my life hard
        (mostly because I can't find a good definition of what order of precedence is in PEG) so use SUBEXPR
        to make more complicated rules"""
        func, arg = args
        temp_position = position
        position, bool, node = func(position, arg)
        if (bool):
            return position, True, node
        else:
            position = temp_position
            return position, False, None

    @cache
    def _test(self, position: int, args):
        """For testing purposes, may be able to refactor somehow to test
        but not sure how"""
        return self._TERMINAL(position, args)

class Parser_Pass_Two():

    def __init__(self):
        self.delete_nodes = (Rules.rm_whitespace, Rules.space_seperator, Rules.terminator, Rules.indent, Rules.operator_assignment, Rules.multiuse_seperator, Rules.typedef_int, Rules.sym_add, Rules.sym_subtract, Rules.sym_modulo, Rules.sym_division, Rules.sym_multiplication, Rules.sym_power, Rules.sym_open_bracket, Rules.sym_close_bracket, Rules.syscall_def, )
        self.passthrough_nodes = (Rules.Alphabet_Upper, Rules.Alphabet_Lower, Rules.Num, Rules.Spaces, Rules.Specials, Rules.ASCII, Rules.typedef, Rules.subexpression, Rules.maths_argument, Rules.maths, Rules.special_instructions, )
        self.collect_nodes = (Rules.int, Rules.variable, )
        # Anyone making modifications be aware everything after line 10 is
        # automatically added to
        self.tokens = deque()
        # generated parsers while everything before it isn't(so I can add the
        # right stuff based on grammar)

    def token_generator(self, node):
        self.tokens.append(node)
        for child in node.children:
            child.parent = node
            self.token_generator(child)

    def delete_kernel(self, node):
        if (node.type in self.delete_nodes):
            node.children = deque()
            if(node.parent is not None):
                node.parent.children.remove(node)
            del node
        else:
            return node

    def passthrough_kernel(self, node):
        if (node.type in self.passthrough_nodes):
            if(node.parent is not None):
                index = node.parent.children.index(node)
                node.children.reverse()
                for child in node.children:
                    node.parent.children.insert(index, child)
                node.parent.children.remove(node)
            del node
        else:
            return node

    def collect_kernel(self, node):
        if (node.type in self.collect_nodes):
            for child in node.children:
                if (child.type != Rules._TERMINAL):
                    raise ValueError(
                        f"Cannot collect if there are non terminals in the nodes childrens. Node_Type: {node.type.name}, Child_Type: {child.type.name}")
            node.content = ""
            for child in node.children:
                node.content += child.content
            node.children = deque()
            return node
        else:
            return node

    def __parse(self, nodes):
        new_deq = deque()
        for index in range(0, len(nodes)):
            node = nodes.pop()
            node = self.delete_kernel(node)
            if (node is not None):
                node = self.passthrough_kernel(node)
            if (node is not None):
                node = self.collect_kernel(node)
            if (node is not None):
                new_deq.append(node)
        return new_deq

    def parse(self, node):
        self.token_generator(node)
        nodes = deque(self.tokens)
        nodes = self.__parse(nodes)
        return nodes



class Grammar_Parser(Parser):

    def _set_src(self, src: str):
        super()._set_src(src)
        for rule in Rules:
            if(rule >= 20): #Less than 20 is core parser stuff, greatereq than 20 is inherited class stuff
                func = getattr(self, rule.name)
                func.cache_clear()

    @cache
    def Alphabet_Upper(self, position: int, dummy = None):
        """
        <Alphabet_Upper> = "A"/"B"/"C"/"D"/"E"/"F"/"G"/"H"/"I"/"J"/"K"/"L"/"M"/"N"/"O"/"P"/"Q"/"R"/"S"/"T"/"U"/"V"/"W"/"X"/"Y"/"Z" ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, "A"), (self._TERMINAL, "B"))), (self._TERMINAL, "C"))), (self._TERMINAL, "D"))), (self._TERMINAL, "E"))), (self._TERMINAL, "F"))), (self._TERMINAL, "G"))), (self._TERMINAL, "H"))), (self._TERMINAL, "I"))), (self._TERMINAL, "J"))), (self._TERMINAL, "K"))), (self._TERMINAL, "L"))), (self._TERMINAL, "M"))), (self._TERMINAL, "N"))), (self._TERMINAL, "O"))), (self._TERMINAL, "P"))), (self._TERMINAL, "Q"))), (self._TERMINAL, "R"))), (self._TERMINAL, "S"))), (self._TERMINAL, "T"))), (self._TERMINAL, "U"))), (self._TERMINAL, "V"))), (self._TERMINAL, "W"))), (self._TERMINAL, "X"))), (self._TERMINAL, "Y"))), (self._TERMINAL, "Z"))))

    @cache
    def Alphabet_Lower(self, position: int, dummy = None):
        """
        <Alphabet_Lower> = "a"/"b"/"c"/"d"/"e"/"f"/"g"/"h"/"i"/"j"/"k"/"l"/"m"/"n"/"o"/"p"/"q"/"r"/"s"/"t"/"u"/"v"/"w"/"x"/"y"/"z" ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, "a"), (self._TERMINAL, "b"))), (self._TERMINAL, "c"))), (self._TERMINAL, "d"))), (self._TERMINAL, "e"))), (self._TERMINAL, "f"))), (self._TERMINAL, "g"))), (self._TERMINAL, "h"))), (self._TERMINAL, "i"))), (self._TERMINAL, "j"))), (self._TERMINAL, "k"))), (self._TERMINAL, "l"))), (self._TERMINAL, "m"))), (self._TERMINAL, "n"))), (self._TERMINAL, "o"))), (self._TERMINAL, "p"))), (self._TERMINAL, "q"))), (self._TERMINAL, "r"))), (self._TERMINAL, "s"))), (self._TERMINAL, "t"))), (self._TERMINAL, "u"))), (self._TERMINAL, "v"))), (self._TERMINAL, "w"))), (self._TERMINAL, "x"))), (self._TERMINAL, "y"))), (self._TERMINAL, "z"))))

    @cache
    def Num(self, position: int, dummy = None):
        """
        <Num> = "0"/"1"/"2"/"3"/"4"/"5"/"6"/"7"/"8"/"9" ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, "0"), (self._TERMINAL, "1"))), (self._TERMINAL, "2"))), (self._TERMINAL, "3"))), (self._TERMINAL, "4"))), (self._TERMINAL, "5"))), (self._TERMINAL, "6"))), (self._TERMINAL, "7"))), (self._TERMINAL, "8"))), (self._TERMINAL, "9"))))

    @cache
    def Spaces(self, position: int, dummy = None):
        """
        <Spaces> = "\t"/"\r"/" " ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, "\t"), (self._TERMINAL, "\r"))), (self._TERMINAL, " "))))

    @cache
    def Specials(self, position: int, dummy = None):
        """
        <Specials> = "+"/"*"/"-"/"&"/"!"/"?"/"<"/">"/'"'/"("/")"/"_"/","/"/"/";"/"="/"\\"/"#"/":"/"|"/"."/"'"/"%" ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, "+"), (self._TERMINAL, "*"))), (self._TERMINAL, "-"))), (self._TERMINAL, "&"))), (self._TERMINAL, "!"))), (self._TERMINAL, "?"))), (self._TERMINAL, "<"))), (self._TERMINAL, ">"))), (self._TERMINAL, '"'))), (self._TERMINAL, "("))), (self._TERMINAL, ")"))), (self._TERMINAL, "_"))), (self._TERMINAL, ","))), (self._TERMINAL, "/"))), (self._TERMINAL, ";"))), (self._TERMINAL, "="))), (self._TERMINAL, '\\'))), (self._TERMINAL, "#"))), (self._TERMINAL, ":"))), (self._TERMINAL, "|"))), (self._TERMINAL, "."))), (self._TERMINAL, "'"))), (self._TERMINAL, "%"))))

    @cache
    def ASCII(self, position: int, dummy = None):
        """
        <ASCII> = <Alphabet_Lower>/<Alphabet_Upper>/<Num>/<Spaces>/<Specials> ;
        
        Need to update packratparsergenerator to allow e.g uint[0-27] rather than needing to write everything out manually 
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.Alphabet_Lower, None)), (self._VAR_NAME, (self.Alphabet_Upper, None)))), (self._VAR_NAME, (self.Num, None)))), (self._VAR_NAME, (self.Spaces, None)))), (self._VAR_NAME, (self.Specials, None)))))

    @cache
    def rm_whitespace(self, position: int, dummy = None):
        """
        <rm_whitespace> = (" "/"\n"/"\t")* ;
        """
        return self._SUBEXPRESSION(position, (self._ZERO_OR_MORE, (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._TERMINAL, " "), (self._TERMINAL, "\n"))), (self._TERMINAL, "\t"))))))

    @cache
    def space_seperator(self, position: int, dummy = None):
        """
        <space_seperator> = " " ;
        
        So I can remove meaningless whitespace 
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, " "))

    @cache
    def terminator(self, position: int, dummy = None):
        """
        <terminator> = <space_seperator>*, "\n" ;
        
        Essentially acts as C semicolon for most things
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))), (self._TERMINAL, "\n"))))

    @cache
    def indent(self, position: int, dummy = None):
        """
        <indent> = (" ", " ", " ", " ")/"\t" ;
        """
        return self._SUBEXPRESSION(position, (self._ORDERED_CHOICE, ((self._SUBEXPRESSION, (self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._TERMINAL, " "), (self._TERMINAL, " "))), (self._TERMINAL, " "))), (self._TERMINAL, " ")))), (self._TERMINAL, "\t"))))

    @cache
    def indentation(self, position: int, dummy = None):
        """
        <indentation> = <indent>* ;
        
         Acts as } in C 
        """
        return self._SUBEXPRESSION(position, (self._ZERO_OR_MORE, (self._VAR_NAME, (self.indent, None))))

    @cache
    def operator_assignment(self, position: int, dummy = None):
        """
        <operator_assignment> = <space_seperator>*, "=", <space_seperator>* ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))), (self._TERMINAL, "="))), (self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))))))

    @cache
    def multiuse_seperator(self, position: int, dummy = None):
        """
        <multiuse_seperator> = <space_seperator>*, ",", <space_seperator>* ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))), (self._TERMINAL, ","))), (self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))))))

    @cache
    def int(self, position: int, dummy = None):
        """
        <int> = "-"?, (((!"0", <Num>), <Num>*)/"0") ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._OPTIONAL, (self._TERMINAL, "-")), (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._SUBEXPRESSION, (self._SEQUENCE, ((self._SUBEXPRESSION, (self._SEQUENCE, ((self._NOT_PREDICATE, (self._TERMINAL, "0")), (self._VAR_NAME, (self.Num, None))))), (self._ZERO_OR_MORE, (self._VAR_NAME, (self.Num, None)))))), (self._TERMINAL, "0")))))))

    @cache
    def typedef_int(self, position: int, dummy = None):
        """
        <typedef_int> = "i", "n", "t" ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._TERMINAL, "i"), (self._TERMINAL, "n"))), (self._TERMINAL, "t"))))

    @cache
    def type_int(self, position: int, dummy = None):
        """
        <type_int> = <typedef_int> ;
        """
        return self._SUBEXPRESSION(position, (self._VAR_NAME, (self.typedef_int, None)))

    @cache
    def typedef(self, position: int, dummy = None):
        """
        <typedef> = <type_int> ;
        
        Currently only int 
        """
        return self._SUBEXPRESSION(position, (self._VAR_NAME, (self.type_int, None)))

    @cache
    def variable(self, position: int, dummy = None):
        """
        <variable> = (<Alphabet_Upper>/<Alphabet_Lower>/"_")+ ;
        """
        return self._SUBEXPRESSION(position, (self._ONE_OR_MORE, (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.Alphabet_Upper, None)), (self._VAR_NAME, (self.Alphabet_Lower, None)))), (self._TERMINAL, "_"))))))

    @cache
    def variable_assignment(self, position: int, dummy = None):
        """
        <variable_assignment> = <indentation>, <typedef>, <space_seperator>+, <variable>, <operator_assignment>, <maths> ;
        
        Currently only way to declare a variable
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.indentation, None)), (self._VAR_NAME, (self.typedef, None)))), (self._ONE_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))))), (self._VAR_NAME, (self.variable, None)))), (self._VAR_NAME, (self.operator_assignment, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def variable_modification(self, position: int, dummy = None):
        """
        <variable_modification> = <indentation>, <variable>, <operator_assignment>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.indentation, None)), (self._VAR_NAME, (self.variable, None)))), (self._VAR_NAME, (self.operator_assignment, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def sym_add(self, position: int, dummy = None):
        """
        <sym_add> = "+" ;
        
         Maths start
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "+"))

    @cache
    def sym_subtract(self, position: int, dummy = None):
        """
        <sym_subtract> = "-" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "-"))

    @cache
    def sym_modulo(self, position: int, dummy = None):
        """
        <sym_modulo> = "%" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "%"))

    @cache
    def sym_division(self, position: int, dummy = None):
        """
        <sym_division> = "/" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "/"))

    @cache
    def sym_multiplication(self, position: int, dummy = None):
        """
        <sym_multiplication> = "*" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "*"))

    @cache
    def sym_power(self, position: int, dummy = None):
        """
        <sym_power> = "*", "*" ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._TERMINAL, "*"), (self._TERMINAL, "*"))))

    @cache
    def sym_open_bracket(self, position: int, dummy = None):
        """
        <sym_open_bracket> = "(" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, "("))

    @cache
    def sym_close_bracket(self, position: int, dummy = None):
        """
        <sym_close_bracket> = ")" ;
        """
        return self._SUBEXPRESSION(position, (self._TERMINAL, ")"))

    @cache
    def add(self, position: int, dummy = None):
        """
        <add> = <maths_argument>, <sym_add>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_add, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def subtract(self, position: int, dummy = None):
        """
        <subtract> = <maths_argument>, <sym_subtract>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_subtract, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def modulo(self, position: int, dummy = None):
        """
        <modulo> = <maths_argument>, <sym_modulo>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_modulo, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def division(self, position: int, dummy = None):
        """
        <division> = <maths_argument>, <sym_division>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_division, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def multiplication(self, position: int, dummy = None):
        """
        <multiplication> = <maths_argument>, <sym_multiplication>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_multiplication, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def power(self, position: int, dummy = None):
        """
        <power> = <maths_argument>, <sym_power>, <maths> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.maths_argument, None)), (self._VAR_NAME, (self.sym_power, None)))), (self._VAR_NAME, (self.maths, None)))))

    @cache
    def subexpression(self, position: int, dummy = None):
        """
        <subexpression> = <sym_open_bracket>, <maths>, <sym_close_bracket> ;
        
        Maths end
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.sym_open_bracket, None)), (self._VAR_NAME, (self.maths, None)))), (self._VAR_NAME, (self.sym_close_bracket, None)))))

    @cache
    def maths_argument(self, position: int, dummy = None):
        """
        <maths_argument> = <space_seperator>*, (<subexpression>/<int>/<variable>), <space_seperator>* ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))), (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.subexpression, None)), (self._VAR_NAME, (self.int, None)))), (self._VAR_NAME, (self.variable, None))))))), (self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))))))

    @cache
    def maths(self, position: int, dummy = None):
        """
        <maths> = <space_seperator>*, (<add>/<subtract>/<power>/<multiplication>/<division>/<modulo>/<maths_argument>), <space_seperator>* ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))), (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.add, None)), (self._VAR_NAME, (self.subtract, None)))), (self._VAR_NAME, (self.power, None)))), (self._VAR_NAME, (self.multiplication, None)))), (self._VAR_NAME, (self.division, None)))), (self._VAR_NAME, (self.modulo, None)))), (self._VAR_NAME, (self.maths_argument, None))))))), (self._ZERO_OR_MORE, (self._VAR_NAME, (self.space_seperator, None))))))

    @cache
    def special_instructions(self, position: int, dummy = None):
        """
        <special_instructions> = <syscall> ;
        """
        return self._SUBEXPRESSION(position, (self._VAR_NAME, (self.syscall, None)))

    @cache
    def syscall_def(self, position: int, dummy = None):
        """
        <syscall_def> = "s", "y", "s", "c", "a", "l", "l" ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._TERMINAL, "s"), (self._TERMINAL, "y"))), (self._TERMINAL, "s"))), (self._TERMINAL, "c"))), (self._TERMINAL, "a"))), (self._TERMINAL, "l"))), (self._TERMINAL, "l"))))

    @cache
    def syscall(self, position: int, dummy = None):
        """
        <syscall> = <indentation>, <syscall_def>, (<space_seperator>, (<int>/<variable>))* ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.indentation, None)), (self._VAR_NAME, (self.syscall_def, None)))), (self._ZERO_OR_MORE, (self._SUBEXPRESSION, (self._SEQUENCE, ((self._VAR_NAME, (self.space_seperator, None)), (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._VAR_NAME, (self.int, None)), (self._VAR_NAME, (self.variable, None))))))))))))

    @cache
    def grammar(self, position: int, dummy = None):
        """
        <grammar> = <rm_whitespace>, ((<syscall>/<variable_assignment>/<variable_modification>), <terminator>)*, (<syscall>/<variable_assignment>/<variable_modification>)?, <rm_whitespace> ;
        """
        return self._SUBEXPRESSION(position, (self._SEQUENCE, ((self._SEQUENCE, ((self._SEQUENCE, ((self._VAR_NAME, (self.rm_whitespace, None)), (self._ZERO_OR_MORE, (self._SUBEXPRESSION, (self._SEQUENCE, ((self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.syscall, None)), (self._VAR_NAME, (self.variable_assignment, None)))), (self._VAR_NAME, (self.variable_modification, None))))), (self._VAR_NAME, (self.terminator, None)))))))), (self._OPTIONAL, (self._SUBEXPRESSION, (self._ORDERED_CHOICE, ((self._ORDERED_CHOICE, ((self._VAR_NAME, (self.syscall, None)), (self._VAR_NAME, (self.variable_assignment, None)))), (self._VAR_NAME, (self.variable_modification, None)))))))), (self._VAR_NAME, (self.rm_whitespace, None)))))