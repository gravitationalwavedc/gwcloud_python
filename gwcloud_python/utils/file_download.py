import concurrent.futures
from functools import partial
import requests
from tqdm import tqdm


GWCLOUD_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/job/apiv1/file/?fileId='
GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/bilby/file_download/?fileId='


def _get_file_map_fn(file_id, file_path, progress_bar, endpoint):
    download_url = endpoint + str(file_id)
    content = b''

    with requests.get(download_url, stream=True) as request:
        for chunk in request.iter_content(chunk_size=1024 * 16, decode_unicode=True):
            progress_bar.update(len(chunk))
            content += chunk
    return (file_path, content)


def _save_file_map_fn(file_id, file_path, progress_bar, endpoint):
    download_url = endpoint + str(file_id)
    file_path.parents[0].mkdir(parents=True, exist_ok=True)

    with requests.get(download_url, stream=True) as request:
        with file_path.open("wb+") as f:
            for chunk in request.iter_content(chunk_size=1024 * 16):
                progress_bar.update(len(chunk))
                f.write(chunk)


def _download_files(map_fn, file_ids, file_paths, total_size, is_uploaded_job):
    endpoint = GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
        if not is_uploaded_job else \
        GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        progress = tqdm(total=total_size, leave=True, unit='B', unit_scale=True)
        files = list(
            executor.map(
                partial(
                    map_fn,
                    progress_bar=progress,
                    endpoint=endpoint
                ),
                file_ids, file_paths
            )
        )
        progress.close()
    return files
