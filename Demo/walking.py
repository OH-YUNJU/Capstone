from Library import *
FOOT_LIST = []
TIME_LIST = []

#측정
def Step_guideline(Landmarks):
    try :
        #골반 좌표가 이미지 안에 들어와있는지 확인 및 좌표 가져오기
        L_PEL.x, L_PEL.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * HEIGHT
        R_PEL.x, R_PEL.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * HEIGHT
        L_KNEE.x, L_KNEE.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y * HEIGHT
        R_KNEE.x, R_KNEE.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y * HEIGHT
        L_FOOT.x, L_FOOT.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * HEIGHT
        R_FOOT.x, R_FOOT.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y * HEIGHT

        
        #가이드라인 안에 있는지 확인
        if(0 < L_PEL.x < 640 and 0 < L_PEL.y < 480 and 0 < R_PEL.x < 640 and 0 < R_PEL.y < 480):
            if(0 < L_KNEE.x < 640 and 0 < L_KNEE.y < 480 and 0 < R_KNEE.x < 640 and 0 < R_KNEE.y < 480): #화면 안에서
                #측정 시작부분
                return True
        
        else:
            #가이드라인 안에 들어와주세요
            STR.guide = "가이드라인 안에 들어와주세요"
        
    #좌표를 가져오지 못함
    except:
        #카메라 안에 들어와주세요
        STR.guide = '카메라안으로 들어와주세요'
    
    return False

def GuideText(frame):
    #텍스트 위치 계산
    text_x, text_y = int((HEIGHT - len(STR.guide)*7) / 2), 40 #가로 중앙으로 설정

    frame = Image.fromarray(frame)
    ImageDraw.Draw(frame).text((text_x,text_y), STR.guide, font=FONT, fill=GREEN)

    frame = np.array(frame)
    return frame

#가이드라인
def Media_Step():
    count = 0
    saveon = False
    Start_Time = time.time()

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cv2.waitKey(1) < 0:
            frames = PIPELINE.wait_for_frames()
            depth_frames = ALIGN.process(frames)
            frame = frames.get_color_frame()
            depth = depth_frames.get_depth_frame()

            if not frame or not depth:
                continue

            frame = cv2.cvtColor(np.asanyarray(frame.get_data()), cv2.COLOR_BGR2RGB)

            MP_landmark = pose.process(frame)

            # #가이드라인 확인 5초마다
            if time.time() - Start_Time > N_SECONDS:
                count += 1
                Start_Time = time.time()

                if Step_guideline(MP_landmark):
                    saveon = save()

            #*미디어 파이프 그리기
            mp_drawing.draw_landmarks(
                frame,
                MP_landmark.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            #가이드 라인 추가 및 텍스트 설정
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame,1)
            frame = GuideText(frame)
            
            #화면 표시
            cv2.imshow("", frame)

            # 종료 조건
            if cv2.waitKey(5) & 0xFF == 27:
                break
            
            # 타임 아웃
            if count > COUNTOUT:
                break
            
            if saveon:
                #저장완료
                break

#영상 저장
def save():
    VIDEO_COLOR_WRITER = cv2.VideoWriter(ROOT_DIR + '/image/step.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (WIDTH, HEIGHT), isColor = True)
    #* 촬영 시작
    STR.guide = '촬영을 시작합니다 3'
    
    stime = cv2.getTickCount()  # 시작 시간 기록
    # RGB 프레임을 받아옴
    with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
        while cv2.waitKey(1) < 0:

            frames = PIPELINE.wait_for_frames()
            depth_frames = ALIGN.process(frames)
            color_frame = frames.get_color_frame()
                        
            if not color_frame: continue
        
            # RGB 프레임을 이미지로 변환
            color_image = np.asanyarray(color_frame.get_data())
                        
            #가이드 라인 체크
            frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            results = pose.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            frame = cv2.flip(frame,1)
            frame = GuideText(frame)
            cv2.imshow("", frame)


            ctime = cv2.getTickCount()  # 현재 시간 기록
            etime = (ctime - stime) / cv2.getTickFrequency()  # 경과 시간 계산


            # 5초가 경과하면 녹화 종료
            if 1 < etime < 2:
                STR.guide = '촬영을 시작합니다 2'
            elif 2 < etime < 3:
                STR.guide = '촬영을 시작합니다 1'
                
            # 동영상에 프레임을 추가
            elif etime > 3:
                STR.guide = "촬영중입니다. 움직이지마세요."
                VIDEO_COLOR_WRITER.write(cv2.flip(color_image,1))
            if etime > 8:
                break

        # 동영상 저장 종료
        VIDEO_COLOR_WRITER.release()

        print('동영상 저장 완료')
        
    return True

def Step_pose(Landmarks):
    L_FOOT.x, L_FOOT.y = Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x * WIDTH, Landmarks.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y * HEIGHT
    FOOT_LIST.append(L_FOOT.x)
    
def One_Step():
    video_path = 'C:/lab/Demo/image/step.mp4'
    #파일 로드
    cap = cv2.VideoCapture(video_path)
    with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
        i = 0
        while cap.isOpened():
            i+=1
            success, frame = cap.read()
            try:
                if not success or frame.shape is not None:
            
                    HEIGHT, WIDTH, _ = frame.shape

                    frame.flags.writeable = False
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    MP_landmark = pose.process(frame)
                    frame.flags.writeable = True
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    Step_pose(MP_landmark)
                    TIME_LIST.append(i)
                                                                                                                                                                                                                                                                                                 
            except:
                li = []
                for k in range(0, len(FOOT_LIST) -1):
                    if(abs(FOOT_LIST[k] - FOOT_LIST[k+1]) < 10):
                        li.append(TIME_LIST[k])
                        lenli = len(li)
                        if((lenli > 2) and ((li[lenli-2] + 1) != li[lenli-1])):
                            li.pop()
                            break                  
                FIRST_T.x = li[0]
                CUT_OFF_T.x = li[-1]
                
                break
            
        cap.release()       

def Step_Video_result():
    # 자를 시간대까지의 프레임을 자르기 전 영상에 저장합니다.
    video_path = 'C:/lab/Demo/image/step.mp4'
    i = 0
    #파일 로드
    cap = cv2.VideoCapture(video_path)
    VIDEO_STEP_WRITER = cv2.VideoWriter(ROOT_DIR + '/image/one_step.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (640,480), isColor = True)
    
    while cap.isOpened() and i < CUT_OFF_T.x:
        i+=1
        success, frame = cap.read()
        if not success or frame.shape is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, (640,480))

    
        if (FIRST_T.x <= i):
            VIDEO_STEP_WRITER.write(frame)
        
        else:
            break    
    
    VIDEO_STEP_WRITER.release()
    cap.release()