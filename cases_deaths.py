#!/usr/bin/env python
# coding: utf-8

# In[25]:


from uk_covid19 import Cov19API
import json
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as wdg

get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.dpi'] = 200


# In[26]:


# determines whether json data will be loaded locally (to provide a visual output pre-API call) 
refreshCount = 0


# In[27]:


# loads local json file

with open("areaCompare2.json", "rt") as INFILE:
    savedJSONdata=json.load(INFILE)


# In[28]:


# adds one to refresh count
def refreshCounter():
    global refreshCount
    refreshCount += 1
    return(refreshCount)


# In[29]:


# makes API call for cumulative deaths by UK region
def refreshAPI():
    filters = [
    'areaType=region'
]

    structure = {
    'Date': 'date',
    'Area': 'areaName',
    'Cases' : 'newCasesByPublishDate',
    'Deaths': 'newDeaths28DaysByPublishDate'
}

    global api 
    
    api = Cov19API(filters=filters, structure=structure)

    global areaCompare

    areaCompare = api.get_json()
    return(areaCompare)


# In[30]:


#refreshAPI()


# In[31]:


# formats API data into json
def newJSON():
    
    areaCompare = refreshAPI()
    
    with open("areaCompare2.json", "wt") as OUTF:
        json.dump(areaCompare, OUTF)

    jsonfile = open("areaCompare2.json", "r")
    data = jsonfile.readline()
    
    with open("areaCompare2.json", "rt") as INFILE:
        data=json.load(INFILE)
    
    
    return(data)


# In[32]:


#newJSON()


# In[33]:


# determines what json data to display
def dataSelect():
    x = refreshCounter()
    global jsonDF
    if x == 1:
        jsonDF = savedJSONdata
    else:
        jsonDF = newJSON()


# In[34]:


dataSelect()


# In[35]:


# produces list of dates between 09/2020 and now
def wrangleData(jsonDF):
    global newdates
    global refresh_count
    global datalist
    
    datalist=jsonDF['data']
    dates=[dictionary['Date'] for dictionary in datalist]
    
    dates.sort()
    dates = list(dict.fromkeys(dates))
    
    newdates = []
    
#    for date in dates:
#        if date[0:7] != '2020-08':
#            x = date
#            newdates.append(x)

    for date in dates:
        if int(date[0:4]) == 2020:
            if int(date[5:7]) > 8:
                x = date
                newdates.append(x)
        else:
            x = date
            newdates.append(x)

    return(newdates)


# In[36]:


#wrangleData(jsonDF)


# In[37]:


# puts data into nested dictionary format - {date:[area:deaths, area:deaths..], date:[area:deaths...] etc., 
def datedictionary():
    global newdates
    global datalist
    newdates = wrangleData(jsonDF)
    datedict = {}

    for date in newdates:
        datedict[date] = {}

    for dictionary in datalist:
        for entry in datedict:
            if dictionary['Date'] == entry:
                tempdict = {dictionary['Area']: [dictionary['Cases'], dictionary['Deaths']]}
                datedict[entry].update(tempdict)
    
    return(datedict)
    #return(datedict['2020-10-16']['London'][1])
          
    


# In[38]:


#datedictionary()


# In[39]:


def parse_date(datestring):
    """ Convert a date string into a pandas datetime object """
    return pd.to_datetime(datestring, format="%Y-%m-%d")


# In[40]:


# sets up the empty dataframe with dates as index
def makeDataframe():
    global datedict
    global areaComparedf
    datedict = datedictionary()
    startdate=parse_date(list(datedict)[0])
    enddate=parse_date(list(datedict)[-1])

    index=pd.date_range(startdate, enddate, freq='D')
    areaComparedf = pd.DataFrame(index=index, columns=['South East', 'Yorkshire and The Humber', 'North East',
                                                 'East Midlands', 'London', 'South West',
                                                 'North West', 'West Midlands',
                                                 'East of England'])
    return areaComparedf


# In[41]:


def covidGraphFunc():
    class covidGraph:
# populates dataframe from nested dictionary

        def cases():
            areaComparedf = makeDataframe()
            for entry in datedict:
                date=parse_date(entry)
    #for dicto in datedict:
                for column in ['South East', 'Yorkshire and The Humber', 'North East',
                                                 'East Midlands', 'London', 'South West',
                                                 'North West', 'West Midlands',
                                                 'East of England']:

                    if pd.isna(areaComparedf.loc[date, column]): 
                        try:
                            value= (datedict[entry][column][0]) if (datedict[entry][column][0])!=None else 0.0
                            areaComparedf.loc[date, column]=value
                        except Exception:
                            pass
    
            # fill in any remaining "holes" due to missing dates
            areaComparedf.fillna(0.0, inplace=True)
            
            return(areaComparedf)

        def deaths():
            areaComparedf = makeDataframe()
            for entry in datedict:
                date=parse_date(entry)
    #for dicto in datedict:
                for column in ['South East', 'Yorkshire and The Humber', 'North East',
                                                 'East Midlands', 'London', 'South West',
                                                 'North West', 'West Midlands',
                                                 'East of England']:
                    if pd.isna(areaComparedf.loc[date, column]): 
                        try:
                            value= (datedict[entry][column][1]) if (datedict[entry][column][1])!=None else 0.0
                            areaComparedf.loc[date, column]=value
                        except Exception:
                            pass
    
            # fill in any remaining "holes" due to missing dates
            areaComparedf.fillna(0.0, inplace=True)
            
            return(areaComparedf)
            
    return(covidGraph)
            
        
        


# In[42]:


# plots graph
def plotData():
    global graph
    data = populateDataframe("Cases")
    areaCompare_graph = data.plot()
    graph = (areaCompare_graph)
    return(graph)


# In[43]:


# sets up selection widget implements widget on final graph
def populate(arg):
    x = covidGraphFunc()
    if arg == 'deaths':
        return(x.deaths())
    elif arg == 'cases':
        return(x.cases())

series=wdg.SelectMultiple(
options=['South East', 'Yorkshire and The Humber', 'North East',
                                                 'East Midlands', 'London', 'South West',
                                                 'North West', 'West Midlands',
                                                 'East of England'],
value=['South East', 'Yorkshire and The Humber', 'North East',
                                                 'East Midlands', 'London', 'South West',
                                                 'North West', 'West Midlands',
                                                 'East of England'],
rows=9,
description='Stats:',
disabled=False
)

scale=wdg.RadioButtons(
    options=['linear', 'log'],
    #value='pineapple', # Defaults to 'pineapple'
    #layout={'width': 'max-content'}, # If the items' names are long
    description='Scale:',
    disabled=False
)

dataoptions=wdg.RadioButtons(
options=['Deaths', 'Cases'],
    #value='pineapple', # Defaults to 'pineapple'
    #layout={'width': 'max-content'}, # If the items' names are long
    description='Select data type:',
    disabled=False
)

controls=wdg.VBox([series, scale, dataoptions])

def setControls(gcols, gscale, dataoptions):
    deaths = populate('deaths')
    cases = populate('cases')
    
    global series
    global scale
    #global areacomparedf
    if gscale=='linear':
        logscale=False
    else: 
        logscale=True
   
    if dataoptions == 'Deaths':
        deaths[list(gcols)].plot(logy=logscale)
    elif dataoptions == 'Cases':
        cases[list(gcols)].plot(logy=logscale)
    else:
        pass
    
    
    print("Click to select data for graph")
    print("(CTRL-Click to select more than one category)")
    
    
def finalGraph():
    graph=wdg.interactive_output(setControls, {'gcols': series, 'gscale' : scale, 'dataoptions' : dataoptions})

    #display(controls, graph)
    combined = wdg.HBox([graph, controls])
    display(combined)


# In[44]:


#finalGraph()


# In[45]:


#sets functionality of refresh button, calling API, looping through all steps and adding to refresh counter

def access_api(button):
    refreshAPI()
    dataSelect()
    newJSON()
    wrangleData(jsonDF)
    datedictionary()
    makeDataframe()
    covidGraphFunc()
    #populate()
    ##populateDataframe()
    #covidGraphFunc()
    #finalGraph()
    refreshCounter()
    print("I'm downloading data from the API...")
    print("...all done.")


# In[46]:


# determines style of refresh button
apibutton=wdg.Button(
    description='Refresh data',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click to download current Public Health England data',
    icon='refresh' # (FontAwesome names without the `fa-` prefix)
)

apibutton.on_click(access_api)


# In[47]:


def start():
    finalGraph()
    display(apibutton)


# In[24]:


start()


# In[ ]:





# In[ ]:




