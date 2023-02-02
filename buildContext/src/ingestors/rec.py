import pandas as pd
import re
import sqlalchemy as sa
import os
import datetime

# REC Update Tool.csv --> REC_Update_Tool_20221231_135045.csv
# waiting on jon
def ingestion(m):
        # WARNING the provided CSV has many empty rows which are not skipped because they are empty strings
    date_cols = ['Zone']
    df = pd.read_csv(m.fileName, header=[2], skiprows=(3,3), dtype={
        'Zone': str, # Bad CSV header (should be curveStart or Month)
        # 'Zone A': pd.Float64Dtype, # ask guys on precision https://beepscore.com/website/2018/10/12/using-pandas-with-python-decimal.html
# ...
        # 'Zone K': pd.Float64Dtype
    }, parse_dates=date_cols).dropna() # acts as context manager
    df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float

    if m.controlArea == "nyiso":
        df.rename(inplace=True, columns={
            'Zone': 'month',
            'ZONE A': 'zone_a_amount',
            'ZONE B': 'zone_b_amount',
            'ZONE C': 'zone_c_amount',
            'ZONE D': 'zone_d_amount',
            'ZONE E': 'zone_e_amount',
            'ZONE F': 'zone_f_amount',
            'ZONE G': 'zone_g_amount',
            'ZONE H': 'zone_h_amount',
            'ZONE I': 'zone_i_amount',
            'ZONE J': 'zone_j_amount',
            'ZONE K': 'zone_k_amount'
            })
    elif m.controlArea == "miso":
        df.rename(inplace=True, columns={
            'Zone': 'month',
            'AMILCIPS': 'amilcips_amount',
            'AMILCILCO': 'amilcilco_amount',
            'AMILIP': 'amilip_amount',
            'INDY HUB': 'indy_amount'
        })
    elif m.controlArea == "ercot":
        df.rename(inplace=True, columns={
            'Zone': 'month',  
            'NORTH ZONE':'north_amount',
            'HOUSTON ZONE':'houston_amount',
            'SOUTH ZONE':'south_amount',
            'WEST ZONE':'west_amount'
        })
    elif m.controlArea == "pjm":
          df.rename(inplace=True, columns={
            'Zone': 'month',
            'AECO':'aeco_amount',
            'AEP':'aep_amount',
            'APS':'aps_amount', 
            'ATSI':'atsi_amount', 
            'BGE':'bge_amount', 
            'COMED':'comed_amount', 
            'DAY':'day_amount', 
            'DEOK':'deok_amount', 
            'DOM':'dom_amount', 
            'DPL':'dpl_amount', 
            'DUQ':'duq_amount', 
            'JCPL':'jcpl_amount', 
            'METED':'meted_amount', 
            'PECO':'peco_amount', 
            'PENELEC':'penelec_amount', 
            'PEPCO':'pepco_amount', 
            'PPL':'ppl_amount', 
            'PSEG':'pseg_amount', 
            'RECO':'reco_amount', 
            'WEST HUB':'west_amount', 
            'AD HUB':'ad_amount', 
            'NI HUB':'ni_amount', 
            'EAST HUB':'east_amount'
          })
    elif m.controlArea == "isone":
        #Zone,MAINE,NEWHAMPSHIRE,VERMONT,CONNECTICUT,RHODEISLAND,SEMASS,WCMASS,NEMASSBOST,MASS HUB
        df.rename(inplace=True, columns={
            'Zone': 'month',
            'MAINE':'maine_amount',
            'NEWHAMPSHIRE': 'newhampshire_amount',
            'VERMONT':'vermont_amount',
            'CONNECTICUT':'connecticut_amount', 
            'RHODEISLAND':'rhodeisland_amount', 
            'SEMASS':'semass_amount', 
            'WCMASS':'wcmass_amount', 
            'NEMASSBOST':'nemassbost_amount', 
            'MASS HUB':'mass_amount'
        })
    else:
        return # error

    df.insert(0, 'strip', m.strip) # stored as object, don't freak on dtypes
    df.insert(0, 'curvestart', m.curveStart) # date on file, not the internal zone/month column
    
    print(df)
    print(len(df.index))
    print(df.dtypes)