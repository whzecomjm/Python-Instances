## cf. MO Implementation of the Robinson-Schensted Correspondence
## https://mathoverflow.net/questions/30910/implementation-of-the-robinson-schensted-correspondence

from bisect import bisect
def RSK(p):
    '''Given a permutation p, spit out a pair of Young tableaux'''
    P = []; Q = []
    def insert(m, n=0):
        '''Insert m into P, then place n in Q at the same place'''
        for r in range(len(P)):
            if m > P[r][-1]:
                P[r].append(m); Q[r].append(n)
                return
            c = bisect(P[r], m)
            P[r][c],m = m,P[r][c]
        P.append([m])
        Q.append([n])

    for i in range(len(p)):
        insert(int(p[i]), i+1)
    return (P,Q)

print(RSK('1364752'))
