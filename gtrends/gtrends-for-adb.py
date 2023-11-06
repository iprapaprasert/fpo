'''
The program for acquiring private consumption indicator from Google Trends
'''
import pandas as pd
from pytrends.request import TrendReq
import datetime
import time

########## PARAMETERS ##########
# Province Tuple = (prov_code, prov_name, region_wgt)
NORTH = [
    (50, "Chiang Mai"), 
    (51, "Lamphun"), 
    (52, "Lampang"),
    (53, "Uttaradit"),
    (54, "Phrae"),
    (55, "Nan"),
    (56, "Phayao"),
    (57, "Chiang Rai"),
    (58, "Mae Hong Son"),
    (60, "Nakhon Sawan"),
    (61, "Uthai Thani"),
    (62, "Kamphaeng Phet"),
    (63, "Tak"),
    (64, "Sukhothai"),
    (65, "Phitsanulok"),
    (66, "Phichit"),
    (67, "Phetchabun")
]
NORTHEAST = [
    (30, "Nakhon Ratchasima"),
    (31, "Buriram"),
    (32, "Surin"),
    (33, "Sisaket"),
    (34, "Ubon Ratchathani"),
    (35, "Yasothon"),
    (36, "Chaiyaphum"),
    (37, "Amnat Charoen"),
    (38, "Bueng Kan"),
    (39, "Nong Bua Lam Phu"),
    (40, "Khon Kaen"),
    (41, "Udon Thani"),
    (42, "Loei"),
    (43, "Nong Khai"),
    (44, "Maha Sarakham"),
    (45, "Roi Et"),
    (46, "Kalasin"),
    (47, "Sakon Nakhon"),
    (48, "Nakhon Phanom"),
    (49, "Mukdahan")
]
CENTRAL = [
    (10, "Bangkok"),
    (11, "Samut Prakan"),
    (12, "Nonthaburi"),
    (13, "Pathum Thani"),
    (14, "Nakhon Si Ayutthaya"),
    (15, "Ang Thong"),
    (16, "Lopburi"),
    (17, "Sing Buri"),
    (18, "Chai Nat"),
    (19, "Saraburi"),
    (20, "Chon Buri"),
    (21, "Rayong"),
    (22, "Chanthaburi"),
    (23, "Trat"),
    (24, "Chachoengsao"),
    (25, "Prachin Buri"),
    (26, "Nakhon Nayok"),
    (27, "Sa Keao"),
    (70, "Ratchaburi"),
    (71, "Kanchanaburi"),
    (72, "Suphan Buri"),
    (73, "Nakhon Pathom"),
    (74, "Samut Sakhon"),
    (75, "Samut Songkhram"),
    (76, "Phetchaburi"),
    (77, "Prachuap Khiri Khan")
]
SOUTH = [
    (80, "Nakhon Si Thammarat"),
    (81, "Krabi"),
    (82, "Phang Nga"),
    (83, "Phuket"),
    (84, "Surat Thani"),
    (85, "Ranong"),
    (86, "Chumphon"),
    (90, "Songkhla"),
    (91, "Satun"),
    (92, "Trang"),
    (93, "Phatthalung"),
    (94, "Pattani"),
    (95, "Yala"),
    (96, "Narathiwat")
]
REGIONS = [NORTH, NORTHEAST, CENTRAL, SOUTH]

# Categories from https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
CATS = [
    (71, "Food & Drink"),
    (68, "Apparel"),
    (45, "Health"),
    (11, "Home & Garden"),
    (47, "Autos & Vehicles"),
    (13, "Internet & Telecom"),
    (22, "Books & Literature"),
    (276, "Restaurants"),
    (179, "Hotels & Accommodations"),
    (44, "Beauty & Fitness"),
    (7, "Finance")
]

# Don't forget to change timeframe, have to more than 5 years 
TIMEFRAME = "2014-01-01 2023-10-01"

##### MAIN PROGRAM #####
def get_interest_over_time(timeframe, cat_key, cat_name, prov_key):
    '''
    Get interest over time for the specific category
    '''
    # Connect to Google
    pytrends = TrendReq()
    # Build payload
    pytrends.build_payload(
        kw_list=["*"],
        cat=cat_key,
        timeframe=timeframe,
        geo="TH-" + str(prov_key),
        gprop=""
    )
    data = pytrends.interest_over_time()
    data = data.rename(columns={"*": cat_name})
    return data[cat_name]


for region in REGIONS:
    region_df = pd.DataFrame()
    for index, (prov_key, prov_name, _) in enumerate(region):
        prov_df = pd.DataFrame()
        for cat_key, cat_name in CATS:
            data = get_interest_over_time(TIMEFRAME, cat_key, cat_name, prov_key)
            if prov_df.empty:
                prov_df = data
            else:
                prov_df = pd.merge(
                    prov_df, 
                    data, 
                    how="outer", 
                    left_on="date", 
                    right_on="date"
                )
            # need sleeping for preventing blocking from Google
            time.sleep(5)
        # create summarize index and merge to region dataset
        prov_df[prov_name] = (
            0.34 * prov_df["Food & Drink"] 
            + 0.05 * prov_df["Apparel"]
            + 0.06 * prov_df["Health"]
            + 0.05 * prov_df["Home & Garden"]
            + 0.17 * prov_df["Autos & Vehicles"]
            + 0.03 * prov_df["Internet & Telecom"]
            + 0.10 * prov_df["Restaurants"]
            + 0.10 * prov_df["Hotels & Accommodations"]
            + 0.03 * prov_df["Beauty & Fitness"]
            + 0.07 * prov_df["Finance"]
        )
        region_df = pd.concat([region_df, prov_df[prov_name]],axis=1)
    # save to disk
    region_df.to_csv(region.lower() + "_" + str(today) + '.csv') 

