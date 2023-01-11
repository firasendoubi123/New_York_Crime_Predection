import pandas as pd
import requests
import numpy as np
import joblib
api_endpoint = 'https://locatenyc.io/arcgis/rest/services/locateNYC/v1/GeocodeServer/reverseGeocode?location='
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZpcmFzamVuZG91YmkxNiIsImV4cGlyZXMiOjE2NzI4Mzg4ODYzNzAsInBlcm1pc3Npb25zIjoiYmFzaWMiLCJpYXQiOjE2NzI3Nzg2NDYsImV4cCI6MTY3MjgzODg4Nn0.13HIvfYD4o3jtQ0H4MY7PDlYDHiVCpv5XEfmoxhnkiQ"
model = joblib.load(r"model\xgboost.joblib")
crime_types = {0:'Violation',1:"Misdemeanor",2:"Felony"}
felony = open(r"crime_types\felony.txt","r").read()
mis = open(r"crime_types\misdemeanor.txt","r").read()
violation = open(r"crime_types\violation.txt","r").read()
def create_df(hour,month,day,latitude,longitude,place,
              vic_age,vic_race,vic_sex):

    hour = int(hour) if int(hour) < 24 else 0
    api_data = None
    try:
      api_data = requests.get(f'{api_endpoint}{longitude},{latitude}&distance=1000&token={api_token}').json()['address']
      pct, boro = int(api_data["policePrecinct"]),api_data["Borough"]
      boro = boro.upper()
    except Exception as e:
       print(e)
    month = int(month)
    day = int(day)
    in_park = 1 if place == "In park" else 0
    in_public = 1 if place == "In public housing" else 0
    in_station = 1 if place == "In station" else 0


    columns = np.array(['EVENT_TIME', 'ADDR_PCT_CD', 'month', 'day', 'Latitude',
       'Longitude', 'IN_PARK', 'IN_PUBLIC_HOUSING', 'IN_STATION','BORO_NM_BRONX','BORO_NM_BROOKLYN', 'BORO_NM_MANHATTAN',
       'BORO_NM_QUEENS', 'BORO_NM_STATEN ISLAND', 'BORO_NM_UNKNOWN',
       'VIC_AGE_GROUP_18-24','VIC_AGE_GROUP_25-44', 'VIC_AGE_GROUP_45-64', 'VIC_AGE_GROUP_65+',
       'VIC_AGE_GROUP_<18', 'VIC_AGE_GROUP_UNKNOWN',
       'VIC_RACE_AMERICAN INDIAN/ALASKAN NATIVE','VIC_RACE_ASIAN / PACIFIC ISLANDER', 'VIC_RACE_BLACK',
       'VIC_RACE_BLACK HISPANIC', 'VIC_RACE_OTHER', 'VIC_RACE_UNKNOWN',
       'VIC_RACE_WHITE', 'VIC_RACE_WHITE HISPANIC', 'VIC_SEX_D', 'VIC_SEX_E',
       'VIC_SEX_F', 'VIC_SEX_M', 'VIC_SEX_U'])

    data = [[hour,114 if api_data == None else pct,month,day,latitude,longitude,in_park,in_public,
       in_station,0 if api_data == None else 1 if boro == "BRONX" else 0, 0 if api_data == None else 1 if boro == "BROOKLYN" else 0,0 if api_data == None else 1 if boro == "MANHATTAN" else 0,0 if api_data == None else 1 if boro == "QUEENS" else 0,
       0 if api_data == None else 1 if boro == "STATEN ISLAND" else 0,1 if api_data == None else 1 if boro not in("BRONX","BROOKLYN","MANHATTAN","QUEENS", "STATEN ISLAND") else 0,
       1 if vic_age in range(18,25) else 0, 1 if vic_age in range(25,45) else 0, 1 if vic_age in range(45,65) else 0, 1 if vic_age>=65 else 0,
       1 if vic_age < 18 else 0, 0, 1 if vic_race == "AMERICAN INDIAN/ALASKAN NATIVE" else 0, 1 if vic_race == "ASIAN / PACIFIC ISLANDER" else 0,
       1 if vic_race == "BLACK" else 0, 1 if vic_race == "BLACK HISPANIC" else 0, 1 if vic_race == "OTHER" else 0,
       1 if vic_race == "UNKNOWN" else 0, 1 if vic_race == "WHITE" else 0, 1 if vic_race == "WHITE HISPANIC" else 0,
       0,0,1 if vic_sex == "Female" else 0,1 if vic_sex == "Male" else 0, 0]]

    df = pd.DataFrame(data,columns=columns)
    return df.values

def predict(data):
   pred = model.predict(data)[0]
   if (pred == 0):
      return crime_types[pred], violation
   elif pred==1:
      return crime_types[pred], mis
   else:
      return crime_types[pred], felony

