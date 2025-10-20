
# AssemblyTranslator: convert simple IR (dict-based) into x86-64 NASM assembly.



import re

class AssemblyTranslator:
    def __init__(self):
        self.asm_output = []
        self.vars = set()
        self.labels = set()
        self.fmt_label = "fmt_int"
        # Relocation prefix for static access
        self.mem_prefix = "rel "

    _ident_re = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

    def _is_ident(self, s):
        return isinstance(s, str) and bool(self._ident_re.match(s))

    def _is_int(self, s):
        return isinstance(s, int)

    def _collect_symbols(self, ir):
        self.vars.clear()
        self.labels.clear()
        for instr in ir:
            op = instr.get('op')
            s1 = instr.get('src1')
            s2 = instr.get('src2')
            d = instr.get('dst')
            if op == 'mark':
                if isinstance(s1, str):
                    self.labels.add(s1)
            else:
                for x in (s1, s2, d):
                    if self._is_ident(x):
                        # treat labels (LabelN) as labels only when used with mark/jump
                        # keep everything else as vars
                        self.vars.add(x)

    def _repr_operand_load(self, operand, target_reg):
        """
        Produce assembly lines to load 'operand' into target_reg.
        Returns list of lines.
        """
        lines = []
        if self._is_int(operand):
            lines.append(f"    mov {target_reg}, {operand}")
        elif self._is_ident(operand):
            lines.append(f"    mov {target_reg}, QWORD [{self.mem_prefix}{operand}]")
        else:
            # Fallback: try to print repr
            lines.append(f"    ; unsupported operand {operand!r}, zeroing")
            lines.append(f"    mov {target_reg}, 0")
        return lines

    def translate(self, ir_code):
        self._collect_symbols(ir_code)
        out = []

        # Data section: format string and variables
        out.append("section .data")
        out.append(f"{self.fmt_label}: db \"%d\", 10, 0")
        # declare each variable/temp as 8 byte (dq) initialized to 0
        for v in sorted(self.vars):
            out.append(f"{v}: dq 0")
        out.append("")  # blank line

        # Text section and externs
        out.append("section .text")
        out.append("extern printf")
        out.append("global main")
        out.append("")  # blank line

        # Function / program entry
        out.append("main:")
        out.append("    push rbp")
        out.append("    mov rbp, rsp")
        out.append("")  # prologue

        # Translate IR
        for instr in ir_code:
            op = instr.get('op')
            s1 = instr.get('src1')
            s2 = instr.get('src2')
            d = instr.get('dst')

            if op == 'assign':
                # assign src1 -> d
                if self._is_int(s1):
                    out.append(f"    mov rax, {int(s1)}")
                else:
                    out += self._repr_operand_load(s1, "rax")
                if self._is_ident(d):
                    out.append(f"    mov QWORD [{self.mem_prefix}{d}], rax")
                else:
                    out.append(f"    ; assign to non-ident {d!r}")
                out.append("")

            elif op in ('+', '-', '*', '/', '%'):
                # dst = s1 op s2
                out += self._repr_operand_load(s1, "rax")
                out += self._repr_operand_load(s2, "rbx")
                if op == '+':
                    out.append("    add rax, rbx")
                elif op == '-':
                    out.append("    sub rax, rbx")
                elif op == '*':
                    out.append("    imul rax, rbx")
                elif op == '/':
                    out.append("    cqo")               # sign extend rax -> rdx:rax
                    out.append("    idiv rbx")         # quotient in rax
                elif op == '%':
                    out.append("    cqo")
                    out.append("    idiv rbx")
                    out.append("    mov rax, rdx")    # remainder in rdx
                if self._is_ident(d):
                    out.append(f"    mov QWORD [{self.mem_prefix}{d}], rax")
                out.append("")

            elif op in ('<', '<=', '>', '>=', '==', '!='):
                # comparison -> dst (0 or 1)
                out += self._repr_operand_load(s1, "rax")
                out += self._repr_operand_load(s2, "rbx")
                out.append("    cmp rax, rbx")
                set_instr = {
                    '<': 'setl', '<=': 'setle', '>': 'setg', '>=': 'setge',
                    '==': 'sete', '!=': 'setne'
                }[op]
                out.append(f"    {set_instr} al")
                out.append("    movzx rax, al")
                if self._is_ident(d):
                    out.append(f"    mov QWORD [{self.mem_prefix}{d}], rax")
                out.append("")

            elif op == 'mark':
                lbl = s1
                out.append(f"{lbl}:")
                out.append("")

            elif op == 'jump':
                lbl = s1
                out.append(f"    jmp {lbl}")
                out.append("")

            elif op == 'jump_if_false':
                # s1 is condition variable (or immediate), s2 is label to jump to
                cond = s1
                lbl = s2
                if self._is_int(cond):
                    out.append(f"    mov rax, {int(cond)}")
                else:
                    out += self._repr_operand_load(cond, "rax")
                out.append("    cmp rax, 0")
                out.append(f"    je {lbl}")
                out.append("")

            elif op == 'output':
                # call printf(fmt, value)
                val = s1
                # load value into rsi, format into rdi
                if self._is_int(val):
                    out.append(f"    mov rsi, {int(val)}")
                else:
                    out += self._repr_operand_load(val, "rsi")
                    # mov rsi, [val] left rsi contains value when using repr_operand_load
                    # repr_operand_load uses mov rsi, [rel val] already
                out.append(f"    lea rdi, [rel {self.fmt_label}]")
                out.append("    xor rax, rax")
                out.append("    call printf")
                out.append("")

            elif op == 'return':
                # src1 may be None or an expression/variable
                if s1 is None:
                    out.append("    mov rax, 0")
                elif self._is_int(s1):
                    out.append(f"    mov rax, {int(s1)}")
                else:
                    out += self._repr_operand_load(s1, "rax")
                out.append("    ; function return")
                out.append("")  # We'll emit epilogue and ret after processing all IR

            else:
                out.append(f"    ; unhandled op: {op} ({instr})")
                out.append("")

        # Epilogue and return
        out.append("    mov rsp, rbp")
        out.append("    pop rbp")
        out.append("    ret")
        out.append("")

        self.asm_output = out
        return out


if __name__ == "__main__":
    # small self-test / demo IR (for the fib example you'd produce a larger IR)
    demo_ir = [
        {'op': 'assign', 'src1': 0, 'src2': None, 'dst': 'a'},
        {'op': 'assign', 'src1': 1, 'src2': None, 'dst': 'b'},
        {'op': 'mark', 'src1': 'loop_start', 'src2': None, 'dst': None},
        {'op': '>', 'src1': 'n', 'src2': 0, 'dst': 'cond1'},
        {'op': 'jump_if_false', 'src1': 'cond1', 'src2': 'loop_end', 'dst': None},
        {'op': 'assign', 'src1': 42, 'src2': None, 'dst': 't'},
        {'op': '+', 'src1': 'a', 'src2': 'b', 'dst': 't'},
        {'op': 'assign', 'src1': 'b', 'src2': None, 'dst': 'a'},
        {'op': 'assign', 'src1': 't', 'src2': None, 'dst': 'b'},
        {'op': '-', 'src1': 'n', 'src2': 1, 'dst': 'n'},
        {'op': 'jump', 'src1': 'loop_start', 'src2': None, 'dst': None},
        {'op': 'mark', 'src1': 'loop_end', 'src2': None, 'dst': None},
        {'op': 'return', 'src1': 'a', 'src2': None, 'dst': None},
    ]
    gen = AssemblyTranslator()
    asm = gen.translate(demo_ir)
    print("\n".join(asm))