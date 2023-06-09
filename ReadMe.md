# Amazon Reviews Scraper.

* this scraper is compiled in a way that avoids connection interruptions.
* this scraper is used to get the following information for lead generation and save it in a .csv file.

## scraped info:

> Country 

> Purchase verified

> Date 

> Free Purchase Reviewer 

> Vice Voice 

> Product Version 

> Reviewer's Name 

> Ratting 

> Title 

> Review


* all the info scraped will be joined in one csv file at the end of the scraping process.

## Inputs:

* pages_to_scrape: the number of pages to scrape.
* record_file: the text file that records the scraping process in case of an uncompleted previous scrape, enter "no" if a new scrape project is wished to be initiated.
* url: the starting page url (must search for the subject and location on a browser first and then take the url and plug it in the scraper to start the program).

## Files Used:

* the .txt tracker file and the .csv files are created in the "outputs" folder.

1. controls.json:

* this file stores the following values which can be changed while the scraper is running:
  a. requests headers: use only the necessary headers like user agent, referer, cookies, referer, etc.
  b. break: if set to true it terminates the makes the crawler function "which is used to send request" enter a while loop of 10 seconds until it's reset to false, this is useful when facing a connection interruption or getting blocked from the server "in this case change the request headers".
  c. nab: time in seconds which the scraper uses to sleep between the requests in case of a request interruption.
  d. empty element: turns to true if the request was successfully made but it doesn't contain the key needed element.
  e. interruption: turns to true if the request is sent but it's unsuccessful.

  > please ensure that the break, empty element & interruption variables are set to it's default values (false) be for running/rerunning the program.


2. tracker file:
   a .txt file records the progress of the scraping process and can be used to build up on uncompleted scraping from a previous time.
3. .csv files:
   a. primary files: individually scraped for each primary stage iteration.
   b. the final output file will be named in the following format (amazon reviews {search_subject}.csv)

> when the scraping process is successfully completed all the primary files will be deleted automatically.
