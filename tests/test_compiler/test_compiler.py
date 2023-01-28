
from tests.conftest import compiler_test
from ml3.compiler.symbol_table import SymbolTable
from ml3.compiler.compiler import Compiler
from os import getcwd
from os.path import join


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

    #print(x._generate_file()) # Not stateless affects something not good
    with open(join(getcwd(), "tests", "test_compiler", "Test1"), "wb") as fp: # Can be used to write it out as a binary file
        fp.write(x)
    #print(c.construct_elf_binary()._generate_file())
    assert 1 == 1

def test_compiler_2():
    node = compiler_test(2)
    s = SymbolTable()
    s.symbolize(node)
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
    print(x)

    #print(x._generate_file()) # Not stateless affects something not good
    #print(c.construct_elf_binary()._generate_file())
    with open(join(getcwd(), "tests", "test_compiler", "Test3"), "wb") as fp: # Can be used to write it out as a binary file
        fp.write(x)
    assert 0 == 1

def test_compiler_3():
    node = compiler_test(3)
    s = SymbolTable()
    s.symbolize(node)
    #s.get_variable("status_code")
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
    print(x)

    #print(x._generate_file()) # Not stateless affects something not good
    #print(c.construct_elf_binary()._generate_file())
    with open(join(getcwd(), "tests", "test_compiler", "Test3"), "wb") as fp: # Can be used to write it out as a binary file
        fp.write(x)
    assert 1 == 1