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


    def update(self, new, index): #update the tracker and returns the block to be written to
        output = None
        cache_set = self.cache[index]

        for i, (block, valid) in enumerate(cache_set):
            if not valid:
                cache_set[i] = (new, True)
                return block
        
        if self.policy == 0: #LRU Logic

            for i, (block, valid) in enumerate(cache_set):
                if block == new:
                    cache_set.remove((block, valid))
                    cache_set.append((new, True))
                    return None
            if len(cache_set) >= self.size:
                output, _ = cache_set.popleft()
            cache_set.append((new, True))
        
        elif self.policy == 1: #FIFO Logic
            if len(cache_set) >= self.size:
                output, _ = cache_set.popleft()  # evict the oldest
            cache_set.append((new, True))    

        return output