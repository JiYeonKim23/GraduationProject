from PIL import Image

#result 폴더에는 EXIF 정보가 날라감

def time_split(time_info) :
    tmp_time = time_info.split()
    
    yymmdd = tmp_time[0].split(":")
    sentence = yymmdd[0] + "년 "
    sentence += yymmdd[1]+ "월 "
    sentence += yymmdd[2] + "일 "
    
    hhmmss = tmp_time[1].split(":")
    sentence += hhmmss[0] + "시 "
    sentence +=  hhmmss[1] + "분 "
    
    return sentence

def exif_info(img_name) : 
    time_tag = [306, 36867, 36868]
    
    info = Image.open("static/upload_images/"+img_name).getexif()
    img_date = "None"
    
    for temp_time_tag in time_tag :
        if temp_time_tag in info :
            img_date = time_split(info[temp_time_tag])
            break
            
    return img_date