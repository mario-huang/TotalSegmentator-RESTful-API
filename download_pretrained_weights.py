from time import sleep

from totalsegmentator.libs import download_pretrained_weights

if __name__ == "__main__":
    """
    Download all pretrained weights
    """
    task_to_id = {
        "total": [291, 292, 293, 294, 295, 298],
        "total_fast": [297, 298],
        "total_mr": [730, 731],
        "total_fast_mr": [732, 733],
        "lung_vessels": [258],
        "cerebral_bleed": [150],
        "hip_implant": [260],
        "coronary_arteries": [503],
        "pleural_pericard_effusion": [315],
        "body": [299],
        "body_fast": [300],
        "head_glands_cavities": [775],
        "headneck_bones_vessels": [776],
        "head_muscles": [777],
        "headneck_muscles": [778, 779],
        "liver_vessels": [8],
        "heartchambers_highres": [301],
        "appendicular_bones": [304],
        "tissue_types": [481],
        "tissue_types_mr": [734],
        "vertebrae_body": [302],
        "face": [303],
        "face_mr": [737],
        "brain_structures": [409],
    }

    for task in task_to_id:
        for task_id in task_to_id[task]:
            download_pretrained_weights(task_id)
