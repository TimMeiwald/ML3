
from tests.conftest import compiler_test
from ml3.compiler.symbol_table import SymbolTable
from ml3.compiler.compiler import Compiler

def test_compiler_1():
    node = compiler_test(1)
    s = SymbolTable()
    s.symbolize(node)
    s.get_variable("status_code")
    c = Compiler(s)
    c.compile(node)
    print(c.TEXT)
    binary = c.TEXT.get_binary()
    print("\n")
    print(binary)
    print("\n")
    print(f"BSS START: {c._bss_start}")
    print(f"TEXT Start: {c._text_start}")
    x = c.construct_elf_binary()

    print(x._generate_file())
    x = x.write_to_file("TestExecutable.elf")
    assert 0 == 1

# def test_compiler_2():
#     node = compiler_test(2)

# def test_compiler_3():
#     node = compiler_test(3)
#     c = Compiler()
#     c.compile(node)
#     assert 0 == 1