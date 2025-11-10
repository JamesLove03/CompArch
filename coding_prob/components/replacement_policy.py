from collections import deque


class RepPolicy:

    def __init__(self, input, size):

        if input == 0:
            self.policy = 0 #LRU
        elif input == 1:
            self.policy = 1 #FIFO
        else:
            print(f"Invalid Replacement Policy: {input}")
        
        self.size = size 

        self.cache = deque()
        


    def update(self, new): #update the tracker and returns the block to be written to
        output = None
        if self.policy == 0: #LRU Logic
            if new in self.cache: 
                    self.cache.remove(new)
                    self.cache.append(new)
            else:
                if len(self.cache) >= self.size:
                    output = self.cache.popleft()
        
        elif self.policy == 1: #FIFO Logic
            
            return 0