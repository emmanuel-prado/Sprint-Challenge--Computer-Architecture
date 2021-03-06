"""CPU functionality."""

import sys
import time


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8  # 8 general 8 bit registers
        # ram is the computer's memory, can hold 256 bytes of RAM total
        self.ram = [0] * 256
        self.PC = 0  # address of the currently executing instruction
        self.SP = 243  # Stack Pointer
        self.reg[7] = self.SP  # Stack Pointer in register
        self.dispatch_table = {"1": self.handle_HLT,
                               "130": self.handle_LDI,
                               "71": self.handle_PRN,
                               "160": self.handle_ADD,
                               "162": self.handle_MUL,
                               "69": self.handle_PUSH,
                               "70": self.handle_POP,
                               "80": self.handle_CALL,
                               "17": self.handle_RET,
                               "167": self.handle_CMP,
                               "84": self.handle_JMP,
                               "85": self.handle_JEQ,
                               "86": self.handle_JNE
                               }
        self.FL = 0b00000000

    def handle_HLT(self, op_a, op_b):
        sys.exit(0)

    def handle_LDI(self, op_a, op_b):
        self.reg[op_a] = op_b
        self.PC += 3

    def handle_PRN(self, op_a, op_b):
        print(self.reg[op_a])
        self.PC += 2

    def handle_ADD(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)
        self.PC += 3

    def handle_MUL(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        self.PC += 3

    def handle_PUSH(self, op_a, op_b):
        self.SP -= 1
        self.ram[self.SP] = self.reg[op_a]
        self.PC += 2

    def handle_POP(self, op_a, op_b):
        self.reg[op_a] = self.ram[self.SP]
        self.SP += 1
        self.PC += 2

    def handle_CALL(self, op_a, op_b):
        self.PC += 2
        self.ram[self.SP] = self.PC
        self.PC = self.reg[op_a]

    def handle_RET(self, op_a, op_b):
        self.PC = self.ram[self.SP]
        self.SP += 1

    def handle_CMP(self, op_a, op_b):
        if self.reg[op_a] == self.reg[op_b]:
            self.FL = 0b00000001
            self.PC += 3
        elif self.reg[op_a] < self.reg[op_b]:
            self.FL = 0b00000100
            self.PC += 3
        elif self.reg[op_b] > self.reg[op_a]:
            self.FL = 0b00000010
            self.PC += 3
        else:
            self.FL = 0b00000000
            self.PC += 3

    def handle_JMP(self, op_a, op_b):
        self.PC = self.reg[op_a]

    def handle_JEQ(self, op_a, op_b):
        mask = 0b00000111
        if self.FL & mask == 1:
            self.PC = self.reg[op_a]
        else:
            self.PC += 2

    def handle_JNE(self, op_a, op_b):
        if self.FL != 1:
            self.PC = self.reg[op_a]
        else:
            self.PC += 2

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    if line == "\n":
                        continue
                    else:
                        line_split = line.split("#")
                        if line_split[0] == '':
                            continue
                        string = line_split[0].strip()
                        instruction = int(string, 2)
                        self.ram[address] = instruction
                        address += 1
        except:
            raise ValueError("Please load a valid program")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            value = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "AND":
            value = self.reg[reg_a] & self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "OR":
            value = self.reg[reg_a] | self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "XOR":
            value = self.reg[reg_a] ^ self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "NOT":
            value = self.reg[reg_a] & self.reg[reg_b]
            self.reg[reg_a] = ~value
        elif op == "SHL":
            value = self.reg[reg_a] << self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "SHR":
            value = self.reg[reg_a] >> self.reg[reg_b]
            self.reg[reg_a] = value
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                raise ValueError("Can't divide by zero")
            value = self.reg[reg_a] % self.reg[reg_b]
            self.reg[reg_a] = value
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        # MAR (Memory Address Register) contains the address being read from
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        # MAR (Memory Address Register) contains the address being written to
        # MDR (Memory Data Register) contains the data to write
        self.ram[MAR] = MDR

    def hlt(self):
        sys.exit()

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02d %02d | %02d %02d %02d |" % (
            self.PC,
            self.FL,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02d" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            self.trace()
            # time.sleep(0.5)
            # The instruction pointed to by the PC is fetched from RAM, decoded, and executed
            # IR = Instruction Register
            IR = self.ram[self.PC]
            # use ram_read() to read the bytes at PC+1 and PC+2 into variables operand_a and operand_b
            # in case the instruction needs them
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)
            self.dispatch_table[str(IR)](operand_a, operand_b)
