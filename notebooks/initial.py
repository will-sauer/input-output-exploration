import pymrio
import numpy as np
import pandas as pd


#! loading the data (need to experiment with one command for this)
exio = pymrio.pymrio.parse_exiobase3('../data/external/IOT_2011_ixi')
exio = pymrio.load_all('../data/external/IOT_2011_ixi')



#! this is all just pulling direct impact data and aggregating / wrangling it
#! no linear algebra and no upstream
#a comprehension (aptly named)
french_nuclear_sectors = [
    sector for sector in exio.A.columns
    if 'fr' in sector[0].lower()
    and 'nuclear' in sector[1].lower()
]


direct_impact = exio.satellite.F[french_nuclear_sectors]
#so this is direct impaxt across all of the f matrix - all impacts

#get some code here to extract all zero values, only list those with values
non_zero_direct_impact = direct_impact[(direct_impact.iloc[:, 0] != 0) | (direct_impact.iloc[:, 1] != 0)]

#just adding across the columns here (so both sectors combined, for a given impact)
total_direct_impact = direct_impact.sum(axis=1).sort_values(ascending=False)

# ! now we're doing leontief ... getting the full picture
I = np.identity(len(exio.A)) #create an identity matrix of the A matrix
L = L = np.linalg.inv(I - exio.A.values) # * THIS IS THE MAGICAL LEONTIEF
F = exio.satellite.F.values #just load all F values into standalone dataframe

total_intensity_vector = F @ L # * the total impact for 1 EUR unit of a given country-sector
#? why does it remove the column / row names?

#adding back in names
reconciled_total_intensity_vector = pd.DataFrame(total_intensity_vector, index=exio.satellite.F.index, columns=exio.A.columns)
#so here we're using the a matrix column names (country - setor) as columns and the impacts as rows)


#! now just stripping out french nuclear from this
total_supply_chain_impact = reconciled_total_intensity_vector[french_nuclear_sectors].sum(axis=1).sort_values(ascending=False)
#? what is axis 1 part doing, but basically adding up the two nuclear sectors per impact

#! now grossing this up (the above was per EUR) for the entire industry's impact
french_nuclear_final_demand_eur = exio.Y[french_nuclear_sectors].sum(axis=1)  # final demand by product
consumptions_based_impact_inventory = reconciled_total_intensity_vector @ french_nuclear_final_demand_eur
#TODO: stopped here, i need to fix how french_nuclear_sectors is defined (it's just a list, want a dataframe)
#TODO and then i want to do this final cons_based_imp_inv calc


#! just sorting and displaying top 10
# impact_vector = pd.Series(french_nuclear_final_demand_eur, index=exio.satellite.F.index).sort_values(ascending=False)
# print(impact_vector.head(10))


print(impact_vector.head(10))


# TODO: extraction doesn't seem to be included
# TODO: want to go through and make sense of what all these are
# TODO: could also compare the processing of nuclear fuel with production of elec by nuclear
# TODO: maybe try to find some nominal data ab extraction, figure out roughly how they did that piece and try to do it?
# TODO: try to visualize this all using matlib 
#could go down the whole rabbit hole of stressors, adding my own impacts etc.    
