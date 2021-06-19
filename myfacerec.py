import cv2
import numpy as np

import operator #sorted->itemgetter

import os
from os import listdir

face_classifier = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

def rotate(frame, num) :
    if num == 1 : 
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif num == 2 :
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif num == 3 :
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def face_one_extractor(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)
    
    if faces is():
        return None

    for(x,y,w,h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200,200))
        return face

#동영상을 사진 50개로 분리
def dividepics(rotate_num) :
    cap = cv2.VideoCapture("static/upload_video/video.mp4")
    
    count=notcount=flag= 0
    
    while count<50 :
        ret, frame = cap.read()
        
        flag+=1
        if flag % 2 != 0 : 
            continue
            
        if frame is None :
            print("영상의 길이가 짧습니다.")
            return
        
        frame = rotate(frame, rotate_num)
        cropped_face = face_one_extractor(frame)
        
        if cropped_face is not None:
            count+=1

            file_name_path = 'faces/user'+str(count)+'.jpg'
            cv2.imwrite(file_name_path,cropped_face)
            
        else:
            notcount+=1
            if notcount==500 :
                print("얼굴을 찾기 어렵습니다. 새로운 동영상을 업로드해주세요.")
                return

    cap.release()
    print('얼굴 100개 찾기 완료')

def training() :
    faces_path = 'faces/'
    faces = os.listdir(faces_path)

    try :
        Training_Data, Labels = [], []

        for i, face in enumerate(faces):
            face_path = faces_path + face
            image = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            Training_Data.append(np.asarray(image, dtype=np.uint8))
            Labels.append(i)

        Labels = np.asarray(Labels, dtype=np.int32)

        model = cv2.face.LBPHFaceRecognizer_create()
        model.train(np.asarray(Training_Data), Labels)

        print("Model Training Complete!!!!!")
        return model
    
    except : 
        print("모델 학습이 완료되지 않음")
        return False

def face_multiple_extractor(img, name):
    try :
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces_loc = face_classifier.detectMultiScale(gray,1.3,5)
    
        if faces_loc is():
            return None, None

        faces = []
    
        for(x,y,w,h) in faces_loc:
            cv2.rectangle(img, (x,y),(x+w,y+h),(0,255,255),2)
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200,200))
            faces.append(face)
    
        return faces, faces_loc
    
    except :
        print(name, "에서 face_multiple_extractor 함수 오류 발생")
        return None, None

def font_thick(w) :
    if w < 100 :
        return 1
    else :
        return max(2,2*w//200)

def face_recognizer(model, img, name) :
    flag = False
    smallest_dist = 500
    highest_similarity = 0
    
    return_face, faces_loc = face_multiple_extractor(img, name)
    
    if faces_loc is None : # faces가 None
        try : 
            img_height = img.shape[0]
            cv2.putText(img, "Face Not Found", (10, img_height-10), cv2.FONT_HERSHEY_SIMPLEX, img_height/400, (255, 0, 0), img_height//200)
        except :
            cv2.putText(img, "Face Not Found", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
        return flag, 500
    
    for face, (x,y,w,h) in zip(return_face, faces_loc) :
        try :            
            result = model.predict(face)
            thickness = font_thick(w)
            
            if result[1] <= 50 :
                similarity = 99
            elif result[1] < 150 :
                similarity = 150 - result[1]
            else :
                similarity = 0
            similarity = int(similarity)
            
            cv2.putText(img,str(similarity)+"% correct", (x,y), cv2.FONT_HERSHEY_SIMPLEX, w/200, (255,255,255), thickness)
            
            if result[1] < 67 :
                cv2.rectangle(img, (x,y),(x+w,y+h),(0,0,255),3)
                cv2.putText(img, "I found you", (x, y+h+w//25), cv2.FONT_HERSHEY_SIMPLEX, w/200, (0, 255, 0), thickness)
                flag = True
            
            if result[1] < smallest_dist :
                smallest_dist = result[1]
                highest_similarity = similarity
                
        except:
            cv2.putText(img, "Face Not Found", (x, y+h+w//25), cv2.FONT_HERSHEY_SIMPLEX, w/200, (255, 0, 0), thickness)
            print("예외가 발생하였음")
    
    return flag, highest_similarity        


def result(model) : 
    img_path_dir = "./static/upload_images/"
    file_list = os.listdir(img_path_dir)
    
    true_result = {}

    for img in file_list :
        image = cv2.imread(str(img_path_dir) + str(img))
        flag, dist = face_recognizer(model, image, str(img))
        
        if flag :
            cv2.imwrite('static/result_true/'+str(img),image)#사진 저장
            true_result[str(img)] = dist
    
    true_result = sorted(true_result.items(), key=operator.itemgetter(1), reverse=True)
    
    return true_result