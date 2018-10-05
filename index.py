import os

import requests

from models import Response


ENDPOINT = "https://api.yelp.com/v3/businesses/search"
API_KEY = os.getenv("YELPAPIKEY")
MAX_PAGE_LIMIT = 50
AUTH_KEY = {"Authorization": f"Bearer {API_KEY}"}


def miles_to_meters(miles: int) -> int:
    return int(miles / 0.00062137)


MAX_RADIUS = miles_to_meters(10)


def get_pf_index(location: str='', offset: int=0) -> int:
    if not location:
        raise Exception("Forgot to include the location")

    params = dict(
        location=location,
        radius=miles_to_meters(10),
        categories="restaurants",
        limit=50,
        offset=offset,
        sort_by="rating"
    )
    response = requests.get(ENDPOINT, params=params, headers=AUTH_KEY)
    if 200 <= response.status_code <= 299:
        response = Response(**response.json())
        businesses = response.businesses
        for idx, business in enumerate(businesses):
            # Logic bad if multiple P.F. Chang's in area/mispell, need to make
            # match on location information.+
            if business.name == "P.F. Chang's":
                return offset + idx
        else:
            if response.total >= offset + MAX_PAGE_LIMIT:
                return get_pf_index(location, offset + MAX_PAGE_LIMIT)
            else:
                # Outside of total, must be > then what we can return from
                # the api
                return response.total + 1
    else:
        # We hit some error, but I"m not going to handle this properly.
        response.raise_for_status()


if __name__ == "__main__":
    # Returns 414
    print(get_pf_index(location="322 W Farms Mall Farmington, CT"))