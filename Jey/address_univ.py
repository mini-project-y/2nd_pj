import time
import requests
import pandas as pd
import os

# Kakao API Geocoding 함수
def geocode_kakao(address, api_key):
    """
    Kakao Local API를 사용해 주소를 위도, 경도로 변환하는 함수
    :param address: 도로명 주소
    :param api_key: Kakao REST API Key
    :return: (latitude, longitude) 좌표 튜플
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result['documents']:
            x = float(result['documents'][0]['x'])  # 경도 (longitude)
            y = float(result['documents'][0]['y'])  # 위도 (latitude)
            return y, x
        else:
            return None, None  # 결과 없음
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None

# CSV 파일 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 경로
file_path = os.path.join(base_dir, "Data_Preprocessing", "university.csv")

# CSV 파일 읽기
try:
    address_df = pd.read_csv(file_path, encoding="utf-8")
    print(f"파일 로드 성공: {file_path}")
except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {file_path}")
    sys.exit(1)
except Exception as e:
    print(f"파일 로드 중 오류 발생: {e}")
    sys.exit(1)

# 결과 저장할 리스트
coordinates = []

# API Key 설정
kakao_api_key = "cb5bbecaab04e070a6fddc4c3f14350b"  # Kakao REST API 키를 입력하세요

# 지오코딩 실행
for idx, row in address_df.iterrows():
    no = row[3]  # 첫 번째 열 (학교 번호 또는 이름)
    address = row[8]  # 세 번째 열 (도로명 주소)

    # Kakao API로 좌표 변환
    lat, lng = geocode_kakao(address, kakao_api_key)
    coordinates.append({'no': no, 'address': address, 'latitude': lat, 'longitude': lng})

    # 진행 상황 출력
    if (idx + 1) % 100 == 0:
        print(f"{idx + 1}/{len(address_df)} addresses processed.")
    
    # API 호출 제한을 피하기 위해 딜레이 추가 (필요시)
    time.sleep(0.2)  # 0.2초 대기 (초당 5건 요청)

# 결과를 데이터프레임으로 변환
coordinates_df = pd.DataFrame(coordinates)

# 결과 저장
output_path = os.path.join(base_dir, "geocoded_univ.csv")
coordinates_df.to_csv(output_path, index=False, encoding="utf-8-sig")  # UTF-8-sig로 저장 (Excel 호환)

print(f"지오코딩 결과 저장 완료: {output_path}")
