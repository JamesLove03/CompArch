import argparse
from components.cache import Cache
from components.replacement_policy import RepPolicy


def run_test(cache, file):

    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            op, addr = line.split()
            if op == "r":
                cache.read(addr)
            elif op == "w":
                cache.write(addr)

    print("===== L1 contents =====")
    cache.print()
    if hasattr(cache, "next"):
        print("===== L2 contents =====")
        cache.next.print()
    
    print_results(cache)


    
def print_results(cache):

    print("===== Simulation results (raw) =====")
    results = {
        "a. number of L1 reads:": cache.read,
        "b. number of L1 read misses:": cache.read_miss,
        "c. number of L1 writes:": cache.write,
        "d. number of L1 write misses:": cache.write_miss,
        "e. L1 miss rate:": cache.miss_rate,
        "f. number of L1 writebacks:": cache.writeback,
    }
    total_traffic = cache.read_miss + cache.write_miss + cache.writeback
    
    if hasattr(cache, "next"): #if L2 exists append these values and update total_traffic
        results.update = {
            "g. number of L2 reads:": cache.next.read,
            "h. number of L2 read misses:": cache.next.read_miss,
            "i. number of L2 writes:": cache.next.write,
            "j. number of L2 write misses:": cache.next.write_miss,
            "k. L2 miss rate:": cache.next.miss_rate,
            "l. number of L2 writebacks:": cache.next.writeback,
            }
        total_traffic = cache.next.read_miss + cache.next.write_miss + cache.next.writeback
    else: #if L2 does not exist append 0s
        results.update = {
            "g. number of L2 reads:": 0,
            "h. number of L2 read misses:": 0,
            "i. number of L2 writes:": 0,
            "j. number of L2 write misses:": 0,
            "k. L2 miss rate:": 0,
            "l. number of L2 writebacks:": 0,
            }

    results.update = {
        "m. total memory traffic:": total_traffic
    }

    for question, value in results.items():
        print(f"{question:<30}{value}")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="cache settings")
    
    parser.add_argument("blocksize", type=int)
    parser.add_argument("L1size", type=int)
    parser.add_argument("L1assoc", type=int)
    parser.add_argument("L2size", type=int)
    parser.add_argument("L2assoc", type=int)
    parser.add_argument("Replacement_Policy", type=int)
    parser.add_argument("Inclusion_Property", type=int)
    parser.add_argument("trace_file", type=str)

    args = parser.parse_args()

    L1cache = Cache(args.blocksize, args.L1size, args.L1assoc,  args.Inclusion_Property, args.Replacement_Policy)

    if args.L2size != 0: 
        L2cache = Cache(args.blocksize, args.L2size, args.L2assoc, args.Inclusion_Property, args.Replacement_Policy)
        L1cache.update_next(L2cache)

    print("===== Simulator configuration =====")
    print(f"{'BLOCKSIZE:':<22}{args.blocksize}")
    print(f"{'L1_SIZE:':<22}{args.L1size}")
    print(f"{'L1_ASSOC:':<22}{args.L1assoc}")
    print(f"{'L2_SIZE:':<22}{args.L2size}")
    print(f"{'L2_ASSOC:':<22}{args.L2assoc}")
    print(f"{'REPLACEMENT POLICY:':<22}{args.Replacement_Policy}")
    print(f"{'INCLUSION PROPERTY:':<22}{args.Inclusion_Property}")
    print(f"{'trace_file:':<22}{args.trace_file}")

    run_test(L1cache, args.trace_file)
    
    