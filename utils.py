import requests


class Skyscanner:

    def __init__(self, base_url, apikey, locale, country, currency, selected_countries):
        self.base_url = base_url
        self.apikey = apikey
        self.locale = locale
        self.country = country
        self.currency = currency
        self.selected_countries = selected_countries
        self.locations = []

    def get_locations(self):
        for country in self.selected_countries:
            url = f"{self.base_url}/autosuggest/v1.0/{self.country}/{self.currency}/{self.locale}"
            params = {"query": country, "apiKey": self.apikey, "includeCountries": "false"}
            r = requests.get(url, params = params)
            for place in r.json()["Places"]:
                self.locations.append(place["PlaceId"])
        return self.locations
