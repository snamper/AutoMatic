from urllib.parse import urlencode
import requests
import aiohttp
import datetime

pc_user_agent =  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'

phton_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'



#通过店铺获取商品
async def aiohttp_get_page(shop_id, page):
    params = {
        'shop_id': shop_id,
        'page': page,
        'pageSize': 100,
        'b_type_new': 0,
        'type':5,
        'sort':1
    }
    # url = 'https://haohuo.snssdk.com/shop/goodsList?' + urlencode(params)
    url = 'https://haohuo.snssdk.com/productcategory/getShopList?' + urlencode(params)
    headers = {
        'user-agent': phton_user_agent,
        'Origin': 'https://haohuo.jinritemai.com',
        'Referer': 'https://haohuo.jinritemai.com/views/shop/index?id=%s' %shop_id
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url,headers=headers,timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print("请求异常：%s" % str(e))
            pass


#通过分类获取商品
async def aiohttp_get_goods_by_cid(cids,id,parentid, page):
    params = {
        'second_cid': cids,
        'type': 5,
        'sort': 1,#销量排序
        'page': page,
        'pageSize': 10
    }
    url = "https://haohuo.snssdk.com/productcategory/getList?" + urlencode(params)
    headers = {
        'user-agent': phton_user_agent,
        'Origin': 'https://haohuo.jinritemai.com',
        'Referer': 'https://haohuo.jinritemai.com/views/channel/categorychoose?cids=%s&parent_id=%s&id=%s&fresh_come=undefined&origin_type=3030005&origin_id=0&new_source_type=100&new_source_id=0&source_type=100&source_id=0&come_from=0' % (cids,parentid,id)
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url,headers=headers,timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print("请求异常：%s" % str(e))
            pass


#通过商品ID更新商品
async def aiohttp_get_goods_by_id(goods_id):
    params = {
        'id': goods_id,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/product/fxgajaxstaticitem?" + urlencode(params)
    header2s = {
        'user-agent': phton_user_agent,
        'Referer': 'https://haohuo.snssdk.com/views/product/item2?id=%s' % goods_id,
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url,headers=header2s,timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print("请求异常：%s" % str(e))
            pass


def get_page(shop_id, page):
    params = {
        'shop_id': shop_id,
        'page': page,
        'pageSize': 100
    }
    url = 'https://haohuo.snssdk.com/shop/goodsList?' + urlencode(params)
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        'Origin': 'https://haohuo.jinritemai.com',
        'Referer': 'https://haohuo.jinritemai.com/views/shop/index?id=%s&origin_type=3030005&origin_id=0&new_source_type=47&new_source_id=0&source_type=47&source_id=0&come_from=0&fxg_req_id=' % shop_id
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("请求异常：%s" % str(e))
        pass


def get_goods(goods_id):
    params = {
        'id': goods_id,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/product/fxgajaxstaticitem?" + urlencode(params)
    header2s = {
        'user-agent': phton_user_agent,
        'Referer': 'https://haohuo.snssdk.com/views/product/item2?id=%s' % goods_id,
    }
    try:
        response = requests.get(url, headers=header2s)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("请求异常：%s" % e)
        pass

#获取所有分类信息
def get_category_all():
    params = {
        'version': 1,
        'is_category': 1
    }
    url = "https://haohuo.snssdk.com/channel/ajaxCategoryAll?" + urlencode(params)
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        'Origin': 'https://haohuo.jinritemai.com',
        'Referer': 'https://haohuo.jinritemai.com/views/channel/categories?a=1&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("请求异常：%s" % e)
        pass

def list_to_dict(lists,key):
    dit = {}
    for element in lists:
        if key not in element.__fields__ and key is not element.__primary_key__:
            raise Exception("Key %s 不存在！" % key)
        dit[element[key]] = element
    return dit

def get_temp_table():
    time_now = datetime.datetime.now().strftime("%Y%m%d")
    return "tmp_%s" % time_now


if __name__ == '__main__':
    print(get_temp_table())