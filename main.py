from threading import Thread
from vk_bot import vk_bot
from tg_bot import func_run_teleg
from admin_panel import admin_panel_run, sender
import schedule

def sheduler():
    schedule.every().hour.do(sender)
    while True:
        schedule.run_pending()

if __name__ == '__main__':
    thr1 = Thread(target=vk_bot)
    thr2 = Thread(target=func_run_teleg)
    thr3 = Thread(target=admin_panel_run)
    thr4 = Thread(target=sheduler)
    thr1.start()
    thr2.start()
    thr3.start()
    thr4.start()