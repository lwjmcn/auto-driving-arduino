import cv2
import numpy as np
from urllib.request import urlopen
import time

ip = '192.168.137.18' # ip 주소 문자열 설정
stream = urlopen('http://'+ ip + ':81/stream') # 설정한 ip주소를 이용하여 주소에 요청을 보내 동영상 스트림을 받아옴
buffer = b''
# 바이트 형태의 데이터를 저장할 buffer 변수 초기화
# 바이트 형태의 데이터는 컴퓨터가 이해하는 이진 데이터
# 여기서 바이트 형태가 필요한 이유: 파일에서 이진 파일을 읽고 쓰기 위해(문자열이 아니라 바이트 형태로 데이터를 다뤄야하기 때문)

while True:
    buffer += stream.read(4096) # 스트림으로부터 최대 4096바이트씩 데이터를 읽어 buffer에 추가
    head = buffer.find(b'\xff\xd8') # buffer 내에서 JPEG 이미지의 시작을 나타내는 바이트 시퀀스 '\xff\xd8'의 인덱스를 찾음
    end = buffer.find(b'\xff\xd9') # buffer 내에서 JPEG 이미지의 끝을 나타내는 바이트 시퀀스 '\xff\xd9'의 인덱스를 찾음
    # \xff\xd8', \xff\xd9'는 JPEG 이미지의 SOI(Start Of Image), EOI(End Of Image)를 나타내는 고정된 바이트 시퀀스
    
    try:
        if head > -1 and end > -1: # buffer에 이미지의 시작과 끝이 모두 존재하는 경우 -> 이미지가 완전한 경우(-1이면 해당 바이트 시퀀스가 없다는 뜻이고, 0 이상의 값이면 찾았다는 뜻)
            jpg = buffer[head:end+2] # jpg 변수에 이미지 데이터를 할당
            # end는 \xff를 가리키고, end+1은 \xd9를 가리킴 => end+2까지 잘라야 JPEG의 끝까지 포함
            buffer = buffer[end+2:] # buffer에서 해당 이미지 데이터를 제거하고 남은 데이터만 buffer에 유지
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED) # jpg 데이터를 NumPy 배열로 변환하고 OpenCV 함수를 사용하여 이미지를 디코딩
            # dtype=np.uint8: 각 바이트를 0~255 사이의 부호 없는 정수로 해석하겠다는 뜻
            # np.frombuffer: 이 바이트 데이터를 NumPy 배열로 변환
            # cv2.IMREAD_UNCHANGED: 이미지를 원래 포맷 그대로 불러오라는 뜻
            # cv2.imdecode: OpenCV에서 메모리 상의 이미지 데이터(NumPy)를 실제 이미지로 디코딩하는 함수
            # => jpg라는 바이트 데이터를 NumPy 배열로 바꾸고, 그 배열을 OpenCV로 디코딩해서 이미지 객체(img)로 만듦
            
            height, width, _ = img.shape # img는 (세로 높이, 가로 높이, 채널 수)와 같은 형태를 가짐. 여기서는 채널이 필요 없으므로 _로 설정한 것
            img = img[height//2:, :] # 이미지의 세로 절반(아래쪽)만 남기고, 가로는 유지
            
            cv2.imshow("AI CAR Streaming", img) # OpenCV 창에 이미지 표시
            
            key = cv2.waitKey(1) # 사용자의 키 입력 대기(아스키코드로 반환), 1(0.001초)은 실시간 영상 스트리밍에서 가장 최소 지연으로 루프를 유지하는 일반적인 사용법
            if key == ord('q'): # q키를 누르면 루프 종료
                break
    except:
        print("에러")
        pass

cv2.destroyAllWindows() # 모든 OpenCV 창을 닫음