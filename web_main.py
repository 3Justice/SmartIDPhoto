from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import timedelta

from u_2_net import my_u2net_test
from to_background import to_background
from to_background import to_standard_trimap
from m_dlib import ai_crop
import os
app = Flask(__name__)

# 输出
@app.route('/')
def hello_world():
    return 'Hello World!'



# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 设置静态文件缓存过期时间
#app.send_file_max_age_default = timedelta(seconds=1)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

# 添加路由
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # 通过file标签获取文件
    f = request.files['file']
    if not (f and allowed_file(f.filename)):
        return jsonify({"error": 1001, "msg": "图片类型：png、PNG、jpg、JPG、bmp"})
    # 当前文件所在路径
    basepath = os.path.dirname(__file__)
    print(basepath)
    # 一定要先创建该文件夹，不然会提示没有该路径
    upload_path = os.path.join(basepath, 'static\images', secure_filename(f.filename))
    print(upload_path)
    # 保存文件
    f.save(upload_path)

    org_img = upload_path
    alpha_img =os.path.join(basepath, 'static\images\meinv_alpha.png')

    #alpha_resize_img = "img\meinv_alpha_resize.png"
    alpha_resize_img = os.path.join(basepath, 'static\images\size_re.png')
    # #
    # 通过u_2_net 获取 alpha
    my_u2net_test.seg_trimap(org_img, alpha_img, alpha_resize_img)
    #
    print("-----------------------------")
    # # 通过alpha 获取 trimap
    trimap =os.path.join(basepath, 'static\images\meinv_trimap_resize.png')
    to_standard_trimap.to_standard_trimap(alpha_resize_img, trimap)
    #
    # 证件照添加蓝底纯色背景
    id_image=os.path.join(basepath, 'static\images\meinv_id.png')
    to_background.to_background(org_img, trimap, id_image, "blue")
    # id_image = "..\\aiphoto\\img\\meinv_id_grid.png"
    # to_background.to_background_grid(org_img, trimap, id_image)
    # image = Image.open(id_image)
    # data = image.getdata()
    # np.savetxt("data6.txt", data,fmt='%d',delimiter=',')

    # 20200719
    # 通过识别人脸关键点，裁剪图像
    deal_img=os.path.join(basepath, 'static\images\deal.png')
    ai_crop.crop_photo(id_image, deal_img)

    # 返回上传成功界面
    return render_template("index.html")
# 重新返回上传界面


if __name__ == '__main__':
    app.run(debug=True)


