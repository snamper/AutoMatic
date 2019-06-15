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
    def __init__(self, name, task, q_goods, q_goods_item, q_goods_tmp, event,goods_id_object,cids):
        threading.Thread.__init__(self)
        self.name = "处理者" + str(name)
        self.task = task
        self.q_goods = q_goods
        self.q_goods_item = q_goods_item
        self.q_goods_tmp = q_goods_tmp
        self.event = event
        self.goods_id_object = goods_id_object
        self.cids = cids

    def run(self):
        while True:
            # 判断栈是否为空
            if self.task.empty() or self.q_goods.full() or self.q_goods_item.full() or self.q_goods_tmp.full():
                # 栈空 线程进入等待
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 判断栈是否已满，为满则在向栈取数据后，则将Flag设置为True,
                # 唤醒前所有在等待的生产者线程
                is_empty = False
                if self.task.full() or self.q_goods.empty() or self.q_goods_item.empty() or self.q_goods_tmp.empty():
                    is_empty = True
                self.do_entitry()
                if is_empty:
                    self.event.set()
                self.task.task_done()

    def do_entitry(self):
        item = self.task.get()
        goods_id = item.get('product_id')
        if not goods_id:
            return
        goods = self.goods_id_object.get(goods_id)

        sell_num = int(item.get('sell_num'))
        shop_id = item.get('shop_id')
        goods_price = item.get('discount_price') / 100
        goods_name = item.get('name')
        cid = item.get('third_cid')
        if not self.cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('img')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            sell_num_old = goods.sell_num
            add_num = sell_num - sell_num_old
            goods.shop_id = shop_id
            goods.cid = cid
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            if time_now != time_last_edit:
                goods.add_num = 0
            elif add_num >= 0:
                goods.add_num = goods.add_num + add_num
            if goods.add_num < 0:
                print(item)
                print("goods_id:%s;add_num:%s;sell_num:%s;last_sell_num:%s;last:%s;" % (goods.goods_id,add_num,sell_num,sell_num_old,goods.add_num))
            goods.sell_num = sell_num
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            goods.edit_time = datetime.datetime.now()

            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100 or item_add_num < 0:
                goods.item_last_sell_num = sell_num
            # await goods.update()
            self.q_goods.put(goods)
        else:
            raise Exception("出错！数据库中没有查询到相应值")
        if item_add_num >= 100:
            goods_item = Goods_Item()
            goods_item.goods_id = goods.id
            goods_item.sell_num = sell_num
            goods_item.add_num = item_add_num
            # await goods_item.save()
            self.q_goods_item.put(goods_item)
        if goods.add_num > 0:
            # await Goods_Tmp.del_by('goods_id=?', goods.id)
            tmp = Goods_Tmp()
            tmp.goods_id = goods.id
            tmp.add_num = goods.add_num
            tmp.sell_num = goods.sell_num
            tmp.edit_time = datetime.datetime.now()
            # await tmp.save()
            self.q_goods_tmp.put(tmp)

