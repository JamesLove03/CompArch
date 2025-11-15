import pdb
from collections import deque
import math
from typing import Union, Dict

LOG_FILE = "logs.txt"

class Cache:
    def __init__(self, blocksize, size, assoc, Inclusion, Replacement, name): 

        
        sets = int(size/(assoc * blocksize))

        self.cache = [[None] * int(assoc) for _ in range(sets)] #holds (tag, valid (True/False), full_address, number(for tracking the replacement))

        self.blocksize = blocksize
        self.size = size
        self.assoc = assoc
        self.inclusion = Inclusion
        self.sets = sets
        self.name = name
        self.MAX = assoc - 1
        self.replacement = Replacement

        self.reads = 0
        self.read_miss = 0
        self.writes = 0
        self.write_miss = 0
        self.miss_rate = 0
        self.writeback = 0
        self.CPU_miss = 0
        self.CPU_hit = 0
        self.silent_wb = 0

    def log(self, message):

        with open(LOG_FILE, "a") as file:
            file.write(message + "\n")
        

    def update_next(self, cache):
        self.next = cache
    

    def cut_addr(self, addr): # cuts the address into the four components

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


    def find_index_by_tag(self, tag, index): # searches for an item and returns the index in the set it is at
        cache_set = self.cache[index]
        for i, item in enumerate(cache_set):
            if item is None:
                continue
            elif item[1] == False:
                continue
            elif item[0].rstrip(" D") == tag:
                return i
        return None


    def evict(self, index): #This block will find a block to evict or the earliest free block and return the index of that block
        cache_set = self.cache[index]
        output = None
        #search first for free blocks 
        for i, item in enumerate(cache_set):
            if item is None:
                return i

        #then invalid blocks
        for i, item in enumerate(cache_set):
            if item[1] is False:
                return i
            
        #then the last counterblock
        for i, item in enumerate(cache_set):
            if item[3] >= self.MAX:
                output = i

        block = self.cache[index][output]

        if self.name == "L2" and self.inclusion == 1: # Could be looking at removing from L1
            poffset, pindex, ptag = self.prev.cut_addr(block[2]) #cut the addr to L1 standards
            pidx = self.prev.find_index_by_tag(ptag, pindex)
            if pidx is not None and self.prev.cache[pindex][pidx][1] == True: #the item does exist in L1 we need to invalidate it
                self.prev.mark_invalid(ptag, pindex)
                self.log(f"Invalidated a block in L1 {ptag}, {pindex}")
                full_tag = self.prev.cache[pindex][pidx][0]
                if (" D") in full_tag:
                    self.silent_wb += 1

        return output

        
            
    def mark_dirty(self, tag, index): # marks an existing item as dirty
        
        idx = self.find_index_by_tag(tag, index)

        tag, valid, address, number = self.cache[index][idx]
        
        if not tag.endswith(" D"):
            tag += " D"
        
        self.cache[index][idx] = (tag, valid, address, number)


    def mark_invalid(self, tag, index): # marks an existing item as invalid

        idx = self.find_index_by_tag(tag, index)

        tag, valid, address, number = self.cache[index][idx]
        
        
        self.cache[index][idx] = (tag, False, address, number)


    def update_trackers(self, index):
        cache_set = self.cache[index]

        for i, item in enumerate(cache_set):
            if item is None:
                continue
            tag, valid, address, number = item
            cache_set[i] = (tag, valid, address, number + 1)


    def update_specific(self, idx, index):
    
        cache_set = self.cache[index]
        
        tag, valid, addr, number = cache_set[idx]

        if number == 0:
            return
        
        old_num = number

        for i, item in enumerate(cache_set):
            if item is None:
                continue
            tag, valid, addr, number = item

            if i == idx:
                number = 0
            elif number < old_num:
                number += 1

            cache_set[i] = (tag, valid, addr, number)

    
    def add(self, idx, tag, index, dirty, addr): # adds an item to a given idx overwriting the old item. Adds new items as -1 before incrementing all counters
        
        cache_set = self.cache[index]

        cache_set[idx] = (tag, True, addr, -1)

        self.update_trackers(index)

        if dirty:
            self.mark_dirty(tag, index)

    
    def read(self, full_addr, Count = True): #returns true on a hit and false on a miss
        #cut up address
        offset, index, tag = self.cut_addr(full_addr)
        self.reads += 1
        block_addr = int(full_addr, 16) - offset

        self.log(f"{self.name} read : {hex(block_addr)} (tag {tag}, index {index})")
        #check_exist

        idx = self.find_index_by_tag(tag, index)
        
        if idx is not None: #hit
            if Count:
                self.CPU_hit += 1

            self.log(f"{self.name} hit")

            if self.replacement == 0: #if LRU update #if FIFO dont update
                self.update_specific(idx, index)

        else: #miss
            self.log(f"{self.name} miss")
            if Count:
                self.CPU_miss += 1    
            self.read_miss += 1

            evicted_idx = self.evict(index) # find block to evict or none
            
            evicted = self.cache[index][evicted_idx] # gets the item to be evicted

            if evicted is not None and evicted[1] is True:

                if evicted[0].endswith(" D"):
                    self.writeback += 1
                    if hasattr(self, "next"):
                            self.next.write(evicted[2], False)
                
            self.add(evicted_idx, tag, index, 0, full_addr) # in all other cases simply add to the cache (Not Dirty on a Read)
            
            if hasattr(self, "next"): #Call L2 if necessary
                self.next.read(full_addr)                


    def write(self, full_addr, Count = True):

        offset, index, tag = self.cut_addr(full_addr) # cut up address

        block_addr = int(full_addr, 16) - offset

        self.log(f"{self.name} write : {hex(block_addr)} (tag {tag}, index {index})")
        self.writes += 1
        
        #check_exist
        idx = self.find_index_by_tag(tag, index)

        if idx is not None: # hit

            self.log(f"{self.name} hit")
            if Count:
                self.CPU_hit += 1
            
            self.mark_dirty(tag, index) #add the dirty tag to this hit

            if self.replacement == 0: #update if LRU
                self.update_specific(idx, index)

        else:
            self.log(f"{self.name} miss")
            if Count:
                self.CPU_miss += 1
     
            self.write_miss += 1

            evicted_idx = self.evict(index) # find block to be evicted

            evicted = self.cache[index][evicted_idx]

            if evicted is not None and evicted[1] is True: #there is free space simply place the block
            
                if evicted[0].endswith(" D"): #deal with writing back the dirty bit
                    self.writeback += 1
                    
                    if hasattr(self, "next"):
                        self.next.write(evicted[2], False)

            self.add(evicted_idx, tag, index, 1, full_addr)
            
            if hasattr(self, "next"):
                self.next.read(full_addr)


    def print(self):
        for i, cache_set in enumerate(self.cache):
            col_width = 10
            row = ""
            for entry in cache_set:
                block, valid = entry[0], entry[1]
                row += f"{block:<{col_width}}"
            
            print(f"{'Set':<8}{str(i) + ':':<8}{row}")









