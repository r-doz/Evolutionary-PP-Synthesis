# Generated from TRUNC.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TRUNCParser import TRUNCParser
else:
    from TRUNCParser import TRUNCParser

# This class defines a complete generic visitor for a parse tree produced by TRUNCParser.

class TRUNCVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TRUNCParser#trunc.
    def visitTrunc(self, ctx:TRUNCParser.TruncContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#ineq.
    def visitIneq(self, ctx:TRUNCParser.IneqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#inop.
    def visitInop(self, ctx:TRUNCParser.InopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#eq.
    def visitEq(self, ctx:TRUNCParser.EqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#eqop.
    def visitEqop(self, ctx:TRUNCParser.EqopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#lexpr.
    def visitLexpr(self, ctx:TRUNCParser.LexprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#monom.
    def visitMonom(self, ctx:TRUNCParser.MonomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#const.
    def visitConst(self, ctx:TRUNCParser.ConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#var.
    def visitVar(self, ctx:TRUNCParser.VarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#idd.
    def visitIdd(self, ctx:TRUNCParser.IddContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#gm.
    def visitGm(self, ctx:TRUNCParser.GmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#list.
    def visitList(self, ctx:TRUNCParser.ListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#sum.
    def visitSum(self, ctx:TRUNCParser.SumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TRUNCParser#sub.
    def visitSub(self, ctx:TRUNCParser.SubContext):
        return self.visitChildren(ctx)



del TRUNCParser