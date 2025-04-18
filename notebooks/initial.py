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

total_intensity_vector = F @ L # * total intensity vector: per 1 M.EUR of nuclear sector(s) output

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




#! change total intensity from per kt extraction / M.EUR to kg extraction / kWh
#TODO: to be completed post preso, only the indexes of exio.y don't match french_nuclear_sectors
#TODO: just need to resolve that and then it should work; but this is the basic flow below
#* french nuclear output in kwh
#* https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=FRANCE&energy=Electricity&year=2011
# french_nuclear_kwh_2011 = 442_387_000_000

#* fr nuclear output in eur from final demand / y matrix
#* takes total output across both processing and production (since i want to get extraction for both sectors)
# french_nuclear_output_eur = exio.Y[french_nuclear_sectors].sum()

#* get a rate from the two
# eur_per_kwh = french_nuclear_output_eur / french_nuclear_kwh_2011

#* convert the total intensity vector's units using the rate
# french_nuclear_total_instensity_vector_only_uranium_per_kwh = french_nuclear_total_intensity_vector_only_uranium * eur_per_kwh


