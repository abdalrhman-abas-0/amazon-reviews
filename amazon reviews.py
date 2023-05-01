# from httpx_html import HTMLSession
import httpx
from bs4 import BeautifulSoup
import time
from time import sleep
import pandas as pd
import numpy as np
import time
from time import sleep
import pandas as pd
import numpy as np
import json
import datetime
from fake_useragent import UserAgent
import os
from tqdm import tqdm
import re

#%%Inputs Cell.

pages_to_scrape = 10
record_file = "tracker OnePlus-Unlocked-Android-Smartphone-Charging at 2023-05-01 22.05.24.txt"
url = "https://www.amazon.com/OnePlus-Unlocked-Android-Smartphone-Charging/product-reviews/B07XWGWPH5/ref=cm_cr_getr_d_paging_btm_4?ie=UTF8&filterByStar=all_stars&pageNumber=1&reviewerType=all_reviews&pageSize=10&sortBy=recent&formatType=all_formats"

#%%main variables


# clears the terminal.
os.system('cls')

# changes the directory to the project folder.
os.chdir('amazon reviews')

# the product to search
search_subject = url.split("/")[3]
    
# the the name of the website being scraped
website = "amazon reviews"

# controls the starting point of the scraping process.
site = url
'''the url that through which the request is made.'''

primary_stage = True
'''if true it enables the run of the primary stage, and it's False when completing a 
previous scraping process where the PRIMARY stage has been completed before.'''

nap = 5
'''time in seconds to sleep between the requests incase of request failure.'''

p_save_index = 0
'''the number of the last saved primary file
(incase of building upon old uncompleted scaping ), it's zero for 
'''

I_P = 0
'''the the index of the last successfully scraped search page "primary stage".'''


#%%txt tracker File

 # if there a record file were given it resets the MAIN variables above to continue upon the previous scraping process,
# and if record file was given as 'no' it leave them to their default values to start a new scraping process. 

if record_file.lower() != 'no':
    txt_tracker = record_file
else:
    date_time = str( f'{datetime.datetime.now()}')[:f'{datetime.datetime.now()}'.index('.')].replace(':','.')
    txt_tracker = f'tracker {search_subject} at {date_time}.txt'
    first_creation = open('./outputs/' + txt_tracker, "w")
    first_creation.close()
    
try:
    with open('./outputs/'+ txt_tracker , 'r') as file:
        file = file.readlines()
        '''an txt file which records the progress of the scraping process'''
        for line in file:
            
            if 'primary.csv' in line:
                # as every pages saved in it's own csv file the save index and 
                # the I_P which is the last page scraped successfully are the same
                p_save_index = I_P = int(re.search(f'(?! {search_subject} )\d+',line)[0])

            elif 'PRIMARY' in line:
                primary_stage = False 

    # the next page url replaces\adds the page number to the url 
    site = re.sub(r"&pageNumber=\d+&",f"&pageNumber={I_P+1}&",url)
    
except:
    pass

#%%crawler Function

def crawler(user_agent, site, element_path,previous_page):
    """ a request maker
    this function enables the program to keep making requests over a given period 
    "nap" until the request is successful and the given element 
    "element_path" is found if the function took so long and the request was failing 
    consistently take a look at the 
    "controls.json" file you may find: 
    ["interruption"] variable: 
        true which means that the connect is interrupted or the given element_path was not found.
    ["break"] variable: 
        false which you can set it to true which allow the program to go in a 
        loop where it sleeps 10 for every iteration then check the connection 
        or change the headers and set it back to false to make the request again.
    
    Args:
        user_agent(str): the user agent to send in the headers of the request.
        site(str): the url of the webpage needed to be scraped.
        element_to_find(str): the path "xpath/css" to locate the "element_to_find". 
        previous_page (str): the previously scrape page url
            to send it under the "referrer" in the request header.
            
    Returns:
        element_to_find(object): the element to look for after the request is made,
            if the element is not found the request is remade until it's found.
        soup(httpx_html.HTML): the response of the request made.

    """
    breaker = False
    
    while breaker == False:

        try:
            # getting the request headers for the controls.json
            with open('controls.json') as j_file:
                content = json.load(j_file)
                
            breaker = content['break']
            nap = content['nap']
                
            header = content['headers'] 
            header['User-Agent'] = user_agent
            
            if previous_page != None:# not always need for each site
                header["referrer"] = previous_page

            session = httpx.Client()
            session.headers = header
            webpage = session.get(site, headers= header)
            soup = BeautifulSoup(webpage.text,"html.parser")
            
            # looking for the given element_path through xpath and css
            try:   
                element_to_find = soup.select(element_path)
            except:
                element_to_find = soup.find_all(element_path)
            
            if len(element_to_find) == 0 or element_to_find == None:   
                content["empty element"] = True    
                with open('controls.json', 'w') as j_file:  
                    json.dump(content, j_file)
            else:
                break

        except:
            with open('controls.json') as j_file:
                content = json.load(j_file)
                
            if  content["interruption"] == False:
                content["interruption"] = True    
                with open('controls.json', 'w') as j_file:  
                    json.dump(content, j_file)
                
            user_agent = UserAgent().random
            sleep(nap)
            
            while breaker == True:
                with open('controls.json') as j_file:
                    content = json.load(j_file)
                breaker = content['break']
                sleep(10)

    content["interruption"] = False 
    with open('controls.json', 'w') as j_file:  
        json.dump(content, j_file)
            
    return element_to_find, soup


#%%Data Frame Builder Function

def df_builder(stage, search_subject):
    """ primary_df/secondary_df Builder
    it looks for a saved PRIMARY/SECONDARY csv file in the "record_file"
    given in the inputs to continue from it, and if it didn't find it
    it concatenates the individually saved primary/secondary csv files
    to one df and save it as PRIMARY/SECONDARY csv file depending 
    on the stage given primary/secondary.
    

    Args:
        stage (str): the last stage of the scraping process primary/secondary.
        search_subject (str): the subject of the search, used to 
            find the PRIMARY/SECONDARY file.
        search_location (str): the location of the search, used to 
            find the PRIMARY/SECONDARY file.

    Returns:
        df_ (pandas.DataFrame): primary_df/secondary_df which will be used 
            to continue the scraping process.

    """
    try:#checking if there was SECONDARY file already saved
        with open('./outputs/' + txt_tracker,'r') as file:
            contents = file.read()
        P_csv_file = re.search(f'{website} {search_subject}.csv',contents)[0].replace('_', ' ')
        df_ = pd.read_csv('./outputs/' + P_csv_file) 
            
    except:
        
        with open('./outputs/' + txt_tracker,'r') as file:
            
            # first_df_built checks if the DataFrame of the first csv file is built or not
            first_df_built = False
            for line in file:
                
                if '.csv' in line and first_df_built == False:
                    df_0 = pd.read_csv('./outputs/' + str(line).strip('\n'))
                    first_df_built = True
                
                elif '.csv' in line and first_df_built == True: #and ' 0 secondary' not in line
                    try:    
                        df_ = pd.concat([df_0, pd.read_csv('./outputs/' + str(line).strip('\n'))], axis=0, ignore_index= True)    
                        df_0 = df_
                    except:
                        df_ = df_0     
                        
        df_ = df_.drop_duplicates()
        df_.to_csv('./outputs/' + f'{website} {search_subject}.csv', index= False)

        with open('./outputs/' + txt_tracker,'a') as file:         
            file.write('\n')
            file.write (f'{website} {search_subject}.csv') 
            
    return df_

#%%Setting Up The Session

# setting up the session and the user agent and converting the pages_to_scrape to a list

ua = UserAgent().random    
pages_to_scrape = list(range(1,pages_to_scrape + 1))

#%%Primary Scraper variables 

previous_page = url

result_list =[]
"""contains the scraped info from the primary stage."""

results_scraped = 0
"""counts the scraped pages."""

previous_page = url
"""the url set as referer in the next page request headers."""

#%%Primary Scraper Cell

# this part "primary stage" scrapes each page and saves its outputs in csv file.
# it scrapes the profiles names and the business names.
if len(pages_to_scrape) > I_P:    
    
    for Page in tqdm(pages_to_scrape[I_P:] ,unit= "page", ncols = 110, colour= '#0A9092'):
        
        # css path of the container element
        path = 'div#cm_cr-review_list.a-section.a-spacing-none.review-views.celwidget div.a-section.review.aok-relative'
        
        container, soup = crawler(ua, site, path, previous_page)
        
        """the parsing code"""    
        
        # iterates through the results
        for R in container:
            
            verification = country= date= free_purchase_reviewer= vice_voice= product_version= reviewer_name= ratting= title= review = "not available"
            # free purchase reviewer badge
            try:
                free_purchase_reviewer = R.select('span.a-color-success.a-text-bold')[0]
            except:
                pass
            
            # purchase
            try:
                verification = R.select('span[data-hook="avp-badge"]')[0].text
            except:
                pass
            
            # vice voice badge
            try:
                vice_voice = R.select("span.a-size-mini.a-color-link.c7yBadgeAUI.c7yTopDownDashedStrike.c7y-badge-text.a-text-bold")[0].text
            except:
                pass
            
            # product version
            try:
                product_version = R.select('a[data-hook="format-strip"]')[0].text
            except:
                pass

            # reviewer_name
            try:
                reviewer_name = R.select('span.a-profile-name')[0].text
            except:
                pass

            # ratting 
            try:
                ratting = R.select('i[data-hook="review-star-rating"]')[0].text
            except:
                pass

            # review title
            try:
                title = R.select('a[data-hook="review-title"]')[0].text
            except:
                pass

            # date and country of the reviewer
            try: 
                date_country = R.select('span[data-hook="review-date"]')
                
                # date
                try:
                    date = re.search(r"(?<=on\s).+",date_country[0].text)[0]
                except:
                    pass

                # country
                try:
                    c = date_country[0].text
                    country = c[len("Reviewed in the "):c.index(" on ")]
                except:
                    pass
                
            except:
                pass
            
            # review
            try:    
                review = R.select('span.review-text-content')[0].text
            except:
                pass
            
            # contains the scraped individual results
            result = {
                "Country":country, 
                "Purchase verified": verification,
                "Date":date, 
                "Free Purchase Reviewer":free_purchase_reviewer, 
                "Vice Voice":vice_voice, 
                "Product Version":product_version, 
                "Reviewer's Name":reviewer_name, 
                "Ratting":ratting, 
                "Title":title, 
                "Review":review
                }            
            
            
            # replaces empty strings with "Not listed"
            for key, value in result.items():
                if value == '':
                    result[key] = "Not Listed"
                
            result_list.append(result)
        
        results_scraped += len(result_list)
        
        p_save_index  += 1
          
        p_df = pd.DataFrame(result_list)
        p_df.to_csv('./outputs/' + f"{website} {search_subject} {p_save_index} primary.csv", index= False)

        try:
            file = open('./outputs/' + txt_tracker ,'a') 
        except:
            file = open('./outputs/' + txt_tracker ,'w')             
        file.write('\n')
        file.write (f"{website} {search_subject} {p_save_index} primary.csv") 
        file.write('\n')
        file.write(F'{site}')   
        file.close() 
        
        result_list = []
        
        I_P = Page
        
        previous_page = site
        
        next_page_button = soup.select("ul.a-pagination li")[-1].attrs['class']
    
        if next_page_button == ['a-last']:
            # constructing the next page url
            site = url.replace('&pageNumber=1&',f"&pageNumber={Page+1}&")
            sleep(1)
        else:
            print('no more pages available, all the available reviews scraped successfully!!')
            break
        
    print(f"primary is done, {results_scraped + len(result_list)} results Scraped successfully.")
    
    
else:
    print('primary stage is already completed.')

#%%building the primary DataFrame

# building the PRIMARY DataFrame, inspect it's contents, save it as csv file
# & delete the individually saved primary csv files used in it's construction.
    
primary_df = df_builder('', search_subject)
primary_df.info()

print(primary_df.tail(), '\n')

files = os.listdir('./outputs/')
for file in files:
    if 'primary' in file :
        os.remove('./outputs/' + file)