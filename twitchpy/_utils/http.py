import math

import aiohttp

from .. import errors

DEFAULT_TIMEOUT: int = 10


async def send_post(url: str, headers: dict, payload: dict) -> None:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])


async def send_post_get_result(url: str, headers: dict, payload: dict) -> list[dict]:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return (await response.json())["data"]


async def send_get(url: str, headers: dict, params: dict) -> list[dict]:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.get(url, headers=headers, params=params) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return (await response.json())["data"]


async def send_get_with_pagination(
    url: str, headers: dict, params: dict, first: int, page_size: int
) -> list[dict]:
    after = ""
    results = []

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        for call in range(math.ceil(first / page_size)):
            params["first"] = min(page_size, first - (page_size * call))

            if after != "":
                params["after"] = after

            async with session.get(url, headers=headers, params=params) as response:
                if not response.ok:
                    raise errors.ClientError((await response.json())["message"])

                response_data = await response.json()
                results.extend(response_data["data"])

                if (
                    "pagination" in response_data
                    and "cursor" in response_data["pagination"]
                ):
                    after = response_data["pagination"]["cursor"]

    return results


async def send_get_with_infinite_pagination(
    url: str, headers: dict, params: dict
) -> list[dict]:
    results = []

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        pagination = True

        while pagination:
            async with session.get(url, headers=headers, params=params) as response:
                if not response.ok:
                    raise errors.ClientError((await response.json())["message"])

                response_data = await response.json()
                results.extend(response_data["data"])

                if "pagination" in response_data:
                    params["after"] = response_data["pagination"]["cursor"]
                    continue

                pagination = False

    return results


async def send_get_text(url: str, params: dict) -> str:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.get(url, params=params) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return await response.text()


async def send_put(url: str, headers: dict, data: dict) -> None:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.put(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])


async def send_put_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.put(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return (await response.json())["data"]


async def send_patch(url: str, headers: dict, data: dict) -> None:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.patch(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])


async def send_patch_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.patch(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return (await response.json())["data"]


async def send_delete(url: str, headers: dict, data: dict) -> None:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.delete(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])


async def send_delete_get_result(url: str, headers: dict, data: dict) -> list[dict]:
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    ) as session:
        async with session.delete(url, headers=headers, data=data) as response:
            if not response.ok:
                raise errors.ClientError((await response.json())["message"])

            return (await response.json())["data"]
