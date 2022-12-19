import time
from smtplib import SMTP as Client
from smtpd import MessageQueueWriter

client = Client("127.0.0.1", 8025)
client.login("apa", "banan")

starts = time.time()
nbr_mails_to_send = 2000
for i in range(nbr_mails_to_send):
    with open('test/files/50k.eml', 'rb') as thefile:
        client.sendmail("use@mailheaders", "use@mailheaders", thefile.read())
    if i > 0 and 0 == (i % 200):
        print("clear queue " + str(i))
        MessageQueueWriter.redis_singleton().delete(MessageQueueWriter.QUEUE_NAME_START + "0")
        MessageQueueWriter.redis_singleton().delete(MessageQueueWriter.QUEUE_NAME_START + "1")
total_time = time.time() - starts
print("time per mail: " + str(total_time / nbr_mails_to_send))
