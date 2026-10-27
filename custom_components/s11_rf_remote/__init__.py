"""S11 RF/IR Remote Manager v3.0.1 - Quản lý Học lệnh, Test & Thư viện trực quan."""
import datetime
import json
import logging
import os
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "s11_rf_remote"
LIBRARY_FILE = "s11_rf_remote_library.json"


def _ensure_translations_sync() -> None:
    """Tự động tạo translations/vi.json và en.json từ strings.json cho Custom Component."""
    try:
        comp_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(comp_dir, "strings.json")
        if not os.path.isfile(strings_path):
            return
        trans_dir = os.path.join(comp_dir, "translations")
        os.makedirs(trans_dir, exist_ok=True)
        for lang in ("vi.json", "en.json"):
            target_path = os.path.join(trans_dir, lang)
            shutil.copyfile(strings_path, target_path)
    except Exception as err:
        _LOGGER.debug("Không thể tự tạo file translations: %s", err)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Khởi tạo cơ bản (không cần YAML)."""
    hass.data.setdefault(DOMAIN, {})
    await hass.async_add_executor_job(_ensure_translations_sync)
    return True


def _load_all_codes_sync(hass: HomeAssistant) -> dict:
    """Đọc và hợp nhất dữ liệu từ thư viện S11 và các file .storage của Home Assistant."""
    _ensure_translations_sync()
    storage_dir = hass.config.path(".storage")
    merged: dict = {}

    # 1. Đọc từ các file .storage của tuya_local / remote nếu có
    if os.path.isdir(storage_dir):
        for fname in os.listdir(storage_dir):
            if fname in ("tuya_local_codes", "remote_codes") or "codes" in fname:
                if fname == LIBRARY_FILE:
                    continue
                fpath = os.path.join(storage_dir, fname)
                if os.path.isfile(fpath):
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            raw = json.load(f)
                        data = raw.get("data", raw)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                if isinstance(v, dict) and v:
                                    first_val = next(iter(v.values()), None)
                                    if isinstance(first_val, dict):
                                        for sub_dev, sub_cmds in v.items():
                                            if isinstance(sub_cmds, dict):
                                                merged.setdefault(str(sub_dev), {})
                                                for c_name in sub_cmds:
                                                    merged[str(sub_dev)][str(c_name)] = {
                                                        "type": "rf/ir",
                                                        "source": fname,
                                                    }
                                    else:
                                        merged.setdefault(str(k), {})
                                        for c_name in v:
                                            merged[str(k)][str(c_name)] = {
                                                "type": "rf/ir",
                                                "source": fname,
                                            }
                    except Exception as err:
                        _LOGGER.debug("Bỏ qua file %s: %s", fname, err)

    # 2. Đọc từ file thư viện riêng của S11 RF Remote Manager
    lib_path = os.path.join(storage_dir, LIBRARY_FILE)
    if os.path.isfile(lib_path):
        try:
            with open(lib_path, "r", encoding="utf-8") as f:
                lib_data = json.load(f)
            if isinstance(lib_data, dict):
                for dev, cmds in lib_data.items():
                    if isinstance(cmds, dict):
                        merged.setdefault(str(dev), {})
                        for c_name, meta in cmds.items():
                            merged[str(dev)][str(c_name)] = (
                                meta if isinstance(meta, dict) else {"type": "rf"}
                            )
        except Exception as err:
            _LOGGER.warning("Không thể đọc thư viện S11: %s", err)

    return merged


def _save_to_library_sync(
    hass: HomeAssistant, device: str, command: str, command_type: str
) -> None:
    """Lưu thông tin nút vừa học vào thư viện S11 ngay lập tức."""
    storage_dir = hass.config.path(".storage")
    os.makedirs(storage_dir, exist_ok=True)
    lib_path = os.path.join(storage_dir, LIBRARY_FILE)

    lib_data = {}
    if os.path.isfile(lib_path):
        try:
            with open(lib_path, "r", encoding="utf-8") as f:
                lib_data = json.load(f)
        except Exception:
            lib_data = {}

    lib_data.setdefault(device, {})
    lib_data[device][command] = {
        "type": command_type,
        "updated_at": datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
    }

    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(lib_data, f, ensure_ascii=False, indent=2)


def _delete_from_library_sync(hass: HomeAssistant, device: str, command: str) -> None:
    """Xóa nút khỏi thư viện S11."""
    storage_dir = hass.config.path(".storage")
    lib_path = os.path.join(storage_dir, LIBRARY_FILE)
    if not os.path.isfile(lib_path):
        return
    try:
        with open(lib_path, "r", encoding="utf-8") as f:
            lib_data = json.load(f)
        if device in lib_data and command in lib_data[device]:
            del lib_data[device][command]
            if not lib_data[device]:
                del lib_data[device]
            with open(lib_path, "w", encoding="utf-8") as f:
                json.dump(lib_data, f, ensure_ascii=False, indent=2)
    except Exception as err:
        _LOGGER.warning("Không thể xóa khỏi thư viện S11: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Khởi tạo tích hợp từ giao diện UI."""
    hass.data.setdefault(DOMAIN, {})
    remote_entity = entry.data.get("remote_entity", "remote.infrared_rf_remote_control")
    hass.data[DOMAIN]["remote_entity"] = remote_entity

    async def async_refresh_library() -> dict:
        codes = await hass.async_add_executor_job(_load_all_codes_sync, hass)
        hass.data[DOMAIN]["storage_codes"] = codes
        total_commands = sum(
            len(cmds) for cmds in codes.values() if isinstance(cmds, dict)
        )

        summary_dict = {
            dev: list(cmds.keys())
            for dev, cmds in codes.items()
            if isinstance(cmds, dict)
        }

        hass.states.async_set(
            f"{DOMAIN}.learned_codes",
            total_commands,
            {
                "friendly_name": "Kho Mã Lệnh RF/IR Đã Học",
                "icon": "mdi:remote-tv",
                "unit_of_measurement": "nút",
                "total_devices": len(summary_dict),
                "devices_summary": summary_dict,
                "detailed_library": codes,
            },
        )
        return codes

    async def async_record_learned(device: str, command: str, command_type: str):
        await hass.async_add_executor_job(
            _save_to_library_sync, hass, device, command, command_type
        )
        await async_refresh_library()

    async def async_remove_learned(device: str, command: str):
        await hass.async_add_executor_job(
            _delete_from_library_sync, hass, device, command
        )
        await async_refresh_library()

    hass.data[DOMAIN]["refresh_cb"] = async_refresh_library
    hass.data[DOMAIN]["record_cb"] = async_record_learned
    hass.data[DOMAIN]["remove_cb"] = async_remove_learned

    async def async_handle_learn(call: ServiceCall):
        remote_target = call.data.get(
            "remote_entity", hass.data[DOMAIN].get("remote_entity", remote_entity)
        )
        dev = call.data.get("device", "quat_tran_phong_khach")
        cmd = call.data.get("command")
        c_type = call.data.get("command_type", "rf")

        await hass.services.async_call(
            "remote",
            "learn_command",
            {
                "entity_id": remote_target,
                "device": dev,
                "command": cmd,
                "command_type": c_type,
                "timeout": 20,
            },
            blocking=True,
        )
        await async_record_learned(dev, cmd, c_type)

    async def async_handle_send(call: ServiceCall):
        remote_target = call.data.get(
            "remote_entity", hass.data[DOMAIN].get("remote_entity", remote_entity)
        )
        dev = call.data.get("device", "quat_tran_phong_khach")
        cmd = call.data.get("command")
        rep = int(call.data.get("repeats", 2))

        await hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": remote_target,
                "device": dev,
                "command": cmd,
                "num_repeats": rep,
                "delay_secs": 0.2,
            },
            blocking=True,
        )

    if not hass.services.has_service(DOMAIN, "learn_command"):
        hass.services.async_register(DOMAIN, "learn_command", async_handle_learn)
    if not hass.services.has_service(DOMAIN, "send_command"):
        hass.services.async_register(DOMAIN, "send_command", async_handle_send)

    await async_refresh_library()
    await hass.config_entries.async_forward_entry_setups(entry, ["fan"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Gỡ bỏ tích hợp."""
    return await hass.config_entries.async_unload_platforms(entry, ["fan"])