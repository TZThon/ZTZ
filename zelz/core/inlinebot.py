import json
import math
import os
import random
import re
import time
from uuid import uuid4
from platform import python_version
from telethon import Button, types, version
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery
from zelz import zedub, zedversion, StartTime
from ..Config import Config
from ..helpers.functions import rand_key, zedalive, check_data_base_heal_th, get_readable_time
from ..plugins import mention
from ..sql_helper.globals import gvarstatus
from . import CMD_INFO, GRP_INFO, PLG_INFO, check_owner
from .logger import logging

LOGS = logging.getLogger(__name__)

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\<buttonurl:(?:/{0,2})(.+?)(:same)?\>)")
MEDIA_PATH_REGEX = re.compile(r"(:?\<\bmedia:(:?(?:.*?)+)\>)")
tr = Config.COMMAND_HAND_LER

def getkey(val):
    for key, value in GRP_INFO.items():
        for plugin in value:
            if val == plugin:
                return key
    return None

def get_thumb(name):
    url = f"https://github.com/TgCatUB/CatUserbot-Resources/blob/master/Resources/Inline/{name}?raw=true"
    return types.InputWebDocument(url=url, size=0, mime_type="image/png", attributes=[])

def ibuild_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb

@zedub.tgbot.on(InlineQuery)
async def inline_handler(event):  # sourcery no-metrics
    builder = event.builder
    result = None
    query = event.text
    string = query.lower()
    query.split(" ", 2)
    str_y = query.split(" ", 1)
    string.split()
    query_user_id = event.query.user_id
    if query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS:
        hmm = re.compile("troll (.*) (.*)")
        match = re.findall(hmm, query)
        inf = re.compile("secret (.*) (.*)")
        match2 = re.findall(inf, query)
        hid = re.compile("hide (.*)")
        match3 = re.findall(hid, query)
        if match or match2 or match3:
            user_list = []
            if match3:
                sandy = "Chat"
                query = query[5:]
                info_type = ["hide", "can't", "Read Message "]
            else:
                sandy = ""
                if match:
                    query = query[6:]
                    info_type = ["troll", "can't", "show message 🔐"]
                elif match2:
                    query = query[7:]
                    info_type = ["secret", "can", "show message 🔐"]
                if "|" in query:
                    iris, query = query.replace(" |", "|").replace("| ", "|").split("|")
                    users = iris.split(" ")
                else:
                    user, query = query.split(" ", 1)
                    users = [user]
                for user in users:
                    usr = int(user) if user.isdigit() else user
                    try:
                        u = await event.client.get_entity(usr)
                    except ValueError:
                        return
                    if u.username:
                        sandy += f"@{u.username}"
                    else:
                        sandy += f"[{u.first_name}](tg://user?id={u.id})"
                    user_list.append(u.id)
                    sandy += " "
                sandy = sandy[:-1]
            old_msg = os.path.join("./zelz", f"{info_type[0]}.txt")
            try:
                jsondata = json.load(open(old_msg))
            except Exception:
                jsondata = False
            timestamp = int(time.time() * 2)
            new_msg = {
                str(timestamp): {"text": query}
                if match3
                else {"userid": user_list, "text": query}
            }
            buttons = [Button.inline(info_type[2], data=f"{info_type[0]}_{timestamp}")]
            result = builder.article(
                title=f"{info_type[0].title()} message  to {sandy}.",
                description="Send hidden text in chat."
                if match3
                else f"Only he/she/they {info_type[1]} open it.",
                thumb=get_thumb(f"{info_type[0]}.png"),
                text="✖✖✖"
                if match3
                else f"🔒 A whisper message to {sandy}, Only he/she can open it.",
                buttons=buttons,
            )
            await event.answer([result] if result else None)
            if jsondata:
                jsondata.update(new_msg)
                json.dump(jsondata, open(old_msg, "w"))
            else:
                json.dump(new_msg, open(old_msg, "w"))
        elif string == "pmpermit":
            controlpmch = gvarstatus("pmchannel") or None
            if controlpmch is not None:
                zchannel = controlpmch.replace("@", "")
                buttons = [[Button.url("⌔ قنـاتـي ⌔", f"https://t.me/{zchannel}")]]
            else:
                buttons = [[Button.url("𝗭𝗧𝗵𝗼𝗻", "https://t.me/ZThon")]]
            PM_PIC = gvarstatus("pmpermit_pic")
            if PM_PIC:
                CAT = [x for x in PM_PIC.split()]
                PIC = list(CAT)
                CAT_IMG = random.choice(PIC)
            else:
                CAT_IMG = None
            query = gvarstatus("pmpermit_text")
            if CAT_IMG and CAT_IMG.endswith((".jpg", ".jpeg", ".png")):
                result = builder.photo(
                    CAT_IMG,
                    # title="Alive zed",
                    text=query,
                    buttons=buttons,
                )
            elif CAT_IMG:
                result = builder.document(
                    CAT_IMG,
                    title="Alive cat",
                    text=query,
                    buttons=buttons,
                )
            else:
                result = builder.article(
                    title="Alive cat",
                    text=query,
                    buttons=buttons,
                )
            await event.answer([result] if result else None)
