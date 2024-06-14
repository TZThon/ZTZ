import asyncio
import os
import re
import urllib
import PIL
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import clippy
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import convert_toimage, reply_id

# ======================================================================================================================================================================================
vars_list = {
    "lbg": "LOGO_BACKGROUND",
    "lfc": "LOGO_FONT_COLOR",
    "lfs": "LOGO_FONT_SIZE",
    "lfh": "LOGO_FONT_HEIGHT",
    "lfw": "LOGO_FONT_WIDTH",
    "lfsw": "LOGO_FONT_STROKE_WIDTH",
    "lfsc": "LOGO_FONT_STROKE_COLOR",
    "lf": "LOGO_FONT",
}
# ======================================================================================================================================================================================
plugin_category = "الترفيه"


@zedub.zed_cmd(
    pattern="لوجو(?: |$)(.*)",
    command=("لوجو", plugin_category),
    info={
        "header": "Make a logo in image or sticker",
        "description": "Just a fun purpose plugin to create logo in image or in sticker.",
        "flags": {
            "s": "To create a logo in sticker instade of image.",
        },
        "usage": [
            "{tr}logo <text>",
            "{tr}slogo <text>",
        ],
        "examples": [
            "{tr}logo Cat",
            "{tr}slogo Cat",
        ],
    },
)
async def very(event):
    "To create a logo"
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)
    reply = await event.get_reply_message()
    if not text and reply:
        text = reply.text
    if not text:
        return await edit_delete(event, "**ಠ∀ಠ Gimmi text to make logo**")
    reply_to_id = await reply_id(event)
    zedevent = await edit_or_reply(event, "`Processing.....`")
    LOGO_FONT_SIZE = gvarstatus("LOGO_FONT_SIZE") or 220
    LOGO_FONT_WIDTH = gvarstatus("LOGO_FONT_WIDTH") or 2
    LOGO_FONT_HEIGHT = gvarstatus("LOGO_FONT_HEIGHT") or 2
    LOGO_FONT_COLOR = gvarstatus("LOGO_FONT_COLOR") or "red"
    LOGO_FONT_STROKE_WIDTH = gvarstatus("LOGO_FONT_STROKE_WIDTH") or 0
    LOGO_FONT_STROKE_COLOR = gvarstatus("LOGO_FONT_STROKE_COLOR") or None
    LOGO_BACKGROUND = (
        gvarstatus("LOGO_BACKGROUND")
        or "https://raw.githubusercontent.com/Jisan09/Files/main/backgroud/black.jpg"
    )

    LOGO_FONT = (
        gvarstatus("LOGO_FONT")
        or "https://github.com/Jisan09/Files/blob/main/fonts/Streamster.ttf?raw=true"
    )

    if not os.path.isdir("./temp"):
        os.mkdir("./temp")
    if not os.path.exists("temp/bg_img.jpg"):
        urllib.request.urlretrieve(LOGO_BACKGROUND, "temp/bg_img.jpg")
    img = Image.open("./temp/bg_img.jpg")
    draw = ImageDraw.Draw(img)
    if not os.path.exists("temp/logo.ttf"):
        urllib.request.urlretrieve(LOGO_FONT, "temp/logo.ttf")
    font = ImageFont.truetype("temp/logo.ttf", int(LOGO_FONT_SIZE))
    image_widthz, image_heightz = img.size
    w, h = draw.textsize(text, font=font)
    h += int(h * 0.21)
    try:
        draw.text(
            (
                (image_widthz - w) / float(LOGO_FONT_WIDTH),
                (image_heightz - h) / float(LOGO_FONT_HEIGHT),
            ),
            text,
            font=font,
            fill=LOGO_FONT_COLOR,
            stroke_width=int(LOGO_FONT_STROKE_WIDTH),
            stroke_fill=LOGO_FONT_STROKE_COLOR,
        )
    except OSError:
        draw.text(
            (
                (image_widthz - w) / float(LOGO_FONT_WIDTH),
                (image_heightz - h) / float(LOGO_FONT_HEIGHT),
            ),
            text,
            font=font,
            fill=LOGO_FONT_COLOR,
            stroke_width=0,
            stroke_fill=None,
        )
    file_name = "badcat.png"
    img.save(file_name, "png")
    if cmd == "":
        await event.client.send_file(
            event.chat_id,
            file_name,
            reply_to=reply_to_id,
        )
    elif cmd == "s":
        await clippy(event.client, file_name, event.chat_id, reply_to_id)
    await zedevent.delete()
    if os.path.exists(file_name):
        os.remove(file_name)
