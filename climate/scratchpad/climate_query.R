

library(climate)
library(ggplot2)
library(ggmap)
library(data.table)

theme_set(theme_bw())

load("/mnt/Work/PersonalData/Raw/GBIF/Data/Vulpes vulpes_Haliaeetus albicilla_Dama dama_Hydropotes inermis_Capreolus capreolus_Cervus elaphus.RData")


dtNames<- data.table(imgw_meteo_abbrev)

setorder(dtNames,abbr_eng)

  
dtStations = nearest_stations_ogimet(
                          country ="United+Kingdom",
                            # point = c(4.951,51.99),
                            no_of_stations = 10000, 
                            add_map = TRUE)

dtStations<-data.table(dtStations)



dtStations<-
  dtStations[ `distance [km]` < 600 ]

if(F){
  
  #  Refer for station ID verification : https://www1.ncdc.noaa.gov/pub/data/noaa/isd-history.txt
  
  # Garbage API
  
  
  df<-meteo_noaa_hourly(
    
    station = "031000-99999",
    # station = "031000",
    # station = paste0(min(ns$wmo_id),'0-',max(ns$wmo_id),"0"),
    year = "2022"
  )
}

df<- 
  rbindlist(
    lapply(
      1:nrow(dtStations),
      function(iRow){
        # iStation= "03857"
        iStation = paste0(dtStations[iRow,wmo_id],"0-99999")
        tryCatch(
          expr = {
            
            dtTemp<- 
              meteo_noaa_hourly(
                station = iStation,
                year = "2022"
              )
            
            dtTemp<-data.table(dtTemp)
            # print(head(dtTemp))
            dtTemp[,
                   station_name := dtStations[iRow, station_names]
                   ]
            
            dtTemp[,
                   station_id := dtStations[iRow, wmo_id]
            ]
            
            dtTemp[,
                   station_lat_deg := dtStations[iRow, lat]
            ]
            
            dtTemp[,
                   station_lon_deg := dtStations[iRow, lon]
            ]
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

save(
  list = 
    "df",
  file = "/mnt/Work/PersonalData/Raw/GBIF/Data/Vulpes vulpes_Haliaeetus albicilla_Dama dama_Hydropotes inermis_Capreolus capreolus_Cervus elaphus_WeatherData.RData"
)





if(F){
  
  # Weather Station Cooridinates
  qmplot(
    data =
      dtStations,
    y = 
      lat,
    x = 
      lon,
    maptype = 
      "terrain",
    # "toner",
    geom = 
      "point",
    # col = 
      # species,
    # 'red',
    size=
      2,
    alpha = 
      0.7
    # zoom = 1
  )
  
}


df = meteo_imgw(
  interval = "daily",
  rank = "synop",
  year = 2020:2021,
  coords = T,
  station = "Baltasound,Weybourne"
  # station = "ŁEBA"
  )

