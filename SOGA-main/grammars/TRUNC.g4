grammar TRUNC; 

trunc: ineq | eq;

ineq: lexpr inop const;
inop: '<=' | '<' | '>' | '>=';

eq: var eqop const;
eqop: '==' | '!=';

lexpr: monom ((sum|sub) monom)*?;
monom: (const '*')? var;

const: NUM | idd;
var: IDV | idd | gm;
idd : IDV '[' (NUM | IDV) ']';
gm: 'gm(' list ',' list ',' list ')';
list: '[' NUM (',' NUM)*? ']';

sum: '+';
sub: '-';

IDV : ALPHA (ALPHA|DIGIT)*;
NUM : '-'? DIGIT+ ('.' DIGIT*)?; 

COMM : '/*' .*? '*/' -> skip;
WS : (' '|'\t'|'\r'|'\n') -> skip;
 
ALPHA : [a-zA-Z];
DIGIT : [0-9];