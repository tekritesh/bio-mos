# 🌏 GBIF powered by covariates
> &#x20;🐸 Open-access biodiversity data

# Documentation and Caveats

This document serves to explain the assumptions and design decisions that brought forward this product. The document is organized as follows:

- Objective
- Data Sources and decisions
- Data Pipeline and Automation
- User Experience
- ✨Future Work

# Objective

Our product seeks to extend the GBIF occurrences with other crucial environmental and human interference data that are currently available through disparate sources. We expect our proposal to save time for ecologists (& environmental data researchers) by automating the laborious data engineering phase.

Our aim is to make GBIF more comprehensive and quicker to adopt by incorporating the following tenets.

> *Access - Improve accessibility to environmental data science by reducing time/programming/data engineering barriers\
> Usefulness -  Integrate data sources that are valuable to the community\
> Quality of open biodiversity data - Create an iterative mechanism to improve data quality and clear documentation and usage instructions.*

Next, we describe the various data sources that are currently available in the pipeline.

# Data Sources and Decisions

## Climate

NOAA

<br>

## Soil

### Properties

The table below shows the properties currently mapped with SoilGrids, their description and mapped units. By dividing the predictions values by the values in the *Conversion factor* column, the user can obtain the more familiar units in the *Conventional units* column.

| **Name**     | **Description**                                                                        | **Mapped units**   | **Conversion factor** | **Conventional units** |
| ------------ | -------------------------------------------------------------------------------------- | ------------------ | --------------------- | ---------------------- |
| **bdod**     | **Bulk density of the fine earth fraction**                                            | **cg/cm³**         | **100**               | **kg/dm³**             |
| **cec**      | **Cation Exchange Capacity of the soil**                                               | **mmol(c)/kg**     | **10**                | **cmol(c)/kg**         |
| **cfvo**     | **Volumetric fraction of coarse fragments (> 2 mm)**                                   | **cm3/dm3 (vol‰)** | **10**                | **cm3/100cm3 (vol%)**  |
| **clay**     | **Proportion of clay particles (< 0.002 mm) in the fine earth fraction**               | **g/kg**           | **10**                | **g/100g (%)**         |
| **nitrogen** | **Total nitrogen (N)**                                                                 | **cg/kg**          | **100**               | **g/kg**               |
| **phh2o**    | **Soil pH**                                                                            | **pHx10**          | **10**                | **pH**                 |
| **sand**     | **Proportion of sand particles (> 0.05 mm) in the fine earth fraction**                | **g/kg**           | **10**                | **g/100g (%)**         |
| **silt**     | **Proportion of silt particles (≥ 0.002 mm and ≤ 0.05 mm) in the fine earth fraction** | **g/kg**           | **10**                | **g/100g (%)**         |
| **soc**      | **Soil organic carbon content in the fine earth fraction**                             | **dg/kg**          | **10**                | **g/kg**               |
| **ocd**      | **Organic carbon density**                                                             | **hg/m³**          | **10**                | **kg/m³**              |
| **ocs**      | **Organic carbon stocks**                                                              | **t/ha**           | **10**                | **kg/m²**              |

### Depth intervals

**SoilGrids predictions are made for the six standard depth intervals specified in the** [**GlobalSoilMap IUSS working group and its specifications**](https://www.isric.org/sites/default/files/GlobalSoilMap_specifications_december_2015_2.pdf)**:**

|                        | **Interval I** | **Interval II** | **Interval III** | **Interval IV** | **Interval V** | **Interval VI** |
| ---------------------- | -------------- | --------------- | ---------------- | --------------- | -------------- | --------------- |
| ***Top depth (cm)***   | **0**          | **5**           | **15**           | **30**          | **60**         | **100**         |
| ***Bottom depth (cm*** | **5**          | **15**          | **30**           | **60**          | **100**        | **200**         |

###

We use the 0-5cm mean depth.\


## Land Cover

The data is from Google's Dynamic World

10m spatial resolution

<br>

## Human Interference

### Light Pollution

Light pollution is a major disturbance for biodiversity, including insects and migratory birds. As habitats shrink, more artificial lights seep into the natural world during the night. We use the data from the "Open night time lights" project by the world bank. The data is captured by the VIIRS (Visible Infrared Imaging Radiometer Suite) satellite.&#x20;

The DNB (day night band) are scanning radiometers capable of low-light imaging and are launched onboard sun-synchronous polar-orbiting platforms. They both collect 14 orbits per day, imaging the daytime and nighttime side of the earth every 24 hours at a 750 m (on an edge) spatial resolution.

Daily data has too much noise to provide meaningful numbers. It is common practice to use monthly or annual composite satellite data to get a sense of the light distribution at a point.

We use [VIIRS stray light corrected DNB monthly composites](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG "VIIRS Stray Light Corrected Nighttime Day/Night Band Composites Version 1 | Earth Engine Data Catalog | Google Developers") data to determine the potential radiance exposure of a GBIF occurrence location. We provide the data using a **20km** radius buffer zone and compute the **average radiance** in the region (assumption: Animal location is not exact and moves around over time, in this case, from day to night if spotted during the day)

**Average radiance range (approximate) and units:  0-300 nanowatts/cm2/sr** (higher being more radiance, avg\_radiance)

### Invasive Species

Invasive species can pose a major threat to the native biodiversity of a land. We flag each GBIF occurrence in a particular location as invasive or not. This signal works as an early indicator of invasive species growth and can drive action to curb the spread. &#x20;

We use the Global invasive species dataset by IUCN

```
Number of rows for sample used:
 GBR    437
 BRA    388
```

The output is a boolean value corresponding to each occurrence (is\_invasive).&#x20;

*Caveat:* We use the global invasive species dataset that does not seem to update very frequently and does not have intra-country invasiveness data. We will replace the main source of this signal if a better option surfaces.

### Human Settlement

Human settlement data can provide information about proximity to urban centers. Such data can be important to understand which areas overlap with significant biodiversity and should be preserved.

Our human settlement data comes from 'The Global Human Settlement Layer (GHSL)' dataset (Latest data: 2015, our database will be updated when there is a new census).

This data can also serve as a proxy for roadways.&#x20;

We provide the data using a **10km** radius buffer zone and compute the **average degree of urbanization** in the region.

Degree of urbanization is quantified on a scale of 0-3:

- Inhabited areas - 0
- Rural grid cells - 1
- Low Density Clusters (towns and cities) - 2&#x20;
- High Density Clusters (cities) - 3

We provide an average degree of urbanization of a 10km radius zone as 'avg\_deg\_urban'.

*Caveat*: If a lot of occurrence data comes from citizen science, there is an inherent bias in the occurrence data.  As the occurrences will be more heavily reported around urban centers. We need to calculate populations with this bias in mind.

# Data Pipeline and Automation

Biodiversity and environmental data are increasing at an exponential scale and will continue to do so. We need to build scalable and robust pipelines and code to handle data that is constantly updated. For our project, we orchestrate our pipeline using Apache Airflow.

Apache airflow is a data orchestration tool to schedule jobs and maintain scalable pipelines. We chose airflow because it is free and open source. it also integrates well with different cloud platforms and has the largest user support community.

Our pipeline fetches daily data from the GBIF API. The next steps are parallel data fetching and integration of our varied data sources (modular and can be easily extended to include more sources/eliminate unimportant ones) corresponding the GBIF temporal and spatial data. Our final step is to combine all the sources which can be queried by our visualization website or the end user.&#x20;

[](https://lucid.app/documents/view/075dc236-c845-4621-97e3-f1d94521c351)

The figure below demonstrates our pipeline run for a select number of days. The pipeline will be set to run on a daily schedule and past data can be backfilled once all the parameters are finalized and the pipeline is moved to the cloud.&#x20;

<br>

![Screen Shot 2022-07-19 at 3.01.04 PM.png](<https://files.nuclino.com/files/bd30d051-ff60-44de-a52f-58a7b20f0f80/Screen Shot 2022-07-19 at 3.01.04 PM.png>)

![Screen Shot 2022-07-19 at 3.01.14 PM.png](<https://files.nuclino.com/files/972e7c8d-e978-453d-b4a9-992d87125bd6/Screen Shot 2022-07-19 at 3.01.14 PM.png>)

# Website and UX

<br>

# Future Work

1. &#x20;Extend prototype for all countries (Present demonstration is only for Brazil and the Great Britain)
2. More data sources upon request
3. Update variables like buffer zone radius, bounding box size if evidence for better thresholds is provided.
4. &#x20;Productionize pipeline in the cloud

<br>

## Resources

1. [NOAA](https://www.noaa.gov/)
2. [SoilGrids — global gridded soil information](https://www.isric.org/explore/soilgrids/ "SoilGrids — global gridded soil information")
3. [Google Dynamic World - Land Cover](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1 "Dynamic World V1 | Earth Engine Data Catalog | Google Developers")
4. [Welcome — Open Nighttime Lights](https://worldbank.github.io/OpenNightLights/welcome.html "Welcome — Open Nighttime Lights")
5. [Global Invasive Species Database](https://www.gbif.org/dataset/b351a324-77c4-41c9-a909-f30f77268bc4 "Global Invasive Species Database")
6. [Global Human Settlement - GHSL Homepage - European Commission](https://ghsl.jrc.ec.europa.eu/ "Global Human Settlement - GHSL Homepage - European Commission")

## Code

[Github Code Repository ](https://github.com/tekritesh/bio-conservation "GitHub - tekritesh/bio-conservation")

\<gcp>

## License

MIT
