import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dedupe
import csv
import IPython
from IPython.display import display, Markdown

print("="*50)
print("VERSIONES DE LIBRERÍAS")
print("="*50)
print(f"Python: {sys.version.split()[0]}")
print(f"pandas: {pd.__version__}")
print(f"numpy: {np.__version__}")
print(f"matplotlib: {plt.matplotlib.__version__}")
print(f"seaborn: {sns.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"IPython: {IPython.__version__}")

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
