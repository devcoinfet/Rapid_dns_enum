import requests
import pandas as pd
from bs4 import BeautifulSoup
import json  
import time

extracted_results = []
session = requests.session()


start_tag = """<div style="margin: 0 8px;">Total: <span style="color: #39cfca; ">"""

end_tag = """</span></div>"""


#100 max results per page we want to divide that by total to get pages in pagination

def Table_Parser(HOST):
    url = "https://rapiddns.io:443/subdomain/{}#result".format(HOST)
    print(url)
    cookies = {"__cfduid": "d5d7911ceb5141dc26b00ff0ef311d0391589005874"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://rapiddns.io/subdomain", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    results = session.get(url, headers=headers, cookies=cookies)
    Total_result = results.text.split(start_tag)[1].split(end_tag)[0]
    print(Total_result)

    tables = pd.read_html(results.text) # Returns list of all tables on page
    rapid_dns_table = tables[0] 
    return rapid_dns_table,Total_result


def Table_Parser_Paginated(HOST,page_num):
    
    url = "https://rapiddns.io:443/subdomain/"+HOST+"?page="+page_num+"#result"
    print(url)
    cookies = {"__cfduid": "d5d7911ceb5141dc26b00ff0ef311d0391589005874"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://rapiddns.io/subdomain", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    headers.update({'Referer':'https://rapiddns.io/subdomain/'+HOST+'?page='+page_num})
    results = session.get(url, headers=headers, cookies=cookies,timeout=3)
    tables = pd.read_html(results.text) # Returns list of all tables on page
    rapid_dns_table = tables[0]
    print(rapid_dns_table)
    return rapid_dns_table


def first_round(host):
    #convert the data to a pandas dataframe and covert to json
    rapid_dns_table,Total = Table_Parser(host)
    json_result = rapid_dns_table.to_json(orient='values')
    json_object = json.loads(json_result)
    print("Located "+str(Total)+" Total Results Generating Pge Count")
    for object_json in json_object:
        values = {}
        values['index'] = object_json[0]
        values['Domain'] = object_json[1]
        values['Address'] = object_json[2]
        values['Type'] = object_json[3]
        clean_result = json.dumps(values)
        extracted_results.append(clean_result)
        print(json.dumps(values))
    return int(Total)


def main():

    HOST = 'starbucks.com'

    Total_Count = first_round(HOST)

    #now some math
    pge_values = int(len(extracted_results))
    Page_Count = Total_Count // pge_values
    print(str(Page_Count)+ " Total Pages")
    if Page_Count  and Page_Count < 100:
       for page in range(1,Page_Count):
           time.sleep(5)
           #try to iterate over the pages 1 at a time and place into global list
           try:
              result = Table_Parser_Paginated(HOST,str(page))
              json_result = result.to_json(orient='values')
              json_object = json.loads(json_result)
              for object_json in json_object:
                  values = {}
                  values['index'] = object_json[0]
                  values['Domain'] = object_json[1]
                  values['Address'] = object_json[2]
                  values['Type'] = object_json[3]
                  clean_result = json.dumps(values)
                  extracted_results.append(clean_result)
                  print(json.dumps(values))

   

           except Exception as mudskippah:
              print(mudskippah)
              pass
            
    extracted_results

    with open(HOST+'_subdomains.json', 'w') as outfile:
       for sub_domain in extracted_results:
           outfile.write(sub_domain+"\n")


     
main()

 
