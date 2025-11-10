import pdb
from replacement_policy import RepPolicy

class Cache:
    def __init__(self, blocksize, L1size, L1assoc, L2size, L2assoc, Replacement): 

        rep_pol = RepPolicy(Replacement)

