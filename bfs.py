import threading
import time
import queue
import math
import socket
import random
import urllib.request
from crawler import canWeCrawl , crawl, URLParser, clean_url
import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
VISITED_SET_KEY = "visited_urls"
socket.setdefaulttimeout(3)  # Set a default timeout for all socket operations because sometimes a soket can wait 
                            #for long long times incase of slow and unresponsive sites which establish a successful connection.

crawled_count = 0
total_errors = 0
total_size = 0
crawled_count_lock = threading.Lock()
total_errors_lock = threading.Lock()
total_size_lock = threading.Lock()

log_lock = threading.Lock()
log_file = "log.txt"

def domain_priority_score(url, domain_counts, depth=2):
    # Example: score by natural logarithm of the 
    # number of pages crawled for a particular domain
    domain = urllib.parse.urlparse(url).netloc
    domain_cnt = domain_counts.get(domain, 1)
    return math.log(domain_cnt) + math.log(depth+1)

def log_url_on_visit(url, page_size, access_time, return_code, page_score, depth, logs):
    with log_lock:
        print(f"Logging to {logs}")
        with open(logs, "a") as f:
            f.write(f"{access_time}\t{url}\tPage Size - {page_size} Bytes\tReturn Code -{return_code}\tPage Score - {page_score}\tDepth - {depth}\n")

def log_stats(crawled_count, num_of_errors, total_size, logs, access_time):
    with log_lock:
        with crawled_count_lock, total_errors_lock, total_size_lock:
            print(f"Logging to {logs}")
            with open(logs, "a") as f:
                f.write(f"At time - {access_time}\tTotal pages crawled approx.- {crawled_count}\tTotal Bytes of Data approx.- {total_size} Bytes\tTotal Errors faced for pages approx.-{num_of_errors}\n")

def worker(pq, max_depth, domain_counts, logs):
    global crawled_count, total_errors, total_size

    while True:
        try:
            score, level, url = pq.get(timeout=1)
        except queue.Empty:
            break

        try:
            if level > max_depth:
                continue

            url = clean_url(url)
            domain = urllib.parse.urlparse(url).netloc

            # Redis atomic check-and-add
            # SADD returns 1 if the url was newly added, 0 if it already existed
            added = redis_client.sadd(VISITED_SET_KEY, url)
            if added == 0:
                print(f"Skipping already visited: {url}", flush=True)
                continue

            if not canWeCrawl(url):
                print(f"Skipping disallowed by robots.txt: {url}", flush=True)
                continue

            print(f"Crawling: {url} at depth {level}", flush=True)

            # Fetch response
            response = urllib.request.urlopen(url, timeout=2)
            html = response.read().decode("utf-8", errors="ignore")

            page_size = len(html)
            return_code = response.getcode()
            access_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # Log visit
            log_url_on_visit(url, page_size, access_time, return_code, score, level, logs)

            # Update stats safely
            with crawled_count_lock:
                crawled_count += 1
            with total_size_lock:
                total_size += page_size

            # Parse child URLs
            parser = URLParser(url)
            parser.feed(html)
            childURLs = parser.childURL

            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            page_score = domain_priority_score(url, domain_counts, depth=level)

            for link in childURLs[:40]:
                link = clean_url(link)
                if not (link.startswith("http://") or link.startswith("https://")):
                    continue

                # Only enqueue if not already visited (check via Redis)
                if redis_client.sismember(VISITED_SET_KEY, link):
                    continue

                link_priority = domain_priority_score(link, domain_counts, level+1)
                pq.put((link_priority, level+1, link))

            if crawled_count % 20 == 0:
                log_stats(crawled_count, total_errors, total_size, logs, access_time)

            print(f"Crawled {crawled_count} pages so far.", flush=True)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error on {url}: {e.code}", flush=True)
            with total_errors_lock:
                total_errors += 1
        except urllib.error.URLError as e:
            print(f"URL Error on {url}: {e.reason}", flush=True)
            with total_errors_lock:
                total_errors += 1
        except socket.timeout:
            print(f"Timeout Error on {url}", flush=True)
            with total_errors_lock:
                total_errors += 1
        except Exception as e:
            print(f"Error on {url}: {e}", flush=True)
            with total_errors_lock:
                total_errors += 1
        finally:
            pq.task_done()
        


def bfs(seed_urls, max_depth=100, num_threads=50, logs = "crawler_log.txt"):
    print(f"logging to {logs}")
    pq = queue.PriorityQueue()
    domain_counts = {}
    for url in seed_urls:
        pq.put((0, 0, url))
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(pq, max_depth, domain_counts, logs))
        t.start()
        threads.append(t)
    pq.join()  # Wait until all tasks are done
    for t in threads:
        t.join()