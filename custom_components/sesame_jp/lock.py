"""Support for Sesame-JP"""
from __future__ import annotations

import asyncio
import base64
import datetime
import logging

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from homeassistant.components.lock import PLATFORM_SCHEMA, LockEntity
from homeassistant.const import (
    CONF_API_KEY,
    CONF_CLIENT_SECRET,
    CONF_DEVICE_ID,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

ATTR_SERIAL_NO = "serial"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_CLIENT_SECRET): cv.string,
})

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    name = config.get(CONF_NAME)
    device_id = config.get(CONF_DEVICE_ID)
    api_key = config.get(CONF_API_KEY)
    client_secret = config.get(CONF_CLIENT_SECRET)

    session = aiohttp_client.async_get_clientsession(hass)

    async_add_entities(
        [SesameJPDevice(
            name=name,
            uuid=device_id,
            api_key=api_key,
            secret_key=client_secret,
            session=session,
        )],
        update_before_add=True,
    )


class SesameJPDevice(LockEntity):
    def __init__(
            self,
            name: str,
            uuid: str,
            api_key: str,
            secret_key: str,
            session: aiohttp.ClientSession,
    ) -> None:
        self._name: str = name
        self._uuid: str = uuid
        self._api_key: str = api_key
        self._secret_key: str = secret_key

        self._session = session
        self._api_url = f"https://app.candyhouse.co/api/sesame2/{uuid}"

        self._is_locked = False
        self._is_locking = False
        self._is_unlocking = False

        self._responsive = False
        self._battery = -1

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def available(self) -> bool:
        return self._responsive

    @property
    def code_format(self) -> str | None:
        return None

    @property
    def is_locked(self) -> bool | None:
        return self._is_locked

    @property
    def is_locking(self) -> bool | None:
        return self._is_locking

    @property
    def is_unlocking(self) -> bool | None:
        return self._is_unlocking

    @property
    def is_jammed(self) -> bool | None:
        """Return true if the lock is jammed (incomplete locking)."""
        return self._attr_is_jammed

    async def async_lock(self, **kwargs):
        await self._sesame_command(action="LOCK")

    async def async_unlock(self, **kwargs):
        await self._sesame_command(action="UNLOCK")

    async def async_open(self, **kwargs):
        await self._sesame_command(action="UNLOCK")

    async def async_update(self) -> None:
        if self._battery == -1:
            await self._sesame_update()

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "uuid": self._uuid,
            "battery_level": self._battery,
        }

    async def _sesame_update(self) -> None:
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.request(
                    "GET",
                    self._api_url,
                    headers={
                        "x-api-key": self._api_key,
                    },
                )
                state = await response.json()
                if state:
                    self._responsive = True

                    if 'CHSesame2Status' in state:
                        if state['CHSesame2Status'] == "locked":
                            self._is_locked = True
                        elif state['CHSesame2Status'] == "unlocked":
                            self._is_locked = False

                    if 'batteryPercentage' in state:
                        self._battery = state['batteryPercentage']

                    if 'message' in state:
                        _LOGGER.error(state['message'])
                else:
                    self._responsive = False
        except asyncio.TimeoutError:
            _LOGGER.error("Failed to connect to Sesame server")

    async def _sesame_command(self, action) -> None:
        if action == "LOCK":
            cmd = 82
            self._is_locking = True
            self._is_unlocking = False
        elif action == "UNLOCK":
            cmd = 83
            self._is_locking = False
            self._is_unlocking = True
        else:
            return

        ts = int(datetime.datetime.now().timestamp())
        message = ts.to_bytes(4, byteorder='little')
        message = message.hex()[2:8]
        cmac = CMAC.new(bytes.fromhex(self._secret_key), ciphermod=AES)
        cmac.update(bytes.fromhex(message))
        sign = cmac.hexdigest()

        try:
            async with async_timeout.timeout(TIMEOUT):
                await self._session.request(
                    "POST",
                    self._api_url + "/cmd",
                    headers={
                        "x-api-key": self._api_key,
                    },
                    json={
                        "cmd": cmd,
                        "history": base64.b64encode(bytes(f"Home-Assistant {action}", 'utf-8')).decode(),
                        "sign": sign,
                    },
                )

                self._is_locking = False
                self._is_unlocking = False

                if action == "LOCK":
                    self._is_locked = True
                elif action == "UNLOCK":
                    self._is_locked = False
        except asyncio.TimeoutError:
            _LOGGER.error("Failed to connect to Sesame server")
