import asyncio
from dataclasses import asdict, dataclass
import os
import signal
import time
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    UploadFile,
)
from fastapi.responses import FileResponse
from totalsegmentator.python_api import totalsegmentator
import nibabel as nib

INPUTS_DIRECTORY = "inputs"
os.makedirs(INPUTS_DIRECTORY, exist_ok=True)
OUTPUTS_DIRECTORY = "outputs"
os.makedirs(OUTPUTS_DIRECTORY, exist_ok=True)


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            if "microsoft" in version_info:
                print("Running inside WSL")
                return True
    except FileNotFoundError:
        pass
    print("Not running inside WSL")
    return False


IS_WSL = is_wsl()

app = FastAPI()


@dataclass
class FileRequestBody:
    ml: bool = Form(True, description="Save one multilabel image for all classes")
    nr_thr_resamp: int = Form(1, description="Nr of threads for resampling")
    nr_thr_saving: int = Form(6, description="Nr of threads for saving segmentations")
    fast: bool = Form(False, description="Run faster lower resolution model (3mm)")
    nora_tag: str = Form(
        "None", description="tag in nora as mask. Pass nora project id as argument."
    )
    preview: bool = Form(False, description="Generate a png preview of segmentation")
    task: str = Form(
        "total",
        description="""
        Select which model to use. This determines what is predicted.
        Choices: 
        "total", "body", "lung_vessels", "cerebral_bleed", "hip_implant", "coronary_arteries", "pleural_pericard_effusion", "test", "appendicular_bones", "tissue_types", "heartchambers_highres", "face", "vertebrae_body", "total_mr", "tissue_types_mr", "face_mr", "head_glands_cavities", "head_muscles", "headneck_bones_vessels", "headneck_muscles", "brain_structures", "liver_vessels"
        """,
    )
    roi_subset: str = Form(
        None,
        description="Define a subset of classes to save (space separated list of class names). If running 1.5mm model, will only run the appropriate models for these rois.",
    )
    statistics: bool = Form(
        False,
        description="Calc volume (in mm3) and mean intensity. Results will be in statistics.json",
    )
    radiomics: bool = Form(
        False,
        description="Calc radiomics features. Requires pyradiomics. Results will be in statistics_radiomics.json",
    )
    crop_path: str = Form(
        None,
        description="Custom path to masks used for cropping. If not set will use output directory.",
    )
    body_seg: bool = Form(
        False,
        description="Do initial rough body segmentation and crop image to body region",
    )
    force_split: bool = Form(
        False,
        description="Process image in 3 chunks for less memory consumption. (do not use on small images)",
    )
    output_type: str = Form(
        "nifti",
        description="Select if segmentations shall be saved as Nifti or as Dicom RT Struct image. Choices: nifti, dicom",
    )
    quiet: bool = Form(False, description="Print no intermediate outputs")
    verbose: bool = Form(False, description="Show more intermediate output")
    test: int = Form(0, description="Only needed for unittesting. Choices: 0, 1, 3")
    skip_saving: bool = Form(
        False,
        description="Skip saving of segmentations for faster runtime if you are only interested in statistics.",
    )
    device: str = Form(
        "gpu", description="Device to run on (default: gpu). Choices: gpu, cpu, mps"
    )
    license_number: str = Form(
        None,
        description="Set license number. Needed for some tasks. Only needed once, then stored in config file.",
    )
    statistics_exclude_masks_at_border: bool = Form(
        True,
        description="Normally statistics are only calculated for ROIs which are not cut off by the beginning or end of image. Use this option to calc anyways.",
    )
    no_derived_masks: bool = Form(
        False, description="Do not create derived masks (e.g. skin from body mask)."
    )
    v1_order: bool = Form(
        False,
        description="In multilabel file order classes as in v1. New v2 classes will be removed.",
    )
    fastest: bool = Form(
        False, description="Run even faster lower resolution model (6mm)"
    )
    roi_subset_robust: str = Form(
        None,
        description="Like roi_subset but uses a slower but more robust model to find the rois.",
    )


@app.post("/segment_file")
async def segment_file(
    input: UploadFile = File(
        ..., description="CT nifti image or folder of dicom slices"
    ),
    body: FileRequestBody = Depends(),
):
    """
    Run segment from api.
    """
    print("body: " + str(body))

    try:
        # sometimes Totalsegmentator hangs, so we need a timeout
        return await asyncio.wait_for(
            process_segment(input, body), timeout=600
        )
    except asyncio.TimeoutError:
        print("Segmentation processing timed out.")
        asyncio.create_task(terminate_process())
        return {"code": 408, "message": "Segmentation processing timed out."}
    finally:
        if IS_WSL:
            os.kill(os.getpid(), signal.SIGINT)


async def process_segment(input, body):
    input_name = input.filename
    if input_name is None:
        return {"code": 0, "message": "The file must have a filename."}
    if input_name.endswith(".gz") is False and input_name.endswith(".zip") is False:
        return {
            "code": 0,
            "message": "A Nifti file or a folder (or zip file) with all DICOM slices of one patient is allowed as input.",
        }
    try:
        timestamp_ms = time.time_ns() // 1000000
        input_path = os.path.join(
            INPUTS_DIRECTORY, str(timestamp_ms) + "-" + input_name
        )
        with open(input_path, "wb") as f:
            f.write(await input.read())
        output_path = os.path.join(OUTPUTS_DIRECTORY, str(timestamp_ms) + ".nii.gz")
        input_img = nib.load(input_path)
        output_img = totalsegmentator(input_img, None, **asdict(body))
        nib.save(output_img, output_path)
        print("Yes! Totalsegmentator Finished!")
    except Exception as e:
        return {
            "code": 0,
            "message": """totalsegmentator failed.
                """
            + str(e),
        }
    else:
        if os.path.isfile(output_path):
            return FileResponse(
                output_path,
                headers={
                    "Content-Disposition": f"attachment; filename={os.path.basename(output_path)}"
                },
                media_type="application/octet-stream",
            )
        return {"code": 0, "message": "totalsegmentator failed."}
    
async def terminate_process():
    await asyncio.sleep(1)
    os.kill(os.getpid(), signal.SIGINT)