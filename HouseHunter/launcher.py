import yaml
import time
import sys
import os
import argparse
import shutil

from HouseHunter.core import Core
from HouseHunter.email_client import EmailClient

def parse_args():
    parser = argparse.ArgumentParser(description="""House Hunter: Track ad information and send out emails when a new ads are found""")
    parser.add_argument('--conf', '-c', metavar='File path', help="""The script * must read a configuration file to set mail server settings *. Default config file config.yaml is located in the root directly.""")
    parser.add_argument('--url', '-u', metavar="URL", help="Search URLs to scrape", nargs='+', default=None)
    parser.add_argument('--email','-e', metavar="Email", help="Email recepients", nargs='+',  default=None)
    parser.add_argument('--skipmail', '-s', help="Do not send emails. This is useful for the first time you scrape as the current ads will be indexed and after removing the flag you will only be sent new ads.", action='store_true')
    parser.add_argument('--all', '-a', help="Consider all ads as new, do not load ads.json file", action='store_true')
    parser.add_argument('--ads' , metavar="File path", help="Load specific ads JSON file. Default file will be store in the config folder")
    parser.add_argument('--interval', '-i', metavar='N', type=int, help="Time to wait between each loop", nargs='+',  default=None)
    parser.add_argument('--version', '-V', help="Print House Hunter version", action='store_true')
    args = parser.parse_args()
    return(args)

def main():
    # parse the arguments 
    args = parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))

    with open(os.path.join(dname, "VERSION"), "r") as versionFile:
        version = versionFile.readline()

    if args.version:
        print('Version: {}'.format(version))
        exit(0)
    else:
        print('-------------------------------\nRunnining House Hunter v{}\n-------------------------------'.format(version))

    if args.interval:
        loop = True # We will want to do multiple iterations
    else: 
        loop = False

    while True:
        # Get configuration path
        filepath = config_path(args.conf)
        
        # Get config values
        print(' - Loading configuration file...')
        if filepath:
            # Read from configuration file
            with open(filepath, "r") as config_file:
                email_config, urls_to_scrape = yaml.safe_load_all(config_file)
            print("   - Loaded config file: %s"%filepath)
        else:
            print("   - ERROR: No config file loaded.")
            sys.exit('No config file loaded.')

        # Initialize the HouseHunter and email client
        ads_filepath=None
        if not args.all:
            print(' - Loading ads.json file...')
            ads_filepath = ads_path(args.ads)
            print('   - Ads file: {}'.format(ads_filepath))
        HouseHunter = Core(ads_filepath)
    
        # Overwrite search URLs if specified
        if args.url: 
            print(' - Overwriting URLs with URLs specified from CLI...')
            urls_to_scrape = [{'url':u} for u in args.url]

        # Nice quit if no URLs
        print(' - Verifying that there are URLs to scrape...')
        if not urls_to_scrape:
            print('   - No URLs specified. Add URLs in the config.yaml file or use --url or configure URLs in the config file.')
            sys.exit('No URLs specified. Add URLs in the config.yaml file or use --url or configure URLs in the config file.')

        # Scrape each url given in config file
        print(' - Scraping URLs...')
        for url_dict in urls_to_scrape:
            url = url_dict.get("url")

            print('   - Scraping: {}'.format(url))

            ads, email_title = HouseHunter.scrape_url_for_ads(url)

            if len(ads) == 1:
                print('     - Found 1 new ad:')
            else:
                print('     - Found {} new ads:'.format(len(ads)))

           

            # Print ads summary list
            for ad_id in ads:
                print('       - {} | {}'.format(str(ads[ad_id]['Title']), str(ads[ad_id]['Url'])))

            # Send email
            if not args.skipmail and len(ads):
                email_client = EmailClient(email_config)
                # Overwrite email recepeients if specified
                if args.email: 
                    email_client.receiver=','.join(args.email)
                email_client.mail_ads(ads, email_title)
                print('     - Email sent to {}'.format(email_client.receiver))
            else: 
                print("     - No email sent.")

        if ads_filepath: 
            print(' - Updating ad list...')
            HouseHunter.save_ads()

        if (loop):
            print(' - Waiting {} seconds until next check...'.format(args.interval[0]))
            time.sleep(args.interval[0])
        else:
            sys.exit(0)

def config_path(conf):
    # Handle custom config file
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))
    
    if conf:
        filepath=conf
        if not os.path.exists(filepath):
            print(' - Configuration file at {} does not exist. Creating it using the default template...'.format(filepath))
            shutil.copyfile(os.path.join(dname, "config.yaml"), filepath)
    else:
        # Find the default config file in the install directory
        filepath=os.path.join(dname, "config.yaml")
        if not os.path.exists(filepath):
            filepath=None
    return filepath

def ads_path(ads):
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))

    if ads: 
        filepath=ads
        if not os.path.exists(filepath):
            print('   - Ads JSON file at {} does not exist. Creating a blank version...'.format(filepath))
            shutil.copyfile(os.path.join(dname, "ads.json"), filepath)
    else:
        # Find default ads.json file in PWD directory
        filepath=os.path.join(dname, "ads.json")
        if not os.path.exists(filepath):
            filepath=None
    return filepath

def find_file(env_location, potential_files, default_content="", create=False):
    potential_paths=[]
    existent_file=None
    # build potential_paths of config file
    for env_var in env_location:
        if env_var in os.environ:
            for file_path in potential_files:
                potential_paths.append(os.path.join(os.environ[env_var],file_path))
    # If file exist, add to list
    for p in potential_paths:
        if os.path.isfile(p):
            existent_file=p
            break
    # If no file foud and create=True, init new template config
    if existent_file==None and create:
        os.makedirs(os.path.dirname(potential_paths[0]), exist_ok=True)
        with open(potential_paths[0],'w') as config_file:
            config_file.write(default_content)
        print("Init new file: %s"%(p))
        existent_file=potential_paths[0]

    return(existent_file)
