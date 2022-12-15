import pytest
from ml3.parser.parser import Grammar_Parser

class Test_variable_assignment():

    @pytest.mark.parametrize("src, answer, position", [('Int a = 5', False, 0), 
    ("int a = 5", True, 9), 
    ("    int a = 5", True, 13), 
    ("int a = 5.5", True, 9),
    ("inta=5", False, 0),
    ("int a=6", True, 7),
    ('int a=6/7', True, 9),
    ('int a=6/7*2', True, 11),
    ('int a=6/7*2+29', True, 14),
    ]) 
    def test_variable(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.variable_assignment)
        if(node != None):
            node.pretty_print()
        assert bool == answer
        assert resultant_position == position