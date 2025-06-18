
import xarray as xr

# Suppress all warnings
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
from dask.diagnostics import ProgressBar
from concurrent.futures import ProcessPoolExecutor
from subprocess import call
from tqdm import tqdm


base_dirs = r'//nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf'
gcm_dirs = os.listdir(base_dirs)


def process_file(gcm, input_path = base_dirs):
    """
    Process a NetCDF file with CDO.

    :param file: path of the file to process
    :return: path of the processed file
    """
    if not os.path.exists(f'{input_path}/{gcm}.nc'):
        arg = f'cdo -L -mergetime -daymean {input_path}/{gcm}/*.nc {input_path}/{gcm}.nc'
        call(arg, shell=True)
        #arg2 = f'cdo daymean {input_path}/{gcm}.nc {input_path}/{gcm}.nc'
        #call(arg2, shell=True)
    return f'{input_path}/{gcm}.nc'


def preprocess(df, remapping_dict=None):
    """
    Rename variables and restructure dataset for downscaling.

    :param df: input xarray Dataset
    :param remapping_dict: dictionary for variable renaming
    :return: preprocessed xarray Dataset
    """
    if remapping_dict is None:
        remapping_dict = VAR_RENAME_DICT

    for var_name in list(df.data_vars):
        if var_name in remapping_dict.keys():
            for level in list(df.lev.values):
                df[f'{remapping_dict[var_name]}_{int(level)}'] = df[var_name].sel(lev=level)
            df = df.drop(var_name)
    try:
        df = df.drop("lev")
    except:
        pass

    return df

print("jere")
VAR_RENAME_DICT = {
    "ua": "u",
    "va": "v",
    "wa": "w",
    "hus": "q",
    "ta": "t",
    "zg":"z"
}
with ProcessPoolExecutor(max_workers=30) as executor:

    print(gcm_dirs)
    result_files = list(tqdm(executor.map(process_file,gcm_dirs), total=len(gcm_dirs)))
    import glob
    files = glob.glob(r'//nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf/1_5_degree/*.nc')
    #file =
    result_files = files
    for file in result_files:
        df = xr.open_dataset(file)
        df = preprocess(df,VAR_RENAME_DICT)
        df.to_netcdf(file[:-3] +'updated.nc')
        os.remove(file)