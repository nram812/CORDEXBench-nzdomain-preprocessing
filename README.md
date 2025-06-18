---

# Processing Data for CORDEX-Bench NZ

This repository provides scripts for processing datasets used in the CORDEX-Bench NZ benchmarking framework. It includes workflows for handling:

* **Perfect data**: Coarsened Regional Climate Model (RCM) output (regridded to 2° resolution)
* **Imperfect data**: Raw Global Climate Model (GCM) output

⚠️ *Note: This is a rough draft and may not be fully reproducible yet. Improvements welcome!*

---

## Folder Structure

There are two main subdirectories:

* `process_perfect/`: Processes high-resolution RCM output.
* `process_imperfect/`: Processes raw GCM output.

---

## Processing Perfect Data (`./process_perfect`)

This workflow processes high-resolution (12 km) CCAM RCM output and uses conservative remapping to coarsen it to a 2°×2° grid, as specified in `new_grid_pacific_2.csv`.

> **Note**: This step is only for predictor variables (e.g., pressure-level variables). Ground truth surface fields have already been processed.

### Steps

1. **Regrid Pressure-Level Data**

   Submit the following SLURM job:

   ```bash
   sbatch submit_job.sl
   ```

   This regrids 6-hourly RCM output (e.g., `u`, `v`, `q`, `t`, `z`) to the target grid. Refer to `submit_job.sl` and `get_ccam.py` for details.

2. **Merge and Average**

   After regridding, compute daily averages and merge variables:

   ```bash
   sbatch process_interp.sl
   ```

   This job runs `process_interp_script.py`, which combines all variables into unified NetCDF files.

---

## Processing Imperfect Data (`./process_imperfect`)

This pipeline handles raw GCM output.

### Step 1: Download GCM Data

Download the required CMIP6 GCM data from ESGF:

> [https://esgf-node.ipsl.upmc.fr/search/cmip6-ipsl/](https://esgf-node.ipsl.upmc.fr/search/cmip6-ipsl/)

For help with download scripts, refer to:

> [https://github.com/nram812/Downscaling-with-AI-reveals-large-role-of-internal-variability-in-fine-scale-projections](https://github.com/nram812/Downscaling-with-AI-reveals-large-role-of-internal-variability-in-fine-scale-projections)

Ensure files are downloaded using the standard CMIP6 directory structure, e.g.:

```
/CMIP6/CMIP/<institution_id>/<model_id>/<experiment_id>/...
```

### Step 2: Regrid and Merge

To process the downloaded files:

```bash
sbatch process_mass.sl
```

This script:

* Regrids each GCM file using conservative remapping
* Merges all time slices and variables
* Outputs one NetCDF file per GCM and scenario
* Automatically deletes temporary files

---

## Final Step: Prepare Training Files

Once both perfect and imperfect datasets are processed, run:

```bash
python process_files.py
```

This script organizes the regridded data into training-ready directories.

---
