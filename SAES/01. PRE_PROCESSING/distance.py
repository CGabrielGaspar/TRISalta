import numpy as np
import math

def hamming(u, v):
    """
    Compute the Hamming distance between two 1-D arrays.
    The Hamming distance between 1-D arrays `u` and `v`, is simply the
    proportion of disagreeing components in `u` and `v`. If `u` and `v` are
    boolean vectors, the Hamming distance is
    .. math::
       \\frac{c_{01} + c_{10}}{n}
    where :math:`c_{ij}` is the number of occurrences of
    :math:`\\mathtt{u[k]} = i` and :math:`\\mathtt{v[k]} = j` for
    :math:`k < n`.
    Parameters
    ----------
    u : (N,) array_like
        Input array.
    v : (N,) array_like
        Input array.
    Returns
    -------
    hamming : double
        The Hamming distance between vectors `u` and `v`.
    Examples
    --------
    >>> from scipy.spatial import distance
    >>> distance.hamming([1, 0, 0], [0, 1, 0])
    0.66666666666666663
    >>> distance.hamming([1, 0, 0], [1, 1, 0])
    0.33333333333333331
    >>> distance.hamming([1, 0, 0], [2, 0, 0])
    0.33333333333333331
    >>> distance.hamming([1, 0, 0], [3, 0, 0])
    0.33333333333333331
    """
    if u.shape != v.shape:
        raise ValueError('The 1d arrays must have equal lengths.')
    u_ne_v = u != v
    return np.average(u_ne_v)

def pdist(X, *, out=None, metric, **kwargs):
    n = X.shape[0]
    out_size = (n * (n - 1)) // 2
    dm = _prepare_out_argument(out, np.double, (out_size,))
    k = 0
    for i in range(X.shape[0] - 1):
        for j in range(i + 1, X.shape[0]):
            dm[k] = metric(X[i], X[j])
            k += 1
    return dm

def _prepare_out_argument(out, dtype, expected_shape):
    if out is None:
        return np.empty(expected_shape, dtype=dtype)

    if out.shape != expected_shape:
        raise ValueError("Output array has incorrect shape.")
    if not out.flags.c_contiguous:
        raise ValueError("Output array must be C-contiguous.")
    if out.dtype != np.double:
        raise ValueError("Output array must be double type.")
    return out

def is_valid_dm(D, tol=0.0, throw=False, name="D", warning=False):
    """
    Return True if input array is a valid distance matrix.
    Distance matrices must be 2-dimensional numpy arrays.
    They must have a zero-diagonal, and they must be symmetric.
    Parameters
    ----------
    D : array_like
        The candidate object to test for validity.
    tol : float, optional
        The distance matrix should be symmetric. `tol` is the maximum
        difference between entries ``ij`` and ``ji`` for the distance
        metric to be considered symmetric.
    throw : bool, optional
        An exception is thrown if the distance matrix passed is not valid.
    name : str, optional
        The name of the variable to checked. This is useful if
        throw is set to True so the offending variable can be identified
        in the exception message when an exception is thrown.
    warning : bool, optional
        Instead of throwing an exception, a warning message is
        raised.
    Returns
    -------
    valid : bool
        True if the variable `D` passed is a valid distance matrix.
    Notes
    -----
    Small numerical differences in `D` and `D.T` and non-zeroness of
    the diagonal are ignored if they are within the tolerance specified
    by `tol`.
    """
    D = np.asarray(D, order='c')
    valid = True
    try:
        s = D.shape
        if len(D.shape) != 2:
            if name:
                raise ValueError(('Distance matrix \'%s\' must have shape=2 '
                                  '(i.e. be two-dimensional).') % name)
            else:
                raise ValueError('Distance matrix must have shape=2 (i.e. '
                                 'be two-dimensional).')
        if tol == 0.0:
            if not (D == D.T).all():
                if name:
                    raise ValueError(('Distance matrix \'%s\' must be '
                                     'symmetric.') % name)
                else:
                    raise ValueError('Distance matrix must be symmetric.')
            if not (D[range(0, s[0]), range(0, s[0])] == 0).all():
                if name:
                    raise ValueError(('Distance matrix \'%s\' diagonal must '
                                      'be zero.') % name)
                else:
                    raise ValueError('Distance matrix diagonal must be zero.')
        else:
            if not (D - D.T <= tol).all():
                if name:
                    raise ValueError(('Distance matrix \'%s\' must be '
                                      'symmetric within tolerance %5.5f.')
                                     % (name, tol))
                else:
                    raise ValueError('Distance matrix must be symmetric within'
                                     ' tolerance %5.5f.' % tol)
            if not (D[range(0, s[0]), range(0, s[0])] <= tol).all():
                if name:
                    raise ValueError(('Distance matrix \'%s\' diagonal must be'
                                      ' close to zero within tolerance %5.5f.')
                                     % (name, tol))
                else:
                    raise ValueError(('Distance matrix \'%s\' diagonal must be'
                                      ' close to zero within tolerance %5.5f.')
                                     % tol)
    except Exception as e:
        if throw:
            raise
        if warning:
            raise
        valid = False
    return valid



def squareform(dist_condensed:np.array,N:int):
    """
    Returns a squareform matrix from a given pairdistance array
    """
    a,b = np.triu_indices(N,k=1)
    dist_matrix = np.zeros((N,N))
    for i in range(len(dist_condensed)):
        dist_matrix[a[i],b[i]] = dist_condensed[i]
        dist_matrix[b[i],a[i]] = dist_condensed[i]
    return dist_matrix


