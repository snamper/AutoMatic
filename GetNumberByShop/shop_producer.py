import threading
import random
import tools
import asyncio
import time


class Producer(threading.Thread):
    def __init__(self, name, q_shops, queue, event, global_goods_ids):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.queue = queue
        self.event = event
        self.q_shops = q_shops
        self.global_goods_ids = global_goods_ids

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.q_shops.empty():
                self.event.set()
                break
            shop_id = self.q_shops.get().shop_id
            print("开始抓取店铺%s" % shop_id)
            self.q_shops.task_done()
            page = 0
            shop_key = []
            while True:
                json = loop.run_until_complete(tools.get_first_goods_by_shop(shop_id, page))
                if json is None:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data') is None or len(json.get('data')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data').get('list') is None or len(json.get('data').get('list')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                items = json.get('data').get('list')
                for item in items:
                    goods_id = item.get('product_id')
                    if self.global_goods_ids.__contains__(goods_id):
                        continue
                    self.global_goods_ids.append(goods_id)
                    one = loop.run_until_complete(tools.get_goods_by_id(goods_id))
                    if one:
                        item = one.get('data')
                        shop_id = item.get('shop_id')
                        shop_tel = item.get('shop_tel')
                        key = '%s %s' % (shop_id,shop_tel)
                        if shop_key.__contains__(key):
                            continue
                        shop_key.append(key)
                    else:
                        continue
                    # 判断栈是否已经满
                    if self.queue.full():
                        print("队列已满，总数%s" % self.queue.qsize())
                        # 栈满 线程进入等待
                        self.event.wait()
                        # 线程唤醒后将flag设置为False
                        if self.event.isSet():
                            self.event.clear()
                    else:
                        # 判断栈是否为空，为空则在向栈添加数据后，则将Flag设置为True,
                        # 唤醒前所有在等待的消费者线程
                        if self.queue.empty():
                            # 未满 向栈添加数据
                            self.queue.put(item)
                            # print("生产数据：%s" + str(item))
                            # 将Flag设置为True
                            self.event.set()
                        else:
                            # 未满 向栈添加数据
                            self.queue.put(item)
                            self.event.set()
                            # print("生产数据：%s" + str(item))
                page += 1
            page = 0
            while True:
                json = loop.run_until_complete(tools.get_goods_by_shop(shop_id, page))
                # print("%s第%s页" % (shop_id, page))
                # time.sleep(3)
                if json is None:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data') is None or len(json.get('data').get('list')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data').get('list') is None or len(json.get('data').get('list')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                items = json.get('data').get('list')
                for item in items:
                    sell_num = item.get('sell_num')
                    goods_id = item.get('product_id')
                    one = loop.run_until_complete(tools.get_goods_by_id(goods_id))
                    if one:
                        item = one.get('data')
                        shop_id = item.get('shop_id')
                        shop_tel = item.get('shop_tel')
                        key = '%s %s' % (shop_id, shop_tel)
                        if shop_key.__contains__(key):
                            continue
                        shop_key.append(key)
                    else:
                        print(item)
                        continue
                    if self.global_goods_ids.__contains__(goods_id):
                        continue
                    self.global_goods_ids.append(goods_id)
                    # 判断栈是否已经满
                    if self.queue.full():
                        print("队列已满，总数%s" % self.queue.qsize())
                        # 栈满 线程进入等待
                        self.event.wait()
                        # 线程唤醒后将flag设置为False
                        if self.event.isSet():
                            self.event.clear()
                    else:
                        # 判断栈是否为空，为空则在向栈添加数据后，则将Flag设置为True,
                        # 唤醒前所有在等待的消费者线程
                        if self.queue.empty():
                            # 未满 向栈添加数据
                            self.queue.put(item)
                            # print("生产数据：%s" + str(item))
                            # 将Flag设置为True
                            self.event.set()
                        else:
                            # 未满 向栈添加数据
                            self.queue.put(item)
                            # self.event.set()
                            # print("生产数据：%s" + str(item))
                page += 1
        print(self.name + "结束")
