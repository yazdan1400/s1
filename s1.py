

#59ac2f63b89a2eb2295d67525af0bbd9bf41c9be
import requests
import time
from collections import deque

api_key = '59ac2f63b89a2eb2295d67525af0bbd9bf41c9be'
headers = {
    'Authorization': f'Token {api_key}',
    'Content-Type': 'application/json'
}


def get_market_price(srcdes):
    api_url = "https://api.nobitex.ir/market/stats"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if srcdes in data['stats']:  # بررسی وجود کلید
            src_toman_price = int(data['stats'][srcdes]['latest'])  # تبدیل به عدد صحیح
            return src_toman_price
        else:
            print(f"Key {srcdes} not found in stats")
            return None
    else:
        print(f"Error fetching market price: {response.status_code}")
        return None
def get_balance(src, des):
    balance_url = "https://api.nobitex.ir/users/wallets/list"
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(balance_url, headers=headers)
    print(response.reason) 
    if response.status_code == 200:
        data = response.json()
        wallets = data.get('wallets', [])
        
        src_balance = next((wallet['balance'] for wallet in wallets if wallet['currency'].lower() == src), None)
        des_balance = next((wallet['balance'] for wallet in wallets if wallet['currency'].lower() == des), None)
        print(f"{src} amount: {src_balance}")
        print(f"{des} amount: {des_balance}")
        return src_balance, des_balance
    else:
        return f"Error: {response.status_code}"



def place_order(src, des, amount, price, side):
    order_url = "https://api.nobitex.ir/market/orders/add"

    order_data = {
        'execution':'limit',
        'type': side,
        'srcCurrency': src,
        'dstCurrency': des,
        'amount':amount,
        'price': price        
    }
    response = requests.post(order_url, headers=headers, json=order_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error placing order: {response.status_code}")
        return None





def get_trade_history(token, symbol):
    url = "https://api.nobitex.ir/market/trades/list"
    headers = {
        'Authorization': f'Token {token}'
    }
    params = {
        'symbol': symbol
    }
    response = requests.get(url, headers=headers, params=params)
    
    # چاپ پاسخ خام برای بررسی
    
    
    try:
        data = response.json()
        if 'trades' in data:
            trades = data['trades']
            return trades
        else:
            return []
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decode error:", e)
        return []

def calculate_average_buy_price(trades, current_balance):
    total_amount = 0
    total_cost = 0
    price=0
    for trade in trades:
        if trade['type'] == 'buy':
            price = float(trade['price'])
            amount = float(trade['amount'])
            total_cost += price * amount
            total_amount += amount
        elif trade['type'] == 'sell':
            amount = float(trade['amount'])
            total_amount -= amount
            total_cost -= price * amount  # فرض می‌کنیم قیمت فروش برابر با قیمت خرید است
    if total_amount > 0:
        return total_cost / total_amount
    else:
        return 0

def get_wallet_balance(token, symbol):
    url = "https://api.nobitex.ir/users/wallets/list"
    headers = {
        'Authorization': f'Token {token}'
    }
    response = requests.get(url, headers=headers)
    print(response.reason)
    # چاپ پاسخ خام برای بررسی
    
    
    try:
        data = response.json()
        if 'wallets' in data:
            wallets = data['wallets']
            for wallet in wallets:
                if wallet['currency'].lower() == symbol:
                    return float(wallet['balance'])
        return 0
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decode error:", e)
        return 0




def analyze_trend(prices):
    increases = 0
    decreases = 0
    for i in range(1, len(prices)-1):
        if prices[i] > prices[i + 1]:
            increases += 1
        elif prices[i] < prices[i + 1]:
            decreases += 1
    return increases, decreases


def moving_average(lst, n=3):
    ret = []
    if len(lst) < n:
        return []  
    for i in range(len(lst) - n + 1):
        
        window = lst[i:i + n]
        avg = sum(window) / n
        ret.append(avg)
    return ret

def determine_trend(lst):
    ma = moving_average(lst)
    
    print(lst)
    if len(ma) < 2:
        return "داده‌های کافی برای تعیین روند وجود ندارد"
    if ma[-1] > ma[0]:
        return "DES"
    elif ma[-1] < ma[0]:
        return "AES"
    else:
        return "NO_ASC_DES"



def get_orderbook(symbol):
    url = f'https://api.nobitex.ir/v3/orderbook/{symbol}'
    response = requests.get(url)
    return response.json()

def calculate_total_volume(orderbook, order_type, top_n=10):
    if order_type in orderbook:  # بررسی وجود کلید
        orders = orderbook[order_type][:top_n]
        total_volume = sum(float(order[1]) for order in orders)
        return total_volume
    else:
        print(f"Key '{order_type}' not found in orderbook")
        return None


def get_active_orders(token):
    url = "https://api.nobitex.ir/market/orders/list"
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'details':'2',
        'status':'open',
        'order':'id'
    }

    response = requests.post(url, headers=headers)
    
    # چاپ پاسخ خام برای بررسی
   
    
    try:
        active_orders = response.json().get('orders', [])
        # فیلتر کردن سفارشات با وضعیت Active
        #active_orders = [order for order in orders if order.get('status') == 'open']
        return active_orders
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decode error:", e)
        return []




def cancel_order(token, clientOrderId):
    url = "https://api.nobitex.ir/market/orders/update-status"
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'clientOrderId': clientOrderId,
        'status': 'canceled'
    }
    response = requests.post(url, headers=headers, json=data)
    print(response)
    
    # چاپ پاسخ خام برای بررسی
   
    
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decode error:", e)
        return {}





def cancel_old_orders(token, execution='limit', src_currency='s', dst_currency='rls', hours=None):
    url = 'https://api.nobitex.ir/market/orders/cancel-old'
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'execution': execution,
        'srcCurrency': src_currency,
        'dstCurrency': dst_currency
    }
    if hours is not None:
        data['hours'] = hours

    response = requests.post(url, headers=headers, json=data)
    return response.json()




def main():



    #####################  مقداردهی اولیه به نوع ارز و میزان خرید  ##################
    sd="s-rls"
    SD='SIRT'
    src='s'
    des='rls'
    amount = 1.5
    buy_count=0
    sell_count=0
    stop_loss_count=0
    ##################### پایان مقداردهی اولیه به نوع ارز و میزان خرید  #############





    #####################  مقداردهی اولیه به متغیرهای مربوط به روند   ###############
    price_history = deque(maxlen=50)  # نگهداری ۱۰ قیمت آخر
    increases=0
    decreases=0
    trend="NO_ASC_DES"
    ##################### پایان مقداردهی اولیه به متغیرهای مربوط به روند   ###########





    ####################  گرفتن قیمت فعلی بازار و موجودی فعلی ###################
    src_balance, des_balance = get_balance(src, des)
    market_price = get_market_price(sd)
    previous_market_price=market_price
    #################### پایان گرفتن قیمت فعلی بازار و موجودی فعلی ###################





    ####################چند بار قیمت یازار خوانده می شود برای تشخیص روند ###################
    for i in range(1,20):
        market_price = get_market_price(sd)  # فرض کنید این تابع قیمت بازار را برمی‌گرداند
        price_history.appendleft(int(market_price))  
        trend=determine_trend(list(price_history))
        print(f"TREND={trend}")          
        time.sleep(5)
    ########################################## پایان تشخیص روند  ################################





    #####################  مقداردهی اولیه به قیمت خرید، قیمت فروش، قیمت توقف خرید، قیمت فعال شدن حد ضرر، قیمت فروش حد ضرر  ##################
    buy_price = get_market_price(sd)
    sell_price = buy_price+3000
    stop_buy_price = buy_price-3000# توقف خرید در این قیمت
    stop_loss_price = buy_price-4000  # حد ضرر
    stop_loss_sell_price = buy_price-5000 # قیمت فروش در حد ضرر  
    previous_market_price=market_price
    ############################################  پایان قیمت گذاری ها  ###########################################





    ####################  چاپ قیمت ها   ###################
    print(f"--------------*****************************-----------------")
    print(f"buy price= {buy_price}")  
    print(f"sell price= {sell_price}")
    print(f"stop buy price= {stop_buy_price}")
    print(f"stop loss price= {stop_loss_price}")
    print(f"stop loss sell price= {stop_loss_sell_price}")
     #################### پایان چاپ قیمت ها   ###################



    #################################  محاسبه و چاپ ترند  ########################
    print(f"--------------*****************************-----------------")
    increases, decreases = analyze_trend(price_history)
    print(f"Increases: {increases}, Decreases: {decreases}")
    trend=determine_trend(list(price_history))
    print(f"TREND={trend}")
################################# پایان محاسبه و چاپ ترند  ########################



    cnt=0
    while True:
        cnt+=1

        ############
        ############3
        ############
        print(f"BUY COUNT=",buy_count)
        print(f"SELL COUNT=",sell_count)
        print(f"STOP LOSS COUNT=",stop_loss_count)
        ##################3
        ###############


        ########################## ....چاپ قیمت های خرید، فروش و ##########################
        print(f"--------------*****************************-----------------")
        print(f"buy price= {buy_price}")  
        print(f"sell price= {sell_price}")
        print(f"stop buy price= {stop_buy_price}")
        print(f"stop loss price= {stop_loss_price}")
        print(f"stop loss sell price= {stop_loss_sell_price}")
        print(f"--------------*****************************-----------------")   
        ########################## ....چاپ قیمت های خرید، فروش و ##########################



        #########################  گرفتن قیمت بازار، لیست سفارشات، حجم سفارشات خرید و فروش و چاپ آنها  ############################
        market_price = get_market_price(sd)  # فرض کنید این تابع قیمت بازار را برمی‌گرداند
        print(f"market price=",market_price)
        if market_price!=previous_market_price:
            price_history.appendleft(int(market_price))
        orderbook = get_orderbook(SD)
        print(f"ORDER BOOK=",orderbook)
        buy_volume = calculate_total_volume(orderbook, 'bids')
        sell_volume = calculate_total_volume(orderbook, 'asks')
        print(f"buy volume: {buy_volume}")
        print(f"sell volume: {sell_volume}")
        ######################### پایان گرفتن قیمت بازار، لیست سفارشات، حجم سفارشات خرید و فروش و چاپ آنها  ############################



        #########################  اگر روند نزولی بود و سفارشات فروش بیشتر از سفارشات خرید بود قیمت خرید و فروش را کاهش بده  #############################
        if len(list(price_history)) >= 20:
            increases, decreases = analyze_trend(price_history)  
            print(f"Increases: {increases}, Decreases: {decreases}")
            trend=determine_trend(list(price_history))
            print(f"TREND={trend}")
            if trend=='DES' and sell_volume>buy_volume:
                buy_price -= 1
                sell_price -= 1
                print(f"buy and sell decreased!")
        #########################  اگر روند صعودی بود و سفارشات فروش بیشتر از سفارشات خرید بود قیمت فروش و قیمت خرید را افزایش بده  #############################        
            elif trend=='ASC' and buy_volume>sell_volume:
                buy_price +=1
                sell_price += 1
                print(f"buy and sell increased!")
        ############################# پایان تغییر قیمت خریدو فروش  ###########################             
                
     
        
        ##################################  سفارش خرید   #############################
        if market_price <= buy_price and market_price > stop_buy_price and trend!='DES':
            if  buy_volume>=sell_volume:
                order_response = place_order(src, des, str(amount), str(market_price), 'buy')
                print(f"Buy order response: {order_response}")
                src_balance, des_balance = get_balance(src, des)
                buy_count=buy_count+1
        ################################## پایان سفارش خرید   #############################



        ###################################  سفارش فروش  ##############################
        if market_price >= sell_price and trend!='ASC':
            if  sell_volume>= buy_volume:
                order_response = place_order(src, des, '222', str(market_price), 'sell')
                print(f"Sell order response: {order_response}")
                src_balance, des_balance = get_balance(src, des)
                sell_count=sell_count+1
        ################################### پایان سفارش فروش  ##############################




        ####################################  سفارش فروش حد ضرر  #######################
        #and float(src_balance) > 0
        if market_price <= stop_loss_price and sell_volume>=buy_volume and determine_trend(list(price_history))!='ASC':
            order_response= cancel_old_orders(api_key)
            print(f"Stop loss sell order response: {order_response}")
            order_response = place_order(src, des, str(src_balance), str(stop_loss_sell_price), 'sell')
            print(f"Stop loss sell order response: {order_response}")
            src_balance, des_balance = get_balance(src, des)
            stop_loss_count=stop_loss_count+1

            ##################################  بروزرسانی لیست قیمت های بازار  #########
            for i in range(1,10):
                market_price = get_market_price(sd)  # فرض کنید این تابع قیمت بازار را برمی‌گرداند
                price_history.appendleft(int(market_price)) 
                trend= determine_trend(list(price_history))
                print(f"TREND={trend}")          
                time.sleep(5)
            ################################## پایان بروزرسانی لیست قیمت های بازار  #########
           

            ##################################  بروزرسانی قیمت خرید پس از سفارش فروش حد ضرر  #########
            buy_price = get_market_price(sd)
            sell_price = buy_price+3000
            stop_buy_price = buy_price-3000# توقف خرید در این قیمت
            stop_loss_price = buy_price-4000  # حد ضرر
            stop_loss_sell_price = buy_price-5000 # قیمت فروش در حد ضرر  
            increases, decreases = analyze_trend(price_history)
            print(f"Increases: {increases}, Decreases: {decreases}")
            trend=determine_trend(list(price_history))
            print(f"TREND={trend}")

             ################################## پایان بروزرسانی قیمت خرید پس از سفارش فروش حد ضرر  #########




         #################################### پایان سفارش فروش حد ضرر  #######################    
       
       
       
        previous_market_price=market_price
        time.sleep(6)
      
       
       
        ############################################# اگر قیمت بازار با قیمت خرید تفاوت زیادی داشت و یا حلقه 30 بار اجرا شده بود  #######################################################
        #############################################       کل سفارشات جاری را حذف کن و قیمت هاو روند را بروزرسانی کن  #######################################################
        buy_volume = calculate_total_volume(orderbook, 'bids')
        sell_volume = calculate_total_volume(orderbook, 'asks')


        if market_price>=buy_price+5000 or cnt==30 or sell_volume>buy_volume:
            order_response= cancel_old_orders(api_key)
            print('All orders canceled')
            cnt=0
            buy_price = get_market_price(sd)
            sell_price = buy_price+3000
            stop_buy_price = buy_price-3000# توقف خرید در این قیمت
            stop_loss_price = buy_price-4000  # حد ضرر
            stop_loss_sell_price = buy_price-5000 # قیمت فروش در حد ضرر  
            increases, decreases = analyze_trend(price_history)
            print(f"Increases: {increases}, Decreases: {decreases}")
            trend=determine_trend(list(price_history))
            print(f"TREND={trend}")
            print("============================================================================")
        #############################################################  پایان تفاوت قیمت خرید با قیمت بازار  ########################################    
        

if __name__ == "__main__":
    main()