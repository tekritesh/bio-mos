


# ==============================================================================
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


# ==============================================================================


if(T){
  
  dtSpecies<-
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
  
  
  dtClimate<- 
    fGetHourlyWeatherData(
      vListofStationIDs = dtStations$wmo_id ,
      vListofStationNames = dtStations$station_names,
      vListofStationLat_Deg = dtStations$lat,
      vListofStationLon_Deg = dtStations$lon,
      year = year
      )

  
}