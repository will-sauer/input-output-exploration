
#! loading from google drive
#* uncomment for use in colab
#* import os

#* from google.colab import drive
#* drive.mount('/content/drive')
#* DATA_LOCATION = '/content/drive/MyDrive/society/academic/505/505-project/final submission/colab data/IOT_2011_ixi'

#* # uncomment for troubleshooting
#* # print(f"Confirm below is IOT_2011_ixi:")
#* # print(f"Using path:", DATA_LOCATION)
#* # print(f"Contents:")
#* # print(os.listdir(DATA_LOCATION))

#* !pip install pymrio

#! remove for use in colab

#* just a stand in for running this in ide, will be replaced by above in colab
DATA_LOCATION = '../data/external/IOT_2011_ixi'

#! imports

import pymrio
import numpy as np
import pandas as pd

#! constants

KG_KT = 1_000_000 #* 1000 kg / 1 kt
MEUR_EUR = 1 / 1_000_000 #* 1 meur / 1000000 eur
EUR_MEUR = 1_000_000 #* 1000000 eur / 1 meur

#! load data

exio = pymrio.load_all(DATA_LOCATION)
exio = pymrio.parse_exiobase3(DATA_LOCATION)

#! calculate database wide total intensity vector (impacts per M.EUR) via leontief

print("First we calculate database wide total intensity vector (impacts per M.EUR) via leontief\n\n")

I = np.identity(len(exio.A)) #* create an identity matrix of the A matrix
L = L = np.linalg.inv(I - exio.A.values) #* LEONTIEF
F = exio.satellite.F.values #* load all F values into standalone dataframe
Y = exio.Y.sum(axis=1) #* sum all rows to get total final demand

total_intensity_vector = F @ L # * total intensity vector: per M.EUR of output

#* add names
total_intensity_vector_w_names = pd.DataFrame(
    total_intensity_vector,
    index=exio.satellite.F.index,
    columns=exio.A.columns
)

print("Now we pare this down for the purposes of investigting French nuclear sector...\n\n")

#! narrow down database wise total intensity vector to only french nuclear sectors x uranium impacts
#* grab names of french nuclear sectors from technical coefficients matrix
french_nuclear_sector_name = [
     sector for sector in exio.A.columns
     if 'fr' in sector[0].lower()
     and 'production of electricity by nuclear' in sector[1].lower()
 ]

print(f"Getting French nuclear sector name... {french_nuclear_sector_name} \n\n")

#* filter total intensity vector down to just the french nuclear sector (down to 1 column)
french_nuclear_total_intensity_vector = total_intensity_vector_w_names[french_nuclear_sector_name]

print(f"Now filtering total intensity vector for just those sectors... {french_nuclear_total_intensity_vector}\n\n")

#* assemble names of uranium impacts for filtering
#* pick the row names (the index) containing uranium
uranium_impact_names = [
    impact for impact in total_intensity_vector_w_names.index 
    if 'uranium' in impact.lower()
]

print(f"Getting uranium impact names... {uranium_impact_names}\n\n")

#* filter impacts of french nuclear sector to only uranium (down to two rows), then sum
french_nuclear_total_intensity_vector_only_uranium = french_nuclear_total_intensity_vector.loc[uranium_impact_names]
french_nuclear_total_intensity_vector_only_uranium_sum = french_nuclear_total_intensity_vector_only_uranium.to_numpy().sum()

print(f"Now filtering total intensity vector for just those sectors... {french_nuclear_total_intensity_vector_only_uranium}\n\n")
value = round(french_nuclear_total_intensity_vector_only_uranium_sum,2)
print(f"This gives us total extraction of uranium across both sectors of... {value} kt / M.EUR\n\n")

#! change total intensity from per kt extraction / M.EUR to kg extraction / kWh
print("Now change total intensity from per kt extraction / M.EUR to kg extraction / kWh\n\n")

#* get total french nuclear elec output from 2011, iea lists as gwh, converted to kwh
#* source: https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=FRANCE&energy=Electricity&year=2011
french_nuclear_output_kwh = 442_387_000_000 

value = round(french_nuclear_output_kwh,2)
print(f"French nuclear output in kWh: {french_nuclear_output_kwh}\n\n")

#* get the total output (leontief @ final demand) of *only* the production of electricity by nuclear sector
total_output = L @ Y
total_output_w_names = pd.Series(total_output, index=Y.index)

#* grab the row pertaining to french nuclear electricity production from total output
french_nuclear_total_output_meur = total_output_w_names[french_nuclear_sector_name]

#* use above to get french nuclear sector output in euros per kWh for conversion of total intensity vector
french_nuclear_total_output_eur_kwh = french_nuclear_total_output_meur / french_nuclear_output_kwh * EUR_MEUR

#* change total intensity from kt extraction / M.EUR to kg extraction / kWh
french_nuclear_extraction_intensity_kg_kwh = (
    french_nuclear_total_intensity_vector_only_uranium_sum * KG_KT * MEUR_EUR * french_nuclear_total_output_eur_kwh
)

print("Now we can calculate the extraction intensity of uranium in the french nuclear sector in kg / kWh\n\n")
value = round(french_nuclear_extraction_intensity_kg_kwh.values[0],2)
print(f"Final Output: French Nuclear Sector's Extraction Intensity: {value} kg / kWh\n\n")
