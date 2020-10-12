from idealista import IdealistaQuery, IdealistaScraper
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes the web looking for real estate ads.')
    parser.add_argument('--district', type=str, required=True)
    parser.add_argument('--neighbourhood', type=str, required=True)
    parser.add_argument('--maxprice', type=int, required=True)

    args = parser.parse_args()

    query = IdealistaQuery(district=args.district, neighbourhood=args.neighbourhood, max_price=args.maxprice)
    scraper = IdealistaScraper(query)

    scraper.run()
