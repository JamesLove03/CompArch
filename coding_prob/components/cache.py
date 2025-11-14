import pdb
from .replacement_policy import RepPolicy
from collections import deque
import math
from typing import Union, Dict

LOG_FILE = "logs.txt"

class Cache:
    def __init__(self, blocksize, size, assoc, Inclusion, Replacement, name): 

        
        sets = int(size/(assoc * blocksize))

        self.cache = [[None] * int(assoc) for _ in range(sets)]

        self.rep_pol = RepPolicy(Replacement, assoc, sets)
        self.blocksize = blocksize
        self.size = size
        self.assoc = assoc
        self.inclusion = Inclusion
        self.sets = sets
        self.name = name

        self.reads = 0
        self.read_miss = 0
        self.writes = 0
        self.write_miss = 0
        self.miss_rate = 0
        self.writeback = 0
        self.CPU_miss = 0
        self.CPU_hit = 0

    def log(self, message):

        with open(LOG_FILE, "a") as file:
            file.write(message + "\n")
        

    def update_next(self, cache):
        self.next = cache


    def check_exist(self, tag, index):  # returns True if a valid block exists
        cache_set = self.cache[index]

        for entry in cache_set:
            # Skip invalid blocks
            if entry is None:
                continue
            block, valid = entry[0], entry[1]
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


    def evict(self, index, tag): #This block will find a block to evict or NONE and remove it so there is space in the queue

        evicted = self.rep_pol.update(tag, index, 0)

        self.log(f"{self.name} update replacement")

        return evicted
            
    def mark_dirty(self, tag, index):
        for i, (block, valid, addr) in enumerate(self.cache[index]):
            if block.rstrip(" D") == tag and valid:
                if not block.endswith(" D"):
                    self.cache[index][i] = (f"{block} D", valid, addr)
                    break

    def add(self, index, tag, dirty, full_addr, way):
        cache_set = self.cache[index]
        output = tag

        if dirty:
            output = output + " D"
        
        cache_set[way] = ((output, 1, full_addr))

    
    def read(self, full_addr, Count = True): #returns true on a hit and false on a miss
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        self.reads += 1
        block_addr = int(full_addr, 16) - offset

        self.log(f"{self.name} read : {hex(block_addr)} (tag {tag}, index {index})")
        #check_exist
        if self.check_exist(tag, index): #hit
            if Count:
                self.CPU_hit += 1

            self.log(f"{self.name} hit")

            if self.rep_pol.policy == 0: #if LRU update #if FIFO dont update
                self.rep_pol.update(tag, index, 1)
                self.log("Update LRU")

        else: #miss
            self.log(f"{self.name} miss")
            if Count:
                self.CPU_miss += 1    
            self.read_miss += 1

            #find block to evict or none
            evicted_way = self.evict(index, tag)

            evicted = self.cache[index][evicted_way] #gets the item to be evicted
                            
            if evicted is None: #there is free space simply place the block
                self.add(index, tag, 0, full_addr, evicted_way) # add new block to cache
            else:
                evicted_addr = evicted[2]

                if evicted[0].endswith(" D"): #deal with writing back the dirty bit
                    self.writeback += 1
                    if hasattr(self, "next"):
                        self.next.write(evicted_addr, False)
                
                if self.name == "L2" and self.inclusion == 1: #here we have inclusive and in L2
                    poffset, pindex, ptag = self.prev.cut_addr(evicted_addr) #cut the addr to L1 standards
                    if self.prev.check_exist(ptag, pindex): #the item does exist in L1 we need to invalidate it
                        for i, (block, valid, addr) in enumerate(self.prev.cache[pindex]):
                            if block.rstrip(" D") == ptag and valid:
                                self.prev.cache[pindex][i] = (block, False, addr) #invalidate the block in L1
                
                self.add(index, tag, 0, full_addr, evicted_way)
            
            if hasattr(self, "next"): #read the next cache if it exists
                self.next.read(full_addr)                

            self.rep_pol.update(tag, index, 0)



    def write(self, full_addr, Count = True):
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        block_addr = int(full_addr, 16) - offset

        self.log(f"{self.name} write : {hex(block_addr)} (tag {tag}, index {index})")
        self.writes += 1
        #check_exist
        if self.check_exist(tag, index): # hit
            self.log(f"{self.name} hit")
            if Count:
                self.CPU_hit += 1
            #add the dirty tag to this hit
            self.mark_dirty(tag, index)

            if self.rep_pol.policy == 0:
                self.rep_pol.update(tag, index, 1)
                self.log("Update LRU")

        else:
            self.log(f"{self.name} miss")
            if Count:
                self.CPU_miss    
            self.write_miss += 1

            evicted_way = self.evict(index, tag) # find block to be evicted

            evicted_full = self.cache[index][evicted_way]

            if evicted_full is None: #there is free space simply place the block
                self.add(index, tag, 1, full_addr, evicted_way)
            else: #someone is getting evicted
                evicted_addr = evicted_full[2]
                
                if evicted_full[0].endswith(" D"): #deal with writing back the dirty bit
                    self.writeback += 1
                    if hasattr(self, "next"):
                        self.next.write(evicted_addr, False)

                if self.name == "L2" and self.inclusion == 1: #here we have inclusive and in L2
                    poffset, pindex, ptag = self.prev.cut_addr(evicted_addr) #cut the addr to L1 standards
                    if self.prev.check_exist(ptag, pindex): #the item does exist in L1 we need to invalidate it
                        for i, (block, valid, addr) in enumerate(self.prev.cache[pindex]):
                            if block.rstrip(" D") == ptag and valid:
                                self.prev.cache[pindex][i] = (block, False, addr) #invalidate the block in L1

                self.add(index, tag, 1, full_addr, evicted_way)
            
            if hasattr(self, "next"):
                self.next.read(full_addr)


            self.rep_pol.update(tag, index, 0)


    def print(self):
        for i, cache_set in enumerate(self.cache):
            col_width = 10
            row = ""
            for entry in cache_set:
                block, valid = entry[0], entry[1]
                row += f"{block:<{col_width}}"
            
            print(f"{'Set':<8}{str(i) + ':':<8}{row}")









