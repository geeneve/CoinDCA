import uuid
import hashlib
from urllib.parse import urlencode
import time
import logging

import requests
import jwt

# Upbit API 키 설정
ACCESS_KEY = 'YOUR_ACCESS_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'
SERVER_URL = 'https://api.upbit.com'

# 로깅 설정
logging.basicConfig(
    filename='upbit_auto_trade.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def buy_bitcoin(amount_krw):
    """
    주어진 금액만큼 비트코인을 매수하는 함수
    :param amount_krw: 매수할 금액 (KRW)
    """
    try:
        query = {
            'market': 'KRW-BTC',
            'side': 'bid',
            'volume': '',  # 매수할 수량을 입력하지 않으면, amount_krw 만큼 매수
            'price': str(amount_krw),
            'ord_type': 'price',
        }
        
        query_string = urlencode(query).encode()
        
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
        
        payload = {
            'access_key': ACCESS_KEY,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }
        
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        authorize_token = f'Bearer {jwt_token}'
        headers = {"Authorization": authorize_token}
        
        # 주문 요청
        response = requests.post(f"{SERVER_URL}/v1/orders", params=query, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 201:
            logging.info(f'매수 성공: {response.json()}')
            print('매수 성공:', response.json())
        else:
            logging.error(f'매수 실패: {response.json()}')
            print('매수 실패:', response.json())
    
    except requests.exceptions.RequestException as req_err:
        logging.error(f'매수 중 요청 오류 발생: {req_err}')
        print(f'매수 중 요청 오류 발생: {req_err}')
    except jwt.exceptions.PyJWTError as jwt_err:
        logging.error(f'JWT 오류 발생: {jwt_err}')
        print(f'JWT 오류 발생: {jwt_err}')
    except Exception as err:
        logging.error(f'매수 중 알 수 없는 오류 발생: {err}')
        print(f'매수 중 알 수 없는 오류 발생: {err}')

def main():
    """
    매일 일정 시간에 비트코인을 매수하는 메인 함수
    """
    amount_krw = 10000  # 매일 매수할 금액 (KRW)
    
    while True:
        # 매수 시도
        buy_bitcoin(amount_krw)
        # 24시간 대기
        time.sleep(24 * 60 * 60)

if __name__ == "__main__":
    main()