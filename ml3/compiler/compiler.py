from ml3.parser.parser import Rules
from ml3.compiler.enums import RawType
from ml3.compiler.symbol_table import SymbolTable
import ml3.compiler.x86_64 as asm
from enum import IntEnum
from collections import deque
from elfgenerator.Binary import Binary
from elfgenerator.ELF_Segment_Utils import Segment
from elfgenerator.ELF import x86_64
class Registers(IntEnum):
    """Probably wrong order Idk need to check properly"""
    EAX = 0
    ECX = 1
    EDX = 2
    EBX = 3
    ESP = 4
    EBP = 5
    ESI = 6
    EDI = 7
    R8D = 8
    R9D = 9
    R10D = 10
    R11D = 11
    R12D = 12
    R13D = 13
    R14D = 14
    R15D = 15



class Compiler():
    
    def __init__(self, symbol_table: SymbolTable):
        self._functions_ = {Rules.variable_assignment: self._variable_assignment,
                            Rules.variable_modification: self._variable_modification, 
                            Rules.syscall: self._syscall,
                }
        self._symbol_table_ = symbol_table
        self.TEXT = TEXT()

        # ELF Prelude is 64 Bytes
        # Each Program Header is 56 Bytes
        # For now have two Program headers of 56 Bytes each
        # So BSS will start after 64+56+56 bytes
        # Text will start after BSS which has a known size
        self._bss_start = 64+56*2
        self._text_start = self._bss_start + self._symbol_table_._BSS_.raw_size
        self._symbol_table_.set_offsets(0x402000)
        #self._symbol_table_.set_offsets(self._bss_start)

    def compile(self, grammar_node):
        assert grammar_node.type == Rules.grammar

        print("################ COMPILER START ###################")
        print(self._symbol_table_)
        for node in grammar_node.children:
            func = self._functions_[node.type]
            func(node)

    def _variable_assignment(self, node):
        assert node.type == Rules.variable_assignment
        type = node.children[0].type
        name = node.children[1].content
        value = node.children[2].content

        vname, vsize, vtype, vaddress = self._symbol_table_.get_variable(name)

        if(type == Rules.type_int and vtype == RawType.INT):
            value = int(value)
            #print(f"ASSIGN {value} to Address: {vaddress}")
            self.TEXT.push_instr(asm.load_const_to_register_displacement_only_32_bit(0, value), "; load constant to register EAX")
            self.TEXT.push_instr(asm.load_register_value_to_memory_address_only_32_bit(0, vaddress), f"; load register value from EAX to memory address {vaddress}")
            return
        raise Exception

    def _variable_modification(self, node):
        assert node.type == Rules.variable_modification
        name = node.children[0].content
        value = node.children[1].content
        name, size, type, address = self._symbol_table_.get_variable(name)

        if(type == RawType.INT):
            value = int(value)
            #print(f"ASSIGN {value} to Address: {address}")
            self.TEXT.push_instr(asm.load_const_to_register_displacement_only_32_bit(0, value), "; load constant to register EAX")
            self.TEXT.push_instr(asm.load_register_value_to_memory_address_only_32_bit(0, address), f"; load register value from EAX to memory address {address}")
            return
        raise Exception

    def _syscall(self, node):
        """
        To make a system call in 64-bit Linux, place the system call number in rax ,
        then its arguments, in order, in rdi , rsi , rdx , r10 , r8 , and r9 , then invoke syscall.
        https://unix.stackexchange.com/questions/421910/why-did-the-system-call-registers-and-order-change-from-intel-32bit-to-64bit

        Need to check an actual source but this will do for now
        """
            
        arg_order = [Registers.EAX, Registers.EDI, Registers.ESI, Registers.EDX, Registers.R10D, Registers.R8D, Registers.R9D]
        assert node.type == Rules.syscall
        try:
            for index, child in enumerate(node.children):
                if(child.type == Rules.variable):
                    name = child.content
                    name, size, type, address = self._symbol_table_.get_variable(name)
                    register = arg_order[index]
                    self.TEXT.push_instr(asm.load_memory_value_to_register_displacement_only_32_bit(register, address), f"; load memory value from address: {address} into register: {register.name}")
                elif(child.type == Rules.int):
                    register = arg_order[index]
                    self.TEXT.push_instr(asm.load_const_to_register_displacement_only_32_bit(register, int(child.content)), f"; load constant {child.content} to register {register.name}")
        except IndexError:
            raise Exception("Too many values for syscall. Can only have 1 syscall parameter and 6 arguments maximum for a total of 7 registers.")
        self.TEXT.push_instr(asm.syscall(), "; syscall")


    def construct_elf_binary(self):
        ELF = x86_64()
        # BSS Data is Zero Initialized Aka no data but memory is allocated in program header
        segment_bss_size = self._symbol_table_._BSS_.raw_size 
        segment_text = self.TEXT.get_binary()
        print(f"TEXT Segment Size: {segment_text.size}")
        # TODO FIX THIS SHIT
        #p_header_text = Segment(1, 0,start_address+segment_bss_size,start_address+segment_bss_size, sizeof_text, sizeof_text, 0x5, 0)
        #p_header_data = Segment(1, 0,start_address,start_address, 0, segment_bss_size, 0x4, 0)
        #p_header_text = Segment(1, 0x001000,0x401000,0x401000,0x001000, 0x001000, 0x5, 2**12)
        #p_header_data = Segment(1, 0x002000,0x402000,0x402000,0x001000, 0x001000, 0x2, 2**12)
        
        # ELF.add_program_segment([p_header_text.binary(), self.TEXT.get_binary()])
        # ELF.add_program_segment([p_header_data.binary(), Binary(0,0,0)])
        
        ELF.set_entry_point(0x402000) # Temp ideally need to get it from somewhere
        ELF.add_segment(7, len(segment_text), len(segment_text), segment_text)
        ELF.add_segment(7, 0, 0x001000, None)
        bin = ELF.generate_executable().binary()
        return bin

class TEXT():


    def __init__(self):
        self.instr_stack = deque()
        self.comment_stack = deque()

    def push_instr(self, instr: Binary, comment: str = ""):
        self.instr_stack.append(instr)
        self.comment_stack.append(comment)

    def __repr__(self):
        response = ""
        padding = 40
        for index, i in enumerate(self.instr_stack):
            instr = i.__repr__()
            comment = self.comment_stack[index]
            response += instr + (padding-len(instr))*" " + comment + "\n"
        return response
    
    def get_binary(self):
        bin = Binary(0,0,0)
        for i in self.instr_stack:
            bin += i
        return bin