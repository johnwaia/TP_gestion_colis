def tri_fusion(elements, cle, decroissant=False):
    n = len(elements)
    # Paires (clé, élément) : la clé n'est évaluée qu'une fois.
    src = [(cle(e), e) for e in elements]
    if n < 2:
        return [e for _, e in src]
    dst = [None] * n

    if decroissant:
        def avant(a, b):  # a doit passer avant b (>= garantit la stabilité)
            return a >= b
    else:
        def avant(a, b):
            return a <= b

    largeur = 1
    while largeur < n:
        for debut in range(0, n, 2 * largeur):
            milieu = min(debut + largeur, n)
            fin = min(debut + 2 * largeur, n)
            i, j, k = debut, milieu, debut
            while i < milieu and j < fin:
                if avant(src[i][0], src[j][0]):
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                k += 1
            while i < milieu:
                dst[k] = src[i]
                i += 1
                k += 1
            while j < fin:
                dst[k] = src[j]
                j += 1
                k += 1
        src, dst = dst, src
        largeur *= 2

    return [e for _, e in src]


def tri_par_denombrement(elements, cle, cle_min, cle_max, decroissant=False):
    seaux = [[] for _ in range(cle_max - cle_min + 1)]
    for e in elements:
        seaux[cle(e) - cle_min].append(e)
    if decroissant:
        seaux.reverse()
    resultat = []
    for s in seaux:
        resultat.extend(s)
    return resultat
