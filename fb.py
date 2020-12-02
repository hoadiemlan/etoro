from fbchat import Client
from fbchat.models import *
from getpass import getpass
import time
username = "senfosic748@gmail.com"
# password = "kieupham3315"
password = "kieupham123"
# username = "lechihieu41000944@gmail.com"
# password = "T*********1"
client = Client(username, password)

name = "hieunctu"

friends = client.searchForUsers(name)
friend = friends[0]
uid = friend.uid
msg = "I love you"
# sent = client.send(msg, thread_id=uid, thread_type=ThreadType.USER)
sent = client.send(Message(text=msg), thread_id=uid, thread_type=ThreadType.USER)
# for i in range(1505):
#     # time.sleep(2)
#     sent = client.send(Message(text=msg + " "+ str(i)), thread_id=uid, thread_type=ThreadType.USER)
