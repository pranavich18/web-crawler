List of Files and their functionalities

main.py - Entry point file for the crawler. Contains all the argument definitions and the starting point to call the BFS Crawling.
crawler.py - Contains crawler utilities which consists of URLParser class derived from HTMLParser, functions like 'canWeCrawl' to check 
            for robot exclusion protocol, 'clean_url' to clean the input url and free it from '#fragments' normalizing the url, removing empty "/", a mime checking function and a getter
            for all the hyperlinks found in the html of the parent url.

search.py - Contains the search_engine function to fetch the top "max_results" number of results for a given string query. This uses 
            ddgs python module  which works on the DuckDuckGo search api.


bfs.py - This is the crux of the crawler. This implements a BFS on the initial set of seed urls with a Priority queue.
         The num_threads argument governs how many threads are used for the urls in the priority queue. The score for URLs is maintained 
         by the Natural Logarithm of the number of pages crawled multiplied by the Logarithm of the depth for a particular domain.
         This runs for the a depth of 100 levels of BFS.

seeds1.txt, seeds2.txt - 30 random seed urls which is used to randomly filter 20 urls to run BFS on.


How to run

pip install ddgs
pip install redis

Open a separate terminal

Install "redis" for eg: on Mac -> command : brew install redis
run command : redis-server

Now open a separate terminal in the project directory and use the below two modes to run the crawler

2 modes to run

1.  Evaluation Mode (e)- 2 output logs, each listing all pages crawled by
                         your crawler for one run from a different set of
                         seeds. Try to crawl at least 5000 pages for each, 
                         more if you can and less if you cannot.

   command: python3 main.py --num_thread 200 --mode e  

2. Query Mode (q) - 1 output log for a given query which fetched top 20 search results
                    and start with them as the seed urls and then run bfs

    command: python3 main.py --num_thread 200 --mode q --query "BigApple"



Exceptions are handled very well and logged in the terminal rather than the log files.
For checking errors/exceptions explicitly one needs to see the command line output logs.

Limitations:
1. After a certain point of time the crawler might give delayed response because the site marks the connection bad and start sending 503 errors.

2. To stop you need to press Control + C as an interrupt because the timing for running the crawler was not defined in the Problem statement.