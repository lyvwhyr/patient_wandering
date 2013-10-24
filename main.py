import cv2,math
import urllib 
import numpy as np
from time import sleep 

    
stream=urllib.urlopen('http://admin:stayclassy404@192.168.4.247/video/mjpg.cgi')
bytes=''
while True:
    bytes+=stream.read(16384)
    a = bytes.find('\xff\xd8')
    b = bytes.find('\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        orig_img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
        img = cv2.flip(orig_img,1)
        
        
        img = cv2.GaussianBlur(orig_img, (5,5), 0)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img = cv2.resize(img, (len(orig_img[0]) / 4, len(orig_img) / 4))
        
        red_lower = np.array([144, 150, 20],np.uint8)
        red_upper = np.array([170, 255, 255],np.uint8)
        red_binary = cv2.inRange(img, red_lower, red_upper)
        
        img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)
        
        
        dilation = np.ones((15, 15), "uint8")
        red_binary = cv2.dilate(red_binary, dilation)
        
        contours, hierarchy = cv2.findContours(red_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        max_area = 0
        largest_contour = None
        for idx, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                largest_contour = contour
                
        if not largest_contour == None:
            moment = cv2.moments(largest_contour)
            if moment["m00"] > 1000 / 4:
                rect = cv2.minAreaRect(largest_contour)
                rect = ((rect[0][0] * 4, rect[0][1] * 4), (rect[1][0] * 4, rect[1][1] * 4), rect[2])
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(orig_img,[box], 0, (0, 0, 255), 2)
                cv2.imshow("ColourTrackerWindow", orig_img)
        else:
            cv2.imshow("ColourTrackerWindow", orig_img)
                
    if cv2.waitKey(1) ==27:
        exit(0)  
