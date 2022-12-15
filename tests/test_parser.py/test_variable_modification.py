import pytest
from ml3.parser.parser import Grammar_Parser

class Test_variable_assignment():

    @pytest.mark.parametrize("src, answer, position", [('a = 5', True, 5), 
    ("a = 5", True, 5), 
    ("    a = 5", True, 9), 
    ("a = 5.5", True, 5),
    ("a=6", True, 3),
    ('a=6/7', True, 5),
    ('a=6/7*2', True, 7),
    ('a=6/7*2+29', True, 10),
    ]) 
    def test_variable(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.variable_modification)
        if(node != None):
            node.pretty_print()
        assert bool == answer
        assert resultant_position == position