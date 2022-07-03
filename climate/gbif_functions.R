
# ============================= GBIF QUERY======================================
fGetSpecies<-function(
  vSpeciesNames="",
  top_left_lat_deg,
  top_left_lon_deg,
  bottom_right_lat_deg,
  bottom_right_lon_deg,
  cNumberofDataPoints=3000){
  
  require(data.table)
  require(logger)
  require(rgbif)
  require(climate)
  
  
  
  
  log_info("Connecting to GBIF Backend")
  log_info(paste0("Getting Data for:",paste(vSpeciesNames,collapse=",")))
 
  
  log_info(
    paste0(
      "Bounding Box:",
      "Lat Limits:[",paste(top_left_lat_deg,bottom_right_lat_deg,sep=","),
      "]\t",
      "Lon Limits:[",paste(top_left_lon_deg,bottom_right_lon_deg,sep = ","),"]"
    ))
  gbif_raw <- 
      occ_data(
        scientificName = vSpeciesNames,
        hasCoordinate = TRUE,
        limit = cNumberofDataPoints,
        decimalLongitude = paste(top_left_lon_deg,bottom_right_lon_deg,sep = ","),
        decimalLatitude = paste(top_left_lat_deg,bottom_right_lat_deg,sep=",")
      )  
  
  
  
  if( length(vSpeciesNames) > 1){
    dtData<-
      rbindlist(
        lapply(
          names(gbif_raw),
          function(iElement){
            
            
            dtTemp<- data.table(
              get(
                "data",
                get(
                  iElement,
                  gbif_raw)
              )
              
            )
            
            return(dtTemp)
          }
        ),
        use.names = T,
        fill = T
      )
    # log_info("Recieved Rows:",nrow(dtData))
  }else{
    
    dtData<- 
      data.table(gbif_raw$data)
    
  }
  
  log_info("Recieved Rows:",nrow(dtData))
  
  return(dtData)
}

# Test

if(F){
  # vSpeciesToQuery<- c("Rhinoceros unicornis","Bubo bengalensis")
  # vSpeciesToQuery<- c("Rhinoceros unicornis")
  # vLongitudeLimits<- "72,91"
  # vLatitudeLimits<- "8.5,31.5"
  # # 
  # dt<-fGetSpecies(
  #   # vSpeciesNames =  c("Rhinoceros unicornis"),
  #   vSpeciesNames =  c("Rhinoceros unicornis","Bubo bengalensis"),
  #   top_left_lat_deg = 8.5,
  #   top_left_lon_deg = 72,
  #   bottom_right_lat_deg = 31.5,
  #   bottom_right_lon_deg = 91,
  #   cNumberofDataPoints = 200000
  # )
  
}


# =================================Get Climate Stations=========================
#  Get nearest climate stations

fGetClimateStations<-function(
  
  country_name = '',
  centre_lat_deg,
  centre_lon_deg,
  no_of_stations = 10000,
  use_country = F
  
){
  
  require(data.table)
  require(climate)
  
  log_info("Connecting to NOAA Backend")
  
  
  
  if(use_country){
    
    if(country_name == ''){
      log_error("Please provide a country name")
      stop()
    }
    
    log_info(
      paste0(
        "Getting Data for:",
        no_of_stations,
        " Stations in: ",
        country_name
        )
      )
    
    dtStations = nearest_stations_ogimet(
      country =country_name,
      # point = c(centre_lon_deg,centre_lat_deg),
      no_of_stations = no_of_stations, 
      add_map = TRUE)
  }else{
    
    log_info(
      paste0("Getting Data for:",
             no_of_stations,
             " Stations around: [",
             centre_lat_deg,
             ",",
             centre_lat_deg,
             "]"
             )
      )
    
    dtStations = nearest_stations_ogimet(
      # country =country_name,
      point = c(centre_lon_deg,centre_lat_deg),
      no_of_stations = no_of_stations, 
      add_map = TRUE)
  }
  
  dtStations<-data.table(dtStations)
  
  log_info("Recieved Stations:",nrow(dtStations))
  
  return(dtStations)
}
# Test

if(F){
  
 dt<- 
   fGetClimateStations(
     # country_name = '',
     centre_lon_deg = 4.951,
     centre_lat_deg= 51.99,
     no_of_stations = 10000,
     use_country = F
     
   )
 
 dt<- 
   fGetClimateStations(
     country_name = 'Brazil',
     # centre_lon_deg = 4.951,
     # centre_lat_deg= 51.99,
     no_of_stations = 10000,
     use_country = T
     
   )
  
}



# =================================Get Climate Stations=========================




fGetHourlyWeatherData<-function(
  vListofStationIDs,
  vListofStationNames,
  vListofStationLat_Deg,
  vListofStationLon_Deg,
  year = ''
){
  
  require(data.table)
  require(climate)
  
  
  log_info("Connecting to NOAA Backend")
  log_info(
    paste0(
      "Getting Hourly Data for Number of Stations: ",
      length(vListofStationIDs),
      " for Year:",
      year
      )
    )
  
  if(length(vListofStationIDs) != length(vListofStationNames)){
    log_error("Please check the number of station ids and names")
    stop()
  }
  
  df<- 
    rbindlist(
      lapply(
        1:length(vListofStationIDs),
        function(iRow){
        
          
          # iStation= "03857"
          iStation = paste0(vListofStationIDs[iRow],"0-99999")
          tryCatch(
            expr = {
              
              dtTemp<- 
                meteo_noaa_hourly(
                  station = iStation,
                  year = as.character(year)
                )
              
              dtTemp<-data.table(dtTemp)
              # print(head(dtTemp))
              dtTemp[,
                     station_name := vListofStationNames[iRow]
              ]
              
              dtTemp[,
                     station_id := vListofStationIDs[iRow]
              ]
              
              dtTemp[,
                     station_lat_deg := vListofStationLat_Deg[iRow]
              ]
              
              dtTemp[,
                     station_lon_deg := vListofStationLon_Deg[iRow]
              ]
              
              log_info(
                paste0(
                  "Getting Hourly Data for Station ID: ",
                  vListofStationIDs[iRow],
                  " Name: ",
                  vListofStationNames[iRow],
                  " Received Rows: ",
                  nrow(dtTemp)
                )
              )
              return(dtTemp)
              # print(head(dtTemp))
              
            },
            error = function(e){
              message(paste0('Error for  Station:', iStation))
              next
              
            }
          )    
          
          
        }
        
      ),use.names = T,fill = T
    )
  return(df)
  
}


# Test

if(F){
  dt<- 
    data.table(
      wmo_id = c(82595,82598),
      station_names = c("Calcanhar","Natal"),
      lon = c(-35.48334,-5.166670),
      lat = c(-5.166670,-5.766682),
      alt = c(12,45)
    )
  dtClimate<-fGetHourlyWeatherData(
    vListofStationIDs = dt$wmo_id,
    vListofStationNames = dt$station_names,
    vListofStationLat_Deg = dt$lat,
    vListofStationLon_Deg = dt$lon,
    year = "2022"
  )
  
}

# =================================Stitching====================================

