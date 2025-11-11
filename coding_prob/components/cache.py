import pdb
from .replacement_policy import RepPolicy
from collections import deque
import math
from typing import Union, Dict


class Cache:
    def __init__(self, blocksize, size, assoc, Inclusion, Replacement): 

        self.rep_pol = RepPolicy(Replacement, size)
        
        sets = int(size/(assoc * blocksize))

        self.cache = [deque(maxlen=int(assoc)) for _ in range(sets)]

        for cache_set in self.cache:
            cache_set.extend(["20018f D"] * assoc)

        self.blocksize = blocksize
        self.size = size
        self.assoc = assoc
        self.inclusion = Inclusion
        self.sets = sets



    def update_next(self, cache):
        self.next = cache


    def check_exist(self, tag, index): #checks if an entry exists in the cache: if yes returns addr else None
        #ADD CHECK TO VALID BIT
        cache_set = self.cache[index]

        for entry in cache_set:
            base_tag = entry.split()[0]
            if base_tag.lower() == tag.lower() and "I" not in entry:
                return True
        return False
    
    def cut_addr(self, addr):

        print(self.sets)
        address = int(addr, 16)

        offset_bits = self.blocksize.bit_length() - 1
        index_bits = self.sets.bit_length() - 1
        tag_bits = 32 - (index_bits + offset_bits)

        offset_mask = (1 << offset_bits) - 1
        index_mask = (1 << index_bits) - 1

        offset = address & offset_mask
        index = (address >> offset_bits) & index_mask
        tag = (address >> (offset_bits + index_bits)) & ((1 << tag_bits) - 1)

        return offset, index, hex(tag)[2:]


    
    def read(self, full_addr): 
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        #check_exist
        if self.check_exist(tag, index):
            self.rep_pol.update()

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
        return 0
        #check_exist

        #true
            #update replacement
            #mark Dirty

        





    def print(self):
        for i, cache_set in enumerate(self.cache):
            col_width = 10
            row = "".join(f"{item:<{col_width}}" for item in cache_set)

            print(f"{'Set':<8}{str(i) + ':':<8}{row}")









