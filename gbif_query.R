
# ==============================LIBS============================================
library(data.table)
library(logger)
library(curl)
library(rgbif)
library(ggplot2)
library(ggmap)

theme_set(theme_bw())


cFilePath  = "/mnt/Work/PersonalData/Raw/GBIF/"

dir.create(
  path = paste0(cFilePath,"Maps/"),
  showWarnings = F,
  recursive = T
)

dir.create(
  path = paste0(cFilePath,"Data/"),
  showWarnings = F,
  recursive = T
)

dir.create(
  path = gsub(pattern = "Raw",replacement = "Processed",x = cFilePath) ,
  showWarnings = F,
  recursive = T
)




# ==============================GBIF QUERY======================================

vSpeciesToQuery<- c("Rhinoceros unicornis")

#Ahmedabad: 23.0225° N, 72.5714° E
#Tripura: 23.9408° N, 91.9882° E
# 
#Amritsar: 31.6340° N, 74.8723° E
#Trivandrum: 8.5241° N, 76.9366° E

# note that coordinate ranges must be specified this way: "smaller, larger" (e.g. "-5, -2")
vLongitudeLimits<- "72,91"
vLatitudeLimits<- "8.5,31.5"


# Species + Coordinates
gbif_raw <- 
  occ_data(
    scientificName = vSpeciesToQuery,
    hasCoordinate = TRUE,
    limit = 20000,
    decimalLongitude = vLongitudeLimits,
    decimalLatitude = vLatitudeLimits
    )  

vCitations<- 
  gbif_citation(gbif_raw)


#Filteting List Object 
dtData<-
  data.table(
    gbif_raw$data
    )







# ===============================GBIF PLOTS=====================================

if(F){
  height <- dtData[, diff(range(decimalLatitude))]
  width <- dtData[, diff(range(decimalLongitude))]
  sac_borders <- c(bottom  = min(dtData$decimalLatitude)  - 0.1 * height, 
                   top     = max(dtData$decimalLatitude)  + 0.1 * height,
                   left    = min(dtData$decimalLongitude) - 0.1 * width,
                   right   = max(dtData$decimalLongitude) + 0.1 * width)
  map <- get_stamenmap(sac_borders, zoom = 10, maptype = "toner-lite")
  
  cFileName<- 
    paste(
      round(sac_borders[1]),
      round(sac_borders[2]),
      round(sac_borders[3]),
      round(sac_borders[4]),
      sep = "_"
    )
  
  save(
    list = "map",
    file = 
      paste0(
        cFilePath,
        "Maps/",
        cFileName,
        ".Rdata"
        )
  )
  
}


qmplot(
  data =
    dtData,
  x = 
    decimalLongitude,
  y = 
    decimalLatitude,
  maptype = 
    "terrain",
    # "toner",
  geom = 
    "point",
  col = 
    'red',
  size=
    2,
  alpha = 
    0.7
  )


# ggmap(map)+
# # ggplot()+
#   geom_point(
#     data = 
#       dtData,
#     aes(
#       x = 
#         decimalLatitude,
#       y =
#         decimalLongitude
#     ),
#     alpha = 
#       0.7
#   )

