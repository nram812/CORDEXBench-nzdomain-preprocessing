import pandas as pd
import xarray as xr
import os
import pandas as pd

gcms = ['ACCESS-CM2', 'EC-Earth3']
ssps = ['historical', 'ssp370']

base_path = '/nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf'
target_base = '/nesi/project/niwa00018/rampaln/get_ccam_data/subset_ccam/output'
# target outputs
target_lat_extent = {'lat': slice(-47.6, -33.9, None), 'lon': slice(166, 179.75, None)}
out_base = os.path.join(base_path, 'ESD_datasets')

test_type = "perfect"
VAR_RENAME_DICT = {
    "ua": "u", "va": "v", "wa": "w",
    "hus": "q", "ta": "t", "zg": "z"
}
TARGET_VARS = ['tasmax', 'pr']
variables = ['u', 'v', 'q', 't', 'z']
levels = [850, 700, 500]

all_combinations = [f"{var}_{level}" for var in variables for level in levels]


def preprocess(df, remapping_dict=None):
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

def save(ds, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ds.to_netcdf(path)


def format_time(df, remove_leap =True):
    # Format time to YYYY-MM-DD
    df['time'] = pd.to_datetime(df.time.dt.strftime("%Y-%m-%d"))

    # Remove leap days (Feb 29)
    """Resampling adds another day into the fold"""
    if remove_leap:
        df = df.sel(time=~((df.time.dt.month == 2) & (df.time.dt.day == 29)))

    return df

def format_target(df):
    df = df[['pr','tasmax']]
    df['pr'] = df['pr'] * 86400
    return df

for gcm in gcms:
    target_dset = format_time(xr.open_dataset(f'{target_base}/{gcm}_hist_ssp370_pr_psl_tasmin_tasmax_sfcwind_sfcwindmax.nc'))
    target_dset = target_dset.sel(target_lat_extent)
    for ssp in ssps:
        print(f"Processing: {gcm} - {ssp}")
        predictor = format_time(xr.open_dataset(f'{base_path}/2_degree/{gcm}_{ssp}.nc'), remove_leap=False)
        predictor = preprocess(predictor)


        if ssp == 'historical':
            # ---- Pseudo-reality (predictors + target)
            predictor_psr = format_time(predictor.sel(time=slice("1961", "1980")).resample(time='1D').mean()[all_combinations])
            target_psr = format_target(target_dset).sel(time = predictor_psr.time)

            # remove lea

            if gcm == 'ACCESS-CM2':
                # Save predictors
                save(predictor_psr, f"{out_base}/train/pseudo_reality/predictors/{gcm}_1961-1980.nc")
                save(target_psr, f"{out_base}/train/pseudo_reality/target/pr_tasmax_{gcm}_1961-1980.nc")

            # ---- Historical test
            predictor_hist = format_time(predictor.sel(time=slice("1981", "2000")).resample(time='1D').mean()[all_combinations])
            target_hist = format_target(target_dset).sel(time= predictor_hist.time)
            save(predictor_hist, f"{out_base}/test/{test_type}/historical/predictors/{gcm}_1981-2000.nc")
            save(target_hist, f"{out_base}/test/{test_type}/historical/target/pr_tasmax_{gcm}_1981-2000.nc")

        elif ssp == 'ssp370':
            # ---- Mid-century
            predictor_mid = format_time(predictor.sel(time=slice("2041", "2060")).resample(time='1D').mean()[all_combinations])
            target_mid = format_target(target_dset).sel(time=predictor_mid .time)
            save(predictor_mid, f"{out_base}/test/{test_type}/mid_century/predictors/{gcm}_2041-2060.nc")
            save(target_mid, f"{out_base}/test/{test_type}/mid_century/target/pr_tasmax_{gcm}_2041-2060.nc")

            # ---- End-century
            predictor_end = format_time(predictor.sel(time=slice("2080", "2099")).resample(time='1D').mean()[all_combinations])
            target_end = format_target(target_dset).sel(time=predictor_end.time)
            save(predictor_end, f"{out_base}/test/{test_type}/end_century/predictors/{gcm}_2080-2099.nc")
            save(target_end, f"{out_base}/test/{test_type}/end_century/target/pr_tasmax_{gcm}_2080-2099.nc")

            # ---- Merged train (only for ACCESS-CM2)
            if gcm == 'ACCESS-CM2':
                predictor_hist_psr = xr.open_dataset(f"{out_base}/train/pseudo_reality/predictors/{gcm}_1961-1980.nc")[all_combinations]
                df_merged = xr.concat([predictor_hist_psr, predictor_end], dim='time')
                target_hist_psr = xr.open_dataset(f"{out_base}/train/pseudo_reality/target/pr_tasmax_{gcm}_1961-1980.nc")
                target_merged = xr.concat([target_hist_psr, target_end], dim='time')

                save(df_merged, f"{out_base}/train/merged/predictors/{gcm}_1961-1980_2080-2099.nc")

                save(target_merged, f"{out_base}/train/merged/target/pr_tasmax_{gcm}_1961-1980_2080-2099.nc")

"""Now for the imperfect data"""

gcms = ['ACCESS-CM2', 'EC-Earth3']
ssps = ['historical', 'ssp370']

base_path = '/nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf'
target_base = '/nesi/project/niwa00018/rampaln/get_ccam_data/subset_ccam/output'
# target outputs
target_lat_extent = {'lat': slice(-47.6, -33.9, None), 'lon': slice(166, 179.75, None)}
out_base = os.path.join(base_path, 'ESD_datasets')

test_type = "imperfect"
VAR_RENAME_DICT = {
    "ua": "u", "va": "v", "wa": "w",
    "hus": "q", "ta": "t", "zg": "z"
}
TARGET_VARS = ['tasmax', 'pr']
variables = ['u', 'v', 'q', 't', 'z']
levels = [850, 700, 500]

all_combinations = [f"{var}_{level}" for var in variables for level in levels]


def preprocess_imperfect(df, remapping_dict=None):
    if remapping_dict is None:
        remapping_dict = VAR_RENAME_DICT
    df = df.rename({"plev":"lev"})

    for var_name in list(df.data_vars):
        if var_name in remapping_dict.keys():
            for level in list(df.lev.values):
                df[f'{remapping_dict[var_name]}_{int(level/100)}'] = df[var_name].sel(lev=level)
            df = df.drop(var_name)
    try:
        df = df.drop("lev")
    except:
        pass
    return df

def save(ds, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ds.to_netcdf(path)


def format_time(df, remove_leap =True):
    # Format time to YYYY-MM-DD
    df['time'] = pd.to_datetime(df.time.dt.strftime("%Y-%m-%d"))

    # Remove leap days (Feb 29)
    """Resampling adds another day into the fold"""
    if remove_leap:
        df = df.sel(time=~((df.time.dt.month == 2) & (df.time.dt.day == 29)))

    return df

def format_target(df):
    df = df[['pr','tasmax']]
    df['pr'] = df['pr'] * 86400
    return df

for gcm in gcms:
    # target_dset = format_time(xr.open_dataset(f'{target_base}/{gcm}_hist_ssp370_pr_psl_tasmin_tasmax_sfcwind_sfcwindmax.nc'))
    # target_dset = target_dset.sel(target_lat_extent)
    for ssp in ssps:
        print(f"Processing: {gcm} - {ssp}")
        predictor = format_time(xr.open_dataset(f'{base_path}/2_degree_imperfect/{gcm}_{ssp}.nc'), remove_leap=True)
        predictor = preprocess_imperfect(predictor)


        if ssp == 'historical':
            # ---- Pseudo-reality (predictors + target)
            predictor_hist = format_time(predictor.sel(time=slice("1981", "2000"))[all_combinations])
            #target_hist = format_target(target_dset).sel(time= predictor_hist.time)
            save(predictor_hist, f"{out_base}/test/{test_type}/historical/predictors/{gcm}_1981-2000.nc")
            #save(target_hist, f"{out_base}/test/{test_type}/historical/target/pr_tasmax_{gcm}_1981-2000.nc")

        elif ssp == 'ssp370':
            # ---- Mid-century
            predictor_mid = format_time(predictor.sel(time=slice("2041", "2060"))[all_combinations])
            save(predictor_mid, f"{out_base}/test/{test_type}/mid_century/predictors/{gcm}_2041-2060.nc")
            # ---- End-century
            predictor_end = format_time(predictor.sel(time=slice("2080", "2099"))[all_combinations])
            save(predictor_end, f"{out_base}/test/{test_type}/end_century/predictors/{gcm}_2080-2099.nc")


# <output_base>/
# ├── train/
# │   ├── pseudo_reality/
# │   │   ├── predictors/
# │   │   │   └── ACCESS-CM2_1961-1980.nc
# │   │   └── target/
# │   │       ├── pr_ACCESS-CM2_1961-1980.nc
# │   │       └── tasmax_ACCESS-CM2_1961-1980.nc
# │   ├── merged/
# │   │   ├── predictors/
# │   │   │   └── ACCESS-CM2_1961-1980_2080-2099.nc
# │   │   └── target/
# │   │       ├── pr_ACCESS-CM2_1961-1980_2080-2099.nc
# │   │       └── tasmax_ACCESS-CM2_1961-1980_2080-2099.nc
# ├── test/
# │   └── perfect/
# │       ├── historical/
# │       │   ├── predictors/
# │       │   │   ├── ACCESS-CM2_1981-2000.nc
# │       │   │   └── EC-Earth3_1981-2000.nc
# │       │   └── target/
# │       │       ├── pr_ACCESS-CM2_1981-2000.nc
# │       │       └── tasmax_ACCESS-CM2_1981-2000.nc
# │       ├── mid_century/
# │       │   ├── predictors/
# │       │   └── target/
# │       └── end_century/
# │           ├── predictors/
# │           └── target/


###
# <xarray.Dataset>
# Dimensions:    (time: 31411, bnds: 2, lon: 16, lat: 16, plev: 5)
# Coordinates:
#   * time       (time) datetime64[ns] 2015-01-01T12:00:00 ... 2100-12-31T12:00:00
#   * lon        (lon) float64 157.5 159.5 161.5 163.5 ... 181.5 183.5 185.5 187.5
#   * lat        (lat) float64 -55.5 -53.5 -51.5 -49.5 ... -31.5 -29.5 -27.5 -25.5
#   * plev       (plev) float64 1e+05 8.5e+04 7e+04 5e+04 2.5e+04
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
time =12
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=171.77)})

# Plot background tasmax
df.isel(time=time).tasmax.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap='YlOrRd',
    cbar_kwargs={'label': 'Max Temperature (°C)'}
)

# Optional: overlay contour of u_850 (if still needed)
# df_pred.isel(time=0).u_850.plot.contour(
#     ax=ax,
#     transform=ccrs.PlateCarree(),
#     colors='k',
#     linewidths=0.5
# )

# Extract u and v wind components at 850 hPa
u = df_pred.isel(time=time).u_850
v = df_pred.isel(time=time).v_850

# Subsample for clarity (adjust step if needed)
step = 1
ax.quiver(
    u.lon.values[::step],
    u.lat.values[::step],
    u.values[::step, ::step],
    v.values[::step, ::step],
    transform=ccrs.PlateCarree(),
    scale=200,
    width=0.005,
    color='black'
)

ax.coastlines()
ax.set_title('850 hPa Wind Vectors and Surface Max Temperature')
fig.savefig('/nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf/ESD_datasets/image_example.png', dpi =500, bbox_inches ='tight')
fig.show()