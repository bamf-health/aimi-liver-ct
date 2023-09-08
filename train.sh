#!/bin/bash

FOLD=${1:-0}
GPU=${2:-0}


echo "Training Fold $FOLD on gpu $GPU"

# Setup nnunet env vars
export nnUNet_raw_data_base="./nnunet_data/nnUNet_raw_data_base"
export nnUNet_preprocessed="./nnunet_data/nnUNet_preprocessed"
export RESULTS_FOLDER="./nnunet_data/nnUNet_trained_models"

# select gpu
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=$GPU

nnUNet_train 3d_fullres nnUNetTrainerV2 Task773_Liver $FOLD "${@:23}"
