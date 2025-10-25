#!/usr/bin/env python3
"""
GUI frontend for the Mini Compiler.

Dependencies:
- lexer.TokenScanner
- parser.SyntaxProcessor
- assembly_translator.AssemblyTranslator

This GUI will try to load examples/test1.c at startup (searches a few likely locations).
It also provides buttons to Open any file into the input area and Save the current input to a file.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
from lexer import TokenScanner
from parser import SyntaxProcessor
from assembly_translator import AssemblyTranslator


class CompilerInterface:
    """Main GUI for the compiler application"""

    def __init__(self, window):
        self.window = window
        self.window.title("Mini Compiler - By Maruf Ahammed")
        self.window.geometry("1400x850")
        self.window.configure(bg='#1e1e1e')

        # Initialize compiler components
        self.scanner = TokenScanner()
        try:
            self.scanner.initialize()
        except Exception:
            pass

        self.processor = SyntaxProcessor()
        try:
            self.processor.initialize()
        except Exception:
            pass

        self.translator = AssemblyTranslator()

        self.build_interface()
        # Load examples/test1.c on startup if present
        self.load_example_on_startup()

    def build_interface(self):
        """Build the GUI components"""
        container = ttk.Frame(self.window, padding="10")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        # Input Section
        input_panel = ttk.LabelFrame(container, text="Input Code", padding="10")
        input_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.code_input = scrolledtext.ScrolledText(input_panel, width=60, height=40, font=('Consolas', 11))
        self.code_input.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        controls = ttk.Frame(container)
        controls.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W,))

        ttk.Button(controls, text="Compile", command=self.run_compilation).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Reset", command=self.reset_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Load examples/test1.c", command=self.load_example_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Open...", command=self.open_file_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Save As...", command=self.save_file_dialog).pack(side=tk.LEFT, padx=4)

        # Output Section
        output_panel = ttk.LabelFrame(container, text="Compilation Results", padding="10")
        output_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.tabs = ttk.Notebook(output_panel)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Create output tabs
        self.make_tab("Token Stream", "tok_view")
        self.make_tab("Symbol Table", "var_view")
        self.make_tab("IR Code", "ir_view")
        self.make_tab("Assembly", "asm_view")
        self.make_tab("Issues", "err_view")

    def make_tab(self, label, attr):
        """Create a new tab and store the ScrolledText widget on self."""
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=label)
        view = scrolledtext.ScrolledText(frame, width=80, height=40, font=('Consolas', 10))
        view.pack(fill=tk.BOTH, expand=True)
        setattr(self, attr, view)

    # -----------------------
    # File loading / saving
    # -----------------------
    def load_example_on_startup(self):
        """Try to load examples/test1.c (several candidate locations)."""
        txt, path = self._find_and_read_test1()
        if txt is not None:
            self.code_input.delete('1.0', tk.END)
            self.code_input.insert('1.0', txt)

    def load_example_file(self):
        """Button action: (re)load examples/test1.c into the input box if it exists."""
        txt, path = self._find_and_read_test1()
        if txt is not None:
            self.code_input.delete('1.0', tk.END)
            self.code_input.insert('1.0', txt)
            messagebox.showinfo("Loaded", f"Loaded {path}")
        else:
            messagebox.showwarning("Not found", "examples/test1.c not found in expected locations.")

    def _find_and_read_test1(self):
        """Search a few likely locations for examples/test1.c and return (text, path) or (None, None)."""
        base = Path(__file__).resolve().parent
        candidates = [
            base / 'examples' / 'test1.c',          # src/examples/test1.c
            base.parent / 'examples' / 'test1.c',   # ../examples/test1.c (project root examples)
            Path.cwd() / 'examples' / 'test1.c'     # ./examples/test1.c from CWD
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                try:
                    return c.read_text(encoding='utf-8'), str(c)
                except Exception:
                    return None, None
        return None, None

    def open_file_dialog(self):
        """Open a file dialog and load the selected file into the input box."""
        path = filedialog.askopenfilename(title="Open source file", filetypes=[("C files", "*.c *.mc *.txt"), ("All files", "*.*")])
        if path:
            try:
                txt = Path(path).read_text(encoding='utf-8')
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', txt)
                messagebox.showinfo("Loaded", f"Loaded {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {path}: {e}")

    def save_file_dialog(self):
        """Save current input to a file via Save As dialog."""
        path = filedialog.asksaveasfilename(title="Save source as", defaultextension=".c",
                                            filetypes=[("C files", "*.c"), ("All files", "*.*")])
        if path:
            try:
                Path(path).write_text(self.code_input.get('1.0', tk.END), encoding='utf-8')
                messagebox.showinfo("Saved", f"Saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {path}: {e}")

    # -----------------------
    # Compilation pipeline
    # -----------------------
    def run_compilation(self):
        """Execute lexer -> parser/semantic -> IR -> assembly pipeline and show outputs."""
        src = self.code_input.get('1.0', tk.END)

        # Clear all output views
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)

        # Clear symbol table before compilation
        try:
            self.processor.registry.clear()
        except Exception:
            pass

        # Phase 1: Lexical Analysis
        tokens, lex_errs = self.scanner.scan(src)

        tok_display = "TOKEN STREAM\n" + "=" * 70 + "\n\n"
        tok_display += f"{'Type':<18} {'Value':<22} {'Line':<6} {'Col':<4}\n"
        tok_display += "-" * 70 + "\n"
        for tok in tokens:
            tok_display += f"{tok['kind']:<18} {str(tok['val']):<22} {tok['ln']:<6} {tok.get('col',''):<4}\n"
        self.tok_view.insert('1.0', tok_display)

        # Phase 2 & 3: Syntax and Semantic Analysis
        self.processor.process(src)

        # Symbol Table Display
        var_display = "SYMBOL TABLE\n" + "=" * 100 + "\n\n"
        var_display += f"{'Identifier':<18} {'Type':<12} {'Context':<15} {'Scope':<20} {'Level':<6}\n"
        var_display += "-" * 100 + "\n"
        for entry in self.processor.registry.all_entries():
            var_display += (
                f"{entry.get('id',''):<18} "
                f"{entry.get('dtype',''):<12} "
                f"{entry.get('ctx',''):<15} "
                f"{entry.get('scope',''):<20} "
                f"{entry.get('scope_level',''):<6}\n"
            )
        self.var_view.insert('1.0', var_display)

        # IR Display
        ir_display = "INTERMEDIATE REPRESENTATION\n" + "=" * 70 + "\n\n"
        for idx, instr in enumerate(self.processor.ir_instructions):
            op = instr.get('op')
            s1 = instr.get('src1')
            s2 = instr.get('src2')
            d = instr.get('dst')
            if op == 'assign':
                ir_display += f"{idx + 1}. {d} := {s1}\n"
            elif op in ['+', '-', '*', '/', '%']:
                ir_display += f"{idx + 1}. {d} := {s1} {op} {s2}\n"
            elif op in ['<', '<=', '>', '>=', '==', '!=']:
                ir_display += f"{idx + 1}. {d} := {s1} {op} {s2}\n"
            elif op == 'mark':
                ir_display += f"{idx + 1}. {s1}:\n"
            elif op == 'jump':
                ir_display += f"{idx + 1}. goto {s1}\n"
            elif op == 'jump_if_false':
                ir_display += f"{idx + 1}. if_false {s1} goto {s2}\n"
            elif op == 'output':
                ir_display += f"{idx + 1}. print {s1}\n"
            elif op == 'return':
                ir_display += f"{idx + 1}. return {s1}\n"
            else:
                ir_display += f"{idx + 1}. {op} {s1} {s2} {d}\n"
        self.ir_view.insert('1.0', ir_display)

        # Phase 4: Code Generation (Assembly)
        try:
            asm = self.translator.translate(self.processor.ir_instructions)
            asm_display = "ASSEMBLY OUTPUT\n" + "=" * 70 + "\n\n" + "\n".join(asm)
            self.asm_view.insert('1.0', asm_display)
        except Exception as e:
            self.asm_view.insert('1.0', f"Code generation failed: {e}")

        # Errors / Issues
        all_errs = []
        if lex_errs:
            all_errs.extend(lex_errs)
        if self.processor.issues:
            all_errs.extend(self.processor.issues)

        if all_errs:
            err_display = "COMPILATION ISSUES\n" + "=" * 70 + "\n\n"
            for idx, err in enumerate(all_errs, 1):
                err_display += f"{idx}. {err}\n"
            self.err_view.insert('1.0', err_display)
            messagebox.showwarning("Issues Found", f"Detected {len(all_errs)} issue(s)")
        else:
            self.err_view.insert('1.0', "✓ Compilation completed successfully!")
            messagebox.showinfo("Success", "Code compiled without errors!")

    def reset_all(self):
        """Clear all input and output fields and reset registry."""
        self.code_input.delete('1.0', tk.END)
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        try:
            self.processor.registry.clear()
        except Exception:
            pass


def main():
    root = tk.Tk()
    app = CompilerInterface(root)
    root.mainloop()


if __name__ == '__main__':
    main()