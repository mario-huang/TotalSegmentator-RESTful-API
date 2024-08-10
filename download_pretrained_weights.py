from time import sleep

from totalsegmentator.libs import download_pretrained_weights

if __name__ == "__main__":
    """
    Download all pretrained weights
    """
    for task_id in range(1, 1000):
        try:
            download_pretrained_weights(task_id)
        except ValueError:
            continue
