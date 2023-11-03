import requests
import os
from bs4 import BeautifulSoup
import time
import logging
import sys
import re
import codecs
import difflib
from pathlib import Path
import schedule
import time


'''
if len(sys.argv) != 2:
    print("Usage: You are missing an argument")
    print("Hint: You might be missing the link")
    sys.exit(1)


URL_TO_MONITOR = sys.argv[1]
'''

#URL_TO_MONITOR = "https://catalog.etsu.edu/preview_program.php?catoid=51&poid=15795&returnto=2480" #change this to the URL you want to monitor
DELAY_TIME = 15 # seconds

programlink = [] 
pdfPrint ="&print"

textFilePath = r"C:\Users\gradapp\OneDrive - East Tennessee State University\diff.html"

def clean_file_name_from_url(url):

    # Remove illegal characters and replace them with underscores

    cleaned_name = re.sub(r'[\\/:"*?<>|&]', '_', url)


    return cleaned_name

def process_html(string):
    soup = BeautifulSoup(string, 'html.parser')

    # make the html look good
    soup.prettify()

    # remove script tags
    for s in soup.select('script'):
        s.extract()

    # remove meta tags 
    for s in soup.select('meta'):
        s.extract()
    
    # convert to a string, remove '\r', and return
    return str(soup).replace('\r', '')

def remove_date_content(html):

    soup = BeautifulSoup(html, 'html.parser')

    date_elements = soup.find_all('span', class_='date')

    for date_element in date_elements:

        date_element.string = "[DATE]"  # Replace the date content with a placeholder

    return str(soup)

def webpage_was_changed(URL_TO_MONITOR): 
    """Returns true if the webpage was changed, otherwise false."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                        'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(URL_TO_MONITOR, headers=headers)

    # create the previous_content.txt if it doesn't exist
    fileName = clean_file_name_from_url(URL_TO_MONITOR)

    # create the previous_content.txt if it doesn't exist
    if not os.path.exists(f"{fileName}_prev.txt"):
        open(f"{fileName}_prev.txt", 'w+',encoding="utf-8").close()


        #Opening the previous file and making a copy in html 
    with open(f"{fileName}_prev.txt", 'r',encoding="utf-8") as file:
        previous_response_html = file.read() 
        previous_response_html_dup = previous_response_html
    file.close()

        #Write copy to html file 
    with open(f"{fileName}_prev_dup.html", 'w+',encoding="utf-8") as file:
        file.write(previous_response_html_dup)                   
    file.close()

    #Get live websites html, prettyfying and making a copy
    current_response_html = response.text
    current_response_html = process_html(current_response_html)
    current_response_html = remove_date_content(current_response_html)
    current_response_html_dup = current_response_html

        #check if the previous html.txt is the same
        #if it the same do nothing else follow steps
    if current_response_html == previous_response_html:
        return False
    else:

        #open the previous and write  the current response to it 
        with open(f"{fileName}_prev.txt",'w',encoding="utf-8") as f:
            f.write(current_response_html)

          

            #open a new html file and write to it
        with open(f"{fileName}_curr_dup.html", 'w+',encoding="utf-8") as f:
            f.write(current_response_html_dup)
            f.close()
            
            #processing the htmls into to be used in the difflib function
        first_file_lines = Path(f"{fileName}_prev_dup.html").read_text(encoding="utf-8").splitlines()
        second_file_lines = Path(f"{fileName}_curr_dup.html").read_text(encoding="utf-8").splitlines()
        html_diff = difflib.HtmlDiff().make_file(first_file_lines, second_file_lines)
           # html_diff = difflib.Differ().compare(previous_response_html,current_response_html)
        try:

            with open( rf"C:\Users\gradapp\OneDrive - East Tennessee State University\Catalog Differences_1\{fileName}.html", 'w',encoding="utf-8") as fh:
                fh.write(html_diff)
            return True
        except:
            with open( rf"C:\Users\gradapp\OneDrive - East Tennessee State University\Catalog Differences_1\{fileName}.html", 'w') as fh:
                fh.write(html_diff)
            return True

   
    


def CheckCatalogUpdate():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    log.info("Running Website Monitor")
    pattern = r'"(.*?)"'
    domain = "https://catalog.etsu.edu/"
    url ="https://catalog.etsu.edu/content.php?catoid=51&navoid=2480"

    index = 0
    webpage = requests.get(url)

    soup = BeautifulSoup(webpage.content, 'html.parser')

    page = soup.find('table', {'class': 'toplevel table_default'})
    #main = page.find('tr', {'role': 'main'})
    #blockContent = main.find('td', {'class': 'block_n2_and_content'})
    links = page.find_all('a')
    for item in links:
        if('preview_program' in item.get('href', [])):
            strLink = str(item)
            links = re.findall(pattern, strLink)
            for i in range(len(links)):
                newlink = domain + links[i]
                newlink = newlink.replace("amp;", "")
                printLink = newlink + pdfPrint
                programlink.append(printLink)
              #  print(programlink)
              
   
#    while True:
        #try:
    for i in range(len(programlink)):

            #for i in programlink:
        if webpage_was_changed(programlink[i]):
            index = index+1
            log.info("WEBPAGE WAS CHANGED.")
            log.info(f"{programlink[i]} was changed {i}")
                                #send_text_alert(f"URGENT! {URL_TO_MONITOR} WAS CHANGED!")
                                #send_email_alert(f"URGENT! {URL_TO_MONITOR} WAS CHANGED!")
        else:
            log.info(f"Webpage was not changed.{i}" )
        #except:
           # log.info("Error checking website.")
           # time.sleep(DELAY_TIME)


CheckCatalogUpdate()

#schedule.every().day.at("11:45").do(CheckCatalogUpdate)    #refresh 4 times days after 2hrs(7200 seconds)
        


#while True:
 #   schedule.run_pending()
  #  time.sleep(1)