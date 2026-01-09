import cv2

capture = cv2.VideoCapture(0)

# 분류기 객체를 만듭니다.
cascade = cv2.CascadeClassifier() 

# 데이터를 입력합니다.
cascade.load('haarcascade_eye.xml') 

while capture.isOpened():
    ret, frame = capture.read()
    if not ret: 
        continue
    frame = cv2.flip(frame, 1) 

    # 회색으로 얼굴 인식이 잘 되도록 합니다.
    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 

    # 영상을 더 잘 분석할 수 있도록 평활화를 합니다.
    grayframe = cv2.equalizeHist(grayframe) 
    
    # Gray 스케일로 바꾼 영상을 분석합니다. 
    # 1.1, 3, 0, (30, 30)는 옵션값입니다.
    objects = cascade.detectMultiScale(grayframe, 1.1, 3, 0, (30, 30))

    # 인식을 하면 x, y, w, h 값을 확인할 수 있습니다.
    # x, y는 인식한 영역의 시작 좌푯값입니다. w와 h는 인식한 영역의 가로와 세로 크기입니다.
    # 눈을 여러 개 인식할 수 있습니다.
    for (x,y,w,h) in objects: 
        # 사각형을 그립니다.         
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)

        # 사각형 위에 'eye'라고 글씨를 씁니다. 
        cv2.putText(frame, 'eye', (x, y-10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 0))
    cv2.imshow('haarcascade', frame)
    if cv2.waitKey(1) == 27: 
        break
    
capture.release()
cv2.destroyAllWindows()