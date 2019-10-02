import urllib
from bs4 import BeautifulSoup
import re
import time
import math
import pandas as pd

# The following class defines our parser. It will be used to grab data from the beer website
class MyParser():
    def __init__(self):
        return None
        
    def open_main_page(self):
        """ Return the html from the main page"""
        
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        
        req = urllib.request.Request('https://www.beermonthclub.com/brewpub/', data=None, headers=hdr)
        
        response = urllib.request.urlopen(req)
        
        return response.read()
        
    def get_state_links(self):
        """ Return a list of links to each state's page on the main website"""
        
        # List of state links
        state_links = []
        
        # Count of breweries per state
        counts = []
        
        # Iterate through main page state sections and extract links
        soup = BeautifulSoup(self.open_main_page())
        
        for result in soup.findAll("a", class_="underline is-inline"):
            state_links.append(result.get('href'))
            
        for result in soup.findAll("span", class_="count"):
            counts.append(result.text)
        
        return (state_links, counts)
    
    def open_state_link(self, link):
        """Return the html from a state page"""
        
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        
        req = urllib.request.Request(link, data=None, headers=hdr)
        
        response = urllib.request.urlopen(req)
        
        return response.read()
    
    def get_brewery_names(self, link, num):
        """ Get a list of brewery names for a state
            input:
                link - First link for the state brewery page
                num - Total number of breweries in each state
            output:
                list of breweries in a state"""
        
        # State landing page
        html = self.open_state_link(link)
        
        # Total number of pages we need to visit
        num_pages = math.ceil(num / 12)
                
        # Brewery names
        names = []
        
        # Meta data
        status = []
        address = []
        website = []
        
        # State name and number of breweries
        state_name = link.split('/')[-1]
        state = [state_name] * num
        num_breweries = [num] * num
        
        # Landing page
        soup = BeautifulSoup(html)

        for result in soup.findAll("h4", class_="margin-bottom-s"):
            names.append(result.text)
            
            curr_attr = 0

            for meta in result.next_sibling.next_sibling.findAll("span", class_="attr-value"):
                # Type
                if curr_attr == 0:
                    status.append(meta.text.replace(' ', '').replace('\n', ''))
                    curr_attr += 1

                # Phone
                elif curr_attr == 1:
                    curr_attr += 1
                    continue

                # Location
                elif curr_attr == 2:
                    address.append(meta.text.replace('\n', ''))
                    curr_attr += 1

                # Website
                elif curr_attr == 3:
                    website.append(meta.text.replace('\n', ''))
        
        # Iterate through state pages and gather links
        for i in range(1, num_pages):
            html = self.open_state_link(link + '?p=' + str(i + 1))
            soup = BeautifulSoup(html)

            for result in soup.findAll("h4", class_="margin-bottom-s"):
                names.append(result.text)
                
                # Keep track of which attribute we're tracking
                curr_attr = 0
                
                for meta in result.next_sibling.next_sibling.findAll("span", class_="attr-value"):
                    # Type
                    if curr_attr == 0:
                        status.append(meta.text.replace(' ', '').replace('\n', ''))
                        curr_attr += 1
                        
                    # Phone
                    elif curr_attr == 1:
                        curr_attr += 1
                        continue
                        
                    # Location
                    elif curr_attr == 2:
                        address.append(meta.text.replace('\n', ''))
                        curr_attr += 1
                        
                    # Website
                    elif curr_attr == 3:
                        website.append(meta.text.replace('\n', ''))

        # Combine names and other features in a dataframe
        df = pd.DataFrame(zip(names, status, address, website, state, num_breweries), columns=['brewery_name', 'type', 'address', 'website', 'state', 'state_breweries'])
        
        return df
    

    def collect(self):
        """ Main function, collects brewery names by state"""
        
        # Get the list of state pages
        state_pages, nums = self.get_state_links()
        
        df = pd.DataFrame(columns=['brewery_name', 'type', 'address', 'website', 'state', 'state_breweries'])
        
        # Iterate through each state and gather brewery info
        for link, num in zip(state_pages, nums):
            print(link, num)
            
            temp_state_df = self.get_brewery_names(link, int(num))
            
            df = df.append(temp_state_df)
            
        return df

def main():
    parser = MyParser()
    
    # Collect brewery info
    brewery_info = parser.collect()

    # Write to csv
    brewery_info.to_csv('breweries_us.csv', index=False)

    data = pd.read_csv('breweries_us.csv')
    print(data.head())

if __name__ == '__main__':
    main()