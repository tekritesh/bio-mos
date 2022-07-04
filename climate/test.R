


# ===================================Libs/Funcs=================================
source(
  paste(
    getwd(),
    'gbif_functions.R',
    sep = '/'
  )
)

#Inputs

vSpeciesNames = c("Rhinoceros unicornis","Bubo bengalensis")
top_left_lat_deg = 8.5
top_left_lon_deg = 72
bottom_right_lat_deg = 31.5
bottom_right_lon_deg = 91
year= '2022'


# ====================================Querys====================================


if(T){
  
    dtRawSpecies<-
      fGetSpecies(
        vSpeciesNames = vSpeciesNames,
        top_left_lat_deg = top_left_lat_deg,
        top_left_lon_deg = top_left_lon_deg,
        bottom_right_lat_deg = bottom_right_lat_deg,
        bottom_right_lon_deg = bottom_right_lon_deg,
        cNumberofDataPoints = 100000
      )
    
  dtStations<-
    fGetClimateStations(
      country_name = ,
      centre_lat_deg = median(dtSpecies$decimalLatitude),
      centre_lon_deg = median(dtSpecies$decimalLongitude),
      no_of_stations = 50,
      use_country = F
      )
  
  
  dtRawClimate<- 
    fGetHourlyWeatherData(
      vListofStationIDs = dtStations$wmo_id ,
      vListofStationNames = dtStations$station_names,
      vListofStationLat_Deg = dtStations$lat,
      vListofStationLon_Deg = dtStations$lon,
      year = year
      )

  
}

# ===========================Stitching is WIP===================================

if(T){
  # Cleaning/subsetting the datasets, standardizing some names
  
  dtRawSpecies<-dtRawSpecies[complete.cases(dtRawSpecies)]
  
  dtSpecies<- 
    dtRawSpecies[,
                 list(
                   species,
                   speciesKey,
                   
                   lat_deg = decimalLatitude,
                   lon_deg = decimalLongitude,
                   gps_error_m = coordinateUncertaintyInMeters,
                   stateProvince,
                   country,
                   
                   year,
                   month,
                   day,
                   eventDate,
                   
                   publishingCountry,
                   basisOfRecord,
                   recordedBy
                 )
    ]
  
  # Questions to Answer: ?
  # What is our strategy to merge by geo coordiantes
  # 1 deg is roughly = 100kms, so 2nd decimal place is around 1km. Is that good enough for climate data?
  # Data that we have has upto 4 decimal places. Shall we go more granular?
  
  # 
  
  dtRawClimate<-dtRawClimate[complete.cases(dtRawClimate)]
  dtClimate<- 
    dtRawClimate[,
                 list(
                   mean_air_temp_C = mean(t2m,na.rm = T)
                 ),
                 list(
                   station_name,
                   lat_deg = round(lat,2),
                   lon_deg = round(lon,2),
                   year,
                   month,
                   day
                 )
    ]
  
  
  
  dtResult<-
    rbindlist(
      lapply(
        1:nrow(dtSpecies),
        function(iRow){
          # iRow = 14
          print(iRow)
          dtUniqueStations<- dtClimate[, .N, list( station_name, lat_deg, lon_deg)]
          dtTemp<-dtSpecies[iRow]
          
          
          iLat_deg = dtTemp[,lat_deg]
          iLon_deg = dtTemp[,lon_deg]
          
          dtUniqueStations[,
                           distance_m := 
                             dtHaversine(
                               lat_from = iLat_deg,
                               lon_from = iLon_deg,
                               lat_to = lat_deg,
                               lon_to = lon_deg
                             )                 
          ]
          
          setorder(dtUniqueStations, distance_m)
          
          iTemp<- dtClimate[
            station_name == 
              dtUniqueStations[1,station_name] & 
              year == dtTemp[, year] &
              month == dtTemp[, month] & 
              day == dtTemp[, day],
            mean_air_temp_C
          ][1]
          
          dtTemp[,mean_air_temp_C := iTemp]
          
          return(dtTemp)
          
        }
      ),
      use.names = T,
      fill = T
    )
  
  
}

# ============================Data Upload=======================================
library(bigQueryR)
library(googleAuthR)
library(googleCloudStorageR)

bqr_auth(json_file = "molten-kit-354506-12dcdc7ea89a.json")

bqr_upload_data(
  projectId = 'molten-kit-354506',
  datasetId =  "sample_gbif_climate",
  tableId = 'sameple_test_upload',
  upload_data = dtResult,
  create = 'CREATE_IF_NEEDED',
  wait = T,
  autodetect = T)




# ==============================================================================




