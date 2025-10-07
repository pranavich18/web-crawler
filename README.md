# 🌐 Multi-threaded BFS Web Crawler

A scalable, thread-safe web crawler that performs **Breadth-First Search (BFS)** crawling on given seed URLs with Redis-backed URL management. It can operate in both **evaluation** and **query** modes, integrating a search API for query-based crawling.

---

## 📁 Project Structure

| File | Description |
|------|--------------|
| **`main.py`** | Entry point of the crawler. Defines command-line arguments and initiates BFS crawling. |
| **`crawler.py`** | Contains core crawler utilities, including the `URLParser` class (derived from `HTMLParser`), `canWeCrawl` for robots.txt checks, `clean_url` for URL normalization, MIME-type checking, and hyperlink extraction. |
| **`search.py`** | Defines the `search_engine` function, which fetches the top N results for a given query using the DuckDuckGo search API via the `ddgs` Python module. |
| **`bfs.py`** | Implements the BFS crawling logic using a **Priority Queue** and multi-threading. URL scores are computed based on logarithmic depth and crawl count per domain. Supports up to 100 BFS depth levels. |
| **`seeds1.txt`, `seeds2.txt`** | Lists of random seed URLs (30 each). The program samples 20 random seeds for each BFS run. |

---

## ⚙️ Installation & Setup

### 1️⃣ Install Dependencies

```bash
pip install ddgs
pip install redis
```

### 2️⃣ Start Redis Server

Run Redis in a separate terminal (example for macOS):

```bash
brew install redis
redis-server
```

---

## 🚀 Usage

Run the crawler from the project directory using one of two modes:

### **1. Evaluation Mode (`--mode e`)**
Crawls from random seed URLs and logs the pages crawled.

```bash
python3 main.py --num_thread 200 --mode e
```

- Produces **two log files**, each for a different seed set.
- Target: Crawl **~5000 pages** per run (or as many as possible).

---

### **2. Query Mode (`--mode q`)**
Fetches top 20 search results for a query and starts BFS crawling from them.

```bash
python3 main.py --num_thread 200 --mode q --query "BigApple"
```

- Uses `search.py` to get top DuckDuckGo results for the given query.
- Runs BFS crawl from those URLs as seeds.

---

## 🧱 Features

- **Multi-threaded crawling** with a configurable thread pool.
- **Redis-backed** URL tracking for race-condition-safe concurrency.
- **Dynamic priority scoring** based on domain depth and crawl count.
- **Robust error handling** — all exceptions are logged to the console.
- **Pluggable search integration** (DuckDuckGo API).

---

## ⚠️ Limitations

1. Some websites may throttle or block connections, leading to **503 errors** after extended runs.
2. The crawler runs indefinitely until interrupted — stop it manually with:
   ```
   Ctrl + C
   ```

---

## 🧰 Example Commands

```bash
# Run evaluation mode with 200 threads
python3 main.py --num_thread 200 --mode e

# Run query mode for "Machine Learning"
python3 main.py --num_thread 150 --mode q --query "Machine Learning"
```

---

## 🧾 Logging

- All exceptions and runtime errors are printed to the **terminal**.
- Log files store URLs successfully crawled.

---

## 📄 License

This project is for educational and research purposes only.  
Unauthorized large-scale web crawling may violate site terms of service.

---

**Author:** Pranav Joshi  
**Language:** Python 3  
**Dependencies:** `redis`, `ddgs`
