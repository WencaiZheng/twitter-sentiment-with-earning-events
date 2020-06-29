import pandas as pd
import numpy as np
import datetime
import warnings
import os 

import processor.load_intraday as load_intraday
import processor.load_api as load_api
import processor.count_down as count_down
import visualization.senti_ploter as senti_ploter
"""
This file get tweets from specific news press accounts from most recent n days
"""


warnings.simplefilter("ignore")
now_time = datetime.datetime.today()
save_path = 'data\\news\\' 


def get_from_news(period):

    request_counter = 0
    api = load_api.api_load()
    names = pd.read_csv('dictionary\\PressName.csv').iloc[:,-1].values
    result = []

    for iname in names:
        last_maxid = None
        time_gap = -1
        
        while time_gap < period:

            request_counter += 1
            time_line = api.user_timeline(iname,max_id=last_maxid,tweet_mode="extended")
            time_gap = (now_time - time_line[-1].created_at).days
            if len(time_line) == 0:
                time_gap = period+1
                continue
            
            last_maxid = time_line[-1].id
            result += [[x.id,x.created_at,x.user.id,x.user.screen_name,x.user.followers_count,x.full_text] for x in time_line]
            
            print(request_counter,iname,time_line[-1].created_at)
            
            # reach limit
            if request_counter >= 179:
                count_down.countdown(16*60)
                request_counter = 0

    result_df = pd.DataFrame(result)
    result_df.columns = ["ID","Created","User_id","User_name","User_flr","Text"]
    # if path not exit, create folders
    if not os.path.exists(save_path):os.makedirs(save_path)
    result_df.to_csv(f'{save_path}\\corona-{str(now_time.date())}.csv')

def analysis_news(kw_list,ticker,filename):

    the_file = pd.read_csv(f'{save_path}{filename}',index_col = 0)
    all_pd = pd.DataFrame()

    for n in range(np.shape(the_file)[1]//2):
        ifile = the_file.iloc[:,n*2:(n+1)*2].dropna()
        press_name = ifile.columns[-1]
        ifile.groupby(ifile.iloc[:,0]).sum()
        ifile.index = pd.to_datetime(ifile.iloc[:,0])
        ifile["datehour"] = list(map(lambda x:f'{x.date()} {x.hour}',ifile.index))
        hourly_data =  ifile.groupby(by="datehour").sum().sort_values('datehour')
        # count news numbers
        count = np.zeros(len(hourly_data))
        for kw in kw_list:
            count += np.array(list(map(lambda x:x.upper().count(kw),hourly_data.loc[:,press_name])))
        count_series = pd.Series(count,index=hourly_data.index.copy())
        count_series.name = press_name
        all_pd = pd.concat([all_pd,count_series],axis=1,join='outer',sort=False)

    all_sentis = all_pd.fillna(0).sum(axis=1)
    all_sentis.index = pd.to_datetime(list(map(lambda x:x+':00:00',all_sentis.index)))
    temp = [i.tz_localize('UTC').tz_convert('US/Eastern') for i in all_sentis.index]
    all_sentis.index = list(map(lambda x:x.replace(tzinfo=None),temp))

    hourly_ohlc = load_intraday.get_hourly_price('SPY')
    senti_ploter.TwitterPlot.plot_news(hourly_ohlc,all_sentis)

if __name__ == "__main__":
    os.chdir(os.getcwd()+'\\')
    #get_news()
    analysis_news(['COVID','CORONA'],'SPY','corona-2020-06-24.csv')
    
