"""
Parser test cases for TyC compiler
TODO: Implement 100 test cases for parser
"""

import pytest
from tests.utils import Parser


# ========== Simple Test Cases (10 types) ==========
def test_empty_program():
    """1. Empty program"""
    assert Parser("").parse() == "success"


def test_program_with_only_main():
    """2. Program with only main function"""
    assert Parser("void main() {}").parse() == "success"


def test_struct_simple():
    """3. Struct declaration"""
    source = "struct Point { int x; int y; };"
    assert Parser(source).parse() == "success"


def test_function_no_params():
    """4. Function with no parameters"""
    source = "void greet() { printString(\"Hello\"); }"
    assert Parser(source).parse() == "success"


def test_var_decl_auto_with_init():
    """5. Variable declaration"""
    source = "void main() { auto x = 5; }"
    assert Parser(source).parse() == "success"


def test_if_simple():
    """6. If statement"""
    source = "void main() { if (1) printInt(1); }"
    assert Parser(source).parse() == "success"


def test_while_simple():
    """7. While statement"""
    source = "void main() { while (1) printInt(1); }"
    assert Parser(source).parse() == "success"


def test_for_simple():
    """8. For statement"""
    source = "void main() { for (auto i = 0; i < 10; ++i) printInt(i); }"
    assert Parser(source).parse() == "success"


def test_switch_simple():
    """9. Switch statement"""
    source = "void main() { switch (1) { case 1: printInt(1); break; } }"
    assert Parser(source).parse() == "success"


def test_assignment_simple():
    """10. Assignment statement"""
    source = "void main() { int x; x = 5; }"
    assert Parser(source).parse() == "success"

# =======================================================================
# PART 2: EXTENDED VALID SYNTAX (~110 CASES)
# =======================================================================
VALID_SCENARIOS = [
    # --- A. Function Structure (14 cases) ---
    ("int add(int a, int b) { return a + b; }", "Func Return Int"),
    ("float pi() { return 3.14; }", "Func Return Float"),
    ("string getName() { return \"TyC\"; }", "Func Return String"),
    ("Point getP() { Point p; return p; }", "Func Return Struct"),
    ("get() { return 1; }", "Func Implicit Return"),
    ("void f(int x) {}", "Param Int"),
    ("void f(float x) {}", "Param Float"),
    ("void f(string x) {}", "Param String"),
    ("void f(Point p) {}", "Param Struct"),
    ("void f(int x, float y) {}", "Params Mixed 2"),
    ("void f(int x, float y, string z) {}", "Params Mixed 3"),
    ("void f() {} int g() {}", "Multi Functions"),
    ("struct A { int x; }; void main() {}", "Struct then Func"),
    ("void main() {} struct A { int x; };", "Func then Struct"),

    # --- B. Struct Declarations (10 cases) ---
    ("struct A { int x; };", "Member Int"),
    ("struct A { float y; };", "Member Float"),
    ("struct A { string s; };", "Member String"),
    ("struct A { B b; };", "Member Struct (No keyword 'struct')"),
    ("struct A { int x; int y; };", "Multi Members Same Type"),
    ("struct A { int x; float y; };", "Multi Members Diff Type"),
    ("struct A { int a; float b; string c; };", "Mixed Members"),
    ("struct Node { int val; Node next; };", "Recursive Struct"),
    ("struct A {};", "Empty Struct"),
    ("struct A { int x; }; struct B { int y; };", "Multi Structs"),

    # --- C. Variable Declarations (11 cases) ---
    ("void main() { int x; }", "Decl Int"),
    ("void main() { float x; }", "Decl Float"),
    ("void main() { string s; }", "Decl String"),
    ("void main() { Point p; }", "Decl Struct"),
    ("void main() { auto x = 1; }", "Auto Init Int"),
    ("void main() { auto y = 1.0; }", "Auto Init Float"),
    ("void main() { auto s = \"s\"; }", "Auto Init String"),
    ("void main() { int x = 1; }", "Init Int"),
    ("void main() { float y = 1.0; }", "Init Float"),
    ("void main() { string s = \"s\"; }", "Init String"),
    ("void main() { Point p; p.x = 1; }", "Struct Access Assign"),

    # --- D. Statements: If/Else (10 cases) ---
    ("void main() { if (x) x=1; }", "If Single"),
    ("void main() { if (x) { x=1; } }", "If Block"),
    ("void main() { if (x) x=1; else x=2; }", "If Else Single"),
    ("void main() { if (x) { x=1; } else { x=2; } }", "If Else Block"),
    ("void main() { if (x) if (y) x=1; }", "Nested If"),
    ("void main() { if (x) if (y) x=1; else x=2; }", "Nested If Else"),
    ("void main() { if (a && b) x=1; }", "If Logic AND"),
    ("void main() { if (a || b) x=1; }", "If Logic OR"),
    ("void main() { if (!a) x=1; }", "If Logic NOT"),
    ("void main() { if ((a+b) > c) x=1; }", "If Expr"),

    # --- E. Statements: Loop & Switch (15 cases) ---
    ("void main() { while(1) x=1; }", "While Single"),
    ("void main() { while(1) { x=1; } }", "While Block"),
    ("void main() { while(1) break; }", "While Break"),
    ("void main() { while(1) continue; }", "While Continue"),
    ("void main() { for(;;) {} }", "For Infinite"),
    ("void main() { for(i=0;;) {} }", "For Init Only"),
    ("void main() { for(;i<10;) {} }", "For Cond Only"),
    ("void main() { for(;;i++) {} }", "For Update Only"),
    ("void main() { for(int i=0;i<10;i++) {} }", "For Full Int"),
    ("void main() { for(auto i=0;i<10;i++) {} }", "For Full Auto"),
    ("void main() { switch(x) {} }", "Switch Empty"),
    ("void main() { switch(x) { case 1: break; } }", "Switch Case"),
    ("void main() { switch(x) { default: break; } }", "Switch Default"),
    ("void main() { switch(x) { case 1: break; default: break; } }", "Switch Mixed"),
    ("void main() { switch(x) { case 1: case 2: break; } }", "Switch Fallthrough"),

    # --- F. Expressions: Math (15 cases) ---
    ("void main() { x = 1 + 2; }", "Add"),
    ("void main() { x = 1 - 2; }", "Sub"),
    ("void main() { x = 1 * 2; }", "Mul"),
    ("void main() { x = 1 / 2; }", "Div"),
    ("void main() { x = 1 % 2; }", "Mod"),
    ("void main() { x = -1; }", "Unary Minus"),
    ("void main() { x = +1; }", "Unary Plus"),
    ("void main() { x = 1 + 2 * 3; }", "Precedence MulAdd"),
    ("void main() { x = (1 + 2) * 3; }", "Parens"),
    ("void main() { x = a + b - c; }", "Assoc Left"),
    ("void main() { x = a * b / c; }", "Assoc MulDiv"),
    ("void main() { x = a % b * c; }", "Assoc ModMul"),
    ("void main() { x = -a * b; }", "Unary Precedence"),
    ("void main() { x = a * -b; }", "Unary Inside"),
    ("void main() { x = --a; }", "Pre Decrement"), # Assuming --a is unary expr

    # --- G. Expressions: Logic & Relational (15 cases) ---
    ("void main() { x = a > b; }", "GT"),
    ("void main() { x = a < b; }", "LT"),
    ("void main() { x = a >= b; }", "GTE"),
    ("void main() { x = a <= b; }", "LTE"),
    ("void main() { x = a == b; }", "EQ"),
    ("void main() { x = a != b; }", "NEQ"),
    ("void main() { x = !a; }", "NOT"),
    ("void main() { x = a && b; }", "AND"),
    ("void main() { x = a || b; }", "OR"),
    ("void main() { x = a && b || c; }", "Precedence AND > OR"),
    ("void main() { x = a || b && c; }", "Precedence AND > OR 2"),
    ("void main() { x = !a && b; }", "Precedence NOT > AND"),
    ("void main() { x = a > b && c < d; }", "Precedence Rel > Logic"),
    ("void main() { x = a == b || c != d; }", "Precedence Eq > Logic"),
    ("void main() { x = (a || b) && c; }", "Logic Parens"),

    # --- H. Advanced Expressions (15 cases) ---
    ("void main() { x = y = z = 0; }", "Chained Assign"),
    ("void main() { x.y = 1; }", "Field Access"),
    ("void main() { x.y.z = 1; }", "Deep Field Access"),
    ("void main() { f(); }", "Call Void"),
    ("void main() { f(1); }", "Call 1 Arg"),
    ("void main() { f(1, 2); }", "Call 2 Args"),
    ("void main() { x = f(); }", "Call Assign"),
    ("void main() { x = f().y; }", "Call Access"),
    ("void main() { f(g()); }", "Nested Call"),
    ("void main() { x++; }", "Post Inc"),
    ("void main() { x--; }", "Post Dec"),
    ("void main() { x.y++; }", "Field Post Inc"),
    ("void main() { x = 1.5e-2; }", "Sci Float"),
    ("void main() { x = \"str\"; }", "String Lit"),
    ("void main() { 1+2; }", "Expr Stmt"),
]

@pytest.mark.parametrize("source, desc", VALID_SCENARIOS)
def test_valid_syntax_extended(source, desc):
    assert Parser(source).parse() == "success", f"Failed Valid Case: {desc}"


# =======================================================================
# PART 3: INVALID SYNTAX (40 CASES)
# =======================================================================
INVALID_SCENARIOS = [
    # --- Struct Syntax Errors ---
    ("struct { int x; };", "Anon Struct"),
    ("struct A { int x };", "Missing Semi Member"),
    ("struct A { auto x; };", "Auto Member"),
    ("struct A { int x }", "Missing Semi Block"),
    ("struct A { struct B b; };", "Struct Keyword in Member"),
    
    # --- Function Syntax Errors ---
    ("void f(auto x) {}", "Auto Param"),
    ("void f(int x,) {}", "Trailing Comma"),
    ("void f(int x int y) {}", "Missing Comma"),
    ("void f(int) {}", "Missing Param ID"),

    
    # --- Variable Decl Errors ---
    ("void main() { int x }", "Missing Semi Decl"),
    ("void main() { int x, y; }", "Multi Decl (Grammar usually strict 1/stmt)"),
    ("void main() { const int x = 1; }", "Const Keyword"),
    ("void main() { int x = ; }", "Empty Init"),
    
    # --- Control Flow Errors ---
    ("void main() { if 1 {} }", "If No Parens"),
    ("void main() { if (1) }", "If No Body"),
    ("void main() { while 1 {} }", "While No Parens"),
    ("void main() { for ) {} }", "For Malformed"),
    ("void main() { switch x {} }", "Switch No Parens"),
    ("void main() { break }", "Break No Semi"),
    ("void main() { continue }", "Continue No Semi"),
    ("void main() { return }", "Return No Semi"),
    ("void main() { case 1: break; }", "Case Outside Switch"),
    ("void main() { default: break; }", "Default Outside Switch"),
    ("void main() { ; }", "Empty Statement"), # This was one of the failures
    
    # --- Expression Errors ---
    ("void main() { x = 1 +; }", "Hanging Op"),
    ("void main() { x = * 1; }", "Bin Op as Unary"),
    ("void main() { x = / 1; }", "Bin Op as Unary"),
    ("void main() { x = % 1; }", "Bin Op as Unary"),
    ("void main() { x = (1 + 1; }", "Unclosed Paren"),
    ("void main() { f(1,); }", "Call Trailing Comma"),
    ("void main() { f(,1); }", "Call Leading Comma"),
    ("void main() { x = arr[i]; }", "Array Access"),
    ("void main() { x = 1 @ 1; }", "Bad Token"),
    ("void main() { x = ..; }", "Double Dot"),
    ("void main() { x = a b; }", "Missing Op"),
    ("void main() { x = a \n b; }", "Missing Op Newline"),
]

@pytest.mark.parametrize("source, desc", INVALID_SCENARIOS)
def test_invalid_syntax_extended(source, desc):
    assert Parser(source).parse() != "success", f"Should Fail: {desc}"