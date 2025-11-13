from enum import Enum
from typing import Dict


class AddressingMode(Enum):
    I, D, N, S, SF, X, SX, SFX = range(8)

    def as_AAA(self) -> int:
        return self.value

    def as_A(self) -> int:
        match self.value:
            case AddressingMode.I.value:
                return 0
            case AddressingMode.X.value:
                return 1
        message = f"Invalid addressing mode for A type: {self.name}"
        raise TypeError(message)


class InstructionType(Enum):
    M = "M"
    R = "R"
    A_ix = "A_ix"
    AAA_all = "AAA_all"
    AAA_i = "AAA_i"
    RAAA_all = "RAAA_all"
    RAAA_noi = "RAAA_noi"

    def allows_addressing_mode(self, am: AddressingMode):
        # Default to no allowed addressing modes
        return am in {
            "A_ix": {AddressingMode.I, AddressingMode.X},
            "AAA_all": {am for am in AddressingMode},
            "AAA_i": {AddressingMode.I},
            "RAAA_all": {am for am in AddressingMode},
            "RAAA_noi": {am for am in AddressingMode} - {AddressingMode.I},
        }.get(self.value, {})


M_INSTRUCTIONS = [
    "RET",
    "NOP",
    "SRET",
    "MOVFLGA",
    "MOVAFLG",
    "MOVSPA",
    "MOVASP",
]
R_PREFIXES = ["NOT", "NEG", "ASL", "ASR", "ROL", "ROR"]
BR_INSTRUCTIONS = [
    f"BR{suffix}"
    for suffix in ["", "LE", "LT", "EQ", "NE", "GE", "GT", "V", "C"]
]
A_IX_INSTRUCTIONS = BR_INSTRUCTIONS + ["CALL"]
RAAA_prefixes = ["ADD", "SUB", "AND", "OR", "XOR", "CPW", "CPB", "LDW", "LDB"]

INSTRUCTION_TYPES: Dict[str, InstructionType] = {
    **{instr: InstructionType.M for instr in M_INSTRUCTIONS},
    **{f"{instr}A": InstructionType.R for instr in R_PREFIXES},
    **{f"{instr}X": InstructionType.R for instr in R_PREFIXES},
    **{instr: InstructionType.A_ix for instr in A_IX_INSTRUCTIONS},
    "SCALL": InstructionType.AAA_all,
    "ADDSP": InstructionType.AAA_all,
    "SUBSP": InstructionType.AAA_all,
    **{f"{instr}A": InstructionType.RAAA_all for instr in RAAA_prefixes},
    **{f"{instr}X": InstructionType.RAAA_all for instr in RAAA_prefixes},
    "STWA": InstructionType.RAAA_noi,
    "STWX": InstructionType.RAAA_noi,
    "STBA": InstructionType.RAAA_noi,
    "STBX": InstructionType.RAAA_noi,
}

DEFAULT_ADDRESSING_MODES: Dict[str, AddressingMode] = {
    **{instr: AddressingMode.I for instr in A_IX_INSTRUCTIONS},
}


BITS: Dict[str, int] = {
    # M-type instructions
    "RET": 0x01,
    "SRET": 0x02,
    "MOVFLGA": 0x03,
    "MOVAFLG": 0x04,
    "MOVSPA": 0x05,
    "MOVASP": 0x06,
    "NOP": 0x07,
    # Intentional gap in opcode space between M- and R-type instructions
    # R-type instructions
    "NEGA": 0x18,
    "NEGX": 0x19,
    "ASLA": 0x1A,
    "ASLX": 0x1B,
    "ASRA": 0x1C,
    "ASRX": 0x1D,
    "NOTA": 0x1E,
    "NOTX": 0x1F,
    "ROLA": 0x20,
    "ROLX": 0x21,
    "RORA": 0x22,
    "RORX": 0x23,
    # A-type instructions
    "BR": 0x24,
    "BRLE": 0x26,
    "BRLT": 0x28,
    "BREQ": 0x2A,
    "BRNE": 0x2C,
    "BRGE": 0x2E,
    "BRGT": 0x30,
    "BRV": 0x32,
    "BRC": 0x34,
    "CALL": 0x36,
    # AAA-type instructions
    "SCALL": 0x38,
    "ADDSP": 0x40,
    "SUBSP": 0x48,
    # RAAA-type instructions
    "ADDA": 0x50,
    "ADDX": 0x58,
    "SUBA": 0x60,
    "SUBX": 0x68,
    "ANDA": 0x70,
    "ANDX": 0x78,
    "ORA": 0x80,
    "ORX": 0x88,
    "XORA": 0x90,
    "XORX": 0x98,
    "CPWA": 0xA0,
    "CPWX": 0xA8,
    "CPBA": 0xB0,
    "CPBX": 0xB8,
    "LDWA": 0xC0,
    "LDWX": 0xC8,
    "LDBA": 0xD0,
    "LDBX": 0xD8,
    "STWA": 0xE0,
    "STWX": 0xE8,
    "STBA": 0xF0,
    "STBX": 0xF8,
}


def as_int(mnemonic: str, am: AddressingMode | None = None) -> int:
    mnemonic = mnemonic.upper()
    bit_pattern, mn_type = BITS[mnemonic], INSTRUCTION_TYPES[mnemonic]

    if mn_type == InstructionType.M or mn_type == InstructionType.R:
        return bit_pattern
    elif mn_type == InstructionType.A_ix:
        return bit_pattern | (0 if am is None else am.as_A())
    else:
        return bit_pattern | (0 if am is None else am.as_AAA())
