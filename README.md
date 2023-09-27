# Liver CT Segmentation

This project trains an nnUNet model to segment liver from CT scans. The model was trained on a dataset of 1565 CT scans from [TotalSegmentator](https://github.com/wasserth/TotalSegmentator/) (N=1204) and [FLARE21](https://flare.grand-challenge.org/) (N=361) datasets. The model is used to generate annotations for liver in 89 CT scans from [TCGA-LIHC](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=6885436) collection.

The [model_performance](model_performance.ipynb) notebook contains the code to evaluate the model performance on the TCGA-LIHC collection against a validation evaluated by a radiologist and a non-expert.

## Running the model

The pretrained model weights are [available at zenodo](https://doi.org/10.5281/zenodo.8270230). The simpliest way to use the model is to build and run the docker container.

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
This model was run on CT scans from the TCGA-LIHC collection. The AI segmentations and corrections by a radioloist for 10% of the dataset are available in the liver-ct.zip file on the [zenodo record](https://doi.org/10.5281/zenodo.8345959).

- [ ] TODO: add notebook for downloading & running model on idc collections

#### Run inference on Medical Decathlon

Task 03 of the [Medical Segmentation Decathlon](http://medicaldecathlon.com/) is to segment liver and liver tumors from CT scans. We can use this dataset to evaluate our model.

1. Download and extract Task03_Liver from the [Medical Segmentation Decathlon](http://medicaldecathlon.com/). You should have a folder structure of `{MSD_DIR}/Task03_Liver/imagesTr` and `{MSD_DIR}/Task03_Liver/labelsTr`.
2. Run the container with the following command, add the `--nifti` flag since inputs and outputs are nifti files.

```bash
docker run --gpus all -v ${MSD_DIR}/Task03_Liver/imagesTr:/data/input -v ${MSD_DIR}/Task03_Liver/predTr:/data/output bamf_liver_ct:latest --nifti
```

### Training your own weights

Refer to the [training instructions](training.md) for more details.
