import pymrio
import numpy

exio = pymrio.pymrio.parse_exiobase3('../data/external/IOT_2011_ixi')
exio = pymrio.load_all('../data/external/IOT_2011_ixi')
#either one or both of these meant i could use A





#combine these into a single thing
france_sectors = [s for s in exio.A.columns if 'FR' in s]
#use data wrangler to show rows
#a comprehension (aptly named)
nuclear_sectors = [sector for sector in france_sectors if 'nuclear' in sector[1].lower()]


direct_impact = exio.satellite.F[nuclear_sectors]
#so this is direct impaxt across all of the f matrix - all impacts

#get some code here to extract all zero values, only list those with values
non_zero_direct_impact = direct_impact[(direct_impact.iloc[:, 0] != 0) | (direct_impact.iloc[:, 1] != 0)]

#just adding across the columns here (so both sectors combined, for a given impact)
total_direct_impact = direct_impact.sum(axis=1).sort_values(ascending=False)

#extraction doesn't seem to be included
#want to go through and make sense of what all these are
#could also compare the processing of nuclear fuel with production of elec by nuclear
#maybe try to find some nominal data ab extraction, figure out roughly how they did that piece and try to do it?


#could go down the whole rabbit hole of stressors, adding my own impacts etc.
# iterate through rows of the dataframe
    

