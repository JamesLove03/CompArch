from collections import deque


class RepPolicy:

    def __init__(self, input, size, sets):

        if input == 0:
            self.policy = 0 #LRU
        elif input == 1:
            self.policy = 1 #FIFO
        else:
            print(f"Invalid Replacement Policy: {input}")
        
        self.size = size 

        self.cache = [deque() for _ in range(sets)]
        
        
    def invalidate(self, tag, index):
        cache_set = self.cache[index]
        for i, (block, valid) in enumerate(cache_set):
            if block == tag and valid:
                cache_set[i] = (block, False)


    def update(self, new, index, exists): #update the tracker and returns the block to be written to
        output = None                               # if the item exists and we are just updating exists = 1 
        cache_set = self.cache[index]               #else if we are adding a new item we pass the way

        if not exists:
            for i, (block, valid, way_idx) in enumerate(cache_set):
                if not valid:
                    cache_set[i] = (new, True, i)
                    return i
            
        if self.policy == 0: #LRU Logic

            for i, (block, valid, way_idx) in enumerate(cache_set):
                if block == new:
                    cache_set.remove((block, valid, way_idx))
                    cache_set.append((new, True, way_idx))
                    return None #return none because we don't need the way_idx in this case
            if len(cache_set) >= self.size:
                output, _ , way_idx= cache_set.popleft()
            else: #adding a block when cache is not full
                for i, item in enumerate(cache_set):
                    if item == None:
                        cache_set.append((new, True, i))

            cache_set.append((new, True, way_idx))
            return way_idx #tell the main code which index to place at / which index to remove
        
        elif self.policy == 1: #FIFO Logic
            if len(cache_set) >= self.size:
                output, _ = cache_set.popleft()  # evict the oldest
            cache_set.append((new, True))    

        return output