import sys
import base64

from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.errors import AccessTokenExpiredError, AccessTokenInvalidError
from ..Config import Config
from .bothseesion import bothseesion
from .client import ZedUserBotClient
from .logger import logging

LOGS = logging.getLogger("زدثــون")
__version__ = "2.10.6"

loop = None
zzz_session = Config.STRING_SESSION

#Write Code By @zzzzl1l - @ZThon
def decrypt_session(zelzal_dev): #Write Code By @zzzzl1l - @ZThon
    zz_sess = base64.b64decode(zelzal_dev)
    return zz_sess

#Write Code By @zzzzl1l - @ZThon
if zzz_session and zzz_session.encode("utf-8").startswith(b"ZTHON"):
    zelzal_dev = zzz_session.replace("ZTHON", "")
    ZThon_Session = decrypt_session(zelzal_dev)
    session = bothseesion(ZThon_Session, LOGS)
elif zzz_session and not zzz_session.encode("utf-8").startswith(b"ZTHON"):
    session = bothseesion(ZThon_Session, LOGS)
else:
    session = "zelzal"

try:
    zedub = ZedUserBotClient(
        session=session,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    )
except Exception as e:
    print(
        f"STRING_SESSION CODE WRONG MAKE A NEW SESSION - {e}\n كود سيشن تيليثـون غير صالح .. قم باستخـراج كود جديد ؟!"
    )
    sys.exit()


try:
    zedub.tgbot = tgbot = ZedUserBotClient(
        session="ZedTgbot",
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    ).start(bot_token=Config.TG_BOT_TOKEN)
except AccessTokenExpiredError:
    LOGS.error("توكن البوت غير صالح قم باستبداله بتوكن جديد من بوت فاذر")
except AccessTokenInvalidError:
    LOGS.error("توكن البوت غير صحيح قم باستبداله بتوكن جديد من بوت فاذر")
