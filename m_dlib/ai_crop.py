import m_dlib.face_marks as fmarks
from PIL import Image

colour_dict = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "blue": (67, 142, 219)
}


def crop_photo(path, target,size_width,size_height, cl, size3):
    path = path
    shape, d = fmarks.predictor_face(path)

    WIDTH_2IN = size_width/2
    HEIGHT_2IN = size_height/2

    # 人像中心点
    X_CENTRE = d.left()+(d.right()-d.left()) / 2
    Y_CENTER = d.top()+(d.bottom()-d.top()) / 2

    im = Image.open(path)
    i=im.size[0]
    j=im.size[1]
    scale_factor=size_width/i

    im = im.resize((size_width,size_height), Image.LANCZOS)

    #im = im.crop((X_CENTRE-i/2, Y_CENTER-j/2+25, X_CENTRE+i/2-10, Y_CENTER+j/2))
    #w= im.size[0]
    #h = im.size[1]
    #scaled_width = int(w * scale_factor*0.9)
    #scaled_height = int(h * scale_factor*0.9)
    #im = im.resize((scaled_width, scaled_height))

    #p = Image.new('RGB',(im.size[0], size3), colour_dict[cl])

    im.save(target)


# 通过识别人脸关键点，裁剪图像
# crop_photo("..//img//meinv_id.png","..//img//2in.jpg")


