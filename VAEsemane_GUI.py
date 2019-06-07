import sys
import os
import torch
import threading
import time
import mido
import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QAction, QFileDialog
from PyQt5.uic import loadUi
from utils.VAE_model import VAE
from utils.LiveInput import LiveParser
from utils.vae_gui import vae_interact, vae_endless, vae_generate
from loadModel import loadModel, loadStateDict


class VirtualDial:
    def __init__(self):
        self.min = -1000
        self.max = 1000
        self.value = 0

    def setMinMax(self, min, max):
        self.min = min
        self.max = max

    def randomize(self):
        rand = np.random.randint(self.min, self.max)
        self.value = rand

    def reset(self):
        self.value = 0


class VAEsemane_GUI(QMainWindow):
    def __init__(self):
        super(VAEsemane_GUI, self).__init__()
        loadUi('raspian_gui.ui', self)
        self.setWindowTitle('VAEsemane')
        self.live_instrument = None
        self.is_running = False
        self.temperature = self.slider_temperature.value()/100.
        self.initUIConnects()

    def initUIConnects(self):
        # menu bar
        # first tab "File"
        self.menu_bar.setNativeMenuBar(False)
        self.action_quit.triggered.connect(self.quit_clicked)
        # second tab "MIDI port", sets instrument
        available_port = mido.get_input_names()
        midi_ports = []
        midi_actions = []
        for port in available_port:
            midi_actions.append(QAction(port, self))
            self.menu_midi_port.addAction(midi_actions[-1])
        self.menu_midi_port.triggered.connect(self.set_instrument)
        # third tab set model path
        self.action_find.triggered.connect(self.set_model_path)
        self.action_pretrained.triggered.connect(self.set_pretrained_model)

        # buttons
        self.btn_run.clicked.connect(self.btn_run_clicked)
        self.btn_stop.clicked.connect(self.btn_stop_clicked)
        self.btn_randomize.clicked.connect(self.btn_randomize_clicked)
        self.btn_reset.clicked.connect(self.btn_reset_clicked)
        self.btn_run_endless.clicked.connect(self.btn_run_endless_clicked)
        self.btn_generate.clicked.connect(self.btn_generate_clicked)

        # dials --> get list of dials and sort them by object name
        self.dials = []
        for i in range(100):
            self.dials.append(VirtualDial())
        # change range of the dials, default is [-100,100] (in %)


        # sliders
        self.lbl_bpm.setText("{} BPM".format(self.slider_bpm.value()))
        self.slider_bpm.valueChanged.connect(self.update_bpm)
        self.lbl_temperature.setText("Temperature {0:.2f}".format(self.temperature))
        self.slider_temperature.valueChanged.connect(self.update_temperature)
        self.lbl_bars.setText("{} bar".format(self.slider_bars.value()))
        self.slider_bars.valueChanged.connect(self.update_bars)

    def quit_clicked(self):
        qApp.quit()

    def set_instrument(self, q):
        self.live_instrument = LiveParser(port=q.text(), ppq=24,
            bars=self.slider_bars.value(), bpm=self.slider_bpm.value())
        self.live_instrument.open_inport(self.live_instrument.parse_notes)
        self.live_instrument.open_outport()
        self.start_metronome()
        # self.start_progress_bar()

    def start_metronome(self):
        metronome_thread = threading.Thread(target=self.update_metronome)
        metronome_thread.setDaemon(True)
        metronome_thread.start()

    def update_metronome(self):
        while True:
            if self.live_instrument.human:
                self.lcd_comp_metronome.display("0")
                self.lcd_human_metronome.display("{}".format(self.live_instrument.metronome))
            else:
                self.lcd_human_metronome.display("0")
                self.lcd_comp_metronome.display("{}".format(self.live_instrument.metronome))
            time.sleep(0.01)


    def update_bpm(self):
        current_val = self.slider_bpm.value()
        self.lbl_bpm.setText("{} BPM".format(current_val))
        if self.live_instrument:
            self.live_instrument.update_bpm(current_val)

    def update_temperature(self):
        self.temperature = self.slider_temperature.value()/100.
        self.lbl_temperature.setText("Temperature {0:.2f}".format(self.temperature))

    def update_bars(self):
        current_val = self.slider_bars.value()
        if current_val > 1:
            self.lbl_bars.setText("{} bars".format(current_val))
        else:
            self.lbl_bars.setText("{} bar".format(current_val))
        if self.live_instrument:
            self.live_instrument.update_bars(current_val)

    def search_instruments(self):
        # this function could search for new midi instruments if they were
        # connected after gui was startet
        pass

    def set_model_path(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open File', os.getenv('..'))[0]
        self.model = VAE()
        try:
            self.model = loadModel(self.model, file_path, dataParallelModel=True)
        except:
            self.model = loadStateDict(self.model, file_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.model.train():
            self.model.eval()

    def set_pretrained_model(self):
        rel_path = "utils/pretrained_models/vae_model.pth"
        self.model = VAE()

        self.model = loadStateDict(self.model, rel_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.model.train():
            self.model.eval()

    def btn_run_clicked(self):
        if not self.is_running:
            vae_thread = threading.Thread(target=vae_interact, args=(self,))
            vae_thread.setDaemon(True)
            vae_thread.start()
            self.is_running = vae_thread.is_alive()

    def btn_run_endless_clicked(self):
        if not self.is_running:
            vae_thread = threading.Thread(target=vae_endless, args=(self,))
            vae_thread.setDaemon(True)
            vae_thread.start()
            self.is_running = vae_thread.is_alive()

    def btn_stop_clicked(self):
        self.is_running = False

    def btn_generate_clicked(self):
        if not self.is_running:
            vae_thread = threading.Thread(target=vae_generate, args=(self,))
            vae_thread.setDaemon(True)
            vae_thread.start()
            self.is_running = vae_thread.is_alive()

    def btn_randomize_clicked(self):
        for dial in self.dials:
            dial.randomize()

    def btn_reset_clicked(self):
        for dial in self.dials:
            dial.reset()

    def test_dials(self):
        for dial in self.dials:
            print(dial.objectName())
            print (dial.value())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = VAEsemane_GUI()
    gui.show()
    sys.exit(app.exec_())
