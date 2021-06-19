import os, time
import shutil #rmtree()
#from werkzeug import secure_filename

# 폴더 삭제하기
def remove_create_directory(name) : 
    try :
        if os.path.isdir(name) :
            shutil.rmtree(name) 
        os.makedirs(name, exist_ok = True)
    except :
        print(name, "디렉토리를 새로 생성하는 데에 실패하였습니다.")
        
def remove_file(name) : 
    try :
        if os.path.isfile(name) :
            os.remove(name)
        else :
            print(name + "파일이 없습니다.")
    except :
        print(name, "파일을 삭제하는 데에 실패하였습니다.")

#결과 폴더 삭제
def remove_create_result() : 
    remove_create_directory("./static/result_true")
    remove_create_directory("./static/result_false")
    remove_file("./static/folder.zip")