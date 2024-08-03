# No Bullshit TotalSegmentator RESTful API
This repository provides a simple and efficient API for medical image segmentation using TotalSegmentator.

## Features
Just give me the **input file**(a CT nifti image or a folder of DICOM slices).
And I will give you the	**output file**(a segmented image as an .nii.gz file).

## Requirements
- Docker
- NVIDIA GPU with drivers installed

## Installation
Use the docker-compose.yml file to set up and run the service.
```bash
docker compose up -d
```

## Usage
| Method | Path           | Body Type | Parameter    |
|--------|----------------|-----------|--------------|
| POST   | `/segment_file` | form-data | `file` |
Send a POST request to the /segment_file endpoint to process your CT images.
```bash
curl -X POST -F "file=@/path/to/ct/image/or/dicom/folder" http://localhost:8001/segment_file -o output.nii.gz
```

## Contributing
Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License
This project is licensed under the MIT License.