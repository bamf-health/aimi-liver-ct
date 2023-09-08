## Training Methodology

The liver annotations from totalsegmentator (N=1204) and FLARE21 (N=361) dataset is employed to train a model for liver segmentation. The dataset includes 1,565 cases with annotated CT scans. An ensemble of fivefold cross-validation within the nnUNet framework is used for automatic nodule segmentation. The model is used to generate annotations for liver in 89 CT scans from TCGA-LIHC collection.

## Training instructions

### Download training datasets

1. Download and extract the [TotalSegmentator dataset](https://doi.org/10.5281/zenodo.6802613) to `./training_data/total_segmentator` folder.

2. Download and extract the [FLARE21 training dataset](https://zenodo.org/record/5903672) to `./training_data/flare21` folder. You should have a `./training_data/flare21/TrainingImg` folder and `./training_data/flare21/TrainingMask` folder.

### Setup nnUNet environment

1. Create a folder `./nnunet_data/nnUNet_raw_data_base`
2. Create a folder `./nnunet_data/nnUNet_preprocessed`
3. Create a folder `./nnunet_data/nnUNet_trained_nmodels`
4. Run `create_nnunet_dataset.ipynb` to setup the nnUnet dataset

### Train model

1. setup environtmnent variables

```
export nnUNet_raw_data_base="./nnunet_data/nnUNet_raw_data_base"
export nnUNet_preprocessed="./nnunet_data/nnUNet_preprocessed"
export RESULTS_FOLDER="./nnunet_data/nnUNet_trained_models"
```

2. Run plan and preprocess `nnUNet_plan_and_preprocess -t 773 --verify_dataset_integrity`
3. Train folds 0-4, you can use the `train.sh` script. Specify the fold with the first arg, and the gpu to train on with the second arg

#### Fixing Total Segmentator dataset

If you get errors like
`ITK ERROR: ITK only supports orthonormal direction cosines.  No orthonormal definition found!`

The first option is to install `SimpleITK=2.0.2`, however if you are using python >3.7, that version of SimpleITK is not available. The second option is to fix the dataset, using the steps below.

1. build the docker image

```
docker build -t fix_total_segmentator:latest ./TotalSegFix
```

2. run the docker image

```
docker run --rm -v $(pwd)/training_data/total_segmentator:/data -v $(pwd)/training_data/total_segmentator_fix:/out_data  -u $(id -u ${USER}):$(id -g ${USER}) fix_total_segmentator:latest
```

3. copy the fixed dataset back to the training_data folder, or used new `training_data/total_segmentator_fix` instead of `training_data/total_segmentator` in the training instructions above.
