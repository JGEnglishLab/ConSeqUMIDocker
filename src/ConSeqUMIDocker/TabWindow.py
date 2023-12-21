import os
import subprocess
from PyQt5.QtWidgets import (
    QLabel,
    # QLineEdit,
    QWidget,
    # QApplication,
    QFormLayout,
    # QComboBox,
    # QCheckBox,
    QPushButton,
    QFileDialog,
    QPlainTextEdit,
    QVBoxLayout,
    # QStyle,
    # QMainWindow,
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QFont
from abc import ABC, ABCMeta, abstractmethod


class AbstractTabWindow(ABCMeta, type(QWidget)):
    pass


class TabWindow(QWidget, metaclass=AbstractTabWindow):
    def __init__(self):
        super().__init__()

        self.p = None
        self.container_id = "samhimes92/conseqdocker-jge"

        dlgLayout = QVBoxLayout()
        fileLayout = QFormLayout()
        settingLayout = QFormLayout()

        instructionLabel = QLabel("Link to Instruction Wiki:")
        instructionLabel.setFont(QFont("Times", 17, QFont.Bold))
        self.instructionLink = QPlainTextEdit()
        self.instructionLink.setReadOnly(True)
        self.set_instruction_link(self.instructionLink)

        dlgLayout.addWidget(instructionLabel)
        dlgLayout.addWidget(self.instructionLink)

        self.set_file_layout(fileLayout)
        fileInputLabel = QLabel("File Input:")
        fileInputLabel.setFont(QFont("Times", 17, QFont.Bold))
        dlgLayout.addWidget(fileInputLabel)
        dlgLayout.addLayout(fileLayout)

        self.set_setting_layout(settingLayout)
        settingsInputLabel = QLabel("Settings:")
        settingsInputLabel.setFont(QFont("Times", 17, QFont.Bold))
        dlgLayout.addWidget(settingsInputLabel)
        dlgLayout.addLayout(settingLayout)

        self.runBtn = QPushButton("Execute")
        self.killBtn = QPushButton("Kill Process")
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        dlgLayout.addWidget(self.runBtn)
        dlgLayout.addWidget(self.killBtn)
        dlgLayout.addWidget(self.text)
        self.runBtn.setDefault(True)
        self.killBtn.setEnabled(False)
        self.killBtn.clicked.connect(self.kill_process)
        self.runBtn.clicked.connect(self.start_process)

        self.setLayout(dlgLayout)

    @abstractmethod
    def set_instruction_link(self, instructionLinkText: type(QFormLayout)) -> None:
        pass

    @abstractmethod
    def set_file_layout(self, fileLayout: type(QFormLayout)) -> None:
        pass

    @abstractmethod
    def set_setting_layout(self, settingLayout: QFormLayout) -> None:
        pass

    @abstractmethod
    def set_args(self) -> list:
        pass

    def get_file(self, text, isFile=False):
        dialog = QFileDialog()
        if isFile:
            fname = QFileDialog.getOpenFileName(self, "Open File", "c:\\")
            text.setText(fname[0])
        else:
            fname = QFileDialog.getExistingDirectory(self, "Open Directory", "c:\\")
            text.setText(fname)

    def message(self, s):
        self.text.appendPlainText(s)

    def kill_process(self):
        self.p.kill()


    def process_finished(self):
        self.message("Process finished.")
        self.killBtn.setEnabled(False)
        self.p = None
        self.message(f"Removing Docker containers from {self.container_id} image")
        remove_command = f'docker rm $(docker stop $(docker ps -a -q --filter ancestor={self.container_id} --format="{{{{.ID}}}}")) '
        subprocess.run(remove_command, shell=True)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)


    def build_umi_cmnd(self, args):
        umi_keep_flag = ""
        umi_length_flag = ""

        for i in range(len(args)):
            #Required Flags
            if args[i] == "-i" or args[i] == "--input":
                umi_input = args[i + 1]
            if args[i] == "-o" or args[i] == "--output":
                umi_output = args[i + 1]
            if args[i] == "-a" or args[i] == "--adapters":
                umi_adapters = args[i + 1]
                umi_adapters_file_type = args[i+1].split(".")[-1]

            #Optional Flags
            if args[i] == "-k" or args[i] == "--keep":
                umi_keep_flag = " -k "
            if args[i] == "-u" or args[i] == "--umiLength":
                umi_length_flag = f" -u {args[i + 1]} "
        try: #Make sure that all the required flags are set
            umi_i_mount = f" -v {umi_input}:/app/umi_input "
            umi_o_mount = f" -v {umi_output}:/app/umi_output "
            umi_a_mount = f" -v {umi_adapters}:/app/umi_adapter.{umi_adapters_file_type} "
        except:
            print("The input output and adapter paths must be filled out.")
            self.message("The input output and adapter paths must be filled out.")
            return None

        command = (
            f"docker run {umi_i_mount}{umi_o_mount}{umi_a_mount}"
            f"{self.container_id} umi "
            f"-i /app/umi_input -o /app/umi_output -a /app/umi_adapter.{umi_adapters_file_type} "
            f"{umi_keep_flag}{umi_length_flag}"
        )
        return command

    def build_benchmark_cmnd(self, args):
        benchmark_last_train_flag = ""
        benchmark_process_num_flag = ""
        benchmark_iter_flag = ""
        benchmark_int_flag = ""
        benchmark_ref_flag = ""
        benchmark_last_train_mount = ""
        benchmark_ref_mount = ""

        for i in range(len(args)):
            #Required Flags
            if args[i] == "-i" or args[i] == "--input":
                benchmark_input = args[i+1]
                benchmark_input_file_type = args[i+1].split(".")[-1]
            if args[i] == "-o" or args[i] == "--output":
                benchmark_output = args[i+1]
            if args[i] == "-c" or args[i] == "--consensusAlgorithm":
                benchmark_algo_flag = f" -c {args[i+1]} "
            #Optional Flags
            if args[i] == "-l" or args[i] == "--lastTrain":
                benchmark_last_train_file_type = args[i+1].split(".")[-1]
                benchmark_last_train_mount = f" -v {args[i+1]}:/app/last_train_file.{benchmark_last_train_file_type} "
                benchmark_last_train_flag = f" -l /app/last_train_file.{benchmark_last_train_file_type} "
            if args[i] == "-r" or args[i] == "--reference":
                benchmark_ref_file_type = args[i+1].split(".")[-1]
                benchmark_ref_mount = f" -v {args[i+1]}:/app/ref_file.{benchmark_ref_file_type} "
                benchmark_ref_flag = f" -r /app/ref_file.{benchmark_ref_file_type} "
            if args[i] == "-p" or args[i] == "--processNum":
                benchmark_process_num_flag = f" -p {args[i+1]} "
            if args[i] == "-iter" or args[i] == "--iterations":
                benchmark_iter_flag = f" -iter {args[i+1]} "
            if args[i] == "-int" or args[i] == "--intervals":
                benchmark_int_flag = f" -int {args[i+1]} "


        try: #Make sure that all the required flags are set
            benchmark_i_mount = f" -v {benchmark_input}:/app/benchmark_input.{benchmark_input_file_type} "
            benchmark_o_mount = f" -v {benchmark_output}:/app/benchmark_output "
            benchmark_algo_flag
        except:
            print("The input and output paths must be filled out.")
            self.message("The input and output paths must be filled out.")
            return None

        command = (
            f"docker run {benchmark_i_mount}{benchmark_o_mount}{benchmark_last_train_mount}{benchmark_ref_mount}"
            f"{self.container_id} benchmark "
            f"-i /app/benchmark_input.{benchmark_input_file_type} -o /app/benchmark_output {benchmark_algo_flag}"
            f"{benchmark_ref_flag}{benchmark_int_flag}{benchmark_iter_flag}{benchmark_process_num_flag}{benchmark_last_train_flag}"
        )
        return command

    def build_cons_cmnd(self, args):
        cons_last_train_flag = ""
        cons_process_num_flag = ""
        cons_min_reads_flag = ""
        cons_last_train_mount = ""

        for i in range(len(args)):
            #Required Flags
            if args[i] == "-i" or args[i] == "--input":
                cons_input = args[i+1]
            if args[i] == "-o" or args[i] == "--output":
                cons_output = args[i+1]
            if args[i] == "-c" or args[i] == "--consensusAlgorithm":
                cons_algo_flag = f" -c {args[i+1]} "
            #Optional Flags
            if args[i] == "-l" or args[i] == "--lastTrain":
                cons_last_train_file_type = args[i+1].split(".")[-1]
                cons_last_train_mount = f" -v {args[i+1]}:/app/last_train_file.{cons_last_train_file_type} "
                cons_last_train_flag = f" -l /app/last_train_file.{cons_last_train_file_type} "
            if args[i] == "-p" or args[i] == "--processNum":
                cons_process_num_flag = f" -p {args[i+1]} "
            if args[i] == "-m" or args[i] == "--minimumReads":
                cons_min_reads_flag = f" -m {args[i+1]} "


        try: #Make sure that all the required flags are set
            cons_i_mount = f" -v {cons_input}:/app/cons_input "
            cons_o_mount = f" -v {cons_output}:/app/cons_output "
            cons_algo_flag
        except:
            print("The input and output paths must be filled out.")
            self.message("The input and output paths must be filled out.")
            return None

        command = (
            f"docker run {cons_i_mount}{cons_o_mount}{cons_last_train_mount}"
            f"{self.container_id} cons "
            f"-i /app/cons_input -o /app/cons_output {cons_algo_flag}"
            f"{cons_min_reads_flag}{cons_process_num_flag}{cons_last_train_flag}"
        )
        return command



    def start_process(self):
        args = self.set_args()
        self.killBtn.setEnabled(True)

        if self.p is None:  # No process running.
            self.message(f"args {args}")
            print(args)

            if args[0] == "umi":
                command = self.build_umi_cmnd(args)
            elif args[0] == "benchmark":
                command = self.build_benchmark_cmnd(args)
            elif args[0] == "cons":
                command = self.build_cons_cmnd(args)
            else:
                command = None

            if command is None:
                return

            print(command)

            self.message("Executing process")
            self.message("conseq " + " ".join(args))
            self.p = (
                QProcess()
            )  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start(command)



