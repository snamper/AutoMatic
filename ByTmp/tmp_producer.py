import threading
import random
import tools
import asyncio
import time
import datetime
from Models.Goods import Goods, Goods_Item, Goods_Tmp


class Producer(threading.Thread):
    def __init__(self, name, task, q_goods, q_goods_item, q_goods_tmp, event, global_goods_ids,
                 goods_id_object, goods_id_tmp, cids):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.task = task
        self.q_goods = q_goods
        self.q_goods_item = q_goods_item
        self.q_goods_tmp = q_goods_tmp
        self.event = event
        self.global_goods_ids = global_goods_ids
        self.goods_id_object = goods_id_object
        self.goods_id_tmp = goods_id_tmp
        self.cids = cids

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.task.empty():
                break
            goods_id = self.task.get()
            self.task.task_done()
            item = loop.run_until_complete(tools.get_num_goods_by_id(goods_id))
            if not item or not item.get('data'):
                continue
            if not item.get('data').get('name') or item.get('data').get('name') == '':
                print("下架： %s" % goods_id)
                continue
            if self.global_goods_ids.__contains__(goods_id):
                continue
            self.global_goods_ids.append(goods_id)
            item = item.get('data')
            # 判断栈是否已经满
            if self.q_goods.full() or self.q_goods_item.full() or self.q_goods_tmp.full():
                print("队列已满，总数%s" % self.q_goods.qsize())
                # 栈满 线程进入等待
                self.event.set()
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                is_empty = False
                if self.q_goods.empty() or self.q_goods_item.empty() or self.q_goods_tmp.empty():
                    is_empty = True
                self.do_entitry(item)
                if is_empty:
                    self.event.set()
                    # print(" %s 唤起其他人" % self.name)
        print(self.name + "结束")

    def do_entitry(self, item):
        goods_id = item.get('product_id')
        if not goods_id:
            return
        goods = self.goods_id_object.get(goods_id)
        sell_num = tools.get_sell_num(item.get('sell_num'))
        shop_id = item.get('shop_id')
        goods_price = item.get('discount_price') / 100
        goods_name = item.get('name')
        cid = item.get('third_cid')
        if not self.cids.__contains__(cid):
            cid = item.get('second_cid')
        first_cid = item.get('first_cid')
        second_cid = item.get('second_cid')
        third_cid = item.get('third_cid')
        goods_picture_url = item.get('img')
        biz_type = item.get('biz_type')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            sell_num_old = goods.sell_num
            add_num = sell_num - sell_num_old
            if add_num < 0:
                return
            goods.shop_id = shop_id
            goods.cid = cid
            goods.first_cid = first_cid
            goods.second_cid = second_cid
            goods.third_cid = third_cid
            goods.biz_type = biz_type
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            if time_now != time_last_edit:
                goods.add_num = 0
            elif add_num >= 0:
                goods.add_num = goods.add_num + add_num
            if goods.add_num < 0:
                return
            goods.sell_num = sell_num
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            goods.edit_time = datetime.datetime.now()

            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100 or item_add_num < 0:
                goods.item_last_sell_num = sell_num
            self.q_goods.put(goods)
        else:
            raise Exception("出错！数据库中没有查询到相应值")
        if item_add_num >= 100:
            goods_item = Goods_Item()
            goods_item.goods_id = goods.id
            goods_item.sell_num = sell_num
            goods_item.add_num = item_add_num
            self.q_goods_item.put(goods_item)
        if goods.add_num > 0:
            tmp = self.goods_id_tmp.get(goods.id)
            if not tmp:
                tmp = Goods_Tmp()
            tmp.goods_id = goods.id
            tmp.add_num = goods.add_num
            tmp.sell_num = goods.sell_num
            tmp.edit_time = datetime.datetime.now()
            self.q_goods_tmp.put(tmp)

