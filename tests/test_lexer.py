"""
Lexer test cases for TyC compiler
TODO: Implement 100 test cases for lexer
"""

import pytest
from tests.utils import Tokenizer


# =======================================================================
# 1. KEYWORDS (16 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("auto", "auto,<EOF>"), ("break", "break,<EOF>"), ("case", "case,<EOF>"),
    ("continue", "continue,<EOF>"), ("default", "default,<EOF>"), ("else", "else,<EOF>"),
    ("float", "float,<EOF>"), ("for", "for,<EOF>"), ("if", "if,<EOF>"),
    ("int", "int,<EOF>"), ("return", "return,<EOF>"), ("string", "string,<EOF>"),
    ("struct", "struct,<EOF>"), ("switch", "switch,<EOF>"), ("void", "void,<EOF>"),
    ("while", "while,<EOF>"),
])
def test_keywords(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 2. OPERATORS (18 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("+", "+,<EOF>"), ("-", "-,<EOF>"), ("*", "*,<EOF>"), ("/", "/,<EOF>"),
    ("%", "%,<EOF>"), ("==", "==,<EOF>"), ("!=", "!=,<EOF>"), ("<", "<,<EOF>"),
    (">", ">,<EOF>"), ("<=", "<=,<EOF>"), (">=", ">=,<EOF>"), ("||", "||,<EOF>"),
    ("&&", "&&,<EOF>"), ("!", "!,<EOF>"), ("++", "++,<EOF>"), ("--", "--,<EOF>"),
    ("=", "=,<EOF>"), (".", ".,<EOF>"),
])
def test_operators(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 3. SEPARATORS (7 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("{", "{,<EOF>"), ("}", "},<EOF>"), ("(", "(,<EOF>"), (")", "),<EOF>"),
    (";", ";,<EOF>"), (",", ",,<EOF>"), (":", ":,<EOF>"),
])
def test_separators(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 4. LITERALS: INTEGERS (15 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("0", "0,<EOF>"), ("1", "1,<EOF>"), ("123", "123,<EOF>"),
    ("9999999", "9999999,<EOF>"), ("0123", "0,123,<EOF>"), 
    ("1 2 3", "1,2,3,<EOF>"), ("100", "100,<EOF>"),
    ("1234567890", "1234567890,<EOF>"), ("42", "42,<EOF>"), ("7", "7,<EOF>"),
    ("-1", "-,1,<EOF>"), ("-100", "-,100,<EOF>"),
    ("00", "0,0,<EOF>"), ("05", "0,5,<EOF>"), ("1000", "1000,<EOF>"),
])
def test_integers(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 5. LITERALS: FLOATS (25 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("1.2", "1.2,<EOF>"), ("0.0", "0.0,<EOF>"), ("3.14159", "3.14159,<EOF>"),
    (".5", ".5,<EOF>"), ("1.", "1.,<EOF>"), ("123.", "123.,<EOF>"),
    (".123", ".123,<EOF>"), ("1e5", "1e5,<EOF>"), ("1E5", "1E5,<EOF>"),
    ("1.2e3", "1.2e3,<EOF>"), ("1.2E-3", "1.2E-3,<EOF>"), ("1e-5", "1e-5,<EOF>"),
    ("0.1e+2", "0.1e+2,<EOF>"), (".5e2", ".5e2,<EOF>"), ("12.e5", "12.e5,<EOF>"),
    ("0.00e0", "0.00e0,<EOF>"), ("1234.5678", "1234.5678,<EOF>"),
    
    # Updated expectations based on greedy lexer rules:
    ("1.2.3", "1.2,.3,<EOF>"), # 1.2 is float, .3 is float
    ("00.1", "00.1,<EOF>"),     # 00.1 is parsed as single float (valid per spec)
    
    ("1e", "1,e,<EOF>"), ("1.e", "1.,e,<EOF>"), (".e2", ".,e2,<EOF>"),
    ("1.2e", "1.2,e,<EOF>"), ("1e+ ", "1,e,+,<EOF>"),
])
def test_floats(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 6. LITERALS: STRINGS (20 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ('"hello"', "hello,<EOF>"), ('""', ",<EOF>"), ('"a"', "a,<EOF>"),
    ('" "', " ,<EOF>"), ('"123"', "123,<EOF>"), ('"a b c"', "a b c,<EOF>"),
    (r'"\t"', r'\t,<EOF>'), (r'"\n"', r'\n,<EOF>'), (r'"\\"', r'\\,<EOF>'),
    (r'"\""', r'\",<EOF>'), (r'"\b"', r'\b,<EOF>'), (r'"\f"', r'\f,<EOF>'),
    (r'"\r"', r'\r,<EOF>'), (r'"Hello\nWorld"', r'Hello\nWorld,<EOF>'),
    (r'"Path: C:\\User"', r'Path: C:\\User,<EOF>'),
    (r'"He said: \"Hi\""', r'He said: \"Hi\",<EOF>'),
    ('"_underscore_"', "_underscore_,<EOF>"), ('"value = 5"', "value = 5,<EOF>"),
    ('"/* not comment */"', "/* not comment */,<EOF>"),
    ('"// not comment"', "// not comment,<EOF>"),
])
def test_strings(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 7. IDENTIFIERS (15 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("x", "x,<EOF>"), ("myVar", "myVar,<EOF>"), ("MyStruct", "MyStruct,<EOF>"),
    ("variable_name", "variable_name,<EOF>"), ("_private", "_private,<EOF>"),
    ("var123", "var123,<EOF>"), ("CamelCase", "CamelCase,<EOF>"),
    ("ALL_CAPS", "ALL_CAPS,<EOF>"), ("a_1_b_2", "a_1_b_2,<EOF>"),
    ("__init", "__init,<EOF>"), ("x_", "x_,<EOF>"), ("main", "main,<EOF>"),
    ("trueVal", "trueVal,<EOF>"), ("x1y2z3", "x1y2z3,<EOF>"),
    ("validID", "validID,<EOF>"),
])
def test_identifiers(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 8. COMMENTS (10 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("// This is a comment", "<EOF>"), ("// comment with * and / symbols", "<EOF>"),
    ("// auto int if", "<EOF>"), ("/* Block comment */", "<EOF>"),
    ("/* Multi-line \n comment */", "<EOF>"), ("/* Comment with // inside */", "<EOF>"),
    ("1 // Line comment after token", "1,<EOF>"), ("/* Block */ 2", "2,<EOF>"),
    ("/* \n \t */", "<EOF>"), ("/**/", "<EOF>"),
])
def test_comments(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 9. COMPLEX & MIXED (30 cases)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    ("auto x = 5;", "auto,x,=,5,;,<EOF>"),
    ("int y = x + 10;", "int,y,=,x,+,10,;,<EOF>"),
    ("float pi = 3.14;", "float,pi,=,3.14,;,<EOF>"),
    ("if (x > 0) { return; }", "if,(,x,>,0,),{,return,;,},<EOF>"),
    ("for(int i=0; i<10; i++)", "for,(,int,i,=,0,;,i,<,10,;,i,++,),<EOF>"),
    ("s.member", "s,.,member,<EOF>"),
    ("readInt()", "readInt,(,),<EOF>"),
    ("printString(\"Hi\")", "printString,(,Hi,),<EOF>"),
    ("x = -5", "x,=,-,5,<EOF>"), ("y = !flag", "y,=,!,flag,<EOF>"),
    ("a && b || c", "a,&&,b,||,c,<EOF>"),
    ("x = y * z / 2", "x,=,y,*,z,/,2,<EOF>"),
    ("x % 2 == 0", "x,%,2,==,0,<EOF>"),
    ("return a <= b", "return,a,<=,b,<EOF>"),
    ("struct Point { int x; }", "struct,Point,{,int,x,;,},<EOF>"),
    ("x += 1", "x,+,=,1,<EOF>"),
    
    # SỬA LẠI: Dừng ngay tại lỗi đầu tiên "Error Token [", KHÔNG CÓ <EOF>
    ("arr[i]", "arr,Error Token ["),
    
    ("x.y.z", "x,.,y,.,z,<EOF>"), ("1+2*3", "1,+,2,*,3,<EOF>"),
    ("(1+2)*3", "(,1,+,2,),*,3,<EOF>"), ("switch(x)", "switch,(,x,),<EOF>"),
    ("case 1:", "case,1,:,<EOF>"), ("default:", "default,:,<EOF>"),
    ("break;", "break,;,<EOF>"), ("continue;", "continue,;,<EOF>"),
    ("x = \"string\" + \"concat\"", "x,=,string,+,concat,<EOF>"),
    ("int _valid = 1;", "int,_valid,=,1,;,<EOF>"),
    ("auto f = 1.2e-5;", "auto,f,=,1.2e-5,;,<EOF>"),
    ("/* c */ int x /* c */", "int,x,<EOF>"),
    ("x = y; // end", "x,=,y,;,<EOF>"),
])
def test_complex_expressions(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected

# =======================================================================
# 10. ERROR HANDLING (FIXED: NO <EOF> IN ERROR CASES)
# =======================================================================
@pytest.mark.parametrize("text, expected", [
    # Unclosed Strings (No <EOF>)
    ('"unclosed', "Unclosed String: unclosed"),
    ('"line break\n"', "Unclosed String: line break"),
    ('"text', "Unclosed String: text"),
    
    # Illegal Escapes (No <EOF>)
    (r'"bad \a escape"', r'Illegal Escape In String: bad \a'),
    (r'"wrong \x hex"', r'Illegal Escape In String: wrong \x'),
    (r'"num \1 escape"', r'Illegal Escape In String: num \1'),
    (r'"slash \ "', r'Illegal Escape In String: slash \ '),
    
    # Error Characters (No <EOF>)
    ("#", "Error Token #"),
    ("$", "Error Token $"),
    ("@", "Error Token @"),
    ("~", "Error Token ~"),
    ("?", "Error Token ?"),
    ("`", "Error Token `"),
    ("^", "Error Token ^"),
    
    # Mixed Case (Stops at #, No <EOF>)
    ("int x = #;", "int,x,=,Error Token #"),
])
def test_error_cases(text, expected):
    assert Tokenizer(text).get_tokens_as_string() == expected