from ml3.parser.parser import Rules
from ml3.compiler.enums import RawType



class SymbolTable():

    def __init__(self):
        self._functions_ = {Rules.variable_assignment: self._variable_assignment,
                }
        self._BSS_ = BSS()

    def symbolize(self, grammar_node):
        assert grammar_node.type == Rules.grammar
        for node in grammar_node.children:
            try: 
                func = self._functions_[node.type]
                func(node)
                #print(self._BSS_)
            except:
                pass
            
    def _variable_assignment(self, node):
        # Need a flag for local scopes if it becomes an issue. 
        assert node.type == Rules.variable_assignment
        type = node.children[0].type
        name = node.children[1].content

        if(type == Rules.type_int):
            size = 4 # 4 bytes 32 bit only for now
            self._BSS_.set_variable(name, size, RawType.INT)
            return 
        raise NotImplementedError
    
    def get_variable(self, name):
        # Once I have multiple segments need to check them all but don't right now. 
        return self._BSS_.get_variable(name=name)
    
    def __repr__(self):
        response = "Symbol Table\n"
        response += self._BSS_.__repr__()
        return response

    def set_offsets(self, bss_offset):
        self._BSS_.set_offset(bss_offset)


class BSS():
    "Uninitialized Global Segment"

    def __init__(self):
        self.__stack__ = []
        self._lookup_position_dict_ = {}
        self.raw_size = 0
        self.position = 0
    
    def set_variable(self, name: str, size: str, type: RawType):
        self.__stack__.append([name, size, type, self.raw_size])
        self._lookup_position_dict_[name] = len(self.__stack__) -1
        self.raw_size += size
        self.position += 1
        return self.position - 1
    
    def update_variable(self, position, value):
        self.__stack__[position][4] = value

    def get_variable(self, position_in_arr: int = None, name: str = None):
        if(position_in_arr == None and name == None):
            raise Exception("One or the other argument must have a value")
        if(name != None):
            position_in_arr = self._lookup_position_dict_[name]
        return self.__stack__[position_in_arr]
            
    def __repr__(self):
        response = f"    BSS, Total Size in Bytes = {self.raw_size}\n"
        for i in self.__stack__:
            response += "        " + str(i) + "\n"
        return response
    
    def set_offset(self, offset: int):
        for item in self.__stack__:
            item[3] = item[3] + offset