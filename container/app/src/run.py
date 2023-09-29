#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import SimpleITK as sitk
import pydicom
import numpy as np


def find_input_series(dicom_dir: Path):
    series_dirs = {
        x.parent
        for x in dicom_dir.rglob("*")
        if x.is_file() and pydicom.misc.is_dicom(str(x))
    }

    return series_dirs


def convert_dcm_to_nii(in_series_dir: Path, out_file: Path) -> bool:
    with TemporaryDirectory() as tmpdir:
        args = [
            "dcm2niix",
            "-o",
            tmpdir,
            "-z",
            "y",
            str(in_series_dir.resolve()),
        ]
        res = subprocess.run(args)
        if res.returncode != 0:
            return False

        out_file.parent.mkdir(parents=True, exist_ok=True)

        nii_files = list(Path(tmpdir).glob("*Eq_*.nii.gz"))
        if len(nii_files) > 1:
            # raise ValueError(f"Expected 1 Eq_*.nii.gz file, found {len(nii_files)}")
            return False
        elif len(nii_files) == 1:
            shutil.move(nii_files[0], out_file)
            return True

        # no Eq images
        nii_files = list(Path(tmpdir).glob("*.nii.gz"))
        if len(nii_files) > 1:
            # raise ValueError(f"Expected 1 *.nii.gz file, found {len(nii_files)}")
            return False
        elif len(nii_files) == 1:
            shutil.move(nii_files[0], out_file)
            return True
        # raise ValueError(f"Expected 1 *.nii.gz file, found 0")
        return False


def run_model(in_dir: Path, out_dir: Path) -> bool:
    args = [
        "nnUNet_predict",
        "-i",
        str(in_dir),
        "-o",
        str(out_dir),
        "-t",
        "Task773_Liver",
    ]
    res = subprocess.run(args)
    return res.returncode == 0


def convert_nii_to_dcm_seg(
    seg_file: Path,
    out_file: Path,
    dcm_dir: Path,
    dicom_seg_meta_json: Path,
    add_background_label: bool = False,
    itkimage2segimage_bin="/app/dcmqi-1.2.5-linux/bin/itkimage2segimage",
) -> bool:
    assert dcm_dir.exists(), dcm_dir
    out_file.parent.mkdir(parents=True, exist_ok=True)

    res = None
    if add_background_label:
        # add background label, offset by 1
        with TemporaryDirectory() as temp_dir:
            temp_seg_file = Path(temp_dir) / "temp_seg.nii.gz"
            img = sitk.ReadImage(str(seg_file))
            img += 1
            sitk.WriteImage(img, str(temp_seg_file))

            args = [
                itkimage2segimage_bin,
                "--skip",
                "--inputImageList",
                str(temp_seg_file),
                "--inputDICOMDirectory",
                str(dcm_dir),
                "--outputDICOM",
                str(out_file),
                "--inputMetadata",
                str(dicom_seg_meta_json),
            ]

            res = subprocess.run(args)
    else:
        args = [
            itkimage2segimage_bin,
            "--skip",
            "--inputImageList",
            str(seg_file),
            "--inputDICOMDirectory",
            str(dcm_dir),
            "--outputDICOM",
            str(out_file),
            "--inputMetadata",
            str(dicom_seg_meta_json),
        ]

        res = subprocess.run(args)

    return res.returncode == 0


def main_dicom(dicom_dir: Path, output_dir: Path, dicom_seg_meta_json: Path):
    series_dirs = find_input_series(dicom_dir)
    nii_input_dir = Path("/tmp/nii")
    pred_dir = Path("/tmp/pred")

    input_series = []
    # create processing file names
    for i, series_dir in enumerate(series_dirs):
        nii_input_file = nii_input_dir / f"scan_{i}_0000.nii.gz"  # nnunet format
        nii_pred_file = pred_dir / f"scan_{i}.nii.gz"  # nnunet format
        dcm_pred_file = (
            output_dir
            / series_dir.parent.relative_to(dicom_dir)
            / f"{series_dir.name}.seg.dcm"
        )
        input_series.append(
            (
                series_dir,
                nii_input_file,
                nii_pred_file,
                dcm_pred_file,
            )
        )

    # convert dicom to nii
    args_dcm_to_nii = []
    for series_dir, nii_input_file, _, _ in input_series:
        args_dcm_to_nii.append((series_dir, nii_input_file))

    nii_conversion_status = list(map(lambda x: convert_dcm_to_nii(*x), args_dcm_to_nii))

    # run model
    run_model(nii_input_dir, pred_dir)

    # convert nii to dicom seg
    for series_dicom_dir, _, nii_pred_file, dcm_pred_file in input_series:
        if not nii_pred_file.exists():
            print(
                f"skipping {nii_pred_file} - {series_dicom_dir.relative_to(dicom_dir)}, does not exist"
            )
        else:
            convert_nii_to_dcm_seg(
                nii_pred_file,
                dcm_pred_file,
                series_dicom_dir,
                dicom_seg_meta_json,
            )


def main_nifti(input_dir: Path, output_dir: Path):
    input_niis = sorted(list(input_dir.rglob("*.nii.gz")))
    nnunet_nii_input_dir = Path("/tmp/nii")
    nnunet_pred_dir = Path("/tmp/pred")

    input_series = []
    # create processing file names
    for i, input_nii in enumerate(input_niis):
        nnunet_nii_input_file = (
            nnunet_nii_input_dir / f"scan_{i}_0000.nii.gz"
        )  # nnunet format
        nii_pred_file = nnunet_pred_dir / f"scan_{i}.nii.gz"  # nnunet format
        out_nii_pred_file = (
            output_dir / input_nii.parent.relative_to(input_dir) / input_nii.name
        )
        input_series.append(
            (
                input_nii,
                nnunet_nii_input_file,
                nii_pred_file,
                out_nii_pred_file,
            )
        )

    # link input niftis to nnunet niftis
    for input_nii, nnunet_nii_input_file, _, _ in input_series:
        nnunet_nii_input_file.parent.mkdir(parents=True, exist_ok=True)
        nnunet_nii_input_file.symlink_to(input_nii)

    # run model
    run_model(nnunet_nii_input_dir, nnunet_pred_dir)

    # convert nii to output file
    for input_nii, _, nii_pred_file, out_nii_pred_file in input_series:
        if not nii_pred_file.exists():
            print(
                f"skipping {nii_pred_file} - {input_nii.relative_to(input_dir)}, does not exist"
            )
        else:
            shutil.copy(nii_pred_file, out_nii_pred_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_dicom_dir",
        type=Path,
        help="Directory containing dicom files. if mutiple series, each series should be in a subdirectory",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Output directory for dicom segmentation files, folder structure of input_dicom_dir will be preserved, with each output being name of the series directory with .seg.dcm extension",
    )
    parser.add_argument(
        "--nifti",
        action="store_true",
        help="Input and Output files are nifti instead of DICOM",
    )
    parser.add_argument(
        "--dicom_seg_meta_json",
        type=Path,
        default="/app/dicom_seg_meta.json",
        help="Path to dicom_seg_meta.json file",
    )

    args = parser.parse_args()
    if args.nifti:
        main_nifti(args.input_dicom_dir, args.output_dir)
    else:
        main_dicom(args.input_dicom_dir, args.output_dir, args.dicom_seg_meta_json)
