from sympy import symbols, Sum, Rational, pi, sin, cos, exp, factorial, sqrt

# Define symbols for use in expressions
i, n, x = symbols('i n x')

# Generating 10 random complex LaTeX mathematical expressions
expressions = [
    Sum(2**i + Rational(3**i, i**3), (i, 0, 10))**i,
    Sum(sin(i)/factorial(i), (i, 1, 10)),
    Sum(cos(i)/(i**2 + 1), (i, 1, 10)),
    Sum(exp(-i**2)/i, (i, 1, 10)),
    pi**i + sqrt(i),
    factorial(i)/exp(i),
    Sum(i/(i**2 + 1), (i, 1, n))**2,
    Sum(1/factorial(i), (i, 0, n)),
    (sin(i) + cos(i))**i,
    (2*pi*i + exp(-i))/(i**2 + 1)
]

# Convert expressions to LaTeX format
latex_expressions = [latex(expr) for expr in expressions]
latex_expressions