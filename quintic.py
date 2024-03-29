import cmath


def solve_quintic(a, b, c, d, e, f):
    # Step 1: Depress the quintic equation
    c = (5*a**2*d - 2*a*b**2) / (5*a**2)
    e = (b**3 - 5*a*b*c) / (5*a**2)
    g = (5*a**2*f - b*c*e + 2*a*b*d*e - b**2*d**2) / (5*a**3)

    # Step 2: Depress ay^5 equation
    p = (5*c - 2*b**2) / (5*a)
    q = (b**5 - 10*a*b**3*c + 25*a**2*b**2*d + 10*a*b*c**2 - 5*a**2*b**2*c) / (25*a**5) - \
        (5*b**2*d**2 - 2*b*c*d**2 - 5*a*c*f**2 +
         b*c*e**2 + 5*a*b*d*f - 2*a*b*e) / (25*a**4)

    # Step 3: Make cubic equation
    A = (-25*p**2 + 5*q) / 125
    B = (p**3 - 5*p*q) / 500

    # Step 4: Solve the depressed cubic equation
    delta = (A/3)**3 - B/2

    if delta >= 0:
        u1 = pow(-B/2 + cmath.sqrt(delta), 1/3)
        u2 = pow(-B/2 - cmath.sqrt(delta), 1/3)
    else:
        theta = cmath.acos(-B/2 / cmath.sqrt((A/3)**3))
        u1 = 2*pow(A/3, 1/3)*cmath.cos(theta/3)
        u2 = u1.conjugate()
        u3 = cmath.exp(complex(0, 2*cmath.pi/3)) * u1

    l1 = u1 - A/(3*u1)
    l2 = u2 - A/(3*u2)

    if delta < 0:
        l3 = u3 - A/(3*u3)
    else:
        l3 = l2

    # Step 5: Find the roots of the original quintic equation
    w1 = l1 - A/(3*l1)
    w2 = l2 - A/(3*l2)
    w3 = l3 - A/(3*l3)

    x1 = w1 - (p/(5*w1)) - (5*d - 2*b**2)/(25*a)
    x2 = w2 - (p/(5*w2)) - (5*d - 2*b**2)/(25*a)
    x3 = w3 - (p/(5*w3)) - (5*d - 2*b**2)/(25*a)
    x4 = -w1 + ((p/(5*w1)) + 1) * cmath.sqrt(3)*1j - (5*d - 2*b**2)/(25*a)
    x5 = -w1 - ((p/(5*w1)) + 1) * cmath.sqrt(3)*1j - (5*d - 2*b**2)/(25*a)

    return x1, x2, x3, x4, x5


print(solve_quintic(1, 1, 1, 1, 1, 1))
print(solve_quintic(2, 3, -4, 5, 6, -7))
