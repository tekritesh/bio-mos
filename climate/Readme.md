## Data Provenance 

1. Where is the data from?
    - The data is from [NOAA](https://www.noaa.gov/)
    
2. Is it reliable? (partially subjective)
    - Yes, one of the most up-to-date data on climate updated hourly at the weather stations
    
## Time measures

1. Time range of the dataset
    - [1901-2022](https://www1.ncdc.noaa.gov/pub/data/noaa/)
    
2. Granularity (Weekly, Monthly, Annual)
    - Frequency of update is 2-5 days depending on the lat, long
    
## Location

1. Is it available for the UK, Brazil/India?
   - Yes

2. Granularity (is it a pin point location?, Rounded coordinates?...)
   - Depends  upon the spread of stations
   
3. Format (shape files, lat long, geographical code)
    - lat, long with temperature, precipitation, wind information
    
## Data Gaps and size

1. Size of the data
    - Not sure of exact size but it is lot of data to be downloaded entirely, we need to subset by space and time
    
2. Available columns and columns of interest
    
   
        
3. Missing data (amount and years/locations missing)
    - N/A

4. Nulls or Nans
    - N/A

5. Primary key
   - Lat/Long/Year
   
6. Columns to join on
   - Lat/Long/Time
   
7. Any additional fields
    - N/A
    
## Ease of access

1. Is there a free to use license?
    - Yes, but I think there is limit to the data return without an account.
    - Need to try out with an account(free) to have unlimited access. 

2. How is data accessed? (API, download)
    - FTP. [R API](https://cran.r-project.org/web/packages/climate/vignettes/getstarted.html)
    
3. Is the documentation straightforward?
    - Examples are baisc. Need to improvise
    
4. Any limits on how much data we can download?
    - Not sure yet
