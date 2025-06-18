# Standard library imports
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from subprocess import call
from tqdm import tqdm
# Third party imports
import xarray as xr
from dask.diagnostics import ProgressBar

# Defining constants
TARGET_PRESSURE_LEVELS = '1000,850,700,500,250'
WEIGHTS_FILE = 'weights.nc'
INPUT_PATH = sys.argv[-5]
OUTPUT_PATH = sys.argv[-4]
OUTPUT_fname = sys.argv[-3]
ssp = sys.argv[-1]
gcm = sys.argv[-2]

print(INPUT_PATH)
# Defining a dictionary to rename variables
VAR_RENAME_DICT = {
    "ua": "u",
    "va": "v",
    "wa": "w",
    "hus": "q",
    "ta": "t",
    "zg": "z"
}


def process_file(file):
    """
    Process a NetCDF file with CDO.

    :param file: path of the file to process  # <--- Fix is here!
    :return: path of the processed file
    """
    fname = f'{OUTPUT_PATH}' +f'/{gcm}_{ssp}' + f'/{file.split("/")[-1]}'
    print(fname)
    if not os.path.exists(fname):
        arg = f'cdo -L -selname,ua,va,wa,ta,hus,zg -intlevel,{TARGET_PRESSURE_LEVELS} -remapcon,new_grid_pacific_2.csv {file} {fname}'
        call(arg, shell=True)
    return fname



os.chdir(r'/nesi/project/niwa00018/rampaln/get_ccam_data')
# Generate interpolation weights if they don't exist
files_to_process = glob.glob(f'{INPUT_PATH}/*.nc')
print(files_to_process,"files")
# arg = f'cdo genbil,target_grid_pacific.csv {files_to_process[0]} {WEIGHTS_FILE}'
# call(arg, shell=True)

# Process NetCDF files in parallel using CDO
with ProcessPoolExecutor(max_workers=30) as executor:

    print(files_to_process)
    result_files = list(tqdm(executor.map(process_file, files_to_process), total=len(files_to_process)))

