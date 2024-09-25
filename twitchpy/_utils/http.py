import math

import requests

from .. import errors

DEFAULT_TIMEOUT: int = 10


def send_post(url: str, headers: dict, payload: dict) -> None:
    response = requests.post(
        url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT
    )

    if not response.ok:
        raise errors.ClientError(response.json()["message"])


def send_post_get_result(url: str, headers: dict, payload: dict) -> list[dict]:
    response = requests.post(
        url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT
    )

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.json()["data"]


def send_get(url: str, headers: dict, params: dict) -> list[dict]:
    response = requests.get(
        url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
    )

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.json()["data"]


def send_get_with_pagination(
    url: str, headers: dict, params: dict, first: int, page_size: int
) -> list[dict]:
    after = ""
    results = []

    for call in range(math.ceil(first / page_size)):
        params["first"] = min(page_size, first - (page_size * call))

        if after != "":
            params["after"] = after

        response = requests.get(
            url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
        )

        if not response.ok:
            raise errors.ClientError(response.json()["message"])

        response = response.json()
        results.extend(response["data"])

        if "pagination" in response and "cursor" in response["pagination"]:
            after = response["pagination"]["cursor"]

    return results


def send_get_with_infinite_pagination(
    url: str, headers: dict, params: dict
) -> list[dict]:
    response = requests.get(
        url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
    )

    results = []

    while response.ok and "pagination" in response.json():
        results.extend(response.json()["data"])
        params["after"] = response.json()["pagination"]["cursor"]

        response = requests.get(
            url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
        )

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return results


def send_get_text(url: str, params: dict) -> str:
    response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.text


def send_put(url: str, headers: dict, data: dict) -> None:
    response = requests.put(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])


def send_put_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    response = requests.put(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.json()["data"]


def send_patch(url: str, headers: dict, data: dict) -> None:
    response = requests.patch(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])


def send_patch_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    response = requests.patch(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.json()["data"]


def send_delete(url: str, headers: dict, data: dict) -> None:
    response = requests.delete(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])


def send_delete_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    response = requests.delete(url, headers=headers, data=data, timeout=DEFAULT_TIMEOUT)

    if not response.ok:
        raise errors.ClientError(response.json()["message"])

    return response.json()["data"]
