from gbif import __version__
from gbif import climate
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





