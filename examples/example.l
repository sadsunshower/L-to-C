INPUT                   | n

                        | TRUE
                        | 1 = F(0)
f := 1;                 | f = F(0)
k := 0;                 | f = F(k)
if n = 0 then           | n = 0
    f := 1;             | f = F(k)
else                    | N(n,0)
    while ~(k = n) do   | (f = F(k)) & N(k,n)
                        | M(f,(k + 1)) = F(k + 1)
        k := k + 1;     | M(f,k) = F(k)
        f := f * k;     | f = F(k)
    od                  | f = F(k) & (k = n)
fi                      | f = F(k)

MATHS
B | F(0) = 1
R | F(k) = k * F(k - 1)
F | M(a,b) = a * b
P | N(a,b) : ~(a = b)

TEST
n = 0
n = 1
n = 3
n = 5