import argparse
from components.cache import Cache
from components.replacement_policy import RepPolicy


def run_test(cache, rep_policy, file):




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

    args = parser.parse_args

    cache = Cache(args.blocksize, args.L1size, args.L1assoc, args.L2size, args.L2assoc, args.Inclusion_Property)
    rep = RepPolicy(args.Replacement_Policy)


    run_test(cache, rep, trace_file)