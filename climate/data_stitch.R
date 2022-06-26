# ==============================LIBS============================================
library(data.table)
library(logger)
library(curl)
library(rgbif)
library(ggplot2)
library(ggmap)
library(climate)
library(geosphere)

theme_set(theme_bw())

load(
  "/mnt/Work/PersonalData/Raw/GBIF/Data/Vulpes vulpes_Haliaeetus albicilla_Dama dama_Hydropotes inermis_Capreolus capreolus_Cervus elaphus.RData"
  )
load("/mnt/Work/PersonalData/Raw/GBIF/Data/Vulpes vulpes_Haliaeetus albicilla_Dama dama_Hydropotes inermis_Capreolus capreolus_Cervus elaphus_WeatherData.RData"
     )


df<-df[complete.cases(df)]
# ===========================Data Cleaning=======================================

# Cleaning the datasets, standardizing names
dtSpecies<- 
    dtData[,
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

dtClimate<- 
  df[,
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

if(F){
  
  # Weather Station Cooridinates
  qmplot(
    data =
      dtClimate[ 
        
        year == 2022 &
          month == 6 &
        day == 23
        ],
    y = 
      lat_deg,
    x = 
      lon_deg,
    maptype = 
      "terrain",
    # "toner",
    geom = 
      "point",
    col =
      mean_air_temp_C,
    # 'red',
    size=
      2,
    alpha = 
      0.7
    # zoom = 1
  )+
    scale_color_continuous(low = 'blue', high = 'red')
}

# ==============================Add Climate=====================================

# Rounding Coordinates so to decrease the spread
# setorder(dtClimate,lat_deg, lon_deg)
# merge(
#   dtClimate,
#   dtSpecies[,
#             list(
#                   lat_deg = round(lat_deg,2),
#                   lon_deg = round(lon_deg,2),
#                   year,
#                   month,
#                   day
#                   )
#     ],
#   by = 
#     c("lat_deg","lon_deg","year","month","day"),
#   all.y = T
# )


# ==============================================================================
dtHaversine <- function(lat_from, lon_from, lat_to, lon_to, r = 6378137){
  radians <- pi/180
  lat_to <- lat_to * radians
  lat_from <- lat_from * radians
  lon_to <- lon_to * radians
  lon_from <- lon_from * radians
  dLat <- (lat_to - lat_from)
  dLon <- (lon_to - lon_from)
  a <- (sin(dLat/2)^2) + (cos(lat_from) * cos(lat_to)) * (sin(dLon/2)^2)
  return(2 * atan2(sqrt(a), sqrt(1 - a)) * r)
}

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

save(
  list = 
    "dtResult",
  file = 
    '/mnt/Work/PersonalData/Processed/GBIF/SampleClimate.Rdata'
)


