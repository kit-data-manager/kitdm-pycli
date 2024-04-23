import vcr
import os
from kitdm_pycli.helpers.base_repo_helper import BaseRepoClient

os.environ["PYCLI_PROPERTIES"] = "./tests/properties-test.json"


@vcr.use_cassette()
def test_base_repo_client_create():
    service_client = BaseRepoClient(False)
    response = service_client.create(
        None, "./tests/input/data_resource.json", None, None
    )

    assert response is not None
    assert len(response) == 1


# assert response[0]['id'] == "ff98569f-57d0-439f-90af-009cba657b0c"


@vcr.use_cassette()
def test_base_repo_client_get():
    service_client = BaseRepoClient(False)
    response = service_client.get("ff98569f-57d0-439f-90af-009cba657b0c", None, None)

    assert response is not None
    assert len(response) == 1


# assert response[0]['id'] == "ff98569f-57d0-439f-90af-009cba657b0c"


@vcr.use_cassette()
def test_base_repo_client_upload():
    service_client = BaseRepoClient(False)
    response = service_client.create(
        "ff98569f-57d0-439f-90af-009cba657b0c",
        None,
        "./tests/input/upload.txt",
        "file.txt",
    )

    assert response is not None
    assert len(response) == 1


# assert response[0]['id'] == "ff98569f-57d0-439f-90af-009cba657b0c"


@vcr.use_cassette()
def test_base_repo_client_download():
    service_client = BaseRepoClient(False)
    response = service_client.download(
        "ff98569f-57d0-439f-90af-009cba657b0c", "file.txt", None
    )

    assert response is not None
    assert response.decode("utf-8") == "This is a test file for upload."
