import detman
#import datetime
#import threading
from apscheduler.schedulers.background import BackgroundScheduler
from detman import detman




sched = BackgroundScheduler()


def process():
    smgr=detman()
    smgr.login_db()
    smgr.login("Lencha")
    smgr.check_topics_position()
    #smgr.clear_topiс_bucket("/sp/bucket/82621/orders/")
    smgr.raise_topics()

sched.add_job(process, 'interval', seconds=20)
sched.start()




#print("START : {}".format(datetime.datetime.now()))
while True : i=1

#process()

#sitemanager.raise_topics()
#sitemanager.get_user_id("lencha")
#sitemanager.login()
#sitemanager.clear_topiс_bucket("/sp/bucket/82621/orders/")
#sitemanager.clear_topiс_bucket_arc("/sp/bucket/82621/orders/")
##select t.id,t.interval_minutes,(strftime('%s','now')-t.last_up_time)/60 d,t.name from topics t where (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes and active=
#sitemanager.add_order("/sp/igr/82621/photos/")
#sitemanager.reject_last_order("/sp/bucket/82621/orders/")


#sitemanager.get_topics()

