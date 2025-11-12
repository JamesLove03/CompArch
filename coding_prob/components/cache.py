import pdb
from .replacement_policy import RepPolicy
from collections import deque
import math
from typing import Union, Dict

LOG_FILE = "logs.txt"

class Cache:
    def __init__(self, blocksize, size, assoc, Inclusion, Replacement, name): 

        
        sets = int(size/(assoc * blocksize))

        self.cache = [deque(maxlen=int(assoc)) for _ in range(sets)]

        self.rep_pol = RepPolicy(Replacement, assoc, sets)
        self.blocksize = blocksize
        self.size = size
        self.assoc = assoc
        self.inclusion = Inclusion
        self.sets = sets
        self.name = name

        self.reads = 5
        self.read_miss = 1
        self.writes = 10
        self.write_miss = 12
        self.miss_rate = 4.3
        self.writeback = 9

    def log(self, message):

        with open(LOG_FILE, "a") as file:
            file.write(message + "\n")
        

    def update_next(self, cache):
        self.next = cache


    def check_exist(self, tag, index):  # returns True if a valid block exists
        cache_set = self.cache[index]

        for block, valid in cache_set:
            # Skip invalid blocks
            if valid and block.rstrip(" D").lower() == tag.lower():
                return True
        return False
    

    def cut_addr(self, addr):

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


    def add(self, index, tag, dirty, full_addr=None):
        cache_set = self.cache[index]

        evicted = self.rep_pol.update(tag, index)
        
        self.log(f"{self.name} update replacement")
        
        if evicted is None:
            self.log(f"{self.name} victim: tag {evicted}, index {index}")
        else:
            found = None
            self.log(f"{self.name} victim: tag {evicted}, index {index}")
            for i, (block, valid) in enumerate(cache_set): #find the block that needs to be removed

                if block.rstrip(" D") == evicted: #removed block is dirty
                    found = block, valid
                    if full_addr:
                        _, old_idx, old_tag = self.prev.cut_addr(full_addr) #get the address stuff from 
                    if self.name == "L2" and self.inclusion == 1 and full_addr and self.prev.check_exist(old_tag, old_idx): #checks if we need to invalidate a previous block
                        self.prev.rep_pol.invalidate(old_idx, old_tag)

                    if block.endswith(" D") and hasattr(self, "next"): #if the block is dirty
                        self.next.add(index, evicted, 1)

            if found:
                cache_set.remove(found)
        output = (tag + (" D" if dirty else ""), True)
        self.log(f"Added the following to cache: {output} index {index}")
        cache_set.append(output)


    
    def read(self, full_addr): #returns true on a hit and false on a miss
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        
        block_addr = int(full_addr, 16) - offset

        self.log(f"{self.name} read : {hex(block_addr)} (tag {tag}, index {index})")
        #check_exist
        if self.check_exist(tag, index): #hit
            
            self.log(f"{self.name} hit")

            if self.rep_pol.policy == 0: #if LRU update #if FIFO dont update
                self.rep_pol.update(tag, index)
                self.log("Update LRU")

        else: #miss
            self.log(f"{self.name} miss")

            if hasattr(self, "next"): #send to next cache

                outcome = self.next.read(full_addr)
                #write the block
                self.add(index, tag, 0)
                #if false also write to L2

            else: #full miss
                return False
            


    def write(self, full_addr):
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        self.log(f"{self.name} write : {full_addr} (tag {tag}, index {index})")

        #check_exist
        if self.check_exist(tag, index): # hit
            
            self.log(f"{self.name} hit")

            cache_set = self.cache[index]
            for i, (block, valid) in enumerate(cache_set):
                if valid and block.rstrip(" D") == tag:
                    if not block.endswith(" D"):
                        cache_set[i] = (block + " D", True)
                break
            
            if self.rep_pol.policy == 0:
                self.rep_pol.update(tag, index)

        else:
            self.log(f"{self.name} miss")
            if hasattr(self, "next"): # send to L2
                self.next.write(full_addr)
            
            self.add(index, tag, 1)
            return False
        





    def print(self):
        for i, cache_set in enumerate(self.cache):
            col_width = 10
            row = ""
            for block, valid in cache_set:
                row += f"{block + (' I' if not valid else ''):<{col_width}}"
            
            print(f"{'Set':<8}{str(i) + ':':<8}{row}")









