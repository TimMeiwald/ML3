import pytest
from ml3.parser.parser import Grammar_Parser

class Test_variable():

    @pytest.mark.parametrize("src, answer, position", [('a', True, 1), 
    ("hello", True, 5), 
    ("_hello", True, 6),
    ("-hello", False, 0),
    ("HELLO", True, 5),
    ('Hey4', True, 3),]) 
    def test_variable(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.variable)
        assert bool == answer
        assert resultant_position == position
        