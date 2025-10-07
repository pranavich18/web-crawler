from ddgs import DDGS

# Initialize the DDGS object
ddgs = DDGS()

def search_engine(query):
    try:
        results = ddgs.text(query=query, max_results=20)
        urls = [result['href'] for result in results]
        return urls
    except Exception as e:
        print(f"An error occurred while fetching DuckDuckGo results: {e}")
        return []