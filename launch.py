from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

from scraper import max_words, word_freq, ics_subdomain, url_hash

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)

    print("Total unique pages:", len(url_hash))
    print("Longest page in words:", max_words)
    print("Most Common 50 words:")
    for k,v in word_freq.most_common(50):
        print(f"   {k}: {v}")
    print("Subdomains of ics.uci.edu:")
    for k,v in sorted(ics_subdomain.items(), key=lambda x: (x[0], -x[1]) ):
        print(f"   {k}: {v}")