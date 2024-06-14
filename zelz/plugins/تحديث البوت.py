import asyncio
import contextlib
import os
import sys
from asyncio.exceptions import CancelledError
from time import sleep

import heroku3
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from . import HEROKU_APP, UPSTREAM_REPO_URL, zedub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _zedutils
from ..sql_helper.global_collection import (
    add_to_collectionlist,
    del_keyword_collectionlist,
    get_collectionlist_items,
)

plugin_category = "الادوات"
cmdhd = Config.COMMAND_HAND_LER
ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger(__name__)
# -- Constants -- #

HEROKU_APP_NAME = Config.HEROKU_APP_NAME or None
HEROKU_API_KEY = Config.HEROKU_API_KEY or None
Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
OLDZED = Config.OLDZED
heroku_api = "https://api.heroku.com"

UPSTREAM_REPO_BRANCH = "master"

REPO_REMOTE_NAME = "temponame"
IFFUCI_ACTIVE_BRANCH_NAME = "master"
NO_HEROKU_APP_CFGD = "no heroku application found, but a key given? 😕 "
HEROKU_GIT_REF_SPEC = "HEAD:refs/heads/master"
RESTARTING_APP = "re-starting heroku application"
IS_SELECTED_DIFFERENT_BRANCH = (
    "looks like a custom branch {branch_name} "
    "is being used:\n"
    "in this case, Updater is unable to identify the branch to be updated."
    "please check out to an official branch, and re-start the updater."
)


# -- Constants End -- #

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

requirements_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    d_form = "%d/%m/%y"
    return "".join(
        f"  • {c.summary} ({c.committed_datetime.strftime(d_form)}) <{c.author}>\n"
        for c in repo.iter_commits(diff)
    )


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def update_bot(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    sandy = await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**•⎆┊تم التحـديث ⎌ بنجـاح**\n**•⎆┊جـارِ إعـادة تشغيـل بـوت زدثــون ⎋ **\n**•⎆┊انتظـࢪ مـن 2 - 1 دقيقـه . . .📟**")
    await event.client.reload(sandy)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is None:
        return await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n **•─────────────────•**\n** ⪼ لم تقـم بوضـع مربـع فـار HEROKU_API_KEY اثنـاء التنصيب وهـذا خطـأ .. قم بضبـط المتغيـر أولاً لتحديث بوت زدثــون ..؟!**", link_preview=False)
    heroku = heroku3.from_key(HEROKU_API_KEY)
    heroku_applications = heroku.apps()
    if HEROKU_APP_NAME is None:
        await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n **•─────────────────•**\n** ⪼ لم تقـم بوضـع مربـع فـار HEROKU_APP_NAME اثنـاء التنصيب وهـذا خطـأ .. قم بضبـط المتغيـر أولاً لتحديث بوت زدثــون ..؟!**", link_preview=False)
        repo.__del__()
        return
    heroku_app = next(
        (app for app in heroku_applications if app.name == HEROKU_APP_NAME),
        None,
    )

    if heroku_app is None:
        await event.edit(
            f"{txt}\n" "**- بيانات اعتماد هيروكو غير صالحة لتنصيب تحديث زدثــون**"
        )
        return repo.__del__()
    sandy = await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n**✾╎جـارِ . . تنصـيب التحـديث الجـذري ⎌**\n**✾╎يُرجـى الانتظـار حتى تنتهـي العمليـة ⎋**\n**✾╎عـادة ما يستغـرق هـذا التحـديث مـن 5 - 4 دقائـق 📟**")
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [sandy.chat_id, sandy.id])
    except Exception as e:
        LOGS.error(e)
    ups_rem.fetch(ac_br)
    repo.git.reset("--hard", "FETCH_HEAD")
    heroku_git_url = heroku_app.git_url.replace(
        "https://", f"https://api:{HEROKU_API_KEY}@"
    )

    if "heroku" in repo.remotes:
        remote = repo.remote("heroku")
        remote.set_url(heroku_git_url)
    else:
        remote = repo.create_remote("heroku", heroku_git_url)
    try:
        remote.push(refspec="HEAD:refs/heads/master", force=True)
    except Exception as error:
        await event.edit(f"{txt}\n**Error log:**\n`{error}`")
        return repo.__del__()
    build_status = heroku_app.builds(order_by="created_at", sort="desc")[0]
    if build_status.status == "failed":
        return await edit_delete(
            event, "`Build failed!\n" "Cancelled or there were some errors...`"
        )
    try:
        remote.push("master:main", force=True)
    except Exception as error:
        await event.edit(f"{txt}\n**Here is the error log:**\n`{error}`")
        return repo.__del__()
    await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n**•⎆┊بـوتك محـدث الـى آخـر إصـدار .. سابقـاً 🤷🏻‍♀\n•⎆┊لـذلك سـوف يتـم إعـادة التشغيـل فقـط 🌐 **")
    with contextlib.suppress(CancelledError):
        await event.client.disconnect()
        if HEROKU_APP is not None:
            HEROKU_APP.restart()

@zedub.zed_cmd(
    pattern="تحدديث البووت$",
)
async def upstream(event):
    if ENV:
        if HEROKU_API_KEY is None or HEROKU_APP_NAME is None:
            return await edit_or_reply(
                event, "**- بيانات اعتماد تنصيبك غير صالحة لتنصيب تحديث زدثــون ❕❌**\n**- يجب تعييـن قيـم مربعـات الفارات التالية يدوياً من حساب هيروكـو 🛂**\n\n\n**- مربـع مفتـاح هيروكـو :** HEROKU_API_KEY\n**- مربـع اسـم التطبيـق :** HEROKU_APP_NAME"
            )
    elif os.path.exists("config.py"):
        return await edit_delete(
            event,
            f"**- أعتقد أنك على الوضـع الذاتي ..**\n**- للتحديث الذاتي ارسـل الامـر** `{cmdhd}تحديث`",
        )
    event = await edit_or_reply(event, f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⪼ يتم تنصيب التحديث  انتظر 🌐 ،**")
    off_repo = "https://github.com/ZThon-Ar/dev"
    os.chdir("/app")
    try:
        txt = (
            "`اووبـس .. لا يمكن لـ الإستمـرار بالتحديث بسبب "
            + "حـدوث بعـض المشاكـل`\n\n**سجـل الاخطـاء:**\n"
        )

        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n\n**- المسـار** {error} **غيـر مـوجـود؟!**")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n**- خطـأ غيـر متـوقـع؟!**\n{error}")
        return repo.__del__()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    with contextlib.suppress(BaseException):
        repo.create_remote("upstream", off_repo)
    zzz1 = await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**")
    await asyncio.sleep(1)
    zzz2 = await zzz1.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟷𝟶 ▬▭▭▭▭▭▭▭▭▭")
    await asyncio.sleep(1)
    zzz3 = await zzz2.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭")
    await asyncio.sleep(1)
    zzz4 = await zzz3.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟹𝟶 ▬▬▬▭▭▭▭▭▭▭")
    await asyncio.sleep(1)
    zzz5 = await zzz4.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟺𝟶 ▬▬▬▬▭▭▭▭▭▭")
    await asyncio.sleep(1)
    zzz6 = await zzz5.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭")
    await asyncio.sleep(1)
    zzz7 = await zzz6.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟼𝟶 ▬▬▬▬▬▬▭▭▭▭")
    await asyncio.sleep(1)
    zzz8 = await zzz7.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟽𝟶 ▬▬▬▬▬▬▬▭▭▭")
    await asyncio.sleep(1)
    zzz9 = await zzz8.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭") 
    await asyncio.sleep(1)
    zzzz10 = await zzz9.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟿𝟶 ▬▬▬▬▬▬▬▬▬▭") 
    await asyncio.sleep(1)
    zzzz11 = await zzzz10.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n**•─────────────────•**\n\n**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯") 
    ac_br = repo.active_branch.name
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    await deploy(zzzz11, repo, ups_rem, ac_br, txt)
