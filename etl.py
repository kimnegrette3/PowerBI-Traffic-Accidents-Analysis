import pandas as pd
import numpy as np

def etl_homicidios():
    # Read datasets homicidios
    h_hechos = pd.read_excel('datasets/homicidios.xlsx', sheet_name='HECHOS', na_values=['SD','SD ''SD-SD', 'Point (. .)', '.', ''])
    h_victims = pd.read_excel('datasets/homicidios.xlsx', sheet_name='VICTIMAS', na_values=['SD', 'SD ','SD-SD'])

    #Drop unncesary columns
    h_hechos.drop(columns=['AAAA', 'MM', 'DD','HORA', 'LUGAR_DEL_HECHO', 'Altura', 'Cruce', 
                            'Dirección Normalizada', 'PARTICIPANTES','VICTIMA'], inplace=True)
    h_victims.drop(columns=['FECHA', 'AAAA', 'MM', 'DD', 'FECHA_FALLECIMIENTO'], inplace=True)

    # Rename columns
    h_hechos.rename(columns={'ID': 'siniestro_id','N_VICTIMAS':'num_victimas', 'FECHA':'fecha', 'HH':'hora', 'Calle':'calle', 
                            'COMUNA':'comuna', 'XY (CABA)': 'geocodificacion_caba', 'TIPO_DE_CALLE':'tipo_calle',
                            'pos x':'longitud', 'pos y':'latitud', 'VICTIMA':'vehiculo_victima', 'ACUSADO':'vehiculo_acusado'}, inplace=True)
    h_victims.rename(columns={'ID_hecho':'siniestro_id', 'ROL':'rol_victima', 'VICTIMA':'vehiculo_victima', 'SEXO':'sexo_victima', 
                                'EDAD': 'edad_victima'}, inplace=True)

    # Change to lowercase
    h_hechos = h_hechos.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    h_victims = h_victims.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    # Change 'ciclista' for 'conductor' in victims 'rol' column
    h_victims['rol_victima'] = h_victims['rol_victima'].apply(lambda x: 'conductor' if x == 'ciclista' else x)


    # Categorize the ages in the victims table
    bins = [0, 18, 29, 39, 49, 59, float('inf')]
    labels = ['menos de 18', 'entre 18 y 29', 'entre 30 y 39', 'entre 40 y 49', 'entre 50 y 59', '60 y mayores']
    h_victims['rango_etario'] = pd.cut(h_victims['edad_victima'], bins=bins, labels=labels, right=False)
    h_victims.drop(columns=['edad_victima'], inplace=True)

    # Add a column called 'gravedad' to differentiate from lesiones, once it's concatenated
    h_victims.insert(loc=5, column='gravedad', value='fatal')

    # Save to csv file
    h_hechos.to_csv('datasets/homicidios_hechos.csv', index=False)
    h_victims.to_csv('datasets/homicidios_victimas.csv', index=False)

    return f'The new csv files "homicidios_hechos.csv" and "homicidios_victimas.csv" were created and stored in datasets folder'


def etl_lesiones():
    # Read datasets lesiones
    l_hechos = pd.read_excel('datasets/lesiones.xlsx', sheet_name='HECHOS', na_values=['SD','SD ','SD-SD','sd', 'Point (. .)', '.', '', 'No especificada'])
    l_victims = pd.read_excel('datasets/lesiones.xlsx', sheet_name='VICTIMAS', na_values=['SD','SD ','sd', 'SD-SD', 'No especificada'])

    #Drop unncesary columns
    l_hechos.drop(columns=['aaaa', 'mm', 'dd','hora', 'direccion_normalizada', 'otra_direccion', 'altura', 'cruce', 
                            'participantes','victima', 'moto', 'auto', 'transporte_publico', 'camion', 'ciclista', 'gravedad'], inplace=True)
    l_victims.drop(columns=['FECHA ', 'AAA', 'MM', 'DD'], inplace=True)

    # Rename columns
    l_hechos.rename(columns={'id': 'siniestro_id','n_victimas':'num_victimas', 'franja_hora':'hora', 
                            'COMUNA':'comuna', 'geocodificacion_CABA': 'geocodificacion_caba', 'latutid':'latitud', 'acusado':'vehiculo_acusado'}, inplace=True)
    l_victims.rename(columns={'ID hecho':'siniestro_id', 'VEHICULO_VICTIMA':'vehiculo_victima', 'SEXO':'sexo_victima', 
                                'EDAD_VICTIMA': 'edad_victima', 'GRAVEDAD':'gravedad'}, inplace=True)

    # Change to lowercase
    l_hechos = l_hechos.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    l_victims = l_victims.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    # Change the dtype of edad_victima and fecha
    l_victims['edad_victima'] = l_victims['edad_victima'].astype('Int64')
    l_hechos['fecha'] = pd.to_datetime(l_hechos['fecha'], errors='coerce')

    # Replace the nulls in column gravedad with 'leve' as stated in the data dictionary
    l_victims['gravedad'].fillna('leve')

    # Categorize the ages in the victims table
    bins = [0, 18, 29, 39, 49, 59, float('inf')]
    labels = ['menos de 18', 'entre 18 y 29', 'entre 30 y 39', 'entre 40 y 49', 'entre 50 y 59', '60 y mayores']
    l_victims['rango_etario'] = pd.cut(l_victims['edad_victima'], bins=bins, labels=labels, right=False)
    l_victims.drop(columns=['edad_victima'], inplace=True)

    # Replace variable names in column sexo_victima to match homocidios
    l_victims['sexo_victima'] = l_victims['sexo_victima'].apply(lambda x: 'femenino' if x=='mujer' else ( 'masculino' if x=='varon' else x))

    # Rearrange columns order so it matches the ones in homicidios
    cols_l_hechos = list(l_hechos.columns)
    cols_l_hechos.insert(6, cols_l_hechos.pop(4))
    l_hechos = l_hechos[cols_l_hechos]

    cols_l_victims = list(l_victims.columns)
    cols_l_victims.insert(3,cols_l_victims.pop(4))
    l_victims = l_victims[cols_l_victims]
    l_victims.insert(loc=1, column='rol_victima', value=np.nan)

    # Save to csv file
    l_hechos.to_csv('datasets/lesiones_hechos.csv', index=False)
    l_victims.to_csv('datasets/lesiones_victimas.csv', index=False)

    return f'The new csv files "lesiones_hechos.csv" and "lesiones_victimas.csv" were created and stored in datasets folder'


etl_homicidios()
etl_lesiones()