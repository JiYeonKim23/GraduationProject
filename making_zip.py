import zipfile
import os

def make_zip(result_true) : #사진을 업로드한 static/upload_images 폴더에서 원본 사진 저장
    file_path = "./static"
    os.chdir(file_path)
    
    zip_file = zipfile.ZipFile("folder.zip", "w")
    for file in result_true :
        zip_file.write(os.path.join("./upload_images", file[0]), compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    os.chdir("..")