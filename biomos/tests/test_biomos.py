from biomos import __version__
from biomos import climate
from biomos import human_interference
from biomos import species
from biomos import land_cover
from biomos import soil_info
import logging

def test_version():
    assert __version__ == '0.1.0'

def test_climate_api():
    inst = climate.GetClimateData(logging.INFO)
    df = inst.get_interpolated_climate_data(
        lat_deg=52.33428,
        lon_deg=4.544288,
        start_date='2022-01-02',
        end_date='2022-01-02')
    assert df['tavg'].values[0] == 10.6
    assert df['tmin'].values[0] == 9.6
    assert df['tmax'].values[0] == 11.4

def test_human_interferance_api():
    inst = human_interference.HumanInterference()
    radiance = inst.get_avg_radiance(
        lat_deg=52.33428,
        lon_deg=4.544288,
        event_date='2022-01-02')
        
    assert round(radiance,2) ==11.75

def test_species_api():
    inst = species.Occurence()
    data= inst.get_occurrences(
        event_date='2022-01-02',
        country="GB"
        )
    assert data['key'].values[0] == 3436650793

def test_land_cover_api():
    inst = land_cover.LandCoverLabel()
    data= inst.get_land_cover_data(
        lat_deg=52.33428,
        lon_deg=4.544288,
        event_date= '2022-04-05T00:00:00Z')

    assert data[0] == 'trees'

def test_soil_composition_api():
    inst = soil_info.SoilComposition()

    df= inst.get_soil_data(
        lat_deg=52.33428,
        lon_deg=4.544288)

    assert df['clay_0-5cm_mean'].values[0] == 73.00000000000001
    assert df['nitrogen_0-5cm_mean'].values[0] == 5376
    assert df['ocd_0-5cm_mean'].values[0] == 501
    assert df['phh2o_0-5cm_mean'].values[0] == 61







