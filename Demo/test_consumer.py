import threading
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Item, Goods_Tmp
from Models.Categorys import Category_Cid
import datetime
import asyncio
from config import configs
import tools
import test
import time


class Consumer(threading.Thread):
    def __init__(self, name, task, queue, event, type, loop):
        threading.Thread.__init__(self)
        self.name = "消费者" + str(name)
        self.task = task
        self.queue = queue
        self.event = event
        self.type = type
        self.loop = loop

    def run(self):
        while True:
            # 判断栈是否为空
            if self.task.empty():
                # 栈空 线程进入等待
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 判断栈是否已满，为满则在向栈取数据后，则将Flag设置为True,
                # 唤醒前所有在等待的生产者线程
                is_empty = self.task.full()
                self.queue.put('stop')
                self.save_or_update()
                if is_empty:
                    self.event.set()
                self.queue.get()
                self.queue.task_done()

    def save_or_update(self):
        start = datetime.datetime.now()
        items = []
        for i in range(self.task.qsize()):
            item = self.task.get()
            items.append(item)
            self.task.task_done()
        if self.type == 'goods_update':
            self.loop.run_until_complete(Goods.batch_update(items))
        elif type == 'goods_insert':
            self.loop.run_until_complete(Goods.batch_insert(items))
        elif self.type == 'goods_item':
            self.loop.run_until_complete(Goods_Item.batch_insert(items))
        elif self.type == 'goods_tmp':
            self.loop.run_until_complete(Goods_Tmp.batch_update(items))
        end = datetime.datetime.now()
        print(u"更新了%s：%s条，%s seconds" % (self.type, len(items), end - start))