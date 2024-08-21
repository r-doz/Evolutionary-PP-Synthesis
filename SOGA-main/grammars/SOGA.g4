grammar SOGA; 

progr : (data ';')*? (instr ';' | array ';')*;

data : 'data' symvars '=' list;

array: 'array[' NUM ']' IDV;

instr : assignment | conditional | prune | observe | loop;

assignment: symvars '=' (const | add | mul) | 'skip';

const: const_term (('+'|'-') const_term)*?;
const_term: (NUM | idd) ('*' (NUM | idd))?;
add: add_term (('+'|'-') add_term)*?;
add_term: ((NUM | idd) '*')? vars | const_term;
mul: ((NUM | idd) '*')? vars '*' vars;

conditional: ifclause elseclause 'end if';

ifclause : 'if' bexpr '{' block '}';
elseclause : 'else' '{' block '}';
block : (instr ';')+;
bexpr : lexpr ('<'|'<='|'>='|'>') (NUM | idd) | symvars ('=='|'!=') (NUM | idd);
lexpr: monom (('+'|'-') monom)*?;
monom: ((NUM | idd) '*')? vars;

prune : 'prune(' NUM ')';

observe: 'observe(' bexpr ')';

loop : 'for' IDV 'in range(' (NUM | idd) ')' '{' block '}' 'end for';

expr : lexpr | (NUM '*')? vars '*' vars | vars '^2' ;

vars: symvars | gm | uniform;
idd: IDV '[' (NUM | IDV) ']';
symvars : IDV | idd;
gm: 'gm(' list ',' list ',' list ')';
uniform: 'uniform(' list ',' NUM ')';
list: '[' NUM (',' NUM)*? ']';

IDV : ALPHA (ALPHA|DIGIT)*;
NUM : '-'? DIGIT+ ('.' DIGIT*)?;

COMM : '/*' .*? '*/' -> skip;
WS : (' '|'\t'|'\r'|'\n') -> skip;

fragment 
ALPHA : [a-zA-Z];
DIGIT : [0-9];