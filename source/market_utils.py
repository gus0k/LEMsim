import numpy as np

def get_value_steps(x, f):
    """
    Given a stepwise function f represented as a list
    of the leftmost points in the intervals, returns
    f(x). The rightmost intervals extends infinitely to the right
    and the leftmost to the left
    
    Returns:
        the pair (x, f(x)) if x is in the domain of f (to the
        right of the first element, or (x, None) otherwise)
    """
    N = len(f)
    for i in range(N):
        if i == N - 1:
            return f[i]
        elif f[i + 1][0] > x:
            return f[i]

def intersect_stepwise_functions(f, g):
    """
    f and g are stepwise constant functions defined
    as a list of (x,y) points where each point is the 
    left most point of the interval. The last interval
    is assumed to continue infitely.
    Params:
        f,g: the two functions to intercept. It is assumed that
        f (demand) is greater than g (supply) until the intersection.
    Returns:
        q_ast: x at which both functions intersect
        
        
    """
    EPS = 1e-8
    sample_f_1 = []
    sample_g_1 = []
    for (q, p) in f:
        sample_f_1.append((q, p, 'f'))
        v = get_value_steps(q, g)
        sample_g_1.append((q, v[1], 'f'))

    ### Compute the value of both functions in the change points of the selling curve
    sample_f_2 = []
    sample_g_2 = []
    for (q, p) in g:
        sample_g_2.append((q, p, 'g'))
        v = get_value_steps(q, f)
        sample_f_2.append((q, v[1], 'g'))

    ### Combine both points into one list
    all_f = sample_f_1 + [x for x in sample_f_2 if x not in sample_f_1]
    all_f = sorted(all_f, key = lambda x: (x[0], x[2]))

    all_g = sample_g_1 + [x for x in sample_g_2 if x not in sample_g_1]
    all_g = sorted(all_g, key = lambda x: (x[0], x[2]))


    ### Find the first time where the curves switch position 
    cont = lambda i, j: all_f[i][1] >= all_g[j][1]
    success = False
    for i in range(len(all_f) - 1):
        if cont(i, i) and not cont(i + 1, i + 1):
            success = True
            break

    if not success:
        return None, None, None
    else:
        q_ast = all_f[i + 1][0]
        if all_f[i + 1][2] == 'f':
            f_q = get_value_steps(q_ast - EPS, f)[0]
            g_q = get_value_steps(q_ast, g)[0]
        else: 
            f_q = get_value_steps(q_ast, f)[0]
            g_q = get_value_steps(q_ast - EPS, g)[0]
        return q_ast, f_q, g_q