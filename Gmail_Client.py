import imaplib
import pyzmail
import re
import os

class Gmail_Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.username, self.password)
        self.mail.select("inbox")

    def parse(self, from_subject, regex_pattern):
        self.result, self.data = self.mail.search(None, from_subject)
        self.ids = self.data[0]
        self.id_list = self.ids.split()
        self.latest_email_id = self.id_list[-1]

        self.result, self.data = self.mail.fetch(self.latest_email_id, "(RFC822)")
        self.raw_email = self.data[0][1]
        self.msg = pyzmail.PyzMessage.factory(self.raw_email)
        self.plainText_email = self.msg.text_part.get_payload().decode(self.msg.text_part.charset)
                

        return re.finditer(regex_pattern, self.plainText_email)
