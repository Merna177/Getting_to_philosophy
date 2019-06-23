import sys 
import time
from bs4 import BeautifulSoup,SoupStrainer
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def avoid_overwhelming():
    time.sleep(0.5)


def get_page(URL):

    avoid_overwhelming()
    options = Options()
    options.headless = True 
    browser = webdriver.Firefox(options=options)
    browser.get(URL)
    page =  browser.page_source
    browser.close()
    return page


def is_red(link):
    if "class" in link.attrs and link["class"][0] == "new":
        return True
    return False 

def is_external_link(link):
    if "class" in link.attrs and link["class"][0] == "external":
        return True
    return False  


def remove_between_brackets(page):
    open_brackets = 0
    open_href = 0
    lst = []
    for char in page:
        if open_href == 1:
            if char == '>' and lst[-1] == 'a' and lst[-2] == '/':
                open_href = 0
            lst.append(char)    
            continue

        if char == 'a' and lst[-1] == '<' and open_brackets == 0:
            open_href = 1
            lst.append(char)
            continue    
        if char == '(':
            open_brackets+=1
        elif char == ')':
            open_brackets-=1
        else:
            if open_brackets == 0:
                lst.append(char)        
    
    page = ''.join(lst)
    return page

def get_first_link(page):
    # ignore : 
    # 1.italic 
    # 2.()
    # 3.red links 
    # 4.external links 
    # 5.links to current page
    
    # stop when reaching: 
    # 1.philosophy 
    # 2.page with no links 
    # 3.doesnot exist 
    # 4.loop 


    #remove brackets and italic    

    soup = BeautifulSoup(page,"html.parser")
    
    #get body
    soup = soup.find('div',id="bodyContent")
    #remove italic
    soup.i.decompose()

    #remove boxes
    for box in soup.findAll('div',class_="mbox-text-span"):
        box.decompose()

    for box in soup.findAll('div',class_="thumb tright"):
        box.decompose()

    for box in soup.findAll('table'):
        box.decompose()

    for box in soup.findAll('span'):
        box.decompose()

    #remove notes
    for note in soup.findAll('div',role="note"):
        note.decompose()
    
    for note in soup.findAll('div',id="contentSub"):
        note.decompose()

    #remove table of contents
    for toc in soup.findAll('div',id="toc"):
        toc.decompose()

    #remove brackets
    soup = BeautifulSoup(remove_between_brackets(str(soup)),"html.parser")

    for link in soup.findAll('a',{'href' : True}):
        if is_red(link):
            continue
        if is_external_link(link):
            continue    
        if "title" in link.attrs.keys():  
            return "https://en.wikipedia.org"+link["href"]      


    sys.exit('page has no links')
            

def start(link):
    visited = set()
    for i in range(0,50):

        lst = link.split('/')
        print(link)
        
        if lst[-1] == "Philosophy":
            return
        
        if link in visited:
            sys.exit('LOOP!!')

        visited.add(link)    
        page = get_page(link)
        link = get_first_link(page)


    sys.exit("couldnot reach")

if __name__ == "__main__":

    if len(sys.argv) == 1:
       sys.exit("ERROR : expected a link as a second arguement")
    start(sys.argv[1])