# Contains the classes definition for CFG objects and the function produce_cfg, that extracts a CFG from a program script in a .txt file. 

# A CFGnode object can belong to six different subclasses (EntryNode, StateNode, TestNode, ObserveNode, MergeNode and ExitNode). All subclasses share the following attributes:
# - node_name, containing a string with a unique name for the node (usually in the form 'nodetypeX' with X integer progressively assigned);
# - node_type, containing a string with the node type;
# - parent, a list containing pointers to the parent nodes;
# - children, a list containing pointers to the children nodes;

# Furthermore some node have additional attributes and methods.

# StateNode objects have:
# - an expr attribute storing a string with a valid assignment instruction generated from the SOGA grammar reported in 'SOGA.g4';
# - a cond attribute which can take value True, False or None;
# - the methods set_expr, set_cond to set the values of the previous attributes to specific values.

# TestNode and ObserveNode objects have:
# - an LBC attribute storing a string with a valid LBC condition generated from the SOGA grammar;
# - the method set_LBC to set the values of the previous attribute to specific values.

# MergeNode objects have:
# - an attribute list_dist storing a list, initialized to the empty string.

# The class CFG is a subclass of the class SOGAListener automatically generetad by ANTLR4 from the grammar contained in 'SOGA.g4'. CFG extends the methods of SOGAListener so that when called on the parse tree of a valid SOGA script, the CFG representing the program in the script is created and stored in the attribute root of the class. Other attributes store relevant information about the structure of the CFG. Finally the method plot_edges, is used to print the edges of the CFG for sebugging purposes.

# The function produce_cfg is invoked on a .txt file containing the valid script of a SOGA program. It uses the libraries SOGALexer and SOGAParser (automatically generated using ANTLR4) to create the parse tree of the program and subsequently explores it recursively using the customized CFG listener. Returns the CFG object generated from the program script.

# TO DO:
# - make array accessible also with expression such as i-1, i+1, ecc.

from antlr4 import *
from SOGALexer import *
from SOGAParser import *
from SOGAListener import *

class CFGnode:
    
    def __init__(self, node_name, node_type):
        self.name = node_name
        self.type = node_type
        
        self.dist = None
        self.p = 1
        self.trunc = None
        
        self.parent = []
        self.children = []
        
    def set_dist(self, dist):
        self.dist = dist
        
    def set_p(self, p):
        self.p = p
        
    def set_trunc(self, trunc):
        self.trunc = trunc
        
class EntryNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'entry')
        
    def __str__(self):
        return 'EntryNode<>'
    
    def __repr__(self):
        return str(self)
        
class StateNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'state')
        self.expr = None
        self.cond = None
        
    def set_expr(self, expr):
        self.expr = expr
        
    def set_cond(self, cond):
        self.cond = cond
        
    def __str__(self):
        return 'StateNode<{},{},{}>'.format(self.name,self.cond,self.expr)
    
    def __repr__(self):
        return str(self)
        
class TestNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'test')
        self.LBC = None
        
    def set_LBC(self, LBC):
        self.LBC = LBC
        
    def __str__(self):
        return 'TestNode<{},{}>'.format(self.name,self.LBC)
    
    def __repr__(self):
        return str(self)
        
class ObserveNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'observe')
        self.LBC = None
        self.hard = None
        
    def set_LBC(self, LBC):
        self.LBC = LBC
        
    def __str__(self):
        return 'ObserveNode<{},{}>'.format(self.name,self.LBC)
  
    def __repr__(self):
        return str(self)
    
class MergeNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'merge')
        self.list_dist = []
        
    def __str__(self):
        return 'MergeNode<{}>'.format(self.name)
    
    def __repr__(self):
        return str(self)
    
class PruneNode(CFGnode):
    def __init__(self, node_name):
        super().__init__(node_name, 'prune')
        self.Kmax = None
        
    def __str__(self):
        return 'PruneNode<{}>'.format(self.name)
    
    def __repr__(self):
        return str(self)
        
    
class LoopNode(CFGnode):
    def __init__(self, node_name):
        super().__init__(node_name, 'loop')
        self.idx = None
        self.const = None
        
    def __str__(self):
        return 'LoopNode<{}>'.format(self.name)
    
    def __repr__(self):
        return str(self)

class ExitNode(CFGnode):
    
    def __init__(self, node_name):
        super().__init__(node_name, 'exit')
        self.list_dist = []
        
    def __str__(self):
        return 'ExitNode<>'
    
    def __repr__(self):
        return str(self)

    
class CFG(SOGAListener):
    
    def __init__(self):
        # counters for nodes of different types
        self.n_state = 0
        self.n_test = 0
        self.n_merge = 0
        self.n_observe = 0
        self.n_loop = 0
        self.n_prune = 0
        # root of the CFG
        self.root = EntryNode('entry')
        # dictionary for data
        self.data = {}
        # dictionary keeping track of the nodes in CFG 
        self.node_list = {'entry':self.root}
        self.ID_list = []
        # hidden variables used in the construction of the CFG
        self._current_node = self.root
        self._flag = None
        self._subroot = []
        
    def enterData(self, ctx):
        data_name = ctx.symvars().getText()
        data_value = eval(ctx.list_().getText())
        self.data[data_name] = data_value
        
    def enterArray(self, ctx):
        n = int(ctx.NUM().getText())
        var_name = ctx.IDV().getText()
        for i in range(n):
            self.ID_list.append(var_name+'['+str(i)+']')
        
    def enterAssignment(self, ctx):
        """ When an Assignment instruction is entered a new StateNode is added to the CFG, storing a string with the assignment instruction. Dependence from a TestNode, encoded in the variable _flag, is checked to initialize the attribute cond."""
        node = StateNode('state{}'.format(self.n_state))
        self.n_state += 1
        if self._flag is not None:
            node.cond = self._flag
            self._flag = None
        node.expr = ctx.getText()
        node.parent.append(self._current_node)
        self._current_node.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node
            

    def enterConditional(self, ctx):
        """ When a Conditional statement is entered a new TestNode is added to the CFG and to the stack _subroot."""
        node = TestNode('test{}'.format(self.n_test))
        self.n_test += 1
        node.parent.append(self._current_node)
        self._current_node.children.append(node)
        self._current_node = node
        self._subroot.append(self._current_node)
        self.node_list[node.name] = node

    def enterIfclause(self, ctx):
        """ When the Ifclause of a conditional statement is entered the LBC is stored as a string in the LBC attribute of the corresponding TestNode and _flag is set to True."""
        self._current_node.LBC = ctx.bexpr().getText()
        self._flag = True
        # first node after if must be a state node with cond=True
        if ctx.block().instr(0).assignment() is None:
            self.create_skip()            
        
    def exitIfclause(self, ctx):
        """ When the Ifclause of a conditional statement is exited the current_node is set to the last added subroot (pointing to the last created TestNode)."""
        self._current_node = self._subroot[-1]
        
    def enterElseclause(self, ctx):
        """ When the Elseclause of a conditional statement is entered _flag is set to False."""
        self._flag = False
        # first node after if must be a state node with cond=False
        if ctx.block().instr(0).assignment() is None:
            self.create_skip()
        
    def exitElseclause(self, ctx):
        """ When the Elseclause of a conditional statement is exited the last added subroot is deleted from the stack and a merge node is added to the cfg"""
        self._current_node = self._subroot.pop()
        node = MergeNode('merge{}'.format(self.n_merge))
        self.n_merge += 1
        node.parent, _ = self.get_leaves(self._current_node, [], [])
        for parent in node.parent:
            parent.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node
               
    def enterObserve(self, ctx):
        """ When an Observe statement is entered an ObserveNode is added to the CFG, storing the LBC condition in the attribute LBC."""
        node = ObserveNode('observe{}'.format(self.n_observe))
        if 'hobserve' in ctx.getText():
            node.hard = True
        else:
            node.hard = False
        node.LBC = ctx.bexpr().getText()
        self.n_observe += 1
        node.parent.append(self._current_node)
        self._current_node.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node       
        
    def enterPrune(self, ctx):
        """ When a merge statement is entered a new MergeNode is added to the CFG."""
        node = PruneNode('prune{}'.format(self.n_merge))
        self.n_prune += 1
        node.parent, _ = self.get_leaves(self._current_node, [], [])
        for parent in node.parent:
            parent.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node
        self._current_node.Kmax = int(ctx.NUM().getText())
        
    def enterLoop(self, ctx):
        node = LoopNode('loop{}'.format(self.n_loop))
        self.n_loop += 1
        node.parent.append(self._current_node)
        self._current_node.children.append(node)
        self._current_node = node
        self._subroot.append(self._current_node)
        self.node_list[node.name] = node
        idx_name = ctx.IDV().getText()
        self._current_node.idx = idx_name
        self.data[idx_name] = [None]
        if not ctx.NUM() is None:
            self._current_node.const = ctx.NUM().getText()
        else:
            self._current_node.const = ctx.idd().getText()
        self._flag = True
        # first node after loop must be a state node with cond=True
        if ctx.block().instr(0).assignment() is None:
            self.create_skip()

    def exitLoop(self, ctx):
        if self._current_node.type != 'state':
            self.create_skip()
        self._current_node.children.append(self._subroot[-1])
        self._subroot[-1].parent.append(self._current_node)
        self._current_node = self._subroot.pop()
        self._flag = False
        self.create_skip()
    
    def exitProgr(self, ctx):
        """ When the end of the program is reached an ExitNode is added to the CFG and all leaves are linked to it."""
        node = ExitNode('exit')
        node.parent, _ = self.get_leaves(self._current_node, [], [])
        for parent in node.parent:
            parent.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node
        
    def enterSymvars(self, ctx):
        """ Symbolic variables names encountered during the parsing are stored in the attribute list ID_list."""
        if not ctx.IDV() is None:
            var = ctx.IDV().getText()
            if var not in self.ID_list and var not in self.data.keys():
                self.ID_list.append(var)
                         
        
    def get_leaves(self, node, leaves, checked):
        """ Recursively finds all the leaves of the subtree starting in node."""
        checked.append(node)
        if len(node.children) == 0:
            if node not in leaves:
                leaves.append(node)
        else:
            for child in node.children:
                if not child in checked:
                    leaves, checked = self.get_leaves(child, leaves, checked)
        return leaves, checked
    
    
    def plot_edges(self):
        edges = []
        for node_name in self.node_list:
            node = self.node_list[node_name]
            for child in node.children:
                edge = '(' + node.name + ',' + child.name + ')'
                edges.append(edge)
        print(edges)
        
    def create_skip(self):
        node = StateNode('state{}'.format(self.n_state))
        self.n_state += 1
        node.cond = self._flag
        self._flag = None
        node.expr = 'skip'
        node.parent.append(self._current_node)
        self._current_node.children.append(node)
        self._current_node = node
        self.node_list[node.name] = node

    def enterUniform(self,ctx):
        pass
        #print("uniform",ctx.getText())    
    
    # Enter a parse tree produced by SOGAParser#gm.
    def enterGm(self, ctx):
        pass
        #print("gm",ctx.getText()) 
        
def produce_cfg(filename):
    """ Parses filename using ANTLR4. Returns a CFG object. """
    #input_file =  open('../script/'+ filename + '.txt', 'r').read()
    input_file =  open(filename, 'r').read()
    lexer = SOGALexer(InputStream(input_file))
    stream = CommonTokenStream(lexer)
    parser = SOGAParser(stream)
    tree = parser.progr()
    cfg = CFG()
    walker = ParseTreeWalker()
    walker.walk(cfg, tree) 
    return cfg