grammar TyC;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:
        result = super().emit()
        raise UncloseString(result.text)
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit()
        raise IllegalEscape(result.text)
    elif tk == self.ERROR_CHAR:
        result = super().emit()
        raise ErrorToken(result.text)
    else:
        return super().emit()
}

options {
    language = Python3;
}

// ======================================
// 1. PARSER RULES
// ======================================

program: decl* EOF;

decl: struct_decl | func_decl;

// --- Declarations ---
struct_decl: STRUCT ID LB member_list RB SEMI;
member_list: member*;
member: type_name ID SEMI;

func_decl: (type_name | VOID)? ID LP param_list? RP block_stmt;
param_list: param (COMMA param)*;
param: type_name ID;

// Types
type_name: INT | FLOAT | STRING | ID;

// --- Statements ---
// Lưu ý: Đã xóa assign_stmt vì expr_stmt sẽ xử lý cả phép gán (x = 5;)
statement: var_decl_stmt
         | if_stmt
         | for_stmt
         | while_stmt
         | return_stmt
         | break_stmt
         | continue_stmt
         | block_stmt
         | expr_stmt
         | switch_stmt
         ;

block_stmt: LB statement* RB;

// Variable Declaration: auto x = 5;
var_decl_stmt: (AUTO | type_name) ID (ASSIGN expr)? SEMI;

// Control Flow
if_stmt: IF LP expr RP statement (ELSE statement)?;
while_stmt: WHILE LP expr RP statement;

// For Loop: for (init; cond; update)
// init: có thể là khai báo biến, biểu thức (gán), hoặc rỗng
// update: là một biểu thức (thường là gán hoặc tăng/giảm)
for_stmt: FOR LP (var_decl_stmt | expr SEMI | SEMI) expr? SEMI expr? RP statement;

switch_stmt: SWITCH LP expr RP LB case_stmt* default_stmt? RB;
case_stmt: CASE expr COLON statement*;
default_stmt: DEFAULT COLON statement*;

break_stmt: BREAK SEMI;
continue_stmt: CONTINUE SEMI;
return_stmt: RETURN expr? SEMI;

expr_stmt: expr SEMI;

// --- Expressions ---
// Thứ tự ưu tiên (Precedence) từ cao xuống thấp
expr: expr DOT ID                               # FieldAccess     // 1. Member access
    | ID LP expr_list? RP                       # FuncCall        // 1. Function Call
    | expr (INC | DEC)                          # PostfixExpr     // 2. Postfix
    | (NOT | MINUS | PLUS | INC | DEC) expr     # UnaryExpr       // 3. Prefix
    | expr (STAR | DIV | MOD) expr              # MulDivExpr      // 4. *, /, %
    | expr (PLUS | MINUS) expr                  # AddSubExpr      // 5. +, -
    | expr (GT | LT | GTE | LTE) expr           # RelExpr         // 6. Relational
    | expr (EQ | NEQ) expr                      # EqualExpr       // 7. Equality
    | expr AND expr                             # LogicAndExpr    // 8. &&
    | expr OR expr                              # LogicOrExpr     // 9. ||
    | <assoc=right> expr ASSIGN expr            # AssignExpr      // 10. Assignment (FIXED)
    | LP expr RP                                # ParenExpr       
    | ID                                        # IdExpr          
    | literal                                   # LiteralExpr     
    ;

expr_list: expr (COMMA expr)*;
literal: INTLIT | FLOATLIT | STRINGLIT;

// ======================================
// 2. LEXER RULES
// ======================================

AUTO: 'auto';
BREAK: 'break';
CASE: 'case';
CONTINUE: 'continue';
DEFAULT: 'default';
ELSE: 'else';
FLOAT: 'float';
FOR: 'for';
IF: 'if';
INT: 'int';
RETURN: 'return';
STRING: 'string';
STRUCT: 'struct';
SWITCH: 'switch';
VOID: 'void';
WHILE: 'while';

PLUS: '+'; MINUS: '-'; STAR: '*'; DIV: '/'; MOD: '%';
NOT: '!'; ASSIGN: '='; EQ: '=='; NEQ: '!=';
LT: '<'; LTE: '<='; GT: '>'; GTE: '>=';
AND: '&&'; OR: '||';
INC: '++'; DEC: '--';
DOT: '.';

LB: '{'; RB: '}';
LP: '('; RP: ')';
SEMI: ';'; COMMA: ','; COLON: ':';

INTLIT: '0' | [1-9][0-9]*;

FLOATLIT: [0-9]+ '.' [0-9]* EXPONENT?
        | '.' [0-9]+ EXPONENT?
        | [0-9]+ EXPONENT
        ;
fragment EXPONENT: [eE] [+-]? [0-9]+;

ID: [a-zA-Z_] [a-zA-Z0-9_]*;

// --- String & Error Handling ---
fragment ESC: '\\' [bfrtn"\\];
fragment SAFE: ~["\\\r\n];

// 1. Illegal Escape: Cắt bỏ dấu ngoặc kép mở đầu (Spec yêu cầu)
ILLEGAL_ESCAPE: '"' (ESC | SAFE)* '\\' ~[bfrtn"\\\r\n] { self.text = self.text[1:] };

// 2. Valid String: Cắt bỏ cả ngoặc kép đầu và cuối
STRINGLIT: '"' (ESC | SAFE)* '"' { self.text = self.text[1:-1] };

// 3. Unclosed String: Cắt bỏ dấu ngoặc kép mở đầu
UNCLOSE_STRING: '"' (ESC | SAFE)* { self.text = self.text[1:] };

BLOCK_COMMENT: '/*' .*? '*/' -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;
WS: [ \t\r\n\f]+ -> skip;

ERROR_CHAR: . ;