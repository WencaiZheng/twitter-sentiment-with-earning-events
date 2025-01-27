import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import requests
import re
import time
import os
from glob import glob
from scipy.stats import norm
from bs4 import BeautifulSoup
from collections import Counter
from bs4 import BeautifulSoup


##############get info from seeking alpha .com#############
head_url_sa ="https://seekingalpha.com/"
# fake a header of a browser
headers = {'User-Agent': 'Chrome/39.0.2171.95'}
###########################################################

def get_earning_news(ticker,key_word):
    the_url = "https://seekingalpha.com/symbol/{0}".format(ticker)
    response = requests.get(the_url, headers=headers)
    # beatifulsoup find all the right tags
    soup = BeautifulSoup(response.text, features='lxml')
    inews=soup.find_all(attrs={"sasource": re.compile("qp_latest")})
    # if key word is in the website address
    key_url= [i.get('href') for i in inews if key_word in i.get('href')]
    return news_result_dict(key_url)


def get_market_news(key_word):
    the_url = "https://seekingalpha.com/market-news"
    # fake a header of a browser
    headers = {'User-Agent': 'Chrome/39.0.2171.95'}
    response = requests.get(the_url, headers=headers)
    # beatifulsoup find all the right tags
    soup = BeautifulSoup(response.text, features='lxml')
    inews = soup.find_all(href=re.compile("news.*"+key_word))
    # if key word is in the website address
    key_url = [i.get('href') for i in inews]

    return news_result_dict(key_url)



def news_result_dict(key_url):
    
    if len(key_url) == 0:
        print("No headline is currenly containing key word you are searching")
        return 0
    print("There are {0} news result containing key word you are searching.".format(len(key_url)))

    news_dic = {}
    for i in range(len(key_url)):
        iurl = key_url[i]
        # get info inside the website
        response = requests.get(head_url_sa+iurl, headers=headers)
        soup = BeautifulSoup(response.text, features='lxml')
        info = soup.find_all("div",id="bullets_ul")
        time  = soup.find_all("time",itemprop="datePublished")
        # print(eps_info[0].text)
        news_dic[key_url[i]] = [time[0].text,info[0].text]
    return news_dic

def save_earning_names(recent_day,index_code):
    """ get the names that have earning in the incoming week
    """
    target_date = pd.to_datetime(datetime.date.today()+datetime.timedelta(days = recent_day))
    all_df =  pd.DataFrame()
    for i in range(1,30):
        the_url = f'https://seekingalpha.com/earnings/earnings-calendar/{i}'
        response = requests.get(the_url, headers=headers)
        # beatifulsoup find all the right tags
        soup = BeautifulSoup(response.text, features='lxml')
        tic = list(map(lambda x:x.text,soup.find_all('a',class_='sym')))
        date = list(map(lambda x:x.text,soup.find_all('span',class_='release-date')))
        time = list(map(lambda x:x.text,soup.find_all('span',class_='release-time')))
        name = list(map(lambda x:x.text,soup.find_all('span',class_='ticker-name')))
        df = pd.DataFrame([tic,name,date,time]).T
        all_df = pd.concat([all_df,df],axis=0)
        last_date = pd.to_datetime(all_df.iloc[-1,2])
        print(last_date)
        if last_date > target_date:break
    all_df.columns=["Ticker","Name","Date","Time"]
    all_df.Date = pd.to_datetime([i for i in all_df.Date])
    all_df = all_df[all_df.Date <=  target_date]
    all_df.index = all_df.Ticker

    if index_code=="SP5":# S&P 500 company?
        sp_names = pd.read_csv("dictionary\\SP500.csv",index_col=0)
        all_df = all_df.join(sp_names,how ="inner").iloc[:,[1,2,3,7]].sort_values(by="Date")
        
    elif index_code =="RU1": #Russel 1000
        rs_names = pd.read_csv("dictionary\\RU1000.csv",index_col=0)
        all_df = all_df.join(rs_names,how ="inner").iloc[:,:].sort_values(by="Date")
    
    elif index_code =="RU3": #Russel 1000
        rs3000_names = pd.read_csv("dictionary\\RU3000.csv",index_col=0)
        all_df = all_df.join(rs3000_names,how ="inner").iloc[:,:]
        all_df.drop(columns=['Ticker','Company'],inplace=True)

    elif index_code == "CN": #Chinese
        cn_names = pd.read_csv("dictionary\\CN.csv",index_col=0)
        all_df = all_df.join(cn_names,how ="inner").iloc[:,[1,2,3,8]].sort_values(by="Date")
    else:
        pass
    all_df.sort_values(by="Date",inplace=True)

    all_df.to_csv(f'data\\earning_names\\{str(datetime.date.today())}.csv')

    return all_df

def load_earning_names():
    """get the saved earning names
    """
    # files = glob(f'data\\earning_names\\*.csv')
    # enames = pd.read_csv(files[-1],index_col=0)
    sp_names = pd.read_csv("dictionary\\FX.csv",index_col=0)
    # names2=pd.concat([enames,sp_names],join='inner',axis=1,sort=False)
    return sp_names.index

if __name__ == "__main__":


    ticker = "ORCL"
    key_word = "bili" # choose from [eps,revenue],"buy" # choose from ["buy","exit","cut"]

    # key_dict_e = get_market_news(key_word)
    # x= get_earning_news('ORCL','revenue')
    x = get_earning_names(recent_day = 5,index_code = "RU3")# All:None,SP500:SP,RS1000:RS,Chinese:CN
    
    
    pass
    # if key_dict:
    #     i=0
    #     for head,info in key_dict.items():
    #         i+=1
    #         print(f'The headline {i} over {len(key_dict.items())} is:\n',head.split("/")[-1])
    #         print("\nThe information is:\n",info)