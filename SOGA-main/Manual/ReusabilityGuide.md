
## Reusability: how to write your SOGA model
A formal description of SOGA's grammar can be found in the file grammars/SOGA.g4.  
A SOGA model is encoded in a .soga file.

### Data
At the beginning of your file you can declare data. These are arrays that can be accessed but cannot be overwritten by the program. To declare data use the keyword `data` before declaring an array. For example:

`data obs = [0., 1., 0., 0., 1.];`

can be accessed at any point of the program using `obs[i]` where `i` is an integer index (indexing starts from 0).

NOTE: currently SOGA does not support index arithmetic. Arrays and data can only be accessed using a single variable or a number, not expressions such as `i+1`.

### Programs

SOGA supports 5 types of instruction: assignments, conditionals, loops, observe and prune.

In the following:

- `var` is any variable name. You do not need to declare scalar variables in advance, as SOGA infers them automatically when parsing the program. For array variables declare `array[size] var` before using the array, for example `array[10] y;`. Array values are accessed using the usual notation `var[i]` where `i` is an integer index ;

- `const` is either a constant (i.e. a number) or a data value;

- `dist` is a distribution. In SOGA all distributions are approximated by Gaussian Mixtures, which are declared as `gm(pi_list, mu_list, sigma_list)` where `pi_list` is a list of scalar weights summing to 1, `mu_list` is a list of scalar means and `sigma_list` is a list of scalar standard deviations. For example a standard normal distribution can be assigned using `gm([1.], [0.], [1.])` or the shortcut `gauss(0,1)`. Supported primitives for assigning distributions are: `gauss(mu, sigma)`, `bernoulli(p)`, `uniform([a,b], C)`, `beta([a,b], C)`, `laplace(mu, sigma, C)`, `exprnd(lambda, C)` where `C` is the number of components of the approximating mixture and `mu`, `sigma`, `a`, `b`, `lambda` are distribution-specific parameters. 

- `block` is any sequence of instructions.

* Assignments assign a program variable with a value. An assignment can be either be linear or non-linear. A linear assignment has the form

`var_name = const + const*var + ... + const*var;`

A non-linear assignment has the form:

` var_name = const*var*var; `  

At the R.H.S. of an assignment `var` can also be a distribution `dist`. To assign more complex expressions use subsequent assignments. For example:

` z = x + y + 1;`

`z = x*z;`

* Conditionals are expressed by if-then-else statements. The main structure is:

` if bexpr { block } else { block } end if;`

Here `bexpr` is a Boolean expression which can either be of the form:

`const*var + ... + const*var (< | <= | >=| > ) const`

where at the L.H.S. `var` can also be a `dist`, or of the form:

` var == const`.

For example:

`if x == 0 { y = 1; } else { y = 2*x +1; } end if;`

* Loops are expressed by *bounded* for statement. The main structure is:

`for var in range(const) { block } end for;`

For example:

`for i in range(10) { x = obs[i]; } end for;`

* Observe are expressed as

`observe(bexpr)` where `bexpr` is as in the conditional statement, except that it cannot contains `dist`.

For example:

`observe(x + y > 0)`

`observe(y == obs[0])`

* Prune instructions have the effect of pruning the current distribution, which is represented as a Gaussian Mixtures, up to a user-defined number of components. They can be inserted in any point of the program to improve scalability using `prune(K)`.

For example, `prune(30)` will prune the current distribution up to 30 components.

You can find a commented SOGA model in the folder `programs/Example/Bernoulli.soga`. Other SOGA models are available in the folder `programs/SOGA/`