import pymrio
import numpy as np
import pandas as pd

#! constants
KG_KT = 1_000_000 #* 1000 kg / 1 kt
MEUR_EUR = 1 / 1_000_000 #* 1 meur / 1000000 eur
EUR_MEUR = 1_000_000 #* 1000000 eur / 1 meur

#! load data (need to experiment with one command for this)

exio = pymrio.load_all('../data/external/IOT_2011_ixi')
exio = pymrio.parse_exiobase3('../data/external/IOT_2011_ixi')

#! calculate database wide total intensity vector (impacts per M.EUR) via leontief

I = np.identity(len(exio.A)) #* create an identity matrix of the A matrix
L = L = np.linalg.inv(I - exio.A.values) #* LEONTIEF
F = exio.satellite.F.values #* load all F values into standalone dataframe

total_intensity_vector = F @ L # * total intensity vector: per M.EUR of output

#* add names
total_intensity_vector_w_names = pd.DataFrame(
    total_intensity_vector,
    index=exio.satellite.F.index,
    columns=exio.A.columns
)

#! narrow down database wise total intensity vector to only french nuclear sectors x uranium impacts
#* grab names of french nuclear sectors from technical coefficients matrix
french_nuclear_sector_names = [
     sector for sector in exio.A.columns
     if 'fr' in sector[0].lower()
     and 'nuclear' in sector[1].lower()
 ]

#* filter total intensity vector down to just the french nuclear sector (down to 2 columns)
french_nuclear_total_intensity_vector = total_intensity_vector_w_names[french_nuclear_sector_names]

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

#* get the output (final demand, in exiobase terminology) of *only* the production of electricity by nuclear sector
nuclear_electricity_production_row_name = [
    row for row in exio.Y.index
    if 'fr' in row[0].lower() and 'production of electricity by nuclear' in row[1].lower()
]

#* extract the column from the Y matrix (this will include all final demand rows) for the production sector
french_nuclear_electricity_final_demand = exio.Y.loc[nuclear_electricity_production_row_name, :].transpose()

#* second, sum all rows to get total final demand
french_nuclear_electricity_final_demand_sum = french_nuclear_electricity_final_demand.sum()

# #* not used directly, just a crosscheck
# #* first, transpose and sort for easier viewing in datawrangler
french_nuclear_electricity_final_demand = french_nuclear_electricity_final_demand.sort_values(
    by=french_nuclear_electricity_final_demand.columns[0],
    ascending=False
)

#* use above to get french nuclear sector output in euros per kWh for conversion of total intensity vector
french_nuclear_output_eur_kwh = french_nuclear_electricity_final_demand_sum / french_nuclear_output_kwh * EUR_MEUR

#*so now i have all the elements to do the calculation ... do this upon return
#* don't forget to conert final demand to eur (from M.EUR?)
french_nuclear_extraction_intensity_kg_kwh = (
    french_nuclear_total_intensity_vector_only_uranium_sum * KG_KT * MEUR_EUR * french_nuclear_output_eur_kwh
)
