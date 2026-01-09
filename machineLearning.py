import cv2 
import numpy as np
import time  # 시간을 제어하기 위해 추가
from keras.models import load_model 

# 1. 설정 및 모델 로드
np.set_printoptions(suppress=True)
try:
    model = load_model('image_model/keras_model.h5', compile=False)
    class_names = open('image_model/labels.txt', 'r', encoding='UTF-8').readlines()
    print("[시스템] 모델 로드 완료")
except Exception as e:
    print(f"[오류] 모델을 불러오는 중 문제가 발생했습니다: {e}")
    exit()

# 2. 카메라 연결 (Windows 호환성 옵션 사용)
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# ----------------------------------------------------------------
# [안정화 단계] 카메라 워밍업 (해상도 강제 지정 대신 사용)
# ----------------------------------------------------------------
if capture.isOpened():
    print("[시스템] 카메라 초기화 중... (약 2초 소요)")
    time.sleep(2)  # 카메라가 전원을 켜고 초점을 잡을 시간을 줍니다.
    
    # 초기 불안정한 프레임 10개를 읽어서 버립니다. (버퍼 비우기)
    for i in range(10):
        capture.read()
    print("[시스템] 카메라 안정화 완료. 시작합니다.")
else:
    print("[오류] 카메라를 열 수 없습니다. 연결을 확인하세요.")
    exit()

while capture.isOpened():    
    # 3. 프레임 읽기
    ret, frame = capture.read()
    
    # 프레임을 읽지 못했다면(카메라 끊김 등), 잠깐 쉬었다가 다시 시도
    if not ret: 
        print("프레임 수신 실패. 재시도 중...")
        time.sleep(0.5)
        continue
    
    # 좌우 반전 (거울 모드)
    frame = cv2.flip(frame, 1)   

    # 4. AI 모델 입력용 데이터 생성 (화면 출력용 frame은 건드리지 않음!)
    # BGR -> RGB 색상 순서 변경
    model_input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 모델 입력 크기(224x224)에 맞게 조절
    model_input = cv2.resize(model_input, (224, 224), interpolation=cv2.INTER_AREA)
    # 차원 변환: (224, 224, 3) -> (1, 224, 224, 3)
    model_input = np.asarray(model_input, dtype=np.float32).reshape(1, 224, 224, 3)
    # 정규화: -1 ~ 1 사이의 값으로 변환 (Teachable Machine 표준)
    model_input = (model_input / 127.5) - 1    

    # 5. 예측 수행
    prediction = model.predict(model_input, verbose=0) # verbose=0으로 불필요한 로그 숨김
    index = np.argmax(prediction)   
    class_name = class_names[index]
    confidence_score = prediction[0][index]  

    # 텍스트 가공
    class_name = class_name[2:].strip()
    confidence_score = round(confidence_score * 100, 2)
    text = f'{class_name} : {confidence_score}%'

    # 6. 화면 출력 (원본 frame 위에 그리기)
    # 배경이 복잡할 수 있으므로 글자 뒤에 검은 배경을 살짝 넣어 가독성을 높임
    cv2.rectangle(frame, (10, 10), (300, 45), (0,0,0), -1) 
    cv2.putText(frame, text, (15, 35), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
    
    cv2.imshow('Machine Learning', frame)
        
    # ESC 키(27)를 누르면 종료
    if cv2.waitKey(1) == 27: 
        break

# 종료 처리
capture.release()
cv2.destroyAllWindows()