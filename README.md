# tinyl

	tinyl is a python version of the dragon book's front end.

## The Grammer

	program	->	block
	block 	->	{ decls stmts }
	decls 	->	decls decl | ε
	decl 	->	type id;
	type 	->	type [num] | basic
	stmts 	->  stmts stmt | ε
	stmt 	-> 	loc = bool;
			|	if (bool) stmt
			| 	if (bool) stmt else stmt
			| 	while (bool) stmt
			| 	do stmt while (bool);
			|	break;
			|	block
	loc 	->	loc [bool] | id
	bool	-> 	bool || join | join
	join 	-> 	join && equality | equality
	equality->	equality == rel | equality != rel | rel
	rel		-> 	expr < expr | expr <= expr | expr > expr | expr >= expr | expr
	expr 	-> 	expr + term | expr - term | term
	term 	-> 	term * unary | term / unary | unary
	unary	-> 	!unary	| -unary | factory
	factory ->	(bool) | loc | num | real | true | false