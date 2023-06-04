from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
import scipy.io as sio
from PyQt5.QtWidgets import QPushButton,QLabel ,QGridLayout, QWidget, QComboBox
from Classifier import Classifier
from EEGSerialCommunication import EEGSerialCommunication
from RectangleWidget import RectangleWidget
from FeatureExtraction import FeatureExtraction
import pyqtgraph as pg
import numpy as np
import sys




class MainWindow(QtWidgets.QMainWindow):


    def set_instructions(self):
        instrukcije_za_test = sio.loadmat("signali\instrukcije_za_test.mat")
        trajanje_svake_instrukcije = sio.loadmat("signali\\trajanje_svake_instrukcije.mat")
        instructions = [el[0] for el in instrukcije_za_test['instrukcije_za_test']]
        instructions_duration = [int(el[0]*160) for el in trajanje_svake_instrukcije['trajanje_svake_instrukcije']]
        instruction_vector = []
        for idx, instruction in enumerate(instructions):
            for _ in range(instructions_duration[idx]):
                instruction_vector.append(instruction)

        return instruction_vector

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.instruction_vector = self.set_instructions()
        self.iterations_counter = 0
        self.cls = Classifier()
        self.eeg_x = list(np.linspace(0.0, 5.0, num=800))
        self.eeg_y = [0 for _ in range(800)]
        self.c3 = []
        self.c4 = []
        self.models = ['lda', 'qda', 'knn', 'xgb']
        self.labels = 0
        self.movement_x = list(np.linspace(0.0, 5.0, num=800))
        self.movement_y = [0 for _ in range(800)]
        self.true_labels = []
        self.predicted_labels = []
        self.plot = False
        self.predicted_values_msg = "Predicted:"
        self.true_values_msg = "       True:"
        self.accuracy_msg = "Accuracy: 0%"

        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.pen = pg.mkPen(color=(142, 68, 173),width= 2)

        self.ser_port = EEGSerialCommunication()
        self.ser_port.turn_simulator_on()
        self.ser_port.turn_channel(255)

        self.initUI()

    def __del__(self):
        self.ser_port.turn_simulator_off()

    def initUI(self):
        self.setWindowTitle("EEG app")
        self.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.layout = QGridLayout()

        self.graphWidgetEEG = pg.PlotWidget()        
        self.graphWidgetEEG.setBackground('#1E1E1E')
        self.graphWidgetEEG.setMaximumSize(600, 200)
        self.graphWidgetEEG.setMinimumSize(600, 200)
        self.graphWidgetEEG.setYRange(-500, 500, padding=0)
        self.graphWidgetEEG.getAxis('left').setPen("#444444")
        self.graphWidgetEEG.getAxis('bottom').setPen('#444444')

        self.rect_right = RectangleWidget()
        self.rect_left = RectangleWidget(right=False)

        self.label_true_values = QLabel()
        self.label_true_values.setStyleSheet("font-size: 20px; color: rgb(142, 68, 173);background-color:  rgb(30, 30, 30);")
        self.label_true_values.setText(self.true_values_msg)
        self.label_predicted_values = QLabel()
        self.label_predicted_values.setStyleSheet("font-size: 20px; color: rgb(142, 68, 173); background-color: rgb(30, 30, 30);")
        self.label_predicted_values.setText(self.predicted_values_msg)
        self.label_accuracy = QLabel()
        self.label_accuracy.setStyleSheet("font-size: 20px; color: rgb(142, 68, 173); background-color: rgb(30, 30, 30);")
        self.label_accuracy.setText(self.accuracy_msg)
    


        self.button = QPushButton('Start')
        self.button.setToolTip("This is a start\stop button")
        self.button.setMaximumSize(100, 40)
        self.button.setMinimumSize(100, 40)
        self.button.setStyleSheet(f"""
        QPushButton {
            "{background-color : rgb(210,39,48)}" if self.plot else "{background-color : rgb(77, 77, 255)}"
        }
        QPushButton:hover {
            "{background-color : rgb(230, 59, 68)}" if self.plot else "{background-color : rgb(97,97,255)}"
        }
    """)
        self.button.clicked.connect(self.start_stop)
        self.button.setFont(QtGui.QFont('Times', 10))


        self.combox = QComboBox()
        self.combox.setStyleSheet("""QComboBox QAbstractItemView {
                                    background: rgb(68, 173, 82);
                                    selection-background-color: blue;
                                    }
                                    QComboBox {
                                    background: rgb(68, 173, 82);
                                    }""")
        self.combox.setMaximumSize(100, 40)
        self.combox.setMinimumSize(100, 40)
        for i in range(24):
            self.combox.addItem("CH" + str(i + 1))

        self.combox.setCurrentIndex(0)

        self.model_cb = QComboBox()
        self.model_cb.setStyleSheet("""QComboBox QAbstractItemView {
                                    background: rgb(68, 173, 82);
                                    selection-background-color: blue;
                                    }
                                    QComboBox {
                                    background: rgb(68, 173, 82);
                                    }""")
        self.model_cb.setMaximumSize(100, 40)
        self.model_cb.setMinimumSize(100, 40)
        self.model_cb.addItems(self.models)
        self.model_cb.setCurrentIndex(0)



        self.layout.addWidget(self.button, 0, 1)
        self.layout.addWidget(self.graphWidgetEEG, 0, 0)
        self.layout.addWidget(self.combox, 0, 2)
        self.layout.addWidget(self.model_cb, 0, 3)
        self.layout.addWidget(self.rect_left, 0, 4)
        self.layout.addWidget(self.rect_right, 0, 5)
        self.layout.addWidget(self.label_true_values, 1, 0)
        self.layout.addWidget(self.label_predicted_values, 2, 0)
        self.layout.addWidget(self.label_accuracy, 3, 0)


        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)


        self.data_line_eeg =  self.graphWidgetEEG.plot(self.eeg_x, self.eeg_y, pen = self.pen)


    def calculate_accuracy(self):
        correct = sum(1 for p, t in zip(self.predicted_labels, self.true_labels) if p == t)
        total = len(self.predicted_labels)
        if total == 0:
            return 0
        accuracy = correct / total * 100
        return accuracy



    def start_stop(self):
        self.plot = not self.plot
        self.button.setText("Stop" if self.plot else "Start")
        self.button.setStyleSheet(f"""
        QPushButton {
            "{background-color : rgb(210,39,48)}" if self.plot else "{background-color : rgb(77, 77, 255)}"
        }
        QPushButton:hover {
            "{background-color : rgb(240, 69, 78)}" if self.plot else "{background-color : rgb(107,107,255)}"
        }
    """)

    def update_plot_data(self):
        
        if self.plot:
            self.model_cb.setDisabled(True)
            current_row = self.ser_port.read_line()
            if not current_row:
                return
            self.eeg_x = self.eeg_x[1:]
            self.eeg_x.append(self.eeg_x[-1] + 0.00625)
            

            self.movement_x = self.movement_x[1:]
            self.movement_x.append(self.movement_x[-1] + 0.00625)

            self.eeg_y = self.eeg_y[1:]
            self.eeg_y.append(current_row[self.combox.currentIndex()])

            self.movement_y = self.movement_y[1:]
            self.movement_y.append(current_row[-1])
            


            self.data_line_eeg.setData(self.eeg_x, self.eeg_y)
            self.c3.append(current_row[2])
            self.c4.append(current_row[3])

            if int(self.instruction_vector[self.iterations_counter])== 1:
                self.rect_right.set_color(QColor(0, 0, 0, 100))
                self.rect_left.set_color(QColor(0, 255, 0, 100))
                self.labels = 1
            elif int(self.instruction_vector[self.iterations_counter])== 2:
                self.rect_right.set_color(QColor(0, 255, 0, 100))
                self.rect_left.set_color(QColor(0, 0, 0, 100))
                self.labels = 2
            else:
                if self.labels != 0:
                    test_sample = np.array(FeatureExtraction.featutre_extraction(self.c3, self.c4))
                    prediction = self.cls.predict(self.models[self.model_cb.currentIndex()], test_sample)
                    self.true_labels.append(self.labels)
                    self.predicted_labels.append(prediction)
                    self.true_values_msg += str(self.labels)+"|"
                    self.predicted_values_msg += str(prediction)+"|"
                    self.accuracy_msg = f"Accuracy: {self.calculate_accuracy()}%"
                    self.label_predicted_values.setText(self.predicted_values_msg)
                    self.label_true_values.setText(self.true_values_msg)
                    self.label_accuracy.setText(self.accuracy_msg)
                    self.c3 = []
                    self.c4 = []
                self.labels = 0
                self.rect_right.set_color(QColor(0, 0, 0, 100))
                self.rect_left.set_color(QColor(0, 0, 0, 100))
            
            self.iterations_counter += 1

            if self.iterations_counter == len(self.instruction_vector):
                self.button.click()
                self.button.setDisabled(True)
        else:
            pass

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())