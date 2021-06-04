import requests
from datetime import datetime
import calendar
from itertools import combinations, product
import os
import json


class Skyscanner:

    def __init__(self, base_url, apikey, locale, country, currency,
                 selected_countries, months):
        self.base_url = base_url
        self.apikey = apikey
        self.locale = locale
        self.country = country
        self.currency = currency
        self.selected_countries = selected_countries
        self.months = months
        self.days = []
        self.locations = []
        self.mapping = {}
        self.quotes = self._quote_dict()

    def process(self):
        self.get_locations()
        self.get_combinations()
        self.get_dates()
        self.get_all_quotes()
        self.map_locations()
        return self.quotes

    def _quote_dict(self):
        return {"Origin": [], "Destination": [], "Price": [], "Date": [],
                "Carrier": []}

    def get_locations(self):
        url = f"{self.base_url}/autosuggest/v1.0/{self.country}/" + \
              f"{self.currency}/{self.locale}"
        for country in self.selected_countries:
            params = {"query": country, "apiKey": self.apikey,
                      "includeCountries": "false"}
            r = requests.get(url, params=params)
            for place in r.json()["Places"]:
                self.locations.append(place["PlaceId"])
                self.mapping[place["PlaceId"]] = place["PlaceName"]

    def get_combinations(self):
        self.locations_pairs = [comb for comb in combinations(self.locations,
                                                              2)]

    def get_dates(self):
        year = datetime.now().year
        for month in self.months:
            num_days = calendar.monthrange(year, month)[1]
            days = [datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").
                    strftime("%Y-%m-%d") for day in range(1, num_days+1)]
            self.days += days

    def get_all_quotes(self):
        for pair, day in product(self.locations_pairs, self.days):
            print(pair, day)
            quotes, carrier = self.get_quote(pair[0], pair[1], day)
            for quote in quotes:
                self.append_quote(pair[0], pair[1], day, quote, carrier)
            quotes, carrier = self.get_quote(pair[1], pair[0], day)
            for quote in quotes:
                self.append_quote(pair[1], pair[0], day, quote, carrier)

    def map_locations(self):
        self.quotes["Origin"] = [self.mapping[place] for place in
                                 self.quotes["Origin"]]
        self.quotes["Destination"] = [self.mapping[place] for place in
                                      self.quotes["Destination"]]

    def append_quote(self, origin, dest, date, quote, carrier):
        self.quotes["Origin"].append(origin)
        self.quotes["Destination"].append(dest)
        self.quotes["Price"].append(quote["MinPrice"])
        self.quotes["Carrier"].append(carrier[0]["Name"] if "Name" in
                                      carrier[0] else "")
        self.quotes["Date"].append(date)

    def get_quote(self, origin, dest, day):
        quote, carrier = "", ""
        url = f"{self.base_url}/browsequotes/v1.0/{self.country}/" + \
              f"{self.currency}/{self.locale}/{origin}/{dest}/{day}/"
        params = {"apiKey": self.apikey}
        r = requests.get(url, params=params)
        if r.json():
            quote = r.json()["Quotes"] if "Quotes" in r.json() else ""
            carrier = r.json()["Carriers"] if "Carriers" in r.json() else ""
        return quote, carrier


class Utils:

    @staticmethod
    def get_output_dir():
        dir = os.path.join(os.path.dirname(__file__), "data")
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    @staticmethod
    def save_json(data, path):
        with open(os.path.join(path, "data.json"), 'w') as f:
            json.dump(data, f)
