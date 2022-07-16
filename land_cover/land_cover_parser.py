import ee
import geemap
import pandas as pd


startDate = '2021-01-01'
endDate = '2022-06-01'
brazil_data = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
uk_data = pd.read_csv('bquxjob_39d5dfa3_181e432946c.csv')

all_data = pd.concat([brazil_data, uk_data])
all_data = all_data.reset_index(drop=True)

#all_data = all_data.iloc[0:5]

land_cover_label = []
problematic_data = []
for index, row in all_data.iterrows():
    try:
        ee.Initialize()
        print(index)
        lat = row['decimalLatitude']
        lon = row['decimalLongitude']
        geometry = ee.Geometry.Point([lon, lat])

        dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(startDate, endDate).filterBounds(geometry)
        dwImage = ee.Image(dw.first())
        dwImagenew = dw.mode()
        label_index = dwImagenew.sample(geometry, scale=10).first().get('label').getInfo()
        label_type = dwImage.getInfo()['bands'][label_index]['id']
        land_cover_label.append(label_type)
    except Exception:
        print('problem')
        problematic_data.append(row)
        land_cover_label.append(None)

print('x')