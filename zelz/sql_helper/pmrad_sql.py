from sqlalchemy import Column, Numeric, String, UnicodeText

from . import BASE, SESSION


class Pmrad(BASE):
    __tablename__ = "zedpmrads"
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
            isinstance(other, Pmrad)
            and self.chat_id == other.chat_id
            and self.keyword == other.keyword
        )


Pmrad.__table__.create(bind=SESSION.get_bind(), checkfirst=True)


def get_pmrad(chat_id, keyword):
    try:
        return SESSION.query(Pmrad).get((str(chat_id), keyword))
    finally:
        SESSION.close()


def get_pmrads(chat_id):
    try:
        return SESSION.query(Pmrad).filter(Pmrad.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def add_pmrad(chat_id, keyword, reply, f_mesg_id):
    to_check = get_pmrad(chat_id, keyword)
    if not to_check:
        adder = Pmrad(str(chat_id), keyword, reply, f_mesg_id)
        SESSION.add(adder)
        SESSION.commit()
        return True
    rem = SESSION.query(Pmrad).get((str(chat_id), keyword))
    SESSION.delete(rem)
    SESSION.commit()
    adder = Pmrad(str(chat_id), keyword, reply, f_mesg_id)
    SESSION.add(adder)
    SESSION.commit()
    return False


def remove_pmrad(chat_id, keyword):
    to_check = get_pmrad(chat_id, keyword)
    if not to_check:
        return False
    rem = SESSION.query(Pmrad).get((str(chat_id), keyword))
    SESSION.delete(rem)
    SESSION.commit()
    return True


def remove_all_pmrads(chat_id):
    if saved_pmrad := SESSION.query(Pmrad).filter(Pmrad.chat_id == str(chat_id)):
        saved_pmrad.delete()
        SESSION.commit()
