import pymrio
import numpy as np
import pandas as pd

#! constants

KG_KT = 1_000_000 #* 1000 kg / 1 kt
MEUR_EUR = 1 / 1_000_000 #* 1 meur / 1000000 eur
EUR_MEUR = 1_000_000 #* 1000000 eur / 1 meur
DATA_LOCATION = '../data/external/IOT_2011_ixi'

#! load data

exio = pymrio.load_all(DATA_LOCATION)
exio = pymrio.parse_exiobase3(DATA_LOCATION)

#! calculate database wide total intensity vector (impacts per M.EUR) via leontief

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

#! narrow down database-wide total intensity vector to only french nuclear sector x uranium impacts
#* grab names of french nuclear sectors from technical coefficients matrix
french_nuclear_sector_name = [
     sector for sector in exio.A.columns
     if 'fr' in sector[0].lower()
     and 'production of electricity by nuclear' in sector[1].lower()
 ]

#* filter total intensity vector down to just the french nuclear sector (down to 1 column)
french_nuclear_total_intensity_vector = total_intensity_vector_w_names[french_nuclear_sector_name]

#* assemble names of uranium impacts for filtering
#* pick the row names (the index) containing uranium
uranium_impact_names = [
    impact for impact in total_intensity_vector_w_names.index 
    if 'uranium' in impact.lower()
]

#* filter impacts of french nuclear sector to only uranium (down to two rows), then sum
french_nuclear_total_intensity_vector_only_uranium = french_nuclear_total_intensity_vector.loc[uranium_impact_names]
french_nuclear_total_intensity_vector_only_uranium_sum = french_nuclear_total_intensity_vector_only_uranium.to_numpy().sum()

#! change total intensity from per kt extraction / M.EUR to kg extraction / kWh

#* get total french nuclear elec output from 2011, iea lists as gwh, converted to kwh
#* source: https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=FRANCE&energy=Electricity&year=2011
french_nuclear_output_kwh = 442_387_000_000

#* get the total output (leontief @ final demand) of *only* the production of electricity by nuclear sector
total_output = L @ Y
total_output_w_names = pd.Series(total_output, index=Y.index)

#* grab the row pertaining to french nuclear electricity production from total output
french_nuclear_total_output_meur = total_output_w_names[french_nuclear_sector_name]

#* use above to get french nuclear sector output in euros per kWh for conversion of total intensity vector
french_nuclear_total_output_eur_kwh = french_nuclear_total_output_meur / french_nuclear_output_kwh * EUR_MEUR

#*so now i have all the elements to do the calculation ... do this upon return
#* don't forget to conert final demand to eur (from M.EUR?)
french_nuclear_extraction_intensity_kg_kwh = (
    french_nuclear_total_intensity_vector_only_uranium_sum * KG_KT * MEUR_EUR * french_nuclear_total_output_eur_kwh
)
