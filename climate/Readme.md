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
UK:
![image](https://user-images.githubusercontent.com/65660549/175902238-7db156b9-0201-4dfb-9482-25df047f3335.png)
India:
![image](https://user-images.githubusercontent.com/65660549/175902426-c4e8ba9e-4a29-419e-8d83-f8dccdfcfbf5.png)

Brazil:
![image](https://user-images.githubusercontent.com/65660549/175902367-7c9017a4-dfd0-43ef-8121-886354d4462b.png)



2. Granularity (is it a pin point location?, Rounded coordinates?...)
   - Depends  upon the spread of stations
   
3. Format (shape files, lat long, geographical code)
    - lat, long with temperature, precipitation, wind information
    
## Data Gaps and size

1. Size of the data
    - Not sure of exact size but it is lot of data to be downloaded entirely, we need to subset by space and time
    
2. Available columns and columns of interest
    ![image](https://user-images.githubusercontent.com/65660549/175902043-737b6d83-cddd-47f6-9391-0c3e71ce8058.png)

   
        
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


## Sample Upload
 -  I took the oppurtunityh to stitch gbif with climate data and upload it [here](https://console.cloud.google.com/bigquery?project=molten-kit-354506&ws=!1m4!1m3!3m2!1smolten-kit-354506!2ssample_gbif_climate).
 ![image](https://user-images.githubusercontent.com/65660549/175912109-83a88247-c0d8-40ac-b198-fbae3210072a.png)

