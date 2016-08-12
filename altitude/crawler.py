import logging
import mimetypes
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class LinkCrawler(HTMLParser):
    """Simple descending link crawler for finding files on domain."""

    def __init__(self):
        super().__init__()
        self.found_items = []
        self.visited_links = []
        self.open_links = []
        self.root = None
        self.current_page = None

    def crawl(self, root_url):
        self.__init__()
        self.root = root_url
        logging.debug("Start crawl from page: %s" % root_url)
        self.open_links.append(root_url)
        while self.open_links:
            logging.debug("%d pages on stack." % len(self.open_links))
            logging.debug("%d items found." % len(self.found_items))
            url = self.open_links.pop(0)
            self.load_and_parse_page(url)

        logging.debug("Finished crawl. Found %d items." % len(self.found_items))
        return self.found_items

    def load_and_parse_page(self, url):
        logging.debug("Parsing page: %s" % url)
        self.current_page = url
        data = load_url(url).decode('utf-8')
        self.reset()
        self.feed(data)
        self.visited_links.append(url)

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            self.parse_anchor(attributes)

    def parse_anchor(self, attributes):
        urls = [x[1] for x in attributes if x[0].lower() == 'href']
        if urls:
            self.parse_url(urls[0])
        return None

    def parse_url(self, url):
        if url.startswith('http'):
            # Absolute link - no work needed
            pass
        elif url.startswith('/'):
            # Relative link from domain root
            parts = urllib.parse.urlparse(self.current_page)
            url = parts.scheme + '://' + parts.netloc + url
        else:
            # Relative link from current page
            url = self.current_page + url

        url_type = guess_type(url)

        should_visit = (
            (url_type == 'text/html') and
            (url not in self.visited_links) and
            (get_domain(url) == get_domain(self.root)) and
            is_child(url, self.root)
        )

        if should_visit:
            logging.debug("Adding page to stack: %s" % url)
            self.open_links.append(url)
        elif url_type and url_type != 'text/html' and \
                url not in self.found_items:
            self.found_items.append(url)


def load_url(url):
    with urllib.request.urlopen(url) as response:
        return response.read()


def get_domain(url):
    return urllib.parse.urlparse(url).netloc.split('.')[-2]


def is_child(url1, url2):
    return get_path(url1).startswith(get_path(url2))


def get_path(url):
    return urllib.parse.urlparse(url).path


def guess_type(url):
    url_type, _ = mimetypes.guess_type(url)
    if url_type is None:
        with urllib.request.urlopen(url) as response:
            if response.getcode() < 400:
                url_type = response.headers.get_content_type()
    return url_type
