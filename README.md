# No Bullshit TotalSegmentator RESTful API

This repository provides a simple and efficient API for medical image segmentation using TotalSegmentator.

## Features

Just give me the **input file**(a CT nifti image or a folder of DICOM slices).
And I will give you the **output file**(a segmented image as an .nii.gz file).

## Requirements

- Docker
- NVIDIA GPU with drivers installed

## Installation

Use the [docker-compose.yml](https://raw.githubusercontent.com/mario-huang/TotalSegmentator-RESTful-API/main/docker-compose.yml) file to set up and run the service.

```bash
docker compose up -d
```

## Usage

For CT images:
| Method | Path | Body Type |
|--------|----------------|-----------|
| POST | `/segment_file` | form-data |

| Parameters | Value    |
| ---------- | -------- |
| `file`     | `xxx.gz` |
| `task`     | `total`  |

Send a POST request to the /segment_file endpoint to process your CT images.

```bash
curl -X POST -F "file=@/path/to/ct/image/or/dicom/folder" http://localhost:8001/segment_file -o output.nii.gz
```

For MR images:
| Method | Path | Body Type |
|--------|----------------|-----------|
| POST | `/segment_file` | form-data |

| Parameters | Value      |
| ---------- | ---------- |
| `file`     | `xxx.gz`   |
| `task`     | `total_mr` |

Send a POST request to the /segment_file endpoint to process your MR images.

```bash
curl -X POST -F "file=@/path/to/mr/image/or/dicom/folder" http://localhost:8001/segment_file -o output.nii.gz
```

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## Reference

This project uses TotalSegmentator. If you use this project, please cite it as follows:

```

Wasserthal, J., Breit, H.-C., Meyer, M.T., Pradella, M., Hinck, D., Sauter, A.W., Heye, T., Boll, D., Cyriac, J., Yang, S., Bach, M., Segeroth, M., 2023. TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images. Radiology: Artificial Intelligence. https://doi.org/10.1148/ryai.230024

```

Please also cite [nnUNet](https://github.com/MIC-DKFZ/nnUNet) since TotalSegmentator is heavily based on it.

```

```
