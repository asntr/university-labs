import json
from knowledge_base import Analyzer
import sys
import random
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QComboBox, QPushButton, QLabel

with open('rules.json', 'r') as rules_list:
    rules = json.load(rules_list)
    # random.shuffle(rules)
with open('values.json', 'r') as values_list:
    values = json.load(values_list)


def start(target, widget):
    analyzer = Analyzer(rules, target, values)
    answer = analyzer.analyze()
    mb = QMessageBox(widget)
    mb.setText('{} value is "{}"'.format(target, str(answer)) if answer else "Can't get value of target key")
    mb.show()


class KnowledgeBaseReporter(QWidget):

    def __init__(self):
        super(KnowledgeBaseReporter, self).__init__()

        self.label = QLabel(self)
        self.label.setText('Choose target option:')
        self.label.move(12, 5)
        self.label.show()

        self.cb = QComboBox(self)
        self.cb.move(10, 30)
        self.cb.show()

        self.button = QPushButton('Start', self)
        self.button.move(5, 60)
        self.button.clicked.connect(lambda: start(self.cb.currentText(), self))

    def set_target_options(self, options):
        self.cb.addItems(options)


def main():
    targets = ('language', 'compiled')
    app = QApplication(sys.argv)
    rep = KnowledgeBaseReporter()
    rep.resize(200, 100)
    rep.set_target_options(targets)
    rep.show()
    app.exec_()

if __name__ == '__main__':
    main()
