# -*- coding: utf-8 -*-
# @Time : 2022/10/5 22:48
# @Author : shuoshuo
# @File : beautify.py
# @Project : 美颜
import math

import cv2
import numpy as np
import matplotlib.pyplot as plt
import face_beauty.face_detect
import face_beauty.ellipse_skin_model

def bilinear_interpolation(img,vector_u,c):
    ux,uy=vector_u
    x1,x2 = int(ux),int(ux+1)
    y1,y2 = int(uy),int(uy+1)

    # f_x_y1 = (x2-ux)/(x2-x1)*img[x1][y1]+(ux-x1)/(x2-x1)*img[x2][y1]
    # f_x_y2 = (x2 - ux) / (x2 - x1) * img[x1][y2] + (ux - x1) / (x2 - x1) * img[x2][y2]

    f_x_y1 = (x2-ux)/(x2-x1)*img[y1][x1][c]+(ux-x1)/(x2-x1)*img[y1][x2][c]
    f_x_y2 = (x2 - ux) / (x2 - x1) * img[y2][x1][c] + (ux - x1) / (x2 - x1) * img[y2][x2][c]

    f_x_y = (y2-uy)/(y2-y1)*f_x_y1+(uy-y1)/(y2-y1)*f_x_y2
    return int(f_x_y)
def Local_scaling_warps(img,cx,cy,r_max,a):
    img1 = np.copy(img)
    for y in range(cy-r_max,cy+r_max+1):
        d = int(math.sqrt(r_max**2-(y-cy)**2))
        x0 = cx-d
        x1 = cx+d
        for x in range(x0,x1+1):
            r = math.sqrt((x-cx)**2 + (y-cy)**2) #求出当前位置的半径
            for c in range(3):
                vector_c = np.array([cx, cy])
                vector_r =np.array([x,y])-vector_c
                f_s = (1-((r/r_max-1)**2)*a)
                vector_u = vector_c+f_s*vector_r#原坐标
                img1[y][x][c] = bilinear_interpolation(img,vector_u,c)
    return img1

def big_eye(img,r_max,a,left_eye_pos=None,right_eye_pos=None):
    img0 = img.copy()
    if left_eye_pos==None or right_eye_pos==None:
        left_eye_pos,right_eye_pos=face_beauty.face_detect.get_face_key_point(img)
    img0 = cv2.circle(img0,left_eye_pos,radius=10,color=(0,0,255))
    img0 = cv2.circle(img0,right_eye_pos,radius=10,color=(0,0,255))
    img= Local_scaling_warps(img,left_eye_pos[0],left_eye_pos[1],r_max=r_max,a=a)
    img = Local_scaling_warps(img,right_eye_pos[0],right_eye_pos[1],r_max=r_max,a=a)
    return img
def guided_filter(I,p,win_size,eps):
    assert I.any() <=1 and p.any()<=1
    mean_I = cv2.blur(I,(win_size,win_size))
    mean_p = cv2.blur(p,(win_size,win_size))

    corr_I = cv2.blur(I*I,(win_size,win_size))
    corr_Ip = cv2.blur(I*p,(win_size,win_size))

    var_I = corr_I-mean_I*mean_I
    cov_Ip = corr_Ip - mean_I*mean_p

    a = cov_Ip/(var_I+eps)
    b = mean_p-a*mean_I

    mean_a = cv2.blur(a,(win_size,win_size))
    mean_b = cv2.blur(b,(win_size,win_size))

    q = mean_a*I + mean_b

    return q
def mopi(img):
    skin,_ = face_beauty.ellipse_skin_model.YCrCb_ellipse_model(img)#获得皮肤的掩膜数组
    #进行一次开运算
    kernel = np.ones((3,3),dtype=np.uint8)
    skin = cv2.erode(skin,kernel=kernel)
    skin = cv2.dilate(skin,kernel=kernel)
    img1 = guided_filter(img/255.0,img/255.0,5,eps=0.001)*255
    img1 = np.array(img1,dtype=np.uint8)
    img1 = cv2.bitwise_and(img1,img1,mask=skin)#将皮肤与背景分离
    skin = cv2.bitwise_not(skin)
    img1 = cv2.add(img1,cv2.bitwise_and(img,img,mask=skin))#磨皮后的结果与背景叠加
    # fig, ax = plt.subplots(1, 2)
    # ax[0].imshow(skin)
    # ax[1].imshow(img1[:, :, ::-1])
    # plt.show()
    return img1
if __name__ == '__main__':

    img = cv2.imread('img.png')

    img1 = mopi(img)
    big_eye(img1,r_max=40,a=0.8)


