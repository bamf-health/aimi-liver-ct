# Liver CT Segmentation

This project trains an nnUNet model to segment liver from CT scans. The model was trained on a dataset of 1565 CT scans from [TotalSegmentator](https://github.com/wasserth/TotalSegmentator/) (N=1204) and [FLARE21](https://flare.grand-challenge.org/) (N=361) datasets. The model is used to generate annotations for liver in 89 CT scans from [TCGA-LIHC](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=6885436) collection.

The [model_performance](model_performance.ipynb) notebook contains the code to evaluate the model performance on the TCGA-LIHC collection against a validation evaluated by a radiologist and a non-expert.

## Running the model

The pretrained model weights are available online. The simpliest way to use the model is to build and run the docker container.

### Build container from pretrained weights

```bash
cd {REPO_DIR}/container
docker build -t bamf_liver_ct:latest .
```

### Running inference

By default the container takes an input directory that contains DICOM files of CT scans, and an output directory where DICOM-SEG files will be placed. To run on multiple scans, place DICOM files for each scan in a separate folder within the input directory. The output directory will have a folder for each input scan, with the DICOM-SEG file inside.

example:

```bash
docker run --gpus all -v /path/to/input/dicoms:/data/input -v /path/for/output/dicoms:/data/output bamf_liver_ct:latest
```

There is an optional `--nifti` flag that will take nifti files as input and output.

#### Run inference on IDC Collections

TODO

#### Run inference on Medical Decathlon

Task 03 of the [Medical Segmentation Decathlon](http://medicaldecathlon.com/) is to segment liver and liver tumors from CT scans. We can use this dataset to evaluate our model.

1. Download and extract Task03_Liver from the [Medical Segmentation Decathlon](http://medicaldecathlon.com/). You should have a folder structure of `{MSD_DIR}/Task03_Liver/imagesTr` and `{MSD_DIR}/Task03_Liver/labelsTr`.
2. Run the container with the following command, add the `--nifti` flag since inputs and outputs are nifti files.

```bash
docker run --gpus all -v ${MSD_DIR}/Task03_Liver/imagesTr:/data/input -v ${MSD_DIR}/Task03_Liver/predTr:/data/output bamf_liver_ct:latest --nifti
```

### Training your own weights

#### Download training datasets

1. Download and extract the [TotalSegmentator dataset](https://doi.org/10.5281/zenodo.6802613) to `./training_data/total_segmentator` folder.

2. Download and extract the [FLARE21 training dataset](https://zenodo.org/record/5903672) to `./training_data/flare21` folder. You should have a `./training_data/flare21/TrainingImg` folder and `./training_data/flare21/TrainingMask` folder.

#### Setup nnUNet environment

1. Create a folder `./nnunet_data/nnUNet_raw_data_base`
2. Create a folder `./nnunet_data/nnUNet_preprocessed`
3. Create a folder `./nnunet_data/nnUNet_trained_nmodels`
4. Run `create_nnunet_dataset.ipynb` to setup the nnUnet dataset

#### Train model

1. setup environtmnent variables

```
export nnUNet_raw_data_base="./nnunet_data/nnUNet_raw_data_base"
export nnUNet_preprocessed="./nnunet_data/nnUNet_preprocessed"
export RESULTS_FOLDER="./nnunet_data/nnUNet_trained_models"
```

2. Run plan and preprocess `nnUNet_plan_and_preprocess -t 773 --verify_dataset_integrity`
3. Train folds 0-4, you can use the `train.sh` script. Specify the fold with the first arg, and the gpu to train on with the second arg

##### Fixing Total Segmentator dataset

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

#### Using your model weights

You can use [nnUNet_predict](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1#run-inference) with your existing nnUNet envirionment. To convert use DICOM as input, or as output, refer to the `container/run.py` script for an example.
