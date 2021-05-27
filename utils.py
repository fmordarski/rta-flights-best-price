import requests
from datetime import datetime
import calendar
from itertools import combinations, product
import pandas as pd
import os


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
        self.quotes = self._quote_dict()

    def process(self):
        self.get_locations()
        self.get_combinations()
        self.get_dates()
        self.get_all_quotes()
        return self.quotes

    def _quote_dict(self):
        return {"Origin": [], "Destination": [], "Price": [], "Date": []}

    def get_locations(self):
        url = f"{self.base_url}/autosuggest/v1.0/{self.country}/" + \
              f"{self.currency}/{self.locale}"
        for country in self.selected_countries:
            params = {"query": country, "apiKey": self.apikey,
                      "includeCountries": "false"}
            r = requests.get(url, params=params)
            for place in r.json()["Places"]:
                self.locations.append(place["PlaceId"])

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
            quotes = self.get_quote(pair[0], pair[1], day)
            for quote in quotes:
                self.append_quote(pair[0], pair[1], day, quote)
            quotes = self.get_quote(pair[1], pair[0], day)
            for quote in quotes:
                self.append_quote(pair[1], pair[0], day, quote)

    def append_quote(self, origin, dest, date, quote):
        self.quotes["Origin"].append(origin)
        self.quotes["Destination"].append(dest)
        self.quotes["Price"].append(quote["MinPrice"])
        self.quotes["Date"].append(date)

    def get_quote(self, origin, dest, day):
        url = f"{self.base_url}/browsequotes/v1.0/{self.country}/" + \
              f"{self.currency}/{self.locale}/{origin}/{dest}/{day}/"
        params = {"apiKey": self.apikey}
        r = requests.get(url, params=params)
        return r.json()["Quotes"]


class Utils:

    @staticmethod
    def convert_to_pandas(dict):
        return pd.DataFrame.from_dict(dict)

    @staticmethod
    def save_xlsx(df, path):
        df.to_csv(path, index=False)

    @staticmethod
    def get_output_dir():
        dir = os.path.dirname(__file__)
        return os.path.join(dir, "output")
