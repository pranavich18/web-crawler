import urllib.robotparser
import urllib.parse
from urllib.parse import urlparse, urljoin, urlunparse
from html.parser import HTMLParser
import mimetypes

ALLOWED_MIME_PREFIXES = ["text/html", "application/xhtml+xml"]

def is_valid_mime(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    filename = parsed.path.split("/")[-1]

    # Guess MIME type from extension
    mime_type, encoding = mimetypes.guess_type(filename)

    # No extension → assume possible HTML
    if mime_type is None:
        return True  

    # Accept only HTML-like resources
    return any(mime_type.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES)


# List of file extensions we do not want to crawl (e.g., images, documents, archives, executables)
BLOCKED_EXTENSIONS = {
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv",
    ".exe", ".bin", ".iso"
}

class URLParser(HTMLParser):
    def __init__(self, url):
        super().__init__()
        self.childURL = []
        self.url = url

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    new_url = urljoin(self.url, attr[1])
                    self.childURL.append(new_url)

# Check if the URL can be crawled based on robots.txt and blocked extensions
def canWeCrawl(url):
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "http://" + url  # Default to http if protocol is missing in url
        domain = urljoin(url, '/robots.txt')
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(domain)
        rp.read()
        return rp.can_fetch("please_lemme_crawl", url) and not any(url.endswith(ext) for ext in BLOCKED_EXTENSIONS) and is_valid_mime(url) # # Check robots.txt and Check for blocked extensions
    except Exception as e:
        print(f"Error checking robots.txt for {url}: {e}")
        return False

# Returns list of child URLs (i.e. Hyperlinks in a crawled URL) from the given URL

def crawl (url):
    parser = URLParser(url)
    childURLS = parser.childURL
    return childURLS

# This removes URL fragments and query parameters which avoids crawling multiple sections of the same page multiple times
def clean_url(url: str) -> str:
    # Strip spaces
    url = url.strip()
    
    # Parse the URL
    parsed = urlparse(url)

    # Lowercase scheme + hostname (case-insensitive)
    scheme = parsed.scheme.lower() if parsed.scheme else "http"
    netloc = parsed.netloc.lower()

    # Remove default ports (:80 for http, :443 for https)
    if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
        netloc = netloc.rsplit(":", 1)[0]

    # Keep path but collapse empty → "/"
    path = parsed.path or "/"

    # Don’t drop query or fragment → they differentiate URLs
    # Example: ?page=1 vs ?page=2 should NOT be collapsed
    query = parsed.query
    fragment = ""   # usually ignored in crawling, safe to drop

    return urlunparse((scheme, netloc, path, "", query, fragment))