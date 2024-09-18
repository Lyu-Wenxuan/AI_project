# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication , QMainWindow, QFileDialog, QMessageBox,QWidget
from MainWin import Ui_MainWindow
import sys
import os
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
import image_utils
from stylize import Stylizer
from PIL import Image, ImageQt
import numpy as np

class MainWindow(QMainWindow,QWidget):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.style_list = {'style1':['style1.pt','images/styleImgs/1.jpg'],
                           'style2':['style2.pt','images/styleImgs/2.jpg'],
                           'style3':['style3.pt','images/styleImgs/3.jpg']}
        self.ch_style_dict = {'梵高风格':'style1','网格风格':'style2','彩笔风格':'style3'}

        self.initMain()
        self.signalconnect()
        self.show_height = 330
        self.show_width = 420


    def signalconnect(self):
        self.ui.imgBtn.clicked.connect(self.getfile)
        self.ui.chageBtn.clicked.connect(self.change_img_style)
        self.ui.comboBox.currentIndexChanged.connect(self.style_change)
        self.ui.saveBtn.clicked.connect(self.save_img)

        self.ui.actionopen.triggered.connect(self.getfile)
        self.ui.action.triggered.connect(self.save_img)


    def initMain(self):
        self.ui.label_4.setStyleSheet("color: red;")


        self.org_path = None
        self.stylized_img = None

        styles = list(self.ch_style_dict.keys())
        self.ui.comboBox.addItems(styles)
        self.choose_style = self.ch_style_dict[self.ui.comboBox.currentText()]
        self.ui.styleLb.setPixmap(QPixmap(self.style_list[self.choose_style][1]))


        self.model_path = os.path.join('models',self.style_list[self.choose_style][0])
        self.model = Stylizer(self.model_path)


        # 设置主页背景图片
        self.setStyleSheet("#MainWindow{border-image:url(./images/bg1.jpg)}")

        # 修改 comboBox 字体大小
        font = self.ui.comboBox.font()  # 获取当前 comboBox 的字体
        font.setPointSize(10)  # 设置字体大小为20
        self.ui.comboBox.setFont(font)  # 将修改后的字体应用到 comboBox

    def style_change(self):
        self.choose_style = self.ch_style_dict[self.ui.comboBox.currentText()]
        self.model_path = os.path.join('models', self.style_list[self.choose_style][0])
        self.ui.styleLb.setPixmap(QPixmap(self.style_list[self.choose_style][1]))
        self.model = Stylizer(self.model_path)

    def getfile(self):
        # 弹出的窗口名称：'Open file'
        # 默认打开的目录：'./'
        # 只能打开.jpg与.gif结尾的图片文件
        # file_path, _ = QFileDialog.getOpenFileName(self.ui.centralwidget, '打开图片', './', "Image files (*.jpg *.gif)")
        file_path, _ = QFileDialog.getOpenFileName(None, '打开图片', './', "Image files (*.jpg *.gif)")
        if not file_path:
            return

        self.org_path = file_path
        self.org_img = Image.open(self.org_path)
        img_width, img_height = self.get_resize_size(self.org_img)

        # resize_img_res = self.resize_image(self.org_img)
        # self.ui.orgImg.setPixmap(ImageQt.toqpixmap(resize_img_res))
        # # self.ui.orgImg.setScaledContents(False)
        # self.ui.TransImg.setPixmap(QPixmap(""))

        resize_img_res = QPixmap(self.org_path).scaled(img_width, img_height)
        self.ui.orgImg.setPixmap(resize_img_res)
        self.ui.orgImg.setAlignment(Qt.AlignCenter)
        self.ui.TransImg.setPixmap(QPixmap(""))

        self.ui.lineEdit.setText(file_path)


    def resize_image(self, img):
        _img = img.copy()
        self.img_width, self.img_height = self.get_resize_size(img)
        pil_res_img = _img.resize((self.img_width, self.img_height),Image.LANCZOS)
        return pil_res_img

    def get_resize_size(self, img):
        _img = img.copy()
        img_width, img_height = _img.size
        ratio = img_width / img_height
        if ratio >= self.show_width /self.show_height:
            self.img_width = self.show_width
            self.img_height = int(self.img_width / ratio)
        else:
            self.img_height = self.show_height
            self.img_width = int(self.img_height * ratio)
        return self.img_width,self.img_height


    def change_img_style(self):
        if self.org_path is None:
            QMessageBox.about(self,'提示','请先选择一张图片！')
            return

        # 将图片缩小
        image_pil = Image.open(self.org_path)
        img_width, img_height = self.get_resize_size(image_pil)
        resize_img_res = image_pil.resize((img_width*2, img_height*2), Image.LANCZOS)

        image_pil = resize_img_res.convert("RGB")
        image_np = np.array(image_pil)
        image_np = image_np.astype(np.float32) / 255.0

        self.stylized_img = self.model.stylize(image_np)
        self.final_img = image_utils.to_pil(self.stylized_img)
        self.res_img = self.resize_image(self.final_img)

        self.change_qpixmap = ImageQt.toqpixmap(self.res_img)
        self.ui.TransImg.setPixmap(self.change_qpixmap)
        self.ui.TransImg.setAlignment(Qt.AlignCenter)
        print('style change successs!')

    def save_img(self):
        if self.stylized_img is None:
            QMessageBox.about(self, '提示', '请先转换图片！')
            return
        # 默认保存在save_imgs目录下
        path, img_name = os.path.split(self.org_path)
        save_path = self.choose_style + '_' + img_name
        save_path = os.path.join('save_imgs', save_path)
        image_utils.save(self.stylized_img, save_path)
        QMessageBox.about(self, '提示', '图片保存成功！')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
