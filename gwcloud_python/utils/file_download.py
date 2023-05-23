import concurrent.futures
from functools import partial
import requests
from gwdc_python.files.constants import JobType
from tqdm import tqdm
from ..settings import GWCLOUD_FILE_DOWNLOAD_ENDPOINT, GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT


def _get_endpoint_from_uploaded(is_uploaded_job):
    return GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
        if not is_uploaded_job else \
        GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT


def _get_file_map_fn(file_id, file_path, job_type, progress_bar):
    if job_type == JobType.GWOSC_JOB:
        download_url = file_path
    else:
        download_url = _get_endpoint_from_uploaded(job_type == JobType.UPLOADED_JOB) + str(file_id)

    content = b''

    with requests.get(download_url, stream=True) as request:
        for chunk in request.iter_content(chunk_size=1024 * 16, decode_unicode=True):
            progress_bar.update(len(chunk))
            content += chunk
    return (file_path, content)


def _save_file_map_fn(file_id, file_path, job_type, progress_bar):
    download_url = _get_endpoint_from_uploaded(job_type) + str(file_id)
    file_path.parents[0].mkdir(parents=True, exist_ok=True)

    with requests.get(download_url, stream=True) as request:
        with file_path.open("wb+") as f:
            for chunk in request.iter_content(chunk_size=1024 * 16):
                progress_bar.update(len(chunk))
                f.write(chunk)


def _download_files(map_fn, file_ids, file_paths, job_type, total_size):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        progress = tqdm(total=total_size, leave=True, unit='B', unit_scale=True)
        files = list(
            executor.map(
                partial(
                    map_fn,
                    progress_bar=progress
                ),
                file_ids, file_paths, job_type
            )
        )
        progress.close()
    return files
