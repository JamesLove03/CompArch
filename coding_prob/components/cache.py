import pdb
from .replacement_policy import RepPolicy
from collections import deque


class Cache:
    def __init__(self, blocksize, size, assoc, Inclusion, Replacement): 

        self.rep_pol = RepPolicy(Replacement, size)
        
        NUM_SETS = size/(assoc * blocksize)

        self.cache = [deque(maxlen=int(assoc)) for _ in range(int(NUM_SETS))]

        for cache_set in self.cache:
            cache_set.extend(["20018f D"] * assoc)



    def update_next(self, cache):
        self.next = cache


    def check_exist(self, addr): #checks if an entry exists in the cache: if yes returns addr else None
        #ADD CHECK TO VALID BIT
        val = False
        for set_index, cache_set in enumerate(self.cache):
            for pos_index, item in enumerate(cache_set):
                if item == addr:
                    val = True

        return val
    
    def read(self, full_addr): 
        #cut up address

        #check_exist

        #true
            #update replacement

        #False
            #if L2 exists
                #check_exist (L2)
                #true 
                    #update replacement
                #false
                    #if inclusive:
                        #need to place into L2
                        #find replacement block in L2
                        #update replacement_policy for L2
                    
                    #find block to replace (WE ARE PLACING THIS BLOCK IN L1)
                    #replace block 
                    #check if block is dirty (for WB)
                    #update replacement
                    #return


            #find block to replace
            #check if block is dirty (for WB)
            #replace block 
            #update replacement
            #return



    def write(self, full_addr):
        #cut up address
        
        #check_exist

        #true
            #update replacement
            #mark Dirty

        





    def print(self):
        for i, cache_set in enumerate(self.cache):
            col_width = 10
            row = "".join(f"{item:<{col_width}}" for item in cache_set)

            print(f"{'Set':<8}{str(i) + ':':<8}{row}")









