import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dedupe
import csv
import re
import unicodedata
import IPython
import pathlib
import rapidfuzz
from pathlib import Path
from IPython.display import display, Markdown
from rapidfuzz import fuzz, process
from itertools import combinations

display(Markdown("### VERSIONES DE LIBRERIAS"))
print(f"Python: {sys.version.split()[0]}")
print(f"pandas: {pd.__version__}")
print(f"numpy: {np.__version__}")
print(f"matplotlib: {plt.matplotlib.__version__}")
print(f"seaborn: {sns.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"IPython: {IPython.__version__}")
print(f"rapidfuzz versión: {rapidfuzz.__version__}")

""" 
Normalización de códigos de barra
Convierte código de barras a string y elimina ceros al inicio
"""
def barcode_normalization(code):
    if pd.isna(code): # Evalua si está vacío
        return None
    code = str(code).strip()
    try:
        # Esto elimina ceros al inicio automáticamente
        code = str(int(float(code)))
    except:
        pass
    return code

"""
Función para detectar string vacíos y valores nulos
"""
def diagnose_missing(df, column, description="valores"):
    missing = df[column].isna() | df[column].astype(str).str.contains(r'^\s*$', na=False)
    total_missing = missing.sum()
    total_present = len(df) - total_missing
    # Conteo de valores únicos
    frecuency = df[~missing][column].value_counts()
    
    display(Markdown("#### Diagnóstico"))
    print(f"Total de productos: {len(df)}")
    print(f"Con {description}: {total_present} ({total_present/len(df)*100:.2f}%)")
    print(f"Sin {description}: {total_missing} ({total_missing/len(df)*100:.2f}%)")
    
    display(Markdown("#### Estadísticas"))
    print(f"Total de {description} con valores únicos: {len(frecuency)}")
    print(f"{description} más frecuente: {frecuency.index[0]} ({frecuency.iloc[0]} productos)")
    print(f"{description} menos frecuente: {frecuency.index[-1]} ({frecuency.iloc[-1]} productos)")

    # Marcas que aparecen solo una vez
    single_product_register = frecuency[frecuency == 1]
    print(f"{description} con un solo producto: {len(single_product_register)} ({len(single_product_register)/len(frecuency)*100:.2f}% del total)")

    return missing

"""

"""
def prepare_data_and_diagnose(
    df_odoo_copy,                    # DataFrame original de Odoo
    df_int_copy,                     # DataFrame original de Interfuerza
    target_column,              # Columna a diagnosticar ('seller_ids' o 'x_studio_...')
    entity_name,                # 'proveedores' o 'marcas'
    int_code_col,               # Columna de código en Interfuerza ('UPC Code')
    int_entity_col,             # Columna de entidad en Interfuerza ('Proveedor Principal' o 'Marca')
    id_col='id'                 # Columna de ID en Odoo (opcional)
):
    """
    Prepara datos, normaliza códigos, diagnostica valores faltantes y crea diccionario.
    
    Retorna:
    - df_odoo_copy: DataFrame de Odoo procesado
    - df_int_copy: DataFrame de Interfuerza procesado
    - missing_mask: máscara de valores faltantes
    - entity_dict: diccionario código → lista de entidades
    """
    
    # 1. Normalización de códigos de barras
    display(Markdown("### Normalización de códigos"))
    df_odoo_copy['barcode_norm'] = df_odoo_copy['barcode'].apply(barcode_normalization)
    df_int_copy['barcode_norm'] = df_int_copy[int_code_col].apply(barcode_normalization)
    
    # 2. Mostrar muestras de normalización
    display(Markdown("#### Muestras de códigos normalizados"))
    overview = pd.DataFrame({
        'original_odoo': df_odoo_copy['barcode'].head(5),
        'normalizado_odoo': df_odoo_copy['barcode_norm'].head(5),
        'original_int': df_int_copy[int_code_col].head(5),
        'normalizado_int': df_int_copy['barcode_norm'].head(5)
    })
    display(overview)
    
    # 3. Diagnóstico inicial
    display(Markdown("### Diagnóstico inicial"))
    missing_mask = diagnose_missing(df_odoo_copy, target_column, entity_name)
    
    # 4. Creación de diccionario (código → lista de entidades)
    df_int_entities = df_int_copy.dropna(subset=['barcode_norm', int_entity_col])
    entity_dict = df_int_entities.groupby('barcode_norm')[int_entity_col].apply(list).to_dict()
    
    display(Markdown(f"##### Creación de diccionario código-{entity_name}"))
    print(f"Mapa creado con {len(entity_dict)} códigos de barras únicos")
    
    return df_odoo_copy, df_int_copy, missing_mask, entity_dict, df_int_entities

"""
Analiza y visualiza códigos con múltiples entidades (marcas/proveedores)
"""
def analyze_multiple_entities(df, code_col, entity_col, entity_name, output_path=None):
    """
    Parámetros:
    - df: DataFrame de Interfuerza
    - code_col: nombre de la columna de código (ej: 'barcode_norm')
    - entity_col: nombre de la columna de entidad (ej: 'Marca' o 'Proveedor Principal')
    - entity_name: nombre legible (ej: 'marcas', 'proveedores')
    - output_path: ruta para guardar CSV (opcional)
    """
    unique_counts = df.groupby(code_col)[entity_col].nunique()
    codes_with_multiple = unique_counts[unique_counts > 1]
    
    display(Markdown(f"#### Análisis de múltiples {entity_name} por código de barras"))
    display(Markdown("\n ##### Estadísticas generales"))
    print(f"Total registros en Interfuerza: {len(df):,}")
    print(f"Total códigos de barras únicos: {len(unique_counts):,}")
    print(f"Códigos con múltiples {entity_name}: {len(codes_with_multiple):,}")
    
    if len(unique_counts) > 0:
        print(f"Porcentaje del total: {len(codes_with_multiple)/len(unique_counts)*100:.2f}%")
    
    display(Markdown("\n ##### Distribución de multiplicidad"))
    print(f"Códigos con 2 {entity_name} diferentes: {(codes_with_multiple == 2).sum()}")
    print(f"Códigos con 3 {entity_name} diferentes: {(codes_with_multiple == 3).sum()}")
    print(f"Códigos con 4+ {entity_name} diferentes: {(codes_with_multiple >= 4).sum()}")
    
    if len(codes_with_multiple) > 0:
        display(Markdown(f"#### Muestra de códigos con múltiples {entity_name}"))
        filtered_data = df[df[code_col].isin(codes_with_multiple.index)]
        df_grouped = filtered_data.groupby(code_col)[entity_col].agg(list).reset_index()
        display(df_grouped.head(10))
        
        if output_path:
            df_grouped.to_csv(output_path, index=False)
            print(f"Archivo '{entity_name.capitalize()}.csv' generado")
    else:
        print(f"\nNo hay códigos con múltiples {entity_name}")
    
    return codes_with_multiple, df_grouped

# Función para asignación de entidades a productos
def assign_entities_to_products(
    df_products,           # DataFrame de productos (Odoo)
    missing_mask,          # Máscara de productos sin la entidad
    codes_to_exclude,      # Códigos a excluir (con múltiples entidades)
    entity_dict,           # Diccionario código → entidad(es)
    entity_name,           # Nombre legible ('marca', 'proveedor')
    id_col,                # Nombre de columna de ID ('id')
    target_col,            # Nombre de columna destino en Odoo
    output_path            # Ruta para guardar CSV
):
    """
    Asigna entidades (marcas/proveedores) a productos faltantes.
    
    Parámetros:
    - df_products: DataFrame con productos
    - missing_mask: máscara booleana (True = sin entidad)
    - codes_to_exclude: códigos a excluir (ej: con múltiples entidades)
    - entity_dict: diccionario {código: entidad}
    - entity_name: 'marca' o 'proveedor' (para textos)
    - id_col: nombre de columna de ID ('id')
    - target_col: nombre del campo en Odoo
    - output_path: ruta para guardar CSV
    
    Retorna:
    - df_import: DataFrame listo para importar
    - df_pending: DataFrame con pendientes
    """
    
    # 1. Filtrar productos sin la entidad
    df_missing = df_products[missing_mask].copy()
    
    # 2. Excluir códigos conflictivos
    if codes_to_exclude is not None and len(codes_to_exclude) > 0:
        df_missing = df_missing[~df_missing['barcode_norm'].isin(codes_to_exclude.index)]
    
    # 3. Mostrar estadísticas
    display(Markdown(f"#### Asignación de productos sin {entity_name}"))
    print(f"Productos sin {entity_name} (excluyendo conflictivos): {len(df_missing)}")
    
    # 4. Aplicar mapa de entidades
    df_missing['entidad_asignada'] = df_missing['barcode_norm'].map(entity_dict)
    
    # 5. Calcular resolución
    assigned = df_missing['entidad_asignada'].notna().sum()
    total_pendings = len(df_missing) - assigned
    pendings = df_missing[df_missing['entidad_asignada'].isna()]
    
    print(f"✅ Resueltos automáticamente: {assigned} ({assigned/len(df_missing)*100:.1f}%)")
    print(f"❌ Pendientes (sin coincidencia): {total_pendings} ({total_pendings/len(df_missing)*100:.1f}%)\n")
    
    # 6. Mostrar pendientes
    if total_pendings > 0:
        display(Markdown(f"\n#### MUESTRA DE PRODUCTOS SIN {entity_name.upper()} PENDIENTES"))
        display(pendings.head(10))
    
    # 7. Preparar archivo para importar
    df_import = df_missing[df_missing['entidad_asignada'].notna()].copy()
    df_import = df_import[[id_col, 'entidad_asignada']]
    df_import.columns = [id_col, target_col]
    
    # 8. Guardar CSV
    df_import.to_csv(output_path, index=False)
    display(Markdown(f"##### Archivo '{output_path.name}' generado"))
    print(f"Contiene {len(df_import)} productos para actualizar")
    
    return df_import, pendings