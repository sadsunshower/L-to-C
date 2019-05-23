# L to C

A transpiler from L to C.

## L

L is a simple imperative programming language, most famous for it's use in UNSW's COMP2111. I have adapted the syntax slightly to be computer-readable.

### An L file: L program

Each L file starts with a program definition:

```
INPUT               | (list of input variables separated by ,)
(l statements...)   | (assertions...)
```

The first line describes a number of (single letter) input variables which are to be used in the program.

Following this, regular L syntax can be used:

#### Assignments

Assign a value to a variable.

```
x := 0;
```

#### While Loops

Iterate while a condition is still met:

```
while ~(x = 4) do
    x := x + 1;
od
```

#### If-else Statements

Conditionally execute code:

```
if (x % 2 = 0) then
    x := x / 2;
else
    x := (3 * x) + 1;
fi
```

Totally blank lines are always ignored and can be added for readability.

Variables do not need to be defined (the script will automatically define them in the C code, but the L code should initialise them reliably)

Each line of L syntax should be annotated with some assertion (TRUE by itself is fine). The assertion can be any boolean expression:

```
x := 0;     | x = 0 & ~(x = 1)
```

Assertions can also exist on their own:

```
            | ~(1 = 0)
```

### An L File: MATHS rules

For the sake of being concise, we sometimes need to externally define functions / propositions. L to C gives us three ways to do this:

#### Recursive functions

Functions can be defined with any number of base cases, and one recursive case, example:

```
MATHS
B | P(x,0) = x
R | P(x,n) = x * P(x,n-1)
```

#### Literal functions

Functions can also be defined literally

```
MATHS
F | A(x,y) = x + y
```

#### Propositions

Propositions can be defined literally

```
MATHS
P | E(n) : (n % 2) == 0
```

Once these are defined, we can use them anywhere in our L program (either in L statements or assertions)

### An L file: TEST cases

We can define some test cases to check our L program against, which will be run when the transpiled C program is run.

Each test case is one line, and consists of comma-separated assignments for the input variables:

```
TEST
a = 1, b = 2
a = 2, b = 1
a = 4, b = 2
```

## Pitfalls

This program is very early in development, and as such has barely any error handling or stability. Pull requests are encouraged.