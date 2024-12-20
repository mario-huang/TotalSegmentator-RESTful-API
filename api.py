from typing import Any
import requests
import asyncio
from dataclasses import asdict, dataclass
import signal
import time
import os
from urllib.parse import urlparse
from fastapi import FastAPI
from fastapi.responses import FileResponse
from main import INPUTS_DIRECTORY, OUTPUTS_DIRECTORY
from totalsegmentator.python_api import totalsegmentator
import nibabel as nib
from pydantic import BaseModel, Field


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


class DataRequest(BaseModel):
    ml: bool = Field(True, description="Save one multilabel image for all classes")
    nr_thr_resamp: int = Field(1, description="Nr of threads for resampling")
    nr_thr_saving: int = Field(6, description="Nr of threads for saving segmentations")
    fast: bool = Field(False, description="Run faster lower resolution model (3mm)")
    nora_tag: str = Field(
        "None", description="tag in nora as mask. Pass nora project id as argument."
    )
    preview: bool = Field(False, description="Generate a png preview of segmentation")
    task: str = Field(
        "total",
        description="""
        Select which model to use. This determines what is predicted.
        Choices: 
        "total", "body", "lung_vessels", "cerebral_bleed", "hip_implant", "coronary_arteries", "pleural_pericard_effusion", "test", "appendicular_bones", "tissue_types", "heartchambers_highres", "face", "vertebrae_body", "total_mr", "tissue_types_mr", "face_mr", "head_glands_cavities", "head_muscles", "headneck_bones_vessels", "headneck_muscles", "brain_structures", "liver_vessels"
        """,
    )
    roi_subset: str = Field(
        None,
        description="Define a subset of classes to save (space separated list of class names). If running 1.5mm model, will only run the appropriate models for these rois.",
    )
    statistics: bool = Field(
        False,
        description="Calc volume (in mm3) and mean intensity. Results will be in statistics.json",
    )
    radiomics: bool = Field(
        False,
        description="Calc radiomics features. Requires pyradiomics. Results will be in statistics_radiomics.json",
    )
    crop_path: str = Field(
        None,
        description="Custom path to masks used for cropping. If not set will use output directory.",
    )
    body_seg: bool = Field(
        False,
        description="Do initial rough body segmentation and crop image to body region",
    )
    force_split: bool = Field(
        False,
        description="Process image in 3 chunks for less memory consumption. (do not use on small images)",
    )
    output_type: str = Field(
        "nifti",
        description="Select if segmentations shall be saved as Nifti or as Dicom RT Struct image. Choices: nifti, dicom",
    )
    quiet: bool = Field(False, description="Print no intermediate outputs")
    verbose: bool = Field(False, description="Show more intermediate output")
    test: int = Field(0, description="Only needed for unittesting. Choices: 0, 1, 3")
    skip_saving: bool = Field(
        False,
        description="Skip saving of segmentations for faster runtime if you are only interested in statistics.",
    )
    device: str = Field(
        "gpu", description="Device to run on (default: gpu). Choices: gpu, cpu, mps"
    )
    license_number: str = Field(
        None,
        description="Set license number. Needed for some tasks. Only needed once, then stored in config file.",
    )
    statistics_exclude_masks_at_border: bool = Field(
        True,
        description="Normally statistics are only calculated for ROIs which are not cut off by the beginning or end of image. Use this option to calc anyways.",
    )
    no_derived_masks: bool = Field(
        False, description="Do not create derived masks (e.g. skin from body mask)."
    )
    v1_order: bool = Field(
        False,
        description="In multilabel file order classes as in v1. New v2 classes will be removed.",
    )
    fastest: bool = Field(
        False, description="Run even faster lower resolution model (6mm)"
    )
    roi_subset_robust: str = Field(
        None,
        description="Like roi_subset but uses a slower but more robust model to find the rois.",
    )


class UrlRequest(BaseModel):
    input: str
    data: DataRequest


@app.post("/segment_url")
async def segment_url(body: UrlRequest):
    print("body: " + str(body))
    try:
        # sometimes Totalsegmentator hangs, so we need a timeout
        return await asyncio.wait_for(
            process_segment(body.input, body.data.model_dump()), timeout=10 * 60
        )
    except asyncio.TimeoutError:
        print("Segmentation processing timed out.")
        terminate_process()
        return {"code": 408, "message": "Segmentation processing timed out."}
    finally:
        if IS_WSL:
            terminate_process()


async def process_segment(input: str, data: dict[str, Any]):
    timestamp_ms = time.time_ns() // 1000000
    filename_with_extension = os.path.basename(urlparse(input).path)
    input_path = os.path.join(INPUTS_DIRECTORY, str(timestamp_ms) + "-" + filename_with_extension)
    await download_file(input, input_path)
    try:
        output_path = os.path.join(OUTPUTS_DIRECTORY, str(timestamp_ms) + ".nii.gz")
        input_img = nib.load(input_path)
        output_img = totalsegmentator(input_img, None, **data)
        nib.save(output_img, output_path)
        print("Yes! Totalsegmentator Finished!")
    except Exception as e:
        return {
            "code": 8001,
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
        return {"code": 8001, "message": "totalsegmentator failed."}


async def terminate_process():
    await asyncio.sleep(3)
    os.kill(os.getpid(), signal.SIGINT)


async def download_file(url: str, path: str):
    response = requests.get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=4194304):
            f.write(chunk)


async def save_file(input, path):
    with open(path, "wb") as f:
        f.write(await input.read())
