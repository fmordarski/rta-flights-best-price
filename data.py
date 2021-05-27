from utils import Skyscanner, Utils
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--apikey', type=str, help='apikey for Skyscanner')
parser.add_argument('--countries', metavar='N', type=str, nargs='+',
                    help="countries for which we collect data")
parser.add_argument('--months', metavar='N', type=int, nargs='+',
                    help="months for which we collect data")

args = parser.parse_args()

base_url = "https://partners.api.skyscanner.net/apiservices"
locale = "en-EN"
country = "PL"
currency = "PLN"
output_folder = Utils.get_output_dir()


api = Skyscanner(base_url, args.apikey, locale, country, currency,
                 args.countries, args.months)
data = api.process()
data = Utils.convert_to_pandas(data)
Utils.save_csv(data, output_folder)
