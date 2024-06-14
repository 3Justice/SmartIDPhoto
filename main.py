
from u_2_net import my_u2net_test
from to_background import to_background
from to_background import to_standard_trimap
from m_dlib import ai_crop


def deal(img_path,color,size1,size2,size3):
    org_img=img_path
    alpha_img = "img\meinv_alpha.png"
    alpha_resize_img = "img\meinv_alpha_resize.png"
    # #
    # 通过u_2_net 获取 alpha
    my_u2net_test.seg_trimap(org_img, alpha_img, alpha_resize_img)
    #
    print("-----------------------------")
    # # 通过alpha 获取 trimap
    trimap = "img\meinv_trimap_resize.png"
    to_standard_trimap.to_standard_trimap(alpha_resize_img, trimap)
    #
    # 证件照添加蓝底纯色背景
    id_image = "img\meinv_id.png"
    to_background.to_background(org_img, trimap, id_image, color)
    # id_image = "..\\aiphoto\\img\\meinv_id_grid.png"
    # to_background.to_background_grid(org_img, trimap, id_image)
    # image = Image.open(id_image)
    # data = image.getdata()
    # np.savetxt("data6.txt", data,fmt='%d',delimiter=',')

    # 20200719
    # 通过识别人脸关键点，裁剪图像
    ai_crop.crop_photo("img\meinv_id.png", "last.jpg",size1,size2,color,size3)


#
# import numpy as np
# from PIL import Image
# if __name__ == "__main__":
#     org_img = "img\meinv.jpg"
#     alpha_img = "img\meinv_alpha.png"
#     alpha_resize_img = "img\meinv_alpha_resize.png"
#     # #
#     # 通过u_2_net 获取 alpha
#     my_u2net_test.seg_trimap(org_img, alpha_img, alpha_resize_img)
#     #
#     print("-----------------------------")
#     # # 通过alpha 获取 trimap
#     trimap = "img\meinv_trimap_resize.png"
#     to_standard_trimap.to_standard_trimap(alpha_resize_img, trimap)
#     #
#     # 证件照添加蓝底纯色背景
#     id_image = "img\meinv_id.png"
#     to_background.to_background(org_img, trimap, id_image, "blue")
#     #id_image = "..\\aiphoto\\img\\meinv_id_grid.png"
#     #to_background.to_background_grid(org_img, trimap, id_image)
#     # image = Image.open(id_image)
#     # data = image.getdata()
#     # np.savetxt("data6.txt", data,fmt='%d',delimiter=',')
#
#     # 20200719
#     # 通过识别人脸关键点，裁剪图像
#     ai_crop.crop_photo("img\meinv_id.png", "img\\in.jpg")
