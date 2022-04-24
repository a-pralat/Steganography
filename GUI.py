from BBS import BBS
from LSB import LSB
from utils import *

class GUI:
    def __init__(self):
        print('GUI class has been initialized')
        self.app = QtWidgets.QApplication([])
        self.window = QtWidgets.QMainWindow()
        self.message_box = QtWidgets.QMessageBox()
        self.bbs = BBS()
        self.lsb = LSB()

        self.setup()

    def setup(self):
        self.app.aboutToQuit.connect(self.quit)
        uic.loadUi('windows/mainWindow.ui', self.window)

        self.window.buttonExecute.clicked.connect(self.execute)

        self.window.actionOpen.triggered.connect(self.open)
        self.window.actionSave.triggered.connect(self.save)
        self.window.actionHelp.triggered.connect(self.help)
        self.window.actionInfo.triggered.connect(self.info)

        self.window.show()

    def execute(self) -> None:
        decrypt = self.window.checkboxMode.isChecked()

        # encryption
        if not decrypt:
            self.encryption()
        else:
            self.decryption()

    def encryption(self) -> None:
        print('Encryption')
        # message
        message = self.window.textPlainText.toPlainText()
        message = str_to_bytes(message)

        # key
        seed = self.window.textSeed.toPlainText()
        if not valid_seed(seed):
            self.message_box.about(self.message_box, 'Info', 'Invalid seed')
            self.window.textSeed.setPlainText('')
            return
        self.bbs.seed = int(seed)
        key = self.bbs.generate_bytes(len(message))

        # encode
        encoded = byte_xor(message, key)
        encoded_file = 'messages/encoded.txt'
        try:
            file = open(encoded_file, 'wb')
            file.write(encoded)
            file.close()
        except Exception:
            raise ValueError('[ENCRYPTION]: Could not save encoded message')
        self.window.textCipher.setPlainText(encoded.decode(sys.getdefaultencoding(), 'strict'))

        # hide
        input_image = self.window.textInputImage.toPlainText()
        if not exists(input_image) or not input_image.lower().endswith(('.bmp', '.png')):
            self.message_box.about(self.message_box, 'Info', 'Invalid input image path')
            return

        output_image = self.window.textOutputImage.toPlainText()
        if output_image == '' or not output_image.lower().endswith(('.bmp', '.png')):
            self.message_box.about(self.message_box, 'Info', 'Invalid output image path')
            return

        lsb_number = self.window.textLSBNumber.toPlainText()
        if not valid_lsb_number(lsb_number):
            self.message_box.about(self.message_box, 'Info', 'Invalid number of LSB')
            return

        self.lsb.hide_data(input_image, encoded_file, output_image, int(lsb_number))

    def decryption(self):
        print('Decryption')


    def open(self) -> None:
        decrypt = self.window.checkboxMode.isChecked()
        if not decrypt:
            filename = self.window.textPlainText.toPlainText() + '.txt'
        else:
            filename = self.window.textCipher.toPlainText() + '.txt'

        if not exists(filename):
            self.message_box.about(self.message_box, 'Error', 'File not found')
        else:
            file = open(filename, 'r')
            data = file.read()
            file.close()
            if not decrypt:
                self.window.textPlainText.setPlainText(data)
            else:
                self.window.textCipher.setPlainText(data)

    def save(self) -> None:
        directory = 'saved'
        plain_text, cipher = f'{directory}/plain_text.txt', f'{directory}/cipher.txt'
        try:
            file_plain_text = open(plain_text, 'w')
            file_cipher = open(cipher, 'w')
        except Exception:
            raise ValueError('[SAVE]: Could not save results')
        text_plain_text = self.window.textPlainText.toPlainText()
        text_cipher = self.window.textCipher.toPlainText()
        file_plain_text.write(text_plain_text)
        file_cipher.write(text_cipher)
        file_plain_text.close()
        file_cipher.close()

    def help(self) -> None:
        pass

    def info(self) -> None:
        pass

    def quit(self) -> None:
        self.window.close()
