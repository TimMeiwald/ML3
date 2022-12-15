import pytest
from ml3.parser.parser import Grammar_Parser

class Test_Syscall():

    @pytest.mark.parametrize("src, answer, position", [('syscall 80 0 5', True, 14), 
    ('syscall', True, 7), 
    ('syscall x y hello', True, 17), 
    ('syscall x', True, 9), 
    ('syscall there', True, 13), 
    ]) 
    def test_syscall(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.syscall)
        if(node != None):
            node.pretty_print()
        assert bool == answer
        assert resultant_position == position