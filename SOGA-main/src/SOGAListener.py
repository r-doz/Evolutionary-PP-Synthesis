# Generated from SOGA.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SOGAParser import SOGAParser
else:
    from SOGAParser import SOGAParser

# This class defines a complete listener for a parse tree produced by SOGAParser.
class SOGAListener(ParseTreeListener):

    # Enter a parse tree produced by SOGAParser#progr.
    def enterProgr(self, ctx:SOGAParser.ProgrContext):
        pass

    # Exit a parse tree produced by SOGAParser#progr.
    def exitProgr(self, ctx:SOGAParser.ProgrContext):
        pass


    # Enter a parse tree produced by SOGAParser#data.
    def enterData(self, ctx:SOGAParser.DataContext):
        pass

    # Exit a parse tree produced by SOGAParser#data.
    def exitData(self, ctx:SOGAParser.DataContext):
        pass


    # Enter a parse tree produced by SOGAParser#array.
    def enterArray(self, ctx:SOGAParser.ArrayContext):
        pass

    # Exit a parse tree produced by SOGAParser#array.
    def exitArray(self, ctx:SOGAParser.ArrayContext):
        pass


    # Enter a parse tree produced by SOGAParser#instr.
    def enterInstr(self, ctx:SOGAParser.InstrContext):
        pass

    # Exit a parse tree produced by SOGAParser#instr.
    def exitInstr(self, ctx:SOGAParser.InstrContext):
        pass


    # Enter a parse tree produced by SOGAParser#assignment.
    def enterAssignment(self, ctx:SOGAParser.AssignmentContext):
        pass

    # Exit a parse tree produced by SOGAParser#assignment.
    def exitAssignment(self, ctx:SOGAParser.AssignmentContext):
        pass


    # Enter a parse tree produced by SOGAParser#const.
    def enterConst(self, ctx:SOGAParser.ConstContext):
        pass

    # Exit a parse tree produced by SOGAParser#const.
    def exitConst(self, ctx:SOGAParser.ConstContext):
        pass


    # Enter a parse tree produced by SOGAParser#const_term.
    def enterConst_term(self, ctx:SOGAParser.Const_termContext):
        pass

    # Exit a parse tree produced by SOGAParser#const_term.
    def exitConst_term(self, ctx:SOGAParser.Const_termContext):
        pass


    # Enter a parse tree produced by SOGAParser#add.
    def enterAdd(self, ctx:SOGAParser.AddContext):
        pass

    # Exit a parse tree produced by SOGAParser#add.
    def exitAdd(self, ctx:SOGAParser.AddContext):
        pass


    # Enter a parse tree produced by SOGAParser#add_term.
    def enterAdd_term(self, ctx:SOGAParser.Add_termContext):
        pass

    # Exit a parse tree produced by SOGAParser#add_term.
    def exitAdd_term(self, ctx:SOGAParser.Add_termContext):
        pass


    # Enter a parse tree produced by SOGAParser#mul.
    def enterMul(self, ctx:SOGAParser.MulContext):
        pass

    # Exit a parse tree produced by SOGAParser#mul.
    def exitMul(self, ctx:SOGAParser.MulContext):
        pass


    # Enter a parse tree produced by SOGAParser#conditional.
    def enterConditional(self, ctx:SOGAParser.ConditionalContext):
        pass

    # Exit a parse tree produced by SOGAParser#conditional.
    def exitConditional(self, ctx:SOGAParser.ConditionalContext):
        pass


    # Enter a parse tree produced by SOGAParser#ifclause.
    def enterIfclause(self, ctx:SOGAParser.IfclauseContext):
        pass

    # Exit a parse tree produced by SOGAParser#ifclause.
    def exitIfclause(self, ctx:SOGAParser.IfclauseContext):
        pass


    # Enter a parse tree produced by SOGAParser#elseclause.
    def enterElseclause(self, ctx:SOGAParser.ElseclauseContext):
        pass

    # Exit a parse tree produced by SOGAParser#elseclause.
    def exitElseclause(self, ctx:SOGAParser.ElseclauseContext):
        pass


    # Enter a parse tree produced by SOGAParser#block.
    def enterBlock(self, ctx:SOGAParser.BlockContext):
        pass

    # Exit a parse tree produced by SOGAParser#block.
    def exitBlock(self, ctx:SOGAParser.BlockContext):
        pass


    # Enter a parse tree produced by SOGAParser#bexpr.
    def enterBexpr(self, ctx:SOGAParser.BexprContext):
        pass

    # Exit a parse tree produced by SOGAParser#bexpr.
    def exitBexpr(self, ctx:SOGAParser.BexprContext):
        pass


    # Enter a parse tree produced by SOGAParser#lexpr.
    def enterLexpr(self, ctx:SOGAParser.LexprContext):
        pass

    # Exit a parse tree produced by SOGAParser#lexpr.
    def exitLexpr(self, ctx:SOGAParser.LexprContext):
        pass


    # Enter a parse tree produced by SOGAParser#monom.
    def enterMonom(self, ctx:SOGAParser.MonomContext):
        pass

    # Exit a parse tree produced by SOGAParser#monom.
    def exitMonom(self, ctx:SOGAParser.MonomContext):
        pass


    # Enter a parse tree produced by SOGAParser#prune.
    def enterPrune(self, ctx:SOGAParser.PruneContext):
        pass

    # Exit a parse tree produced by SOGAParser#prune.
    def exitPrune(self, ctx:SOGAParser.PruneContext):
        pass


    # Enter a parse tree produced by SOGAParser#observe.
    def enterObserve(self, ctx:SOGAParser.ObserveContext):
        pass

    # Exit a parse tree produced by SOGAParser#observe.
    def exitObserve(self, ctx:SOGAParser.ObserveContext):
        pass


    # Enter a parse tree produced by SOGAParser#loop.
    def enterLoop(self, ctx:SOGAParser.LoopContext):
        pass

    # Exit a parse tree produced by SOGAParser#loop.
    def exitLoop(self, ctx:SOGAParser.LoopContext):
        pass


    # Enter a parse tree produced by SOGAParser#expr.
    def enterExpr(self, ctx:SOGAParser.ExprContext):
        pass

    # Exit a parse tree produced by SOGAParser#expr.
    def exitExpr(self, ctx:SOGAParser.ExprContext):
        pass


    # Enter a parse tree produced by SOGAParser#vars.
    def enterVars(self, ctx:SOGAParser.VarsContext):
        pass

    # Exit a parse tree produced by SOGAParser#vars.
    def exitVars(self, ctx:SOGAParser.VarsContext):
        pass


    # Enter a parse tree produced by SOGAParser#idd.
    def enterIdd(self, ctx:SOGAParser.IddContext):
        pass

    # Exit a parse tree produced by SOGAParser#idd.
    def exitIdd(self, ctx:SOGAParser.IddContext):
        pass


    # Enter a parse tree produced by SOGAParser#symvars.
    def enterSymvars(self, ctx:SOGAParser.SymvarsContext):
        pass

    # Exit a parse tree produced by SOGAParser#symvars.
    def exitSymvars(self, ctx:SOGAParser.SymvarsContext):
        pass


    # Enter a parse tree produced by SOGAParser#gm.
    def enterGm(self, ctx:SOGAParser.GmContext):
        pass

    # Exit a parse tree produced by SOGAParser#gm.
    def exitGm(self, ctx:SOGAParser.GmContext):
        pass


    # Enter a parse tree produced by SOGAParser#uniform.
    def enterUniform(self, ctx:SOGAParser.UniformContext):
        pass

    # Exit a parse tree produced by SOGAParser#uniform.
    def exitUniform(self, ctx:SOGAParser.UniformContext):
        pass


    # Enter a parse tree produced by SOGAParser#list.
    def enterList(self, ctx:SOGAParser.ListContext):
        pass

    # Exit a parse tree produced by SOGAParser#list.
    def exitList(self, ctx:SOGAParser.ListContext):
        pass



del SOGAParser