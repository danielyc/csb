from PyQt5 import QtWidgets, uic, QtGui, QtCore
from collections import OrderedDict
import sys, os, ast, bot, update
import encrypt as enc
import selenium.webdriver.chrome.service as services
REGION = ''

paydetails = OrderedDict(
    [('Name', ''), ('Email', ''), ('Phone', ''), ('Addr1', ''), ('Addr2', ''), ('Addr3', ''),
     ('City', ''), ('Post/zip code', ''), ('Country', ''), ('CardType', ''), ('Cardno', ''),
     ('CardCVV', ''), ('CardMonth', ''), ('CardYear', ''), ('Region', '')])

itemdetails = OrderedDict(
    [('Category', ''), ('Keywords', ''), ('Colour', ''), ('Size', ''), ('Time', '')])


def getLoc(f):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, f)

def readPath():
    if sys.platform == 'win32':
        if os.path.isfile('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'):
            return 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    elif sys.platform == 'darwin':
        if os.path.isfile('/Applications/Google Chrome.app'):
            return '/Applications/Google Chrome.app'
    elif os.path.isfile('chromepath.txt'):
        f = open(getLoc("chromepath.txt"), "r").readlines()
        makeitastring = ''.join(map(str, f))
        return makeitastring
    else:
        print('"chromepath.txt" not found in current directory')


class itemSel(QtWidgets.QMainWindow):
    def __init__(self):
        global service, capabilities, newProxy
        self.useProxy = False
        newProxy = proxy()
        chromePath = readPath()
        if sys.platform == 'win32':
            service = services.Service('chromedriver.exe')
        elif sys.platform == 'darwin':
            service = services.Service('./chromedriver')
        capabilities = {'chrome.binary': chromePath}

        QtWidgets.QWidget.__init__(self)
        self.ui = uic.loadUi(getLoc('GUIS/itemConfig.ui'), self)
        self.setWindowIcon(QtGui.QIcon(getLoc('GUIS/icon.png')))
        self.label.setPixmap(QtGui.QPixmap(getLoc('GUIS/title.png')))
        self.strictItemSelect = True
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
        self.populateDropdowns()
        self.ui.category.currentIndexChanged.connect(self.updateFields)
        self.ui.add_item.clicked.connect(self.addItem)
        self.ui.delete_item.clicked.connect(self.removeItem)
        self.ui.start.clicked.connect(self.go)
        self.updateFields()
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet("QMenuBar::item::selected { background-color: rgb(200, 200, 200);}"
                                   "QMenuBar { background-color: rgb(226, 226, 226);}")
        optMenu = self.menubar.addMenu('Options')
        proxyMenu = self.menubar.addMenu('Proxy')
        self.useProxyS = QtWidgets.QAction("Use proxy", self, checkable=True)
        changeProxy = QtWidgets.QAction("Proxy Settings", self, checkable=False)
        changeProxy.triggered.connect(self.openProxy)
        self.useProxyS.triggered.connect(self.setProxy)
        proxyMenu.addAction(self.useProxyS)
        proxyMenu.addAction(changeProxy)
        strictAct = QtWidgets.QAction('Strict item selection', self, checkable=True)
        strictAct.triggered.connect(self.strict)
        strictAct.setChecked(True)
        optMenu.addAction(strictAct)

    def setProxy(self):
        self.useProxy = not self.useProxy

    def openProxy(self):
        newProxy.show()

    def populateTime(self, strict):
        self.ui.time.clear()
        if strict:
            for x in range(0, 24):
                self.ui.time.addItem(str(x).zfill(2) + ':00')
                self.ui.time.addItem(str(x).zfill(2) + ':59')
        else:
            for x in range(0, 24):
                self.ui.time.addItem(str(x).zfill(2) + ':00')

    def populateDropdowns(self):
        cats = ['jackets','shirts','tops_sweaters','sweatshirts','pants','shorts','t-shirts','hats','bags','accessories',
                'skate','shoes']
        for x in cats:
            self.ui.category.addItem(x)
        self.populateTime(True)

    def updateStatus(self, text):
        self.ui.status.setStyleSheet('color: RED')
        self.ui.status.setText('Status: ' + text)

    def warnStatus(self, text):
        self.updateStatus(text)
        self.ui.status.setStyleSheet('color: ORANGE')

    def clearStatus(self):
        self.updateStatus('OK')
        self.ui.status.setStyleSheet('color: GREEN')

    def strict(self):
        self.strictItemSelect = not self.strictItemSelect
        self.populateTime(self.strictItemSelect)

    def go(self):
        itemdets = []
        for x in range(0, len(self.ui.item_list)):
            text = ast.literal_eval(self.ui.item_list.item(x).text())
            itemdets.append(text)
        time = self.ui.time.currentText()
        bot.openChrome(paydetails, itemdets, time, self.strictItemSelect, service, capabilities, self.useProxy, newProxy.selected_ip)

    def removeItem(self):
        if self.ui.item_list.currentRow() != -1:
            self.ui.item_list.takeItem(self.ui.item_list.currentRow())
            self.warnStatus('Item removed')
        else:
            self.updateStatus('No item selected')

    def addItem(self):
        self.clearStatus()
        if len(self.ui.keywords.text()) == 0:
            self.updateStatus('No keywords specified')
            return None
        if len(self.ui.colour.text()) == 0:
            self.warnStatus('No ' + self.ui.colour_text.text()[:-1].lower() + ' specified')
        if len(self.ui.size.text()) == 0 and self.ui.size.isEnabled():
            self.warnStatus('First available size selected')
        if len(self.ui.size.text()) == 0 and self.ui.size.isEnabled() and len(self.ui.colour.text()) == 0:
            self.warnStatus('First available size/' + self.ui.colour_text.text()[:-1].lower() + ' selected')
        if self.ui.size.isEnabled():
            self.ui.item_list.addItem(str([self.ui.category.currentText(), self.ui.keywords.text(),
                                           self.ui.colour.text().title(), self.ui.size.text()]))
        elif self.ui.size_drop.isEnabled():
            self.ui.item_list.addItem(str([self.ui.category.currentText(), self.ui.keywords.text(),
                                           self.ui.colour.text().title(), self.ui.size_drop.currentText()]))

    def updateFields(self):
        sizes = ['Small','Medium','Large','XLarge', 'First available']
        sizeCats = ['jackets', 'shirts','tops_sweaters','sweatshirts','t-shirts','shorts']
        if self.ui.category.currentText() == 'skate':
            self.ui.colour_text.setText('Board size:')
            self.ui.size_text.hide()
            self.ui.size.setEnabled(False)
            self.ui.size.hide()
            self.ui.size_drop.setEnabled(False)
            self.ui.size_drop.hide()
        else:
            self.ui.colour_text.setText('Colour:')
            self.ui.size_text.show()
            self.ui.size.setEnabled(True)
            self.ui.size.show()

        if self.ui.category.currentText() in sizeCats:
            self.ui.size.setEnabled(False)
            self.ui.size.hide()
            self.ui.size_drop.setEnabled(True)
            self.ui.size_drop.show()
            self.ui.size_drop.clear()
            for x in sizes:
                self.ui.size_drop.addItem(x)
        elif self.ui.category.currentText() == 'shoes':
            self.ui.size_drop.setEnabled(False)
            self.ui.size_drop.hide()
            self.ui.size.setEnabled(True)
            self.ui.size.show()
            if REGION == 'EU':
                self.ui.size.setPlaceholderText('US 9 / UK 8, ...')
            elif REGION == 'US':
                self.ui.size.setPlaceholderText('7, 8, 9, ...')
        elif self.ui.category.currentText() != 'skate':
            self.ui.size_drop.setEnabled(False)
            self.ui.size_drop.hide()
            self.ui.size.setEnabled(True)
            self.ui.size.show()
            self.ui.size.setPlaceholderText('')


class paydet(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = uic.loadUi(getLoc('GUIS/PDConfig.ui'), self)
        self.setWindowIcon(QtGui.QIcon(getLoc('GUIS/icon.png')))
        self.logo.setPixmap(QtGui.QPixmap(getLoc('GUIS/title.png')))
        self.cc = True
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
        self.updateRegion()
        self.populateCC()
        self.ui.continue_btn.clicked.connect(self.cont)
        self.ui.save_btn.clicked.connect(self.saveConfig)
        self.loadToolTips()

    def loadToolTips(self):
        self.ui.email.setToolTip("Must contain '@' & '.'")
        self.ui.tel_num.setToolTip("Must contain at least 8 digits")
        self.ui.cc_num.setToolTip("Must contain 16 digits")

    def updateStatus(self, text):
        self.ui.status.setStyleSheet('color: RED')
        self.ui.status.setText('Status: ' + text)

    def clearStatus(self):
        self.updateStatus('OK')
        self.ui.status.setStyleSheet('color: GREEN')

    def populateCC(self):
        for x in range(1, 13):
            self.ui.cc_month.addItem(str(x).zfill(2))
        for x in range(0, 11):
            y = 2018 + x
            self.ui.cc_year.addItem(str(y))

    def updateStates(self):
        if self.ui.country_selection.currentText() == 'USA':
            self.ui.addr3_dropdown.clear()
            for x in sus:
                self.ui.addr3_dropdown.addItem(x)
        elif self.ui.country_selection.currentText() == 'CANADA':
            self.ui.addr3_dropdown.clear()
            for x in sca:
                self.ui.addr3_dropdown.addItem(x)

    def checkcc(self):
        if self.ui.payment_type.currentText() == 'PayPal' or self.ui.payment_type.currentText() == '代金引換':
            self.ui.cc_num.setEnabled(False)
            self.ui.cc_cvv.setEnabled(False)
            self.ui.cc_month.setEnabled(False)
            self.ui.cc_year.setEnabled(False)
            self.cc = False
        else:
            self.ui.cc_num.setEnabled(True)
            self.ui.cc_cvv.setEnabled(True)
            self.ui.cc_month.setEnabled(True)
            self.ui.cc_year.setEnabled(True)
            self.cc = True

    def cont(self):
        if self.checkFields():
            self.populatePdet()
            itemSelection(True)

    def saveConfig(self):
        if self.checkFields(True):
            self.populatePdet()
            enc.paydetails = paydetails
            new = self.ui.save_name.text() + ".cnf"
            enc.initConf(new)
            enc.password = self.ui.password.text().encode('utf-8')
            for x in paydetails:
                enc.writeToConf(x, paydetails[x], new)
            itemSelection(True)

    def checkFields(self, safe=False):
        if len(self.ui.full_name.text()) == 0:
            self.updateStatus('Name not provided')
            return None
        if len(self.ui.email.text()) == 0 and not '@' in self.ui.email.text() and not '.' in self.ui.email.text():
            self.updateStatus('Invalid email address provided')
            return None
        if len(self.ui.tel_num.text()) < 8 and not self.ui.tel_num.text().isdigit():
            self.updateStatus('Invalid phone number provided')
            return None
        if len(self.ui.addr_1.text()) == 0:
            self.updateStatus('No address 1 provided')
            return None
        if len(self.ui.city.text()) == 0:
            self.updateStatus('City not provided')
            return None
        if len(self.ui.zip_code.text()) == 0:
            self.updateStatus('Post/zip code not provided')
            return None
        if self.cc:
            if len(self.ui.cc_num.text()) != 16 and not self.ui.cc_num.text().isdigit():
                self.updateStatus('Card number not provided')
                return None
            if len(self.ui.cc_cvv.text()) == 0 and not self.ui.cc_cvv.text().isdigit():
                self.updateStatus('Card CVV not provided')
                return None
        if safe:
            if len(self.ui.password.text()) == 0:
                self.updateStatus('No password specified')
                return None
            elif len(self.ui.password.text()) <= 6:
                self.updateStatus('Weak password')
                self.ui.status.setStyleSheet('color: ORANGE')
                return None
            elif len(self.ui.save_name.text()) == 0:
                self.updateStatus('No save name specified')
                return None
        self.clearStatus()
        return True

    def populatePdet(self):
        global paydetails
        paydetails['Country'] = self.ui.country_selection.currentText()
        paydetails['Name'] = self.ui.full_name.text()
        paydetails['Email'] = self.ui.email.text()
        paydetails['Phone'] = self.ui.tel_num.text()
        paydetails['Addr1'] = self.ui.addr_1.text()
        if len(self.ui.addr_2.text()) > 0:
            paydetails['Addr2'] = self.ui.addr_2.text()
        else:
            paydetails['Addr2'] = ''
        if len(self.ui.addr_3.text()) > 0 and REGION == 'EU':
            if len(self.ui.addr_3.text()) > 0:
                paydetails['Addr3'] = self.ui.addr_3.text()
            else:
                paydetails['Addr3'] = ''
        elif REGION == 'US' or REGION == 'ASIA':
            paydetails['Addr3'] = self.ui.addr3_dropdown.currentText()

        paydetails['City'] = self.ui.city.text()
        paydetails['Post/zip code'] = self.ui.zip_code.text()

        if REGION != 'US':
            paydetails['CardType'] = self.ui.payment_type.currentText()
        else:
            paydetails['CardType'] = 'None'
        if self.cc:
            paydetails['Cardno'] = self.ui.cc_num.text()
            paydetails['CardCVV'] = self.ui.cc_cvv.text()
            paydetails['CardMonth'] = self.ui.cc_month.currentText()
            paydetails['CardYear'] = self.ui.cc_year.currentText()

    def updateRegion(self):
        global sus, sca
        peu = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'Solo':'solo', 'PayPal':'paypal'}
        ceu = {'GB':'UK', 'UK (N. IRELAND)':'NB', 'AUSTRIA':'AT', 'BELARUS':'BY', 'BELGIUM':'BE', 'BULGARIA':'BG',
               'CROATIA':'HR', 'CZECH REPUBLIC':'CZ', 'DENMARK':'DK', 'ESTONIA':'EE', 'FINLAND':'FI', 'FRANCE':'FR',
               'GERMANY':'DE', 'GREECE':'GR', 'HUNGARY':'HU', 'ICELAND':'IS', 'IRELAND':'IE', 'ITALY':'IT',
               'LATVIA':'LV', 'LITHUANIA':'LT', 'LUXEMBOURG':'LU', 'MONACO':'MC', 'NETHERLANDS':'NL', 'NORWAY':'NO',
               'POLAND':'PL', 'PORTUGAL':'PT', 'ROMANIA':'RO', 'RUSSIA':'RU', 'SLOVAKIA':'SK', 'SLOVENIA':'SI',
               'SPAIN':'ES', 'SWEDEN':'SE', 'SWITZERLAND':'CH', 'TURKEY':'TR'}
        pus = ['Not available']
        cus = {'USA':'USA', 'CANADA':'CANADA'}
        sus = ['AL','AK','AS','AZ','AR','CA','CO','CT','DE','DC','FM','FL','GA','GU','HI','ID','IL','IN','IA','KS','KY',
               'LA','ME','MH','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','MP','OH','OK',
               'OR','PW','PA','PR','RI','SC','SD','TN','TX','UT','VT','VI','VA','WA','WV','WI','WY']
        sca = ['AB','BC','MB','NB','NL','NT','NS','NU','ON','PE','QC','SK','YT']
        pasia = {'Visa':'visa', 'American Express':'american_express', 'Mastercard':'master', 'JCB':'jcb', '代金引換':'cod'}
        rasia = ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県','茨城県','栃木県','群馬県','埼玉県','千葉県','東京都',
                 '神奈川県','新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県','三重県','滋賀県','京都府',
                 '大阪府','兵庫県','奈良県','和歌山県','鳥取県','島根県','岡山県','広島県','山口県','徳島県','香川県','愛媛県','高知県',
                 '福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']
        if REGION == 'EU':
            for x in peu.keys():
                self.ui.payment_type.addItem(x)
            for x in ceu.keys():
                self.ui.country_selection.addItem(x)
            self.ui.addr3_dropdown.hide()
            self.ui.payment_type.currentIndexChanged.connect(self.checkcc)
            paydetails['Region'] = "EU"
        elif REGION == 'US':
            for x in pus:
                self.ui.payment_type.addItem(x)
            self.ui.payment_type.setEnabled(False)
            for x in cus.keys():
                self.ui.country_selection.addItem(x)
            for x in sus:
                self.ui.addr3_dropdown.addItem(x)
            self.ui.addr3_label.setText('State:')
            self.ui.addr2_label.setText('Apt, unit, ...:')
            self.ui.addr_3.hide()
            self.ui.country_selection.currentIndexChanged.connect(self.updateStates)
            paydetails['Region'] = "US"
        elif REGION == 'ASIA':
            for x in pasia.keys():
                self.ui.payment_type.addItem(x)
            self.ui.country_selection.addItem('JAPAN')
            self.ui.addr3_label.setText('Province:')
            self.ui.addr_3.hide()
            for x in rasia:
                self.ui.addr3_dropdown.addItem(x)
            self.ui.payment_type.currentIndexChanged.connect(self.checkcc)
            paydetails['Region'] = "ASIA"


class config(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = uic.loadUi(getLoc('GUIS/SelectConfig.ui'), self)
        self.setWindowIcon(QtGui.QIcon(getLoc('GUIS/icon.png')))
        self.ui.label.setText('<a href="http://www.csb.center"><img src="' + getLoc('GUIS/title.png') + '"></a>')
        self.ui.label.setOpenExternalLinks(True)
        self.ui.donate.setText('<a href="https://www.paypal.me/supportcsb"><img src="' + getLoc('GUIS/donate.png') + '"></a>')
        self.ui.donate.setOpenExternalLinks(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
        self.ui.use_conf.clicked.connect(self.useConfig)
        self.ui.new_conf.clicked.connect(self.newConfig)
        self.ui.ASIA_btn.setEnabled(False)
        self.findFiles()

        u = update.updateManager('https://github.com/danielyc/csb', '3.0.10')
        if u.update:
            QtWidgets.QMessageBox.about(self, 'Update available', 'There is an update available, please download the latest version from the website.')

    def updateStatus(self, text):
        self.ui.status.setStyleSheet('color: RED')
        self.ui.status.setText('Status: ' + text)

    def clearStatus(self):
        self.updateStatus('OK')
        self.ui.status.setStyleSheet('color: GREEN')

    def findFiles(self):
        found = False
        for file in os.listdir(os.getcwd()):
            if file[-4:] == '.cnf':
                found = True
                self.ui.conf_file.addItem(file)
                self.ui.use_conf.setEnabled(True)
                self.ui.password.setEnabled(True)
                self.ui.conf_file.setEnabled(True)
        if not found:
            self.ui.use_conf.setEnabled(False)
            self.ui.password.setEnabled(False)
            self.ui.conf_file.setEnabled(False)
            self.updateStatus('No save files detected')

    def newConfig(self):
        global REGION
        if self.ui.EU_btn.isChecked():
            REGION = 'EU'
            bot.reg = 'EU'
        elif self.ui.US_btn.isChecked():
            REGION = 'US'
            bot.reg = 'US'
        elif self.ui.ASIA_btn.isChecked():
            REGION = 'ASIA'
            bot.reg = 'ASIA'
        else:
            self.updateStatus('No region selected')
            return None
        self.clearStatus()
        payDetails()

    def useConfig(self):
        global REGION, paydetails
        correctPass = False
        if len(self.ui.password.text()) > 0:
            selected_file = self.ui.conf_file.currentText()
            enc.password = self.ui.password.text().encode('utf-8')
            for x in paydetails:
                paydetails[x] = enc.readConf(x, selected_file)

            for x in paydetails:
                if paydetails[x] == "":
                    correctPass = False
                else:
                    correctPass = True

            if correctPass:
                print("Successfully Loaded: " + selected_file)
                self.ui.status.setStyleSheet('color: GREEN')
                self.updateStatus('Correct Password')
                itemSelection()
            else:
                print("Empty Values detected, assuming wrong password.")
                self.ui.status.setStyleSheet('color: RED')
                self.updateStatus('Wrong Password')
        else:
            self.updateStatus('No password specified')
            return None

class proxy(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = uic.loadUi(getLoc('GUIS/IPConfig.ui'), self)
        self.setWindowIcon(QtGui.QIcon(getLoc('GUIS/icon.png')))
        self.selected_ip = ""
        self.ui.ipinput.setText(self.selected_ip)
        self.ui.continue_ip.clicked.connect(self.setIP)
        self.ui.default_ip.clicked.connect(self.resetIP)

    def setIP(self):
        ip = self.ui.ipinput.text()
        port = self.ui.portinput.text()
        if port != "" and ip :
            endParam = ip + ":" + port
            self.selected_ip = endParam
        self.close()

    def resetIP(self):
        self.ui.ipinput.setText("")
        self.ui.portinput.setText("")


def itemSelection(cont=False):
    if cont:
        p.close()
    else:
        c.close()
    i = itemSel()
    i.show()


def payDetails():
    global p
    c.close()
    p = paydet()
    p.show()


def start():
    global c
    app = QtWidgets.QApplication(sys.argv)
    c = config()
    c.show()
    sys.exit(app.exec_())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    start()
