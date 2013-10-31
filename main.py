#numpy and opencv2 library needed to run the code below

import cv2,math,os,sys
import urllib 
import numpy as np
from time import sleep 
#import to get date time
import datetime
import threading



class bodyDetectThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
        #default peoiple detection(not very good method of detection**)
        #self.hog = cv2.HOGDescriptor()
        #self.hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )
        
        #retrieve current directory
        pathname = os.path.dirname(sys.argv[0])
        current_dir = os.path.abspath(pathname)
        
        #training data for detecting sections of body
        self.upperbody = cv2.CascadeClassifier(current_dir+"cascade_classifier/haarcascade_upperbody.xml")
        self.frontface = cv2.CascadeClassifier(current_dir+"cascade_classifier/haarcascade_frontalface_alt.xml")
        self.fullbody = cv2.CascadeClassifier(current_dir+"cascade_classifier/haarcascade_fullbody.xml")
        
        #forbackround subtraction
        self.backsub = cv2.BackgroundSubtractorMOG()
        self.img = None
        #post processed image for detection
        self.proImg = None
        #background image mask
        self.mask = None

        self.filterdRect = []
        self.rect = []
        self.lineWidth = 1
        
    def inside(self,r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
    def run(self):
        while True:
            if not self.img == None:
            
                try:
                    if False:
                        #**background removal test code not active
                        self.mask = cv2.GaussianBlur(self.img, (5,5), 0)
                        element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                        self.mask = cv2.erode(self.mask,element)
                        self.mask = self.backsub.apply(self.mask, None, 0.10)
                        self.mask = cv2.cvtColor(self.mask,cv2.COLOR_GRAY2BGR)
                        
                        apply image mask on binary level to remove background
                        self.proImg = self.img & self.mask
                        
                        
                    if False:
                        #**background removal test code not active
                        #self.rect, w = self.hog.detectMultiScale(self.proImg, winStride=(4,4), padding=(16,16), scale=1.05)
                    
                    #**Cascade classfier detection code 
                    cascade file xml upper body detection
                    self.rect = self.upperbody.detectMultiScale(self.img, scaleFactor=1.3, minNeighbors=4, minSize=(4,4), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)
                    if len(self.rect) > 0:
                        print 'upper body'
                    
                    if len(self.rect) < 1:
                        self.rect = self.frontface.detectMultiScale(self.img, scaleFactor=1.3, minNeighbors=4, minSize=(4,4), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)
                        if len(self.rect) > 0:
                            print 'face'
                        
                    
                    if len(self.rect) < 1:
                        self.rect = self.fullbody.detectMultiScale(self.img, scaleFactor=1.3, minNeighbors=4, minSize=(4,4), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)
                        if len(self.rect) > 0:
                            print 'full body'

                    #remove overlaping rectagles and place results in filterdRect
                    self.filterdRect = []
                    for ri, r in enumerate(self.rect):
                        for qi, q in enumerate(self.rect):
                            if ri != qi and self.inside(r, q):
                                break
                        else:
                            self.filterdRect.append(r)

                except Exception as ex:
                    print 'failed to detect body\n', str(ex)
                
                

                

        
def main_loop():
    stream=urllib.urlopen('http://admin:stayclassy404@192.168.4.247/video/mjpg.cgi')
    bytes=''

    
    bodyDetect = bodyDetectThread()
    bodyDetect.start()
    
    while True:
        #Read bytes from url and look for jpeg flaf in file
        bytes+=stream.read(16384)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            bodyDetect.img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            
            #look for stored rectagles from body detect thred to draw on to final image
            for x, y, w, h in bodyDetect.rect:
                # the HOG detector returns slightly larger rectangles than the real objects.
                # so we slightly shrink the rectangles to get a nicer output.
                pad_w, pad_h = int(0.15*w), int(0.05*h)
                cv2.rectangle(bodyDetect.img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), 1)
            
            
            #if not bodyDetect.mask == None:
                #cv2.imshow('people detection demo', bodyDetect.mask)
            #if not bodyDetect.proImg == None:
                #cv2.imshow('people detection demo', bodyDetect.proImg)
            if not bodyDetect.img == None:    
                cv2.imshow('people detection demo', bodyDetect.img)
        #exit applicaiton when the escape key is pressed
        if cv2.waitKey(1) ==27:
            bodyDetect._Thread__stop()
            exit(0)  
            
            
main_loop()
