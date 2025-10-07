from bfs import bfs, crawled_count_lock, total_errors_lock, total_size_lock, log_lock
from search import search_engine
import random
import argparse
import os
import glob
import threading


with open("seeds1.txt", "r") as f:
    all_urls_in_1 = [line.strip() for line in f if line.strip()]

# Randomly select 20 URLs for set 1 of seeds
seed_urls1 = random.sample(all_urls_in_1, min(20, len(all_urls_in_1)))

with open("seeds2.txt", "r") as f:
    all_urls_in_2 = [line.strip() for line in f if line.strip()]

# Randomly select 20 URLs for set 2 of seeds
seed_urls2 = random.sample(all_urls_in_2, min(20, len(all_urls_in_2)))

def restricted_int(val):
    ivalue = int(val)
    if ivalue < 1 or ivalue > 500:
        raise argparse.ArgumentTypeError(f"{val} is out of range (1–120)")
    return ivalue

parser = argparse.ArgumentParser(description="Process number of threads and query mode")

# Define parameters
parser.add_argument("--num_thread", type=restricted_int, default=60, help="Number of threads (1-7)")
parser.add_argument("--mode", type = str, default="e", choices = ["q","e"], help="Choose mode: e or q (default: e)")
parser.add_argument("--query", type = str, default="abcd", help="Enter your search query")

args = parser.parse_args()

for file in glob.glob("*log*.txt"):  # match files ending with *log*.txt and delete them to generate fresh logs
    os.remove(file)

if(args.mode == "e"):
    threads = []
    t1 = threading.Thread(target=bfs, args=(seed_urls1, 100, args.num_thread, "crawl_log1.txt"))
    t1.start()
    threads.append(t1)
    t2 = threading.Thread(target=bfs, args=(seed_urls2, 100, args.num_thread,  "crawl_log2.txt"))
    t2.start()
    threads.append(t2)
    for t in threads:
        t.join()
        

elif(args.mode == "q"):
    search_query = args.query
    print(f"Fetching search results for query: {search_query}")
    result = search_engine(search_query)
    bfs(result, 100, args.num_thread, "crawl_log_query.txt")
