from pathlib import Path
import SimpleITK as sitk
from p_tqdm import p_map


def fix_nifti(input_file: Path, output_file: Path):
    original_img = sitk.ReadImage(str(input_file))
    arr = sitk.GetArrayFromImage(original_img)
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing(original_img.GetSpacing())
    img.SetOrigin(original_img.GetOrigin())
    img.SetDirection(original_img.GetDirection())
    output_file.parent.mkdir(parents=True, exist_ok=True)
    sitk.WriteImage(img, str(output_file), useCompression=True, compressionLevel=9)


def main(input_dir: Path, output_dir: Path):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    args = []
    for input_file in input_dir.rglob("*.nii.gz"):
        output_file = output_dir / input_file.relative_to(input_dir)
        args.append((input_file, output_file))

    p_map(lambda x: fix_nifti(*x), args)


if __name__ == "__main__":
    main(Path("/data"), Path("/data_out"))
