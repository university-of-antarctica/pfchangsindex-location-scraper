import json

from bs4 import BeautifulSoup
import requests

urls_queue = ["https://www.pfchangs.com/locations/index.html"]


def clean_str(elem):
    # Replacing , since city sometimes includes it.
    return elem.get_text().replace(",", "").strip()


class Address:
    __slots__ = ["street_addrs", "state", "city", "zip"]

    def __init__(self, elem):
        addr_elem = elem.find(class_="c-address-street")
        self.street_addrs = [clean_str(c) for c in addr_elem.children]
        self.state = clean_str(elem.find(class_="c-address-state"))
        self.city = clean_str(elem.find(class_="c-address-city"))
        self.zip = clean_str(elem.find(class_="c-address-postal-code"))

    def __str__(self):
        street_addrs = '\n'.join(self.street_addrs)
        return f"{street_addrs}\n{self.city}, {self.state} {self.zip}"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            'street_addrs': self.street_addrs,
            'state': self.state,
            'city': self.city,
            'zip': self.zip
        }


def valid_url(url):
    """Checks if a url is a valid one to add to our search list.

    Valid in this case is relative to the locations page, or an absolute url
    that is a location path.
    """
    return url[:3] in ("us/", "../", "pr/") or \
        ("www.pfchangs" in url and "locations" in url)


def clean_url(url_to_clean, page_url):
    """Converting relative to absolute urls."""
    if url_to_clean[:4] == "http":
        return url_to_clean
    page_up = 1
    pos = 0
    while True:
        if url_to_clean[pos:pos + 3] == "../":
            page_up += 1
            pos += 3
        else:
            url_to_clean = url_to_clean[pos:]
            break
    page_parts = page_url.rstrip("/").split("/")
    return "/".join(page_parts[:-page_up] + [url_to_clean])


def main():
    visited_urls = set()
    addresses = []
    while urls_queue:
        print(len(urls_queue))
        url = urls_queue.pop()
        visited_urls.add(url)
        response = requests.get(url)
        if 200 <= response.status_code <= 299:
            html = BeautifulSoup(response.text, 'html.parser')
            # If this elem on page, then we know it's a location page.
            # We can stop searching for more urls.
            if html.find(class_="c-location-hours"):
                addresses.append(Address(html.find("address")))
            else:
                urls_on_page = [clean_url(a["href"], url)
                                for a in html.find_all("a")
                                if valid_url(a["href"])]
                urls_to_add = [url for url in set(urls_on_page)
                               if url not in visited_urls]
                urls_queue.extend(urls_to_add)
        else:
            print("Error with url {}".format(url))

    with open("locations.json", "w") as f:
        f.write(json.dumps({'locations': [a.to_dict() for a in addresses]}))



if __name__ == "__main__":
    main()