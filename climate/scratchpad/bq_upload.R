library(bigQueryR)
library(googleAuthR)
library(googleCloudStorageR)
library(data.table)

Sys.setenv("GCS_DEFAULT_BUCKET" = "bio-conservation",
           "GCS_AUTH_FILE" = "molten-kit-354506-12dcdc7ea89a.json")
gcs_setup()

# gcs_auth()

# gar_set_client("molten-kit-354506-12dcdc7ea89a.json")
gar_auth_service(json_file="molten-kit-354506-12dcdc7ea89a.json")
gcs_global_bucket("bio-conservation")

# load('/mnt/Work/PersonalData/Processed/GBIF/SampleClimate.Rdata')

# gcs_upload(dtResult, name = "sample.csv")

bqr_auth(json_file = "molten-kit-354506-12dcdc7ea89a.json")

bqr_upload_data(
  projectId = 'molten-kit-354506',
  datasetId =  "sample_gbif_climate",
  tableId = 'sameple_test_upload',
  upload_data = dtResult,
  create = 'CREATE_IF_NEEDED',wait = T, autodetect = T)

bqr_upload_data(
  
  
  
)
