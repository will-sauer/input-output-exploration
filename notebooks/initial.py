import pymrio
import numpy as np
import pandas as pd


#! loading the data (need to experiment with one command for this)
exio = pymrio.parse_exiobase3('../data/external/IOT_2011_ixi')
exio = pymrio.load_all('../data/external/IOT_2011_ixi')


#! this is all just pulling direct impact data and aggregating / wrangling it
#! no linear algebra and no upstream
#* a comprehension (aptly named)
french_nuclear_sectors = [
     sector for sector in exio.A.columns
     if 'fr' in sector[0].lower()
     and 'nuclear' in sector[1].lower()
 ]


#* so this locates rows from f matrix that have entries under the french nuclear sector columns (this gets us to a long list of two columns)
direct_impact = exio.satellite.F[french_nuclear_sectors]


#* get some code here to extract all zero values, only list those with values (using a comprehension)
non_zero_direct_impact = direct_impact[(direct_impact.iloc[:, 0] != 0) | (direct_impact.iloc[:, 1] != 0)]


#* just adding across the columns here (so both nuclear sectors combined, for a given impact—procesing and elec production)
total_direct_impact = direct_impact.sum(axis=1).sort_values(ascending=False)

# ! now we're doing leontief ... getting the full picture per 1 EUR (the total instensity vector)

I = np.identity(len(exio.A)) #* create an identity matrix of the A matrix
L = L = np.linalg.inv(I - exio.A.values) # * THIS IS THE MAGICAL LEONTIEF
F = exio.satellite.F.values #* just load all F values into standalone dataframe

total_intensity_vector = F @ L # * the total impact for 1 EUR unit of a given country-sector

#* adding back in names
total_intensity_vector_w_names = pd.DataFrame(total_intensity_vector, index=exio.satellite.F.index, columns=exio.A.columns)

#! narrow down the total intensity vector to what i want: two fr nuclear sectors and uranium extraction

#* narrowing down to only 2 columns (from all sectors in europe) — just french nuclear sector
french_nuclear_total_intensity_vector = total_intensity_vector_w_names[french_nuclear_sectors]

#* filter for only the uranium extraction impacts, down to just two rows
uranium_impacts = [
    impact for impact in total_intensity_vector_w_names.index #* pick the rows (the index) with uranium
    if 'uranium' in impact.lower()
]
french_nuclear_total_intensity_vector_only_uranium = french_nuclear_total_intensity_vector.loc[uranium_impacts]
