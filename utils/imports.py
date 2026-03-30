import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dedupe
import csv
import IPython
from IPython.display import display, Markdown

# ============================================
# IMPRESIÓN DE VERSIONES
# ============================================

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
