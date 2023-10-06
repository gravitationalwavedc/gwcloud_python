import concurrent.futures
from functools import partial
import requests
from tqdm import tqdm

from ..exceptions import ExternalFileDownloadException
from ..settings import GWCLOUD_FILE_DOWNLOAD_ENDPOINT, GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT


def _get_endpoint_from_uploaded(is_uploaded_job):
    return GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
        if not is_uploaded_job else \
        GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT


def _get_file_map_fn(file_id, file_ref, progress_bar, **kwargs):
    if file_ref.parent.is_external():
        raise ExternalFileDownloadException(file_ref.path)

    download_url = _get_endpoint_from_uploaded(file_ref.parent.is_uploaded()) + str(file_id)

    content = b''

    with requests.get(download_url, stream=True) as request:
        for chunk in request.iter_content(chunk_size=1024 * 16, decode_unicode=True):
            progress_bar.update(len(chunk))
            content += chunk
    return (file_ref.path, content)


def _save_file_map_fn(file_id, file_ref, progress_bar, root_path):
    if file_ref.parent.is_external():
        raise ExternalFileDownloadException(file_ref.path)

    download_url = _get_endpoint_from_uploaded(file_ref.parent.is_uploaded()) + str(file_id)

    output_path = root_path / file_ref.path
    output_path.parents[0].mkdir(parents=True, exist_ok=True)

    with requests.get(download_url, stream=True) as request:
        with output_path.open("wb+") as f:
            for chunk in request.iter_content(chunk_size=1024 * 16):
                progress_bar.update(len(chunk))
                f.write(chunk)


def _download_files(map_fn, file_ids, file_refs, root_path=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        progress = tqdm(total=file_refs.get_total_bytes(), leave=True, unit='B', unit_scale=True)
        files = list(
            executor.map(
                partial(
                    map_fn,
                    progress_bar=progress,
                    root_path=root_path
                ),
                file_ids, file_refs
            )
        )
        progress.close()
    return files
