"""
AST Generation module for TyC programming language.
This module contains the ASTGeneration class that converts parse trees
into Abstract Syntax Trees using the visitor pattern.
"""

from functools import reduce
from build.TyCVisitor import TyCVisitor
from build.TyCParser import TyCParser
from src.utils.nodes import *


class ASTGeneration(TyCVisitor):
    """AST Generation visitor for TyC language."""

    # ======================================================================
    # PROGRAM & DECLARATIONS
    # ======================================================================

    # program: decl* EOF;
    def visitProgram(self, ctx: TyCParser.ProgramContext):
        # Lấy tất cả các decl và tạo thành list
        decls = [self.visit(x) for x in ctx.decl()]
        return Program(decls)

    # decl: struct_decl | func_decl;
    def visitDecl(self, ctx: TyCParser.DeclContext):
        # Chuyển tiếp tới struct hoặc func
        return self.visit(ctx.getChild(0))

    # struct_decl: STRUCT ID LB member_list RB SEMI;
    def visitStruct_decl(self, ctx: TyCParser.Struct_declContext):
        name = ctx.ID().getText()
        members = self.visit(ctx.member_list())
        return StructDecl(name, members)

    # member_list: member*;
    def visitMember_list(self, ctx: TyCParser.Member_listContext):
        return [self.visit(x) for x in ctx.member()]

    # member: type_name ID SEMI;
    def visitMember(self, ctx: TyCParser.MemberContext):
        typ = self.visit(ctx.type_name())
        name = ctx.ID().getText()
        return MemberDecl(typ, name)

    # func_decl: (type_name | VOID)? ID LP param_list? RP block_stmt;
    def visitFunc_decl(self, ctx: TyCParser.Func_declContext):
        name = ctx.ID().getText()
        
        # Xử lý Return Type
        return_type = None  # None nghĩa là Auto/Implicit
        if ctx.VOID():
            return_type = VoidType()
        elif ctx.type_name():
            return_type = self.visit(ctx.type_name())
        
        # Xử lý Params
        params = []
        if ctx.param_list():
            params = self.visit(ctx.param_list())
            
        # Xử lý Body
        body = self.visit(ctx.block_stmt())
        
        return FuncDecl(return_type, name, params, body)

    # param_list: param (COMMA param)*;
    def visitParam_list(self, ctx: TyCParser.Param_listContext):
        return [self.visit(x) for x in ctx.param()]

    # param: type_name ID;
    def visitParam(self, ctx: TyCParser.ParamContext):
        typ = self.visit(ctx.type_name())
        name = ctx.ID().getText()
        return Param(typ, name)

    # ======================================================================
    # TYPE SYSTEM
    # ======================================================================

    # type_name: INT | FLOAT | STRING | ID;
    def visitType_name(self, ctx: TyCParser.Type_nameContext):
        if ctx.INT():
            return IntType()
        elif ctx.FLOAT():
            return FloatType()
        elif ctx.STRING():
            return StringType()
        else:
            # ID -> StructType (ClassType)
            return StructType(ctx.ID().getText())

    # ======================================================================
    # STATEMENTS
    # ======================================================================

    # statement: ...
    def visitStatement(self, ctx: TyCParser.StatementContext):
        return self.visit(ctx.getChild(0))

    # block_stmt: LB statement* RB;
    def visitBlock_stmt(self, ctx: TyCParser.Block_stmtContext):
        stmts = [self.visit(x) for x in ctx.statement()]
        return BlockStmt(stmts)

    # var_decl_stmt: (AUTO | type_name) ID (ASSIGN expr)? SEMI;
    def visitVar_decl_stmt(self, ctx: TyCParser.Var_decl_stmtContext):
        name = ctx.ID().getText()
        
        # Var Type: None nếu là AUTO, ngược lại visit type_name
        var_type = None
        if ctx.type_name():
            var_type = self.visit(ctx.type_name())
            
        # Init Value
        init_val = None
        if ctx.expr():
            init_val = self.visit(ctx.expr())
            
        return VarDecl(var_type, name, init_val)

    # if_stmt: IF LP expr RP statement (ELSE statement)?;
    def visitIf_stmt(self, ctx: TyCParser.If_stmtContext):
        cond = self.visit(ctx.expr())
        then_stmt = self.visit(ctx.statement(0))
        
        else_stmt = None
        if ctx.ELSE():
            else_stmt = self.visit(ctx.statement(1))
            
        return IfStmt(cond, then_stmt, else_stmt)

    # while_stmt: WHILE LP expr RP statement;
    def visitWhile_stmt(self, ctx: TyCParser.While_stmtContext):
        cond = self.visit(ctx.expr())
        body = self.visit(ctx.statement())
        return WhileStmt(cond, body)

    # for_stmt: FOR LP (var_decl_stmt | expr SEMI | SEMI) expr? SEMI expr? RP statement;
    def visitFor_stmt(self, ctx: TyCParser.For_stmtContext):
        # Xử lý phần Init
        init = None
        # Xác định các thành phần tiếp theo (cond, update) bắt đầu từ index nào trong ds expr
        expr_idx = 0 
        
        if ctx.var_decl_stmt():
            init = self.visit(ctx.var_decl_stmt())
            # var_decl_stmt đã chứa init expr nếu có, không ảnh hưởng list ctx.expr() của For
        elif ctx.getChild(2).getText() == ';':
            # Trường hợp 'FOR LP SEMI ...' -> Init rỗng
            init = None
        else:
            # Trường hợp 'FOR LP expr SEMI ...' -> Init là ExprStmt
            # Biểu thức đầu tiên trong list expr thuộc về init
            init_expr = self.visit(ctx.expr(expr_idx))
            init = ExprStmt(init_expr)
            expr_idx += 1

        # Xử lý Cond (expr?)
        # Kiểm tra xem có cond không bằng cách nhìn vào các dấu chấm phẩy
        # Logic: 
        # - Nếu var_decl: FOR ( var_decl ...
        # - Nếu expr: FOR ( expr ; ...
        # - Nếu semi: FOR ( ; ...
        # Sau phần init luôn là dấu chấm phẩy thứ nhất (SEMI 1).
        # Sau SEMI 1 là cond (nếu có), rồi đến SEMI 2.
        
        # Cách đơn giản hơn: Duyệt children để tìm vị trí các dấu chấm phẩy
        children = [c.getText() for c in ctx.getChildren()]
        semi_indices = [i for i, x in enumerate(children) if x == ';']
        # semi_indices[0] là dấu chấm phẩy sau init
        # semi_indices[1] là dấu chấm phẩy sau cond
        
        cond = None
        # Kiểm tra giữa 2 dấu chấm phẩy có token nào không?
        # children[semi_indices[0] + 1] có phải là ';' không?
        # Tuy nhiên ctx.expr() trả về list node đã parse, ta cần biết cái nào là cond.
        
        # Ta dùng `expr_idx` để lấy tuần tự từ list expr()
        
        # Kiểm tra xem có biểu thức điều kiện không?
        # Dựa vào grammar: expr? SEMI. 
        # Nếu token ngay trước SEMI thứ 2 KHÔNG phải là SEMI thứ 1, thì có cond.
        if children[semi_indices[1] - 1] != ';': 
            # Có expression cho condition
            if expr_idx < len(ctx.expr()):
                cond = self.visit(ctx.expr(expr_idx))
                expr_idx += 1
                
        # Xử lý Update (expr?)
        update = None
        # Nếu token ngay trước RP ')' KHÔNG phải là SEMI thứ 2, thì có update
        if children[children.index(')') - 1] != ';':
            if expr_idx < len(ctx.expr()):
                update = self.visit(ctx.expr(expr_idx))
                expr_idx += 1
                
        body = self.visit(ctx.statement())
        
        return ForStmt(init, cond, update, body)

    # switch_stmt: SWITCH LP expr RP LB case_stmt* default_stmt? RB;
    def visitSwitch_stmt(self, ctx: TyCParser.Switch_stmtContext):
        expr = self.visit(ctx.expr())
        cases = [self.visit(x) for x in ctx.case_stmt()]
        
        default_case = None
        if ctx.default_stmt():
            default_case = self.visit(ctx.default_stmt())
            
        return SwitchStmt(expr, cases, default_case)

    # case_stmt: CASE expr COLON statement*;
    def visitCase_stmt(self, ctx: TyCParser.Case_stmtContext):
        expr = self.visit(ctx.expr())
        stmts = [self.visit(x) for x in ctx.statement()]
        return CaseStmt(expr, stmts)

    # default_stmt: DEFAULT COLON statement*;
    def visitDefault_stmt(self, ctx: TyCParser.Default_stmtContext):
        stmts = [self.visit(x) for x in ctx.statement()]
        return DefaultStmt(stmts)

    # break_stmt: BREAK SEMI;
    def visitBreak_stmt(self, ctx: TyCParser.Break_stmtContext):
        return BreakStmt()

    # continue_stmt: CONTINUE SEMI;
    def visitContinue_stmt(self, ctx: TyCParser.Continue_stmtContext):
        return ContinueStmt()

    # return_stmt: RETURN expr? SEMI;
    def visitReturn_stmt(self, ctx: TyCParser.Return_stmtContext):
        expr = None
        if ctx.expr():
            expr = self.visit(ctx.expr())
        return ReturnStmt(expr)

    # expr_stmt: expr SEMI;
    def visitExpr_stmt(self, ctx: TyCParser.Expr_stmtContext):
        return ExprStmt(self.visit(ctx.expr()))

    # ======================================================================
    # EXPRESSIONS
    # ======================================================================

    # expr DOT ID (FieldAccess -> MemberAccess)
    def visitFieldAccess(self, ctx: TyCParser.FieldAccessContext):
        obj = self.visit(ctx.expr())
        member = ctx.ID().getText()
        return MemberAccess(obj, member)

    # ID LP expr_list? RP (FuncCall)
    def visitFuncCall(self, ctx: TyCParser.FuncCallContext):
        name = ctx.ID().getText()
        args = []
        if ctx.expr_list():
            args = self.visit(ctx.expr_list())
        return FuncCall(name, args)
    
    # Helper for expr_list: expr (COMMA expr)*
    def visitExpr_list(self, ctx: TyCParser.Expr_listContext):
        return [self.visit(x) for x in ctx.expr()]

    # expr (INC | DEC) (PostfixExpr -> PostfixOp)
    def visitPostfixExpr(self, ctx: TyCParser.PostfixExprContext):
        # ctx.getChild(1) là toán tử (++ hoặc --)
        op = ctx.getChild(1).getText()
        expr = self.visit(ctx.expr())
        return PostfixOp(op, expr)

    # (NOT | MINUS | PLUS | INC | DEC) expr (UnaryExpr -> PrefixOp)
    def visitUnaryExpr(self, ctx: TyCParser.UnaryExprContext):
        op = ctx.getChild(0).getText()
        expr = self.visit(ctx.expr())
        return PrefixOp(op, expr)

    # Helper function for standard Binary Operations
    def _visitBinary(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        # Toán tử luôn nằm ở vị trí child thứ 1 (giữa 2 expr)
        op = ctx.getChild(1).getText()
        return BinaryOp(left, op, right)

    # expr (STAR | DIV | MOD) expr
    def visitMulDivExpr(self, ctx: TyCParser.MulDivExprContext):
        return self._visitBinary(ctx)

    # expr (PLUS | MINUS) expr
    def visitAddSubExpr(self, ctx: TyCParser.AddSubExprContext):
        return self._visitBinary(ctx)

    # expr (GT | LT | GTE | LTE) expr
    def visitRelExpr(self, ctx: TyCParser.RelExprContext):
        return self._visitBinary(ctx)

    # expr (EQ | NEQ) expr
    def visitEqualExpr(self, ctx: TyCParser.EqualExprContext):
        return self._visitBinary(ctx)

    # expr AND expr
    def visitLogicAndExpr(self, ctx: TyCParser.LogicAndExprContext):
        return self._visitBinary(ctx)

    # expr OR expr
    def visitLogicOrExpr(self, ctx: TyCParser.LogicOrExprContext):
        return self._visitBinary(ctx)

    # <assoc=right> expr ASSIGN expr
    def visitAssignExpr(self, ctx: TyCParser.AssignExprContext):
        lhs = self.visit(ctx.expr(0))
        rhs = self.visit(ctx.expr(1))
        return AssignExpr(lhs, rhs)

    # LP expr RP
    def visitParenExpr(self, ctx: TyCParser.ParenExprContext):
        return self.visit(ctx.expr())

    # ID
    def visitIdExpr(self, ctx: TyCParser.IdExprContext):
        return Identifier(ctx.ID().getText())

    # literal
    def visitLiteralExpr(self, ctx: TyCParser.LiteralExprContext):
        return self.visit(ctx.literal())

    # ======================================================================
    # LITERALS
    # ======================================================================

    def visitLiteral(self, ctx: TyCParser.LiteralContext):
        if ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            return FloatLiteral(float(ctx.FLOATLIT().getText()))
        elif ctx.STRINGLIT():
            # Lexer đã xử lý strip quotes, lấy nguyên chuỗi
            return StringLiteral(ctx.STRINGLIT().getText())
        return None