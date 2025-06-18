#!/bin/bash -l
#SBATCH --job-name=predict_gpu
#SBATCH --nodes=1
#SBATCH --time=64:12:00
#SBATCH --mem=64G
#SBATCH --account=niwa00018
#SBATCH --partition=niwa_work
#SBATCH --cpus-per-task=15
#SBATCH --mail-user=neelesh.rampal@niwa.co.nz
#SBATCH --mail-type=ALL
#SBATCH --output log/%j-%x.out
#SBATCH --error log/%j-%x.out


module use /opt/nesi/modulefiles/
module unuse /opt/niwa/CS500_centos7_skl/modules/all
module unuse /opt/niwa/share/modules/all

export SYSTEM_STRING=CS500
export OS_ARCH_STRING=centos7
export CPUARCH_STRING=skl
#export PYTHONNOUSERSITE=/home/rampaln/.local/lib/python3.9/site-packages
export PYTHONUSERBASE=/nesi/project/niwa00018/rampaln/conda_tmp
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/rampaln/.local/lib/python3.9/site-packages
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64
### Note add a separate log folder that Maxime has outlined
module purge # optional
module load NIWA
module load gcc/9.3.0
module load CDO/1.9.5-GCC-7.1.0
module load Miniforge3
source activate ml_env
#module load Miniconda3/4.12.0

#conda activate ml_env

gcms=("ACCESS-CM2" "EC-Earth3" "NorESM2-MM")
#"ACCESS-CM2","CNRM-CM6-1" "AWI-CM-1-1-MR" "EC-Earth3" "GFDL-ESM4"
# Array of SSPs
ssps=("historical" "ssp370")
# Loop through each GCM
for gcm in "${gcms[@]}"; do
    # Loop through each SSP
    for ssp in "${ssps[@]}"; do
        # Construct the command
        command="/home/rampaln/.conda/envs/ml_env/bin/python get_ccam.py /nesi/project/niwa00018/gibsonp/run_ccam/post_processing/production_runs/CCAM_CMIP6/${ssp}/${gcm}/OUTPUT/Pacific_domain //nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/cordex_tf ${gcm}_${ssp}_CCAM_fixed.nc ${gcm} ${ssp}"

        # Execute the command
        echo "Running: $command"
        eval $command
    done
done

# original command
#python get_ccam.py /nesi/project/niwa00018/gibsonp/run_ccam/post_processing/production_runs/CCAM_CMIP6/ssp370/ACCESS-CM2/OUTPUT/Pacific_domain "/nesi/project/niwa00018/rampaln/get_ccam_data/post_processed_output/fixed_outputs" "ACCESS-CM2_ssp370_CCAM_fixed.nc"

