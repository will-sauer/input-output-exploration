
#! imports

import pymrio
import numpy as np
import pandas as pd

#! constants

KG_KT = 1_000_000 #* 1000 kg / 1 kt
MEUR_EUR = 1 / 1_000_000 #* 1 meur / 1000000 eur
EUR_MEUR = 1_000_000 #* 1000000 eur / 1 meur

#! remove for colab
DATA_LOCATION = '../data/external/IOT_2011_ixi'

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

print("Now we pare this down for the purposes of investigting Polish coal sector...\n\n")


#! narrow down database-wide total intensity vector to only polish coal sector x coal impacts
#* grab names of polish coal sectors from technical coefficients matrix
polish_coal_sector_name = [
     sector for sector in exio.A.columns
     if 'pl' in sector[0].lower()
     and 'production of electricity by coal' in sector[1].lower()
 ]

print(f"Getting Polish coal sector name... {polish_coal_sector_name} \n\n")


#* filter total intensity vector down to just the polish coal sector (down to 1 column)
polish_coal_total_intensity_vector = total_intensity_vector_w_names[polish_coal_sector_name]

print(f"Now filtering total intensity vector for just those sectors... {polish_coal_total_intensity_vector}\n\n")


#* assemble names of coal impacts for filtering
#* pick the row names (the index) containing coal
coal_impact_names = [
    impact for impact in exio.satellite.F.index
    if 'coal' in impact.lower() and 'extraction' in impact.lower() and 
    ('bituminous' in impact.lower() or 'lignite' in impact.lower())
]

print(f"Getting coal impact names... {coal_impact_names}\n\n")


#* filter impacts of polish coal sector to only coal (down to two rows), then sum
polish_coal_total_intensity_vector_only_elec_coal = polish_coal_total_intensity_vector.loc[coal_impact_names]
polish_coal_total_intensity_vector_only_elec_coal_sum = polish_coal_total_intensity_vector_only_elec_coal.to_numpy().sum()

print(f"Now filtering total intensity vector for just those sectors... {polish_coal_total_intensity_vector_only_elec_coal}\n\n")
value = round(polish_coal_total_intensity_vector_only_elec_coal_sum,2)
print(f"This gives us total extraction of coal across both sectors of... {value} kt / M.EUR\n\n")

#! change total intensity from per kt extraction / M.EUR to kg extraction / kWh
print("Now change total intensity from per kt extraction / M.EUR to kg extraction / kWh\n\n")

#* get total polish coal elec output from 2011, iea lists as gwh, converted to kwh
#* source: https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=POLAND&energy=Electricity&year=2011
polish_coal_output_kwh = 141_571_000_000

value = round(polish_coal_output_kwh,2)
print(f"Polish coal output in kWh: {polish_coal_output_kwh}\n\n")

#* get the total output (leontief @ final demand) of *only* the production of electricity by coal sector
total_output = L @ Y
total_output_w_names = pd.Series(total_output, index=Y.index)

#* grab the row pertaining to polish coal electricity production from total output
polish_coal_total_output_meur = total_output_w_names[polish_coal_sector_name]

#* use above to get polish coal sector output in euros per kWh for conversion of total intensity vector
polish_coal_total_output_eur_kwh = polish_coal_total_output_meur / polish_coal_output_kwh * EUR_MEUR

#* change total intensity from kt extraction / M.EUR to kg extraction / kWh
polish_coal_extraction_intensity_kg_kwh = (
    polish_coal_total_intensity_vector_only_elec_coal_sum * KG_KT * MEUR_EUR * polish_coal_total_output_eur_kwh
)

print("Now we can calculate the extraction intensity of coal in the Polish coal sector in kg / kWh\n\n")
value = round(polish_coal_extraction_intensity_kg_kwh.values[0],2)
print(f"Final Output: Polish coal sector's extraction intensity: {value} kg / kWh\n\n")
