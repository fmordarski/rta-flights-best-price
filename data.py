from utils import Skyscanner
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--apikey', type=str, help='apikey for Skyscanner')
parser.add_argument('countries', metavar='N', type=str, nargs='+', help="countries for which we collect data")

args = parser.parse_args()

base_url = "https://partners.api.skyscanner.net/apiservices"
locale = "en-EN"
country = "PL"
currency = "PLN"


api = Skyscanner(base_url, args.apikey, locale, country, currency, args.countries)
locations = api.get_locations()
print(locations)