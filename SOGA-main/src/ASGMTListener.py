# Generated from ASGMT.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ASGMTParser import ASGMTParser
else:
    from ASGMTParser import ASGMTParser

# This class defines a complete listener for a parse tree produced by ASGMTParser.
class ASGMTListener(ParseTreeListener):

    # Enter a parse tree produced by ASGMTParser#assignment.
    def enterAssignment(self, ctx:ASGMTParser.AssignmentContext):
        pass

    # Exit a parse tree produced by ASGMTParser#assignment.
    def exitAssignment(self, ctx:ASGMTParser.AssignmentContext):
        pass


    # Enter a parse tree produced by ASGMTParser#add.
    def enterAdd(self, ctx:ASGMTParser.AddContext):
        pass

    # Exit a parse tree produced by ASGMTParser#add.
    def exitAdd(self, ctx:ASGMTParser.AddContext):
        pass


    # Enter a parse tree produced by ASGMTParser#add_term.
    def enterAdd_term(self, ctx:ASGMTParser.Add_termContext):
        pass

    # Exit a parse tree produced by ASGMTParser#add_term.
    def exitAdd_term(self, ctx:ASGMTParser.Add_termContext):
        pass


    # Enter a parse tree produced by ASGMTParser#term.
    def enterTerm(self, ctx:ASGMTParser.TermContext):
        pass

    # Exit a parse tree produced by ASGMTParser#term.
    def exitTerm(self, ctx:ASGMTParser.TermContext):
        pass


    # Enter a parse tree produced by ASGMTParser#symvars.
    def enterSymvars(self, ctx:ASGMTParser.SymvarsContext):
        pass

    # Exit a parse tree produced by ASGMTParser#symvars.
    def exitSymvars(self, ctx:ASGMTParser.SymvarsContext):
        pass


    # Enter a parse tree produced by ASGMTParser#idd.
    def enterIdd(self, ctx:ASGMTParser.IddContext):
        pass

    # Exit a parse tree produced by ASGMTParser#idd.
    def exitIdd(self, ctx:ASGMTParser.IddContext):
        pass


    # Enter a parse tree produced by ASGMTParser#gm.
    def enterGm(self, ctx:ASGMTParser.GmContext):
        pass

    # Exit a parse tree produced by ASGMTParser#gm.
    def exitGm(self, ctx:ASGMTParser.GmContext):
        pass


    # Enter a parse tree produced by ASGMTParser#list.
    def enterList(self, ctx:ASGMTParser.ListContext):
        pass

    # Exit a parse tree produced by ASGMTParser#list.
    def exitList(self, ctx:ASGMTParser.ListContext):
        pass


    # Enter a parse tree produced by ASGMTParser#sub.
    def enterSub(self, ctx:ASGMTParser.SubContext):
        pass

    # Exit a parse tree produced by ASGMTParser#sub.
    def exitSub(self, ctx:ASGMTParser.SubContext):
        pass



del ASGMTParser