from dataclasses import dataclass, InitVar, field
from typing import List, Optional


@dataclass
class Location:
    address1: str
    address2: str
    address3: str
    city: str
    country: str
    state: str
    zip_code: str
    display_address: Optional[List[str]] = field(default_factory=list)


@dataclass
class Category:
    alias: str
    title: str


@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class Business:
    categories: InitVar[List[Category]]
    phone: str
    distance: float
    id: str
    alias: str
    is_closed: bool
    location: InitVar[Location]
    coordinates: InitVar[List[Coordinate]]
    name: str
    phone: str
    rating: float
    review_count: int
    url: str
    image_url: str
    transactions: List[str]
    display_phone: List[str] = field(default_factory=list)
    price: str = ''

    def __post_init__(self, categories, location, coordinates):
        self.categories = [Category(**c) for c in categories]
        self.coordinates = Coordinate(**coordinates)
        self.location = Location(**location)

@dataclass
class Region:
    center: Coordinate

    def __init__(self, center):
        self.center = Coordinate(**center)


@dataclass
class Response:
    total: int
    businesses: InitVar[List[Business]]
    region: InitVar[Region]

    def __post_init__(self, businesses, region):
        self.businesses = [Business(**b) for b in businesses]
        self.region = Region(**region)
