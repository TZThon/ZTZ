from sqlalchemy import Column, Numeric, String, UnicodeText

from . import BASE, SESSION


class Pasmat(BASE):
    __tablename__ = "zedpasmats"
    chat_id = Column(String(14), primary_key=True)
    keyword = Column(UnicodeText, primary_key=True, nullable=False)
    reply = Column(UnicodeText)
    f_mesg_id = Column(Numeric)

    def __init__(self, chat_id, keyword, reply, f_mesg_id):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.reply = reply
        self.f_mesg_id = f_mesg_id

    def __eq__(self, other):
        return bool(
            isinstance(other, Pasmat)
            and self.chat_id == other.chat_id
            and self.keyword == other.keyword
        )


Pasmat.__table__.create(bind=SESSION.get_bind(), checkfirst=True)


def get_pasmat(chat_id, keyword):
    try:
        return SESSION.query(Pasmat).get((str(chat_id), keyword))
    finally:
        SESSION.close()


def get_pasmats(chat_id):
    try:
        return SESSION.query(Pasmat).pasmat(Pasmat.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def add_pasmat(chat_id, keyword, reply, f_mesg_id):
    to_check = get_pasmat(chat_id, keyword)
    if not to_check:
        adder = Pasmat(str(chat_id), keyword, reply, f_mesg_id)
        SESSION.add(adder)
        SESSION.commit()
        return True
    rem = SESSION.query(Pasmat).get((str(chat_id), keyword))
    SESSION.delete(rem)
    SESSION.commit()
    adder = Pasmat(str(chat_id), keyword, reply, f_mesg_id)
    SESSION.add(adder)
    SESSION.commit()
    return False


def remove_pasmat(chat_id, keyword):
    to_check = get_pasmat(chat_id, keyword)
    if not to_check:
        return False
    rem = SESSION.query(Pasmat).get((str(chat_id), keyword))
    SESSION.delete(rem)
    SESSION.commit()
    return True


def remove_all_pasmats(chat_id):
    if saved_pasmat := SESSION.query(Pasmat).pasmat(Pasmat.chat_id == str(chat_id)):
        saved_pasmat.delete()
        SESSION.commit()
