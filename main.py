import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify #jsonify : ip 주소
import sys
import myfacerec, image_exif_info, making_zip, all_folders
import os

application = Flask(__name__)

video_play = True
video_uploaded = False
photos_uploaded = False
rotate_num = 0

#인식할 사람(동영상) 삭제
def remove_create_person() :
    global video_play, video_uploaded, rotate_num
    video_play = False
    video_uploaded= False
    rotate_num = 0
    time.sleep(0.1)
    
    all_folders.remove_create_directory("./faces")
    try :
        all_folders.remove_create_directory("./static/upload_video")
    except :
        print("video 재생 중이므로 삭제할 수 없음")

# 갤러리 삭제
def remove_create_gallery() :
    global photos_uploaded
    photos_uploaded = False
    all_folders.remove_create_directory("./static/upload_images")

def remove_create_everything() :
    all_folders.remove_create_result()
    remove_create_person() 
    remove_create_gallery()

remove_create_everything()

@application.route("/")
def hello():
    return render_template("main.html", video_uploaded = video_uploaded, photos_uploaded = photos_uploaded)

def gen():
    """Video streaming generator function"""
    cap = cv2.VideoCapture('static/upload_video/video.mp4')
    global rotate_num
    
    while(cap.isOpened() and video_play) :
        ret, img = cap.read()
        img = myfacerec.rotate(img, rotate_num)
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.5, fy = 0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else:
            break
    
    cap.release()

@application.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag"""
    return Response(gen(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@application.route("/rotate/<int:index>")
def rotate(index):
    global rotate_num
    rotate_num += 1
    if rotate_num == 4 :
        rotate_num = 0
    if index == 0 : #main 화면
        return redirect(url_for("hello"))
    else : #upload_success 화면
        global video_uploaded, photos_uploaded
        return render_template("upload_success.html", flag = "video",video_uploaded = video_uploaded, photos_uploaded = photos_uploaded)

@application.route("/remove_person_gallery")
def remove_person_gallery():
    remove_create_everything()
    return redirect(url_for("hello"))

@application.route("/upload_video")
def upload_video():
    return render_template("upload_video.html")

@application.route("/upload_done", methods=["POST"])
def upload_done():
    uploaded_file = request.files["file"]
    uploaded_file.save("static/upload_video/video.mp4")
    global video_play, video_uploaded, photos_uploaded
    video_play = True
    video_uploaded = True
    return render_template("main.html", flag = "video",  video_uploaded = video_uploaded, photos_uploaded = photos_uploaded)

@application.route("/upload_photo")
def upload_photo():
    return render_template("upload_photo.html")

@application.route("/upload_pic_done", methods=["POST"])
def upload_pic_done():
    img_extension = ['.jpg', '.jpeg', '.JPG', '.bmp', '.png']
    uploaded_files = request.files.getlist("file[]")
    for file in uploaded_files :
        if os.path.splitext(file.filename)[1] in img_extension :
            index = file.filename.rfind('/')
            file.save("static/upload_images/"+file.filename[index+1:])
    global video_uploaded, photos_uploaded
    photos_uploaded = True
    return render_template("main.html", flag = "pic",  video_uploaded = video_uploaded, photos_uploaded = photos_uploaded)

@application.route("/upload_pics_done", methods=["POST"])
def upload_pics_done():
    uploaded_files = request.files.getlist("file[]")
    for file in uploaded_files :
        file.save("static/upload_images/"+file.filename)
    global video_uploaded, photos_uploaded
    photos_uploaded = True
    return render_template("main.html", flag = "pic",  video_uploaded = video_uploaded, photos_uploaded = photos_uploaded)

@application.route("/dividepics")
def dividepics():
    myfacerec.dividepics(rotate_num)
    global model
    model = myfacerec.training()
    return redirect(url_for("result"))

@application.route("/result")
def result():
    global model
    if not model : 
        model = myfacerec.training()
        print("모델이 비어 있음")
    result_true = myfacerec.result(model)
    length_true = len(result_true)
    making_zip.make_zip(result_true)
    return render_template("result.html", result_true = result_true, length_true = length_true)

@application.route("/image_info/<string:index>")
def image_info(index):
    photo =  str(index)
    date = image_exif_info.exif_info(photo)
    if date == "None" :
        return render_template("image_info.html", photo = "result_true/"+photo, img_date = "None")
    return render_template("image_info.html", photo = "result_true/"+photo, img_date = date)

if __name__ == '__main__' :
    application.run()