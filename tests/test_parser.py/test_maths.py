import pytest
from ml3.parser.parser import Grammar_Parser

class Test_maths():

    @pytest.mark.parametrize("src, answer, position", [('a', True, 1), 
    ("5", True, 1), 
    ("5.55", True, 1),
    ("'a'", False, 0),
    ('"string"', False, 0),
    ("1235.61", True, 4), # Shoulw read first 4 chars as an int
    ('-0', True, 2), 
    ("", False, 0),
    ("*", False, 0), 
    ("-1245", True, 5),
    ("-1", True, 2),
    ("**", False, 0),
    ("-1235.61", True, 5)]) 
    def test_int(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.maths)
        assert bool == answer
        assert resultant_position == position


    @pytest.mark.parametrize("src, answer, position", [('5 + 79', True, 6), 
    ("5/29", True, 4), 
    ("10-738", True, 6),
    ("'a'", False, 0),
    ('"string"', False, 0),
    ("-25*-5", True, 6), # Shoulw read first 4 chars as an int
    ('-0', True, 2), 
    ("", False, 0),
    ("*", False, 0), 
    ("-25**2", True, 6),
    ("-1", True, 2),
    ("4**a", True, 4),
    ("-57%-3", True, 6)]) 
    def test_int_maths(self, parser, src, answer, position): # Note parser is provided by module fixture in conftest.py
        resultant_position, bool, node = parser.parse(src, parser.maths)
        assert bool == answer
        assert resultant_position == position