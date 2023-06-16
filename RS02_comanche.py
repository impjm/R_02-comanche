import pandas as pd # manipulate data
import numpy as np  # call func
import datetime # handle datetime
import  streamlit as st # DB
import warnings # ignore warning
warnings.filterwarnings("ignore")

# layout
st.set_page_config(
    page_title="RS02",
    layout = 'wide',
)
st.title("RS_02 Reservation Made Today by Date")

# Upload
uploaded_files = st.file_uploader("Choose a CSV file", type='CSV', accept_multiple_files=True)
if uploaded_files:
    all= []
    for uploaded_file in uploaded_files:
        try:
            for uploaded_file in uploaded_files:
                df= pd.read_csv(uploaded_file, skiprows=[0, 1, 2,3], encoding='latin-1') # skip rows , and encoding latin (have latin name) 
                if not df.empty:
                    all.append(df)
        except Exception as e:
            pass
    if all:
        all = pd.concat(all)

        def perform(R02):
            # rename
            R02= R02.rename(columns={'Book\r\nStatus': 'Book Status','Rm\r\nType':'Room Type'
                                     ,'#Of\r\nRms':'OfRms','Pax\r\nAd/Ch':'Pax Ad/Ch','Company/Agent\r\nAgent':'Company/Agent'
                                     ,'All Revenue\r\n':'All Revenue','BK\r\nSour.':'BK Sour.'})
            R02['Date'] = R02['Unnamed: 1'].str.split(': ').str[1]
            R02['Rate'] = R02['Rate'].str.replace(',', '').astype(float)
            R02_1 = R02.drop(['Unnamed: 1','Unnamed: 3','Time'], axis=1)
            R02_1 = R02_1.rename(columns={'Unnamed: 18':'Time'})
            R02_1['Date'] = R02_1['Date'].ffill()
            R02_1['RSVN#'] = R02_1['RSVN#'].fillna(method='backfill')
            R02_2 = R02_1.dropna(axis=0)
            R02_2 = R02_2.groupby(['Date','RSVN#'])
            R02_2 = R02_2.first()
            R02_2 = R02_2.reset_index()
            R02_2[['adult', 'children']] = R02_2['Pax Ad/Ch'].str.split('/', expand=True)
            R02_2 = R02_2.drop('Pax Ad/Ch', axis=1)
            R02_2['adult'] = pd.to_numeric(R02_2['adult'], errors='coerce')
            R02_2 = R02_2.dropna()
            R02_3 = R02_2.groupby(['Date','RSVN#'])
            R02_3 = R02_3.first()
            R02_31 = R02_3.reset_index()
            R02_31["Arrival"] = pd.to_datetime(R02_31["Arrival"],dayfirst=True)
            R02_31["Date"] = pd.to_datetime(R02_31["Date"],dayfirst=True)
            R02_31["Departure"] = pd.to_datetime(R02_31["Departure"],dayfirst=True)
            R02_31["Length of stay"] = (R02_31["Departure"] - R02_31["Arrival"]).dt.days
            R02_31["Lead time"] = (R02_31["Arrival"] - R02_31["Date"]).dt.days
            R02_31['Stay'] = R02_31.apply(lambda row: pd.date_range(row['Arrival'], row['Departure']), axis=1)
            R02_31 = R02_31.explode('Stay').reset_index(drop=True)
            return R02_31
    # pivot data
    R02_31 = perform(all)
    R02_ADR = R02_31.pivot_table(index='Stay', columns=['Company/Agent','Room Type','Rate code'], values=['Rate'])
    R02_LOS = R02_31.pivot_table(index='Stay', columns=['Company/Agent','Room Type','Rate code'], values=['Length of stay'])
    R02_Leadtime = R02_31.pivot_table(index='Stay', columns=['Company/Agent','Room Type','Rate code'], values=['Lead time'])
    RS02_ADR= R02_ADR.stack(level=['Company/Agent','Room Type'])
    RS02_LOS= R02_LOS.stack(level=['Company/Agent','Room Type'])
    RS02_LT= R02_Leadtime.stack(level=['Company/Agent','Room Type'])

    # show data
    data_s = st.selectbox('Clike data',['RS02_ADR','RS02_LOS','RS02_Leadtime'])
    if data_s == 'RS02_ADR':
        st.write(RS02_ADR.to_html(), unsafe_allow_html=True)
    elif data_s == 'RS02_LOS':
        st.write(RS02_LOS.to_html(), unsafe_allow_html=True)
    else:
        st.write(RS02_LT.to_html(), unsafe_allow_html=True)

else:
    st.markdown("**No file uploaded.**")
