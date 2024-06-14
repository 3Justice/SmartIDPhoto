# -*- coding: utf-8 -*-
# @Time : 2022/10/18 21:54
# @Author : shuoshuo
# @File : ellipse_skin_model.py
# @Project : 美颜
import numpy as np
import cv2


def YCrCb_ellipse_model(img):
    skinCrCbHist = np.zeros((256,256), dtype= np.uint8)
    cv2.ellipse(skinCrCbHist, (113,155),(23,25), 43, 0, 360, (255,255,255), -1) #绘制椭圆弧线
    YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB) #转换至YCrCb空间
    (Y,Cr,Cb) = cv2.split(YCrCb) #拆分出Y,Cr,Cb值
    skin = np.zeros(Cr.shape, dtype = np.uint8) #掩膜
    (x,y) = Cr.shape
    for i in range(0, x):
        for j in range(0, y):
            if skinCrCbHist [Cr[i][j], Cb[i][j]] > 0: #若不在椭圆区间中
                skin[i][j] = 255
    res = cv2.bitwise_and(img,img, mask = skin)
    return skin,res
if __name__ == '__main__':
    pass
