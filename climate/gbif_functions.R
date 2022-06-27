

library(data.table)
library(logger)
library(curl)
library(rgbif)
library(ggplot2)
library(ggmap)
library(climate)
library(geosphere)

# ============================= GBIF QUERY======================================
fGetSpecies<-function(
  vSpeciesNames="",
  top_left_lat_deg,
  top_left_lon_deg,
  bottom_right_lat_deg,
  bottom_right_lon_deg,
  cNumberofDataPoints=3000){
  
  
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
# vSpeciesToQuery<- c("Rhinoceros unicornis","Bubo bengalensis")
# vSpeciesToQuery<- c("Rhinoceros unicornis")
# vLongitudeLimits<- "72,91"
# vLatitudeLimits<- "8.5,31.5"
# 
# dt<-fGetSpecies(
#   # vSpeciesNames =  c("Rhinoceros unicornis"),
#   vSpeciesNames =  c("Rhinoceros unicornis","Bubo bengalensis"),
#   top_left_lat_deg = 8.5,
#   top_left_lon_deg = 72,
#   bottom_right_lat_deg = 31.5,
#   bottom_right_lon_deg = 91,
#   cNumberofDataPoints = 200000
# )

# =================================Get Climate Stations=========================
#  Get nearest climate stations








