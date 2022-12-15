from elfgenerator.Binary import Binary
from enum import IntEnum


def syscall():
    return Binary(0x050F, 2, 2)

def modrm(mod: int, r: int, m: int):
    """Intel Volume 2A 2-6
    
    r changes row
    m changes column
    Not sure which way it's meant to be as long as you're consistent works."""
    mod = mod*2**6
    m = m*2**3
    return mod+r+m



def load_const_to_register_displacement_only_32_bit(register: int, constant):
    binary = Binary(0,0,0)
    if(register >= 8):
        binary = Binary(0x41, 1, 1)
        register -= 8
    binary += Binary(modrm(2, register, 7), 1, 1) + Binary(constant, 4, 4)
    return binary

def load_memory_value_to_register_displacement_only_32_bit(register: int, address):
    if(register >= 8):
        pre_prefix = Binary(0x44, 1, 1)
        register -= 8
    else:
        pre_prefix = Binary(0,0,0)
    prefix = Binary(0x8b, 1, 1)
    value = modrm(0, 4, register)
    register = Binary(value, 1, 1)
    suffix = Binary(0x25, 1, 1)
    address = Binary(address, 4, 4)
    return pre_prefix + prefix + register + suffix + address 

def load_register_value_to_memory_address_only_32_bit(register: int, address):
    if(register >= 8):
        pre_prefix = Binary(0x44, 1, 1)
        register -= 8
    else:
        pre_prefix = Binary(0,0,0)
    prefix = Binary(0x89, 1, 1)
    value = modrm(0, 4, register)
    register = Binary(value, 1, 1)
    suffix = Binary(0x25, 1, 1)
    address = Binary(address, 4, 4)
    return pre_prefix + prefix + register + suffix + address 


if __name__ == "__main__":
    for i in range(0, 8):
        print(load_register_value_to_memory_address_only_32_bit(i, 0x40))
    
