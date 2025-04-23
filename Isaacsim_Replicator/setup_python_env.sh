#!/bin/bash
# MODIFIED: This script now relies on the ISAAC_SIM_ROOT environment variable
#           being set to the root directory of the Isaac Sim installation.

# SCRIPT_DIR is no longer needed here as we use ISAAC_SIM_ROOT

if [ -z "$ISAAC_SIM_ROOT" ]; then
  echo "Error: ISAAC_SIM_ROOT environment variable is not set."
  echo "Please set it to the root directory of your Isaac Sim installation."
  echo "Example: export ISAAC_SIM_ROOT=~/isaacsim"
  return 1 # Use return instead of exit as this script is sourced
fi

# Check if ISAAC_SIM_ROOT is a valid directory
if [ ! -d "$ISAAC_SIM_ROOT" ]; then
  echo "Error: ISAAC_SIM_ROOT points to a non-existent directory: $ISAAC_SIM_ROOT"
  return 1
fi

# Construct PYTHONPATH using ISAAC_SIM_ROOT
# Appending existing PYTHONPATH at the end
export PYTHONPATH=${ISAAC_SIM_ROOT}/kit/python/lib/python3.10:${ISAAC_SIM_ROOT}/kit/python/lib/python3.10/site-packages:${ISAAC_SIM_ROOT}/python_packages:${ISAAC_SIM_ROOT}/exts/isaacsim.simulation_app:${ISAAC_SIM_ROOT}/extsDeprecated/omni.isaac.kit:${ISAAC_SIM_ROOT}/kit/kernel/py:${ISAAC_SIM_ROOT}/kit/plugins/bindings-python:${ISAAC_SIM_ROOT}/exts/isaacsim.robot_motion.lula/pip_prebundle:${ISAAC_SIM_ROOT}/exts/isaacsim.asset.exporter.urdf/pip_prebundle:${ISAAC_SIM_ROOT}/extscache/omni.kit.pip_archive-0.0.0+d02c707b.lx64.cp310/pip_prebundle:${ISAAC_SIM_ROOT}/exts/omni.isaac.core_archive/pip_prebundle:${ISAAC_SIM_ROOT}/exts/omni.isaac.ml_archive/pip_prebundle:${ISAAC_SIM_ROOT}/exts/omni.pip.compute/pip_prebundle:${ISAAC_SIM_ROOT}/exts/omni.pip.cloud/pip_prebundle${PYTHONPATH:+:${PYTHONPATH}}

# Construct LD_LIBRARY_PATH using ISAAC_SIM_ROOT
# Appending existing LD_LIBRARY_PATH at the end
export LD_LIBRARY_PATH=${ISAAC_SIM_ROOT}/.:${ISAAC_SIM_ROOT}/exts/omni.usd.schema.isaac/plugins/IsaacSensorSchema/lib:${ISAAC_SIM_ROOT}/exts/omni.usd.schema.isaac/plugins/RangeSensorSchema/lib:${ISAAC_SIM_ROOT}/exts/isaacsim.robot_motion.lula/pip_prebundle:${ISAAC_SIM_ROOT}/exts/isaacsim.asset.exporter.urdf/pip_prebundle:${ISAAC_SIM_ROOT}/kit:${ISAAC_SIM_ROOT}/kit/kernel/plugins:${ISAAC_SIM_ROOT}/kit/libs/iray:${ISAAC_SIM_ROOT}/kit/plugins:${ISAAC_SIM_ROOT}/kit/plugins/bindings-python:${ISAAC_SIM_ROOT}/kit/plugins/carb_gfx:${ISAAC_SIM_ROOT}/kit/plugins/rtx:${ISAAC_SIM_ROOT}/kit/plugins/gpu.foundation${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

# Add return 0 for successful sourcing
return 0