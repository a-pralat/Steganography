from BBS import BBS
from LSB import LSB
from utils import *


class GUI:
    def __init__(self):
        print('GUI class has been initialized')
        self.app = QtWidgets.QApplication([])
        self.window = QtWidgets.QMainWindow()
        self.message_box = QtWidgets.QMessageBox()
        self.pixmap = QtGui.QPixmap()
        self.bbs, self.lsb = BBS(), LSB()

        self.setup()

    def setup(self) -> None:
        self.app.aboutToQuit.connect(self.quit)
        uic.loadUi('windows/mainWindow.ui', self.window)

        self.window.buttonExecute.clicked.connect(self.execute)

        self.window.actionOpen.triggered.connect(self.open)
        self.window.actionSave.triggered.connect(self.save)

        self.window.actionInfo.triggered.connect(self.info)
        self.window.actionHelp.triggered.connect(self.help)
        self.window.actionAbout.triggered.connect(self.about)

        self.window.show()

    def execute(self) -> None:
        decrypt = self.window.checkboxMode.isChecked()

        if not decrypt:
            self.encrypt()
        else:
            self.decrypt()

    def encrypt(self) -> None:
        print('Encryption')
        # message
        message = self.window.textPlainText.toPlainText()
        message = str_to_bytes(message)

        # key
        seed = self.window.textSeed.toPlainText()
        if not valid_seed(seed):
            self.message_box.about(self.message_box, 'Info', 'Invalid seed')
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

        result = self.lsb.hide_data(input_image, encoded_file, output_image, int(lsb_number))
        if result is not None:
            self.message_box.about(self.message_box, 'Info', result)
        else:
            # show and compare images
            self.pixmap = QtGui.QPixmap(input_image).scaled(460, 400)
            self.window.imageBefore.setPixmap(self.pixmap)
            self.pixmap = QtGui.QPixmap(output_image).scaled(460, 400)
            self.window.imageAfter.setPixmap(self.pixmap)

    def decrypt(self) -> None:
        print('Decryption')
        # recover
        input_image = self.window.textInputImage.toPlainText()
        if not exists(input_image) or not input_image.lower().endswith(('.bmp', '.png')):
            self.message_box.about(self.message_box, 'Info', 'Invalid input image path')
            return

        output_file = 'messages/output.txt'

        lsb_number = self.window.textLSBNumber.toPlainText()
        if not valid_lsb_number(lsb_number):
            self.message_box.about(self.message_box, 'Info', 'Invalid number of LSB')
            return

        message = self.lsb.recover_data(input_image, output_file, int(lsb_number))
        if isinstance(message, str):
            self.message_box.about(self.message_box, 'Info', message)
        else:
            # key
            seed = self.window.textSeed.toPlainText()
            if not valid_seed(seed):
                self.message_box.about(self.message_box, 'Info', 'Invalid seed')
                return
            self.bbs.seed = int(seed)
            key = self.bbs.generate_bytes(len(message))

            # decode
            decoded = byte_xor(message, key)
            decoded_file = 'messages/decoded.txt'
            try:
                file = open(decoded_file, 'wb')
                file.write(decoded)
                file.close()
            except Exception:
                raise ValueError('[ENCRYPTION]: Could not save encoded message')

    def open(self) -> None:
        filename = self.window.textPlainText.toPlainText() + '.txt'

        if not exists(filename):
            self.message_box.about(self.message_box, 'Error', 'File not found')
        else:
            file = open(filename, 'r')
            data = file.read()
            file.close()
            self.window.textPlainText.setPlainText(data)

    def save(self) -> None:
        plain_text = f'messages/saved.txt'
        try:
            file_plain_text = open(plain_text, 'w')
        except Exception:
            raise ValueError('[SAVE]: Could not save results')
        text_plain_text = self.window.textPlainText.toPlainText()
        file_plain_text.write(text_plain_text)
        file_plain_text.close()

    def info(self) -> None:
        self.message_box.about(
            self.message_box, 'Info: Steganography with BBS and LSB',
            'Encryption\n'
            '1. Create pseudorandom key with chosen BBS seed\n'
            '2. Encrypt message by XOR operation with key and message\n'
            '3. Hide encrypted message in image with chosen LSB number\n\n'
            'Decryption\n'
            '1. Recover encrypted message from image with chosen LSB number\n'
            '2. Create pseudorandom key with chosen BBS seed\n'
            '3. Decrypt encrypted message by XOR operation with key and message\n'
        )

    def help(self) -> None:
        self.message_box.about(
            self.message_box, 'Help',
            'Input text: plain text / file path\n'
            'Input image: image path (.bmp or .png)\n'
            'Output image: image path (.bmp or .png)\n'
            'Data size: limited by system\n'
            'Data format: Unicode encoding\n'
            'Open text file: File -> Open\n'
            'Save text file: File -> Save\n'
        )

    def about(self) -> None:
        self.message_box.about(
            self.message_box, 'About',
            'Author: Anna Prałat 145395\n'
            'Language: Python 3.9\n'
            'GUI library: PyQt5\n'
            'IDE: Pycharm 2022.1\n'
        )

    def quit(self) -> None:
        self.window.close()
