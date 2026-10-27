"""Config Flow & Options Flow v3.2 - Tự động mồi tần số đánh thức RF."""
import asyncio
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

_LOGGER = logging.getLogger(__name__)
DOMAIN = "s11_rf_remote"

DEFAULT_DEVICES = [
    "quat_tran_phong_khach",
    "tivi_phong_khach",
    "dieu_hoa_phong_khach",
    "quat_phong_ngu",
]

DEFAULT_COMMANDS = [
    "speed_1",
    "speed_2",
    "speed_3",
    "speed_4",
    "speed_5",
    "speed_6",
    "turn_off",
    "power",
    "light",
    "reverse",
    "vol_up",
    "vol_down",
    "mute",
]


def _build_remote_selector(
    hass: HomeAssistant, current_default: str = "remote.infrared_rf_remote_control"
) -> tuple[str, selector.SelectSelector]:
    options = []
    found_ids = []

    if hass is not None:
        for state in hass.states.async_all("remote"):
            eid = state.entity_id
            fname = state.attributes.get("friendly_name", eid)
            found_ids.append(eid)
            options.append({"label": f"{fname} ({eid})", "value": eid})

    if current_default not in found_ids:
        options.insert(
            0, {"label": f"Mặc định ({current_default})", "value": current_default}
        )
        default_val = found_ids[0] if found_ids else current_default
    else:
        default_val = current_default

    sel = selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=options,
            custom_value=True,
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )
    return default_val, sel


class S11RFConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        existing_entries = self._async_current_entries()

        if user_input is not None:
            if existing_entries:
                entry = existing_entries[0]
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self.hass.data.setdefault(DOMAIN, {})["remote_entity"] = user_input[
                    "remote_entity"
                ]
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="single_instance_allowed")

            return self.async_create_entry(title="S11 RF/IR Hub", data=user_input)

        current_remote = "remote.infrared_rf_remote_control"
        if existing_entries:
            current_remote = existing_entries[0].data.get(
                "remote_entity", current_remote
            )

        default_val, remote_sel = _build_remote_selector(self.hass, current_remote)

        data_schema = vol.Schema(
            {
                vol.Required("remote_entity", default=default_val): remote_sel,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return S11RFOptionsFlowHandler(config_entry)


class S11RFOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(
        self, config_entry: config_entries.ConfigEntry | None = None
    ) -> None:
        super().__init__()
        self._fallback_entry = config_entry
        self._active_device: str = "quat_tran_phong_khach"
        self._active_command: str = "speed_1"
        self._active_type: str = "rf_315"
        self._status_banner: str = ""

    @property
    def _entry(self) -> config_entries.ConfigEntry | None:
        return getattr(self, "config_entry", None) or self._fallback_entry

    def _get_remote_entity(self) -> str:
        entry = self._entry
        if entry and entry.data:
            return entry.data.get("remote_entity", "remote.infrared_rf_remote_control")
        return self.hass.data.get(DOMAIN, {}).get(
            "remote_entity", "remote.infrared_rf_remote_control"
        )

    def _get_saved_codes(self) -> dict:
        return self.hass.data.get(DOMAIN, {}).get("storage_codes", {})

    def _get_device_options(self) -> list[str]:
        codes = self._get_saved_codes()
        devices = [str(k) for k in codes.keys() if k]
        for d in DEFAULT_DEVICES:
            if d not in devices:
                devices.append(d)
        if self._active_device and self._active_device not in devices:
            devices.insert(0, self._active_device)
        return devices

    def _get_command_options(self, device: str | None = None) -> list[str]:
        codes = self._get_saved_codes()
        cmds = []
        if device and device in codes and isinstance(codes[device], dict):
            cmds.extend([str(k) for k in codes[device].keys() if k])
        for c in DEFAULT_COMMANDS:
            if c not in cmds:
                cmds.append(c)
        if self._active_command and self._active_command not in cmds:
            cmds.insert(0, self._active_command)
        return cmds

    async def async_step_init(self, user_input=None):
        if "refresh_cb" in self.hass.data.get(DOMAIN, {}):
            try:
                await self.hass.data[DOMAIN]["refresh_cb"]()
            except Exception as err:
                _LOGGER.debug("Lỗi làm mới thư viện: %s", err)

        if user_input is not None:
            choice = user_input.get("menu_choice", "learn_command")
            if choice == "learn_command":
                return await self.async_step_learn_command()
            if choice == "library":
                return await self.async_step_library()
            if choice == "send_command":
                return await self.async_step_send_command()
            if choice == "settings":
                return await self.async_step_settings()

        data_schema = vol.Schema(
            {
                vol.Required(
                    "menu_choice", default="learn_command"
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {
                                "label": "1. 📡 Học lệnh mới (Test ngay ➔ Confirm lưu)",
                                "value": "learn_command",
                            },
                            {
                                "label": "2. 📚 Thư viện lệnh đã lưu (Xem kho, Bắn thử & Xóa)",
                                "value": "library",
                            },
                            {
                                "label": "3. ⚡ Phát thử nhanh lệnh bất kỳ",
                                "value": "send_command",
                            },
                            {
                                "label": "4. ⚙️ Cài đặt thực thể Hub S11+",
                                "value": "settings",
                            },
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)

    async def async_step_learn_command(self, user_input=None):
        errors = {}
        remote_target = self._get_remote_entity()

        if user_input is not None:
            dev = str(user_input["device"]).strip()
            cmd = str(user_input["command"]).strip()
            c_type = user_input["command_type"]

            self._active_device = dev
            self._active_command = cmd
            self._active_type = c_type

            # Tự động mồi tần số ngầm nếu chọn RF 315MHz
            if c_type == "rf_315":
                for eid in (
                    f"number.{remote_target.split('.')[-1]}_rf_frequency",
                    f"number.{remote_target.split('.')[-1]}_frequency",
                ):
                    if self.hass.states.get(eid):
                        try:
                            # Bước 1: Mồi sang 433 để ép cập nhật state
                            await self.hass.services.async_call(
                                "number", "set_value", {"entity_id": eid, "value": 433.92}
                            )
                            await asyncio.sleep(0.3)
                            # Bước 2: Kéo về 315 để Hub kích hoạt dải thu thực tế
                            await self.hass.services.async_call(
                                "number", "set_value", {"entity_id": eid, "value": 315.00}
                            )
                            await asyncio.sleep(0.3)
                        except Exception:
                            pass

            service_payload = {
                "entity_id": remote_target,
                "device": dev,
                "command": cmd,
                "timeout": 20,
            }

            if c_type == "rf_315":
                service_payload["command_type"] = "rf"
                service_payload["frequency"] = 315.00
            elif c_type == "rf_433":
                service_payload["command_type"] = "rf"
                service_payload["frequency"] = 433.92
            else:
                service_payload["command_type"] = "ir"

            try:
                try:
                    await self.hass.services.async_call(
                        "remote", "learn_command", service_payload, blocking=True
                    )
                except Exception:
                    clean_payload = {
                        "entity_id": remote_target,
                        "device": dev,
                        "command": cmd,
                        "command_type": "rf" if "rf" in c_type else "ir",
                        "timeout": 20,
                    }
                    await self.hass.services.async_call(
                        "remote", "learn_command", clean_payload, blocking=True
                    )

                tag_type = "RF (315/433)" if "rf" in c_type else "IR"
                if "record_cb" in self.hass.data.get(DOMAIN, {}):
                    await self.hass.data[DOMAIN]["record_cb"](dev, cmd, tag_type)

                self._status_banner = (
                    f"🎯 Đã bắt được mã {tag_type} cho nút [{cmd}] của thiết bị [{dev}]!"
                )
                return await self.async_step_confirm_test()

            except Exception as err:
                _LOGGER.error("Lỗi khi học lệnh trên %s: %s", remote_target, err)
                errors["base"] = "learn_failed"

        device_opts = self._get_device_options()
        cmd_opts = self._get_command_options(self._active_device)
        default_cmd = self._active_command if self._active_command else "speed_1"

        data_schema = vol.Schema(
            {
                vol.Required(
                    "device", default=self._active_device
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=device_opts,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("command", default=default_cmd): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=cmd_opts,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    "command_type", default=self._active_type
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {
                                "label": "📡 Sóng RF 315MHz (Báo động, Cửa cuốn, Quạt Tuya)",
                                "value": "rf_315",
                            },
                            {
                                "label": "📡 Sóng RF 433MHz (Cửa cuốn chuẩn, Chuông cửa)",
                                "value": "rf_433",
                            },
                            {
                                "label": "🔴 Hồng ngoại IR (Tivi, Điều hòa, Quạt IR)",
                                "value": "ir",
                            },
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="learn_command",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"remote": remote_target},
        )

    async def async_step_confirm_test(self, user_input=None):
        remote_target = self._get_remote_entity()

        if user_input is not None:
            choice = user_input.get("action_choice", "test")
            repeats = int(user_input.get("repeats", 2))

            if choice == "test":
                try:
                    await self.hass.services.async_call(
                        "remote",
                        "send_command",
                        {
                            "entity_id": remote_target,
                            "device": self._active_device,
                            "command": self._active_command,
                            "num_repeats": repeats,
                            "delay_secs": 0.2,
                        },
                        blocking=True,
                    )
                    self._status_banner = (
                        f"✅ Đã bắn thử [{self._active_command}] ({repeats} lần lặp). "
                        "Thiết bị đã phản hồi chưa?"
                    )
                except Exception as err:
                    self._status_banner = f"❌ Bắn thử thất bại: {err}"
                return await self.async_step_confirm_test(None)

            if choice == "save_and_next":
                if self._active_command.startswith("speed_"):
                    try:
                        num = int(self._active_command.split("_")[1])
                        if num < 6:
                            self._active_command = f"speed_{num + 1}"
                        else:
                            self._active_command = "turn_off"
                    except Exception:
                        pass
                return await self.async_step_learn_command(None)

            if choice == "relearn":
                return await self.async_step_learn_command(None)

            if choice == "delete_abort":
                try:
                    await self.hass.services.async_call(
                        "remote",
                        "delete_command",
                        {
                            "entity_id": remote_target,
                            "device": self._active_device,
                            "command": self._active_command,
                        },
                        blocking=True,
                    )
                except Exception:
                    pass
                if "remove_cb" in self.hass.data.get(DOMAIN, {}):
                    await self.hass.data[DOMAIN]["remove_cb"](
                        self._active_device, self._active_command
                    )
                return await self.async_step_init(None)

            return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required("action_choice", default="test"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {
                                "label": "🚀 Phát thử lệnh vừa học (Test ngay)",
                                "value": "test",
                            },
                            {
                                "label": "✅ Xác nhận chuẩn & Hoàn tất (Confirm & Close)",
                                "value": "confirm",
                            },
                            {
                                "label": "➕ Xác nhận chuẩn & Học tiếp nút khác",
                                "value": "save_and_next",
                            },
                            {
                                "label": "🔄 Thiết bị chưa nhận - Học lại (Re-learn)",
                                "value": "relearn",
                            },
                            {
                                "label": "🗑️ Hủy & Xóa mã vừa học",
                                "value": "delete_abort",
                            },
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Optional("repeats", default=2): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=5, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="confirm_test",
            data_schema=data_schema,
            description_placeholders={
                "status_info": self._status_banner,
                "device": self._active_device,
                "command": self._active_command,
                "wave_type": self._active_type.upper(),
            },
        )

    async def async_step_library(self, user_input=None):
        remote_target = self._get_remote_entity()
        if "refresh_cb" in self.hass.data.get(DOMAIN, {}):
            try:
                await self.hass.data[DOMAIN]["refresh_cb"]()
            except Exception:
                pass

        codes = self._get_saved_codes()

        if user_input is not None:
            lib_action = user_input.get("lib_action", "close")
            selected = user_input.get("selected_item", "")

            if lib_action == "back_menu":
                return await self.async_step_init(None)

            if lib_action == "close" or not selected or "::" not in selected:
                if lib_action == "add_new":
                    return await self.async_step_learn_command(None)
                return self.async_create_entry(title="", data={})

            dev, cmd = selected.split("::", 1)
            self._active_device = dev
            self._active_command = cmd

            if lib_action == "test":
                try:
                    await self.hass.services.async_call(
                        "remote",
                        "send_command",
                        {
                            "entity_id": remote_target,
                            "device": dev,
                            "command": cmd,
                            "num_repeats": 2,
                            "delay_secs": 0.2,
                        },
                        blocking=True,
                    )
                    self._status_banner = (
                        f"🚀 Đã phát thử thành công: [{dev}] ➔ [{cmd}]!"
                    )
                except Exception as err:
                    self._status_banner = f"❌ Phát thử thất bại: {err}"
                return await self.async_step_library(None)

            if lib_action == "relearn":
                return await self.async_step_learn_command(None)

            if lib_action == "add_new":
                self._active_command = "speed_1"
                return await self.async_step_learn_command(None)

            if lib_action == "delete":
                try:
                    await self.hass.services.async_call(
                        "remote",
                        "delete_command",
                        {
                            "entity_id": remote_target,
                            "device": dev,
                            "command": cmd,
                        },
                        blocking=True,
                    )
                except Exception:
                    pass
                if "remove_cb" in self.hass.data.get(DOMAIN, {}):
                    await self.hass.data[DOMAIN]["remove_cb"](dev, cmd)
                self._status_banner = (
                    f"🗑️ Đã xóa nút [{cmd}] của thiết bị [{dev}] khỏi thư viện."
                )
                return await self.async_step_library(None)

        item_options = []
        summary_lines = []
        total_btns = 0

        for dev, cmds in codes.items():
            if isinstance(cmds, dict) and cmds:
                cmd_names = list(cmds.keys())
                total_btns += len(cmd_names)
                summary_lines.append(
                    f"📦 **{dev}** ({len(cmd_names)} nút): `{', '.join(cmd_names)}`"
                )
                for c_name, meta in cmds.items():
                    w_type = (
                        meta.get("type", "rf").upper()
                        if isinstance(meta, dict)
                        else "RF/IR"
                    )
                    item_options.append(
                        {
                            "label": f"📂 {dev}  ➔  🔘 {c_name} ({w_type})",
                            "value": f"{dev}::{c_name}",
                        }
                    )

        if not item_options:
            empty_msg = (
                "📭 Thư viện hiện đang trống (0 nút).\n"
                "Hãy chọn 'Học lệnh mới' bên dưới để bắt đầu thêm thiết bị!"
            )
            data_schema = vol.Schema(
                {
                    vol.Required(
                        "lib_action", default="add_new"
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"label": "📡 Học lệnh mới ngay", "value": "add_new"},
                                {"label": "🔙 Quay lại Menu chính", "value": "back_menu"},
                                {"label": "✅ Đóng cửa sổ", "value": "close"},
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            )
            return self.async_show_form(
                step_id="library",
                data_schema=data_schema,
                description_placeholders={
                    "banner": self._status_banner
                    or "Chào mừng đến với Thư viện mã S11+",
                    "library_summary": empty_msg,
                },
            )

        summary_text = (
            f"Tổng cộng: **{len(summary_lines)} thiết bị** | **{total_btns} nút lệnh** đã lưu:\n\n"
            + "\n".join(summary_lines)
        )
        default_selected = item_options[0]["value"]

        data_schema = vol.Schema(
            {
                vol.Required(
                    "selected_item", default=default_selected
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=item_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("lib_action", default="test"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {
                                "label": "🚀 Phát thử nút đang chọn (Test ngay)",
                                "value": "test",
                            },
                            {
                                "label": "🔄 Học đè lại mã cho nút đang chọn (Re-learn)",
                                "value": "relearn",
                            },
                            {
                                "label": "➕ Học thêm nút mới cho thiết bị này",
                                "value": "add_new",
                            },
                            {
                                "label": "🗑️ Xóa nút đang chọn khỏi thư viện",
                                "value": "delete",
                            },
                            {
                                "label": "🔙 Quay lại Menu chính",
                                "value": "back_menu",
                            },
                            {"label": "✅ Đóng thư viện", "value": "close"},
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )

        banner_text = (
            self._status_banner
            or "💡 Chọn một nút trong danh sách bên dưới để Phát thử, Học lại hoặc Xóa:"
        )
        self._status_banner = ""

        return self.async_show_form(
            step_id="library",
            data_schema=data_schema,
            description_placeholders={
                "banner": banner_text,
                "library_summary": summary_text,
            },
        )

    async def async_step_send_command(self, user_input=None):
        errors = {}
        remote_target = self._get_remote_entity()

        if user_input is not None:
            try:
                await self.hass.services.async_call(
                    "remote",
                    "send_command",
                    {
                        "entity_id": remote_target,
                        "device": user_input["device"],
                        "command": user_input["command"],
                        "num_repeats": int(user_input.get("repeats", 2)),
                        "delay_secs": 0.2,
                    },
                    blocking=True,
                )
                return self.async_create_entry(title="", data={})
            except Exception as err:
                _LOGGER.error("Lỗi khi phát lệnh trên %s: %s", remote_target, err)
                errors["base"] = "send_failed"

        default_cmd = self._active_command if self._active_command else "speed_1"
        data_schema = vol.Schema(
            {
                vol.Required(
                    "device", default=self._active_device
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=self._get_device_options(),
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("command", default=default_cmd): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=self._get_command_options(self._active_device),
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("repeats", default=2): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=5, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="send_command", data_schema=data_schema, errors=errors
        )

    async def async_step_settings(self, user_input=None):
        if user_input is not None:
            entry = self._entry
            if entry is not None:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
            self.hass.data.setdefault(DOMAIN, {})["remote_entity"] = user_input[
                "remote_entity"
            ]
            return self.async_create_entry(title="", data={})

        default_val, remote_sel = _build_remote_selector(
            self.hass, self._get_remote_entity()
        )
        data_schema = vol.Schema(
            {
                vol.Required("remote_entity", default=default_val): remote_sel,
            }
        )
        return self.async_show_form(step_id="settings", data_schema=data_schema)