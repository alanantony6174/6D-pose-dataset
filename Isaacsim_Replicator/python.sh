#!/bin/bash

set -e

error_exit()
{
    echo "There was an error during script execution."
    # Added detail based on where the error might occur
    if [[ "$1" == "env_setup" ]]; then
        echo "Error likely occurred during environment setup (setup_python_env.sh)."
    elif [[ "$1" == "python_exec" ]]; then
        echo "Error likely occurred during python script execution."
    fi
    exit 1
}

# SCRIPT_DIR now refers to the location of *this* script (e.g., ~/Desktop/6D-Pose-Dataset/Isaacsim_Replicator)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# --- Isaac Sim Root Setup ---
# Check if ISAAC_SIM_ROOT is set
if [ -z "$ISAAC_SIM_ROOT" ]; then
  echo "Error: ISAAC_SIM_ROOT environment variable is not set."
  echo "Please set it to the root directory of your Isaac Sim installation before running this script."
  echo "Example: export ISAAC_SIM_ROOT=~/isaacsim"
  exit 1
fi

# Check if ISAAC_SIM_ROOT is a valid directory
if [ ! -d "$ISAAC_SIM_ROOT" ]; then
  echo "Error: ISAAC_SIM_ROOT points to a non-existent directory: $ISAAC_SIM_ROOT"
  exit 1
fi
echo "Using ISAAC_SIM_ROOT: $ISAAC_SIM_ROOT"
# --- End Isaac Sim Root Setup ---


# Setup python env by sourcing the MODIFIED setup script *from this directory*
# Pass potential errors back up using the return code check and error_exit
source "${SCRIPT_DIR}/setup_python_env.sh" || error_exit "env_setup"


# Set Carb/Isaac/Exp paths relative to the *actual* Isaac Sim installation
export CARB_APP_PATH=$ISAAC_SIM_ROOT/kit
export ISAAC_PATH=$ISAAC_SIM_ROOT
export EXP_PATH=$ISAAC_SIM_ROOT/apps


# Determine the python executable path relative to the *actual* Isaac Sim installation
# By default use our python, but allow overriding it by checking if PYTHONEXE env var is defined:
python_exe=${PYTHONEXE:-"${ISAAC_SIM_ROOT}/kit/python/bin/python3"}

# Check if the determined python executable exists
if [ ! -f "$python_exe" ]; then
    echo "Error: Python executable not found at expected location: $python_exe"
    echo "Check your ISAAC_SIM_ROOT or PYTHONEXE environment variable."
    exit 1
fi
echo "Using Python executable: $python_exe"


if ! [[ -z "${CONDA_PREFIX}" ]]; then
  echo "Warning: running in conda env, please deactivate before executing this script"
  echo "If conda is desired please source setup_conda_env.sh in your python 3.10 conda env and run python normally (not using this script)."
fi

# Check if we are running in a docker container (less relevant when running outside docker, but keep for consistency)
if [ -f /.dockerenv ]; then
  # Check for vulkan in docker container
  if [[ -f "${ISAAC_SIM_ROOT}/vulkan_check.sh" ]]; then
    echo "Running Vulkan check (inside docker)..."
    ${ISAAC_SIM_ROOT}/vulkan_check.sh
  fi
fi

# Show icon if not running headless
export RESOURCE_NAME="IsaacSim"

# Set LD_PRELOAD relative to the *actual* Isaac Sim installation
LD_PRELOAD_PATH="${ISAAC_SIM_ROOT}/kit/libcarb.so"
if [ ! -f "$LD_PRELOAD_PATH" ]; then
    echo "Error: libcarb.so not found at expected location: $LD_PRELOAD_PATH"
    echo "Check your ISAAC_SIM_ROOT environment variable."
    exit 1
fi
export LD_PRELOAD=$LD_PRELOAD_PATH
echo "Setting LD_PRELOAD: $LD_PRELOAD_PATH"


# Execute the python script passed as arguments
echo "Executing: $python_exe $@"
$python_exe "$@" || error_exit "python_exec"

echo "Script finished successfully."