import pymrio
import numpy as np
import pandas as pd

#! prep / setting up the data for leontief
#* load data (need to experiment with one command for this)
exio = pymrio.parse_exiobase3('../data/external/IOT_2011_ixi')
exio = pymrio.load_all('../data/external/IOT_2011_ixi')

#* pull direct impact data and aggregate / wrangle it
#* no linear algebra and no upstream impact
#* using a python comprehension (aptly named) on the dataframe
french_nuclear_sectors = [
     sector for sector in exio.A.columns
     if 'fr' in sector[0].lower()
     and 'nuclear' in sector[1].lower()
 ]

#* locate rows from f matrix that have entries under the french nuclear sector columns
#* returns a long list of two columns — one for each of two french nuclear sectors
direct_impact = exio.satellite.F[french_nuclear_sectors]

#* remove zero value impact rows
non_zero_direct_impact = direct_impact[(direct_impact.iloc[:, 0] != 0) | (direct_impact.iloc[:, 1] != 0)]

#* combine impacts from each of the two sectors into a single total
total_direct_impact = direct_impact.sum(axis=1).sort_values(ascending=False)


#! doing leontief and total intensity vector for all sectors
I = np.identity(len(exio.A)) #* create an identity matrix of the A matrix
L = L = np.linalg.inv(I - exio.A.values) #* LEONTIEF
F = exio.satellite.F.values #* load all F values into standalone dataframe

total_intensity_vector = F @ L # * total intensity vector: per M.EUR of output

#* add back in names
total_intensity_vector_w_names = pd.DataFrame(total_intensity_vector, index=exio.satellite.F.index, columns=exio.A.columns)

#! use previous data prep to extract just fr nuclear sector resuls

#* filter to only the french nuclear sector (down to 2 columns)
french_nuclear_total_intensity_vector = total_intensity_vector_w_names[french_nuclear_sectors]

#* filter for only the uranium extraction impacts (down to 2 rows)
uranium_impacts = [
    impact for impact in total_intensity_vector_w_names.index #* pick the rows (the index) with uranium
    if 'uranium' in impact.lower()
]
french_nuclear_total_intensity_vector_only_uranium = french_nuclear_total_intensity_vector.loc[uranium_impacts]
french_nuclear_total_intensity_vector_only_uranium_sum = french_nuclear_total_intensity_vector_only_uranium.to_numpy().sum()

#! change total intensity from per kt extraction / M.EUR to kg extraction / kWh

kg_kt = 1_000_000 #* 1000 kg / 1 kt
meur_eur = 1 / 1_000_000 #* 1 meur / 1000000 eur
eur_meur = 1_000_000 #* 1 eur / 1 meur
french_nuclear_output_2011_kwh = 442_387_000_000 #* iea lists as gwh, converted to kwh
#* https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=FRANCE&energy=Electricity&year=2011

#* get the output of *only* the production of electricity by nuclear sector
nuclear_electricity_row = [
    row for row in exio.Y.index
    if 'fr' in row[0].lower() and 'production of electricity by nuclear' in row[1].lower()
]

#* extract the column from the Y matrix (this will include all final demand rows) for the production sector
#* transpose and sort for easier viewing in datawrangler
french_nuclear_electricity_final_demand = exio.Y.loc[nuclear_electricity_row, :].transpose()
french_nuclear_electricity_final_demand = french_nuclear_electricity_final_demand.sort_values(by=french_nuclear_electricity_final_demand.columns[0], ascending=False)

#* doing the same thing in different way as a check: sum all rows to get total final demand
french_nuclear_electricity_final_demand_total = french_nuclear_electricity_final_demand.sum(axis=None)

#* 2011 output in euros per kWh
french_nuclear_output_eur_kwh = french_nuclear_electricity_final_demand_total / french_nuclear_output_2011_kwh * eur_meur

#*so now i have all the elements to do the calculation ... do this upon return
#* don't forget to conert final demand to eur (from M.EUR?)
french_extraction_intensity_kg_kwh = french_nuclear_total_intensity_vector_only_uranium_sum * kg_kt * meur_eur * french_nuclear_output_eur_kwh
