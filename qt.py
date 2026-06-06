import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QTextEdit, QProgressBar, QFrame
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import the main function from checksum module to handle checksum operations
import checksum

class ChecksumWorker(QThread):
    result_signal = pyqtSignal(object)

    def __init__(self, task_type, selected_file, user_input=None, hash_combo_text=None):
        super().__init__()
        self.task_type = task_type
        self.selected_file = selected_file
        self.user_input = user_input
        self.hash_combo_text = hash_combo_text

    def run(self):
        if self.task_type == "check":
            if not self.user_input:
                self.result_signal.emit("⚠️ Error: No checksum String provided.")
                return
            try:
                is_match = checksum.compare_checksum_with_string(self.selected_file, self.user_input, self.hash_combo_text, console=False)
                self.result_signal.emit({"type": "check", "value": is_match, "input": self.user_input})
            except Exception as e:
                self.result_signal.emit(f"💥 Error checking checksum: {e}")

        elif self.task_type == "generate":
            try:
                all_checksums = checksum.get_all_checksums(self.selected_file)
                self.result_signal.emit({"type": "generate", "value": all_checksums})
            except Exception as e:
                self.result_signal.emit(f"💥 Error generating checksums: {e}")

class QtDriver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.window = self  
        self.selected_file = None
        self.worker = None  
        
        self.resize(800, 600)
        self.setWindowTitle("Qt Driver")
        
        main_layout = QHBoxLayout(self)

        # Left side Layout Container Widget
        left_side_container = QWidget()
        left_side_container.setFixedWidth(220) 
        
        left_side = QVBoxLayout(left_side_container)
        left_side.setContentsMargins(0, 0, 0, 0) 
        
        self.file_btn = QPushButton("File Picker")
        self.file_btn.clicked.connect(self.select_file)
        left_side.addWidget(self.file_btn)

        self.gen_btn = QPushButton("Generate All Checksums")
        self.gen_btn.clicked.connect(self.generate_all_checksums)
        left_side.addWidget(self.gen_btn)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        left_side.addWidget(separator)

        self.hash_combo_box = QComboBox()
        for hash_type in checksum.HASH_TYPES:
            self.hash_combo_box.addItem(hash_type.upper())
        left_side.addWidget(self.hash_combo_box)

        self.check_btn = QPushButton("Check Checksum")
        self.check_btn.clicked.connect(self.check_checksum)
        left_side.addWidget(self.check_btn)
        
        left_side.addStretch(1)

        # Right side Layout
        right_side = QVBoxLayout()
        
        file_row_layout = QHBoxLayout()
        self.file_info_label = QLabel("Select file")
        self.file_info_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.clear_file_btn = QPushButton("Clear File ❌")
        self.clear_file_btn.setSizePolicy(self.clear_file_btn.sizePolicy().Policy.Fixed, self.clear_file_btn.sizePolicy().Policy.Fixed)
        self.clear_file_btn.clicked.connect(self.clear_file)

        file_row_layout.addWidget(self.clear_file_btn)
        file_row_layout.addWidget(self.file_info_label)
        right_side.addLayout(file_row_layout)

        input_row_layout = QHBoxLayout()
        input_label = QLabel("Enter Checksum:")
        input_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        input_label.setSizePolicy(input_label.sizePolicy().Policy.Fixed, input_label.sizePolicy().Policy.Fixed)
        
        self.input_text_box = QLineEdit()
        input_row_layout.addWidget(input_label)
        input_row_layout.addWidget(self.input_text_box)
        right_side.addLayout(input_row_layout)

        self.status_indicator = QTextEdit()
        self.status_indicator.setReadOnly(True)
        self.status_indicator.setStyleSheet("background-color: transparent;")
        right_side.addWidget(self.status_indicator)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.hide()         
        right_side.addWidget(self.progress_bar)

        main_layout.addWidget(left_side_container)
        main_layout.addLayout(right_side)

    def set_ui_enabled(self, enabled):
        self.file_btn.setEnabled(enabled)
        self.gen_btn.setEnabled(enabled)
        self.check_btn.setEnabled(enabled)
        self.clear_file_btn.setEnabled(enabled)
        self.hash_combo_box.setEnabled(enabled)

    def reset_styles(self):
        self.input_text_box.setStyleSheet("background-color: transparent;")
        self.status_indicator.setStyleSheet("background-color: transparent;")

    def check_checksum(self):
        # FIXED: Safe reference validation logic sequence
        if self.worker is not None:
            return

        self.reset_styles()
        if not self.selected_file:
            self.status_indicator.setText("⚠️ Error: No file selected yet via File Picker.")
            return

        user_input = self.input_text_box.text().strip()
        if not user_input:
            self.status_indicator.setText("⚠️ Error: No checksum string provided.")
            return

        hash_type = self.hash_combo_box.currentText().lower()

        self.set_ui_enabled(False)
        self.progress_bar.show()
        self.status_indicator.setText("⏳ Calculating and verifying hash signature...")
        
        self.worker = ChecksumWorker("check", self.selected_file, user_input, hash_type)
        self.worker.result_signal.connect(self.display_result)
        
        # FIXED: Explicit lifecycle management connections
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)  
        self.worker.start()

    def generate_all_checksums(self):
        # FIXED: Safe reference validation logic sequence
        if self.worker is not None:
            return

        self.reset_styles()
        if not self.selected_file:
            self.status_indicator.setText("⚠️ Error: No file selected yet via File Picker.")
            return

        self.set_ui_enabled(False)
        self.progress_bar.show()
        self.status_indicator.setText("⏳ Extracting all cryptographic hash sequences...")
        
        self.worker = ChecksumWorker("generate", self.selected_file)
        self.worker.result_signal.connect(self.display_result)
        
        # FIXED: Explicit lifecycle management connections
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)  
        self.worker.start()

    # FIXED: This clean-up hook resets the pointer container safely on completion
    def on_worker_finished(self):
        self.worker = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)")
        if file_path:
            self.selected_file = file_path
            self.file_info_label.setText(f"📂 File securely selected: {self.selected_file}")
            self.reset_styles()
            self.status_indicator.setText("")

    def clear_file(self):
        self.selected_file = None
        self.input_text_box.clear()
        self.file_info_label.setText("Select file")
        self.reset_styles()
        self.status_indicator.setText("")

    def display_result(self, result):
        self.progress_bar.hide()
        self.set_ui_enabled(True)  
        
        if isinstance(result, str):
            self.status_indicator.setText(result)
            return

        if result["type"] == "check":
            is_match = result["value"]
            if is_match:
                self.status_indicator.setText("✅ Checksum matches")
                self.status_indicator.setStyleSheet("background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;")
                self.input_text_box.setStyleSheet("background-color: #d4edda; color: #155724;")
            else:
                self.status_indicator.setText("❌ Checksum does not match")
                self.status_indicator.setStyleSheet("background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;")
                self.input_text_box.setStyleSheet("background-color: #f8d7da; color: #721c24;")

        elif result["type"] == "generate":
            checksums_dict = result["value"]
            output_string = "📋 Generated Checksums:\n\n"
            for algo, value in checksums_dict.items():
                output_string += f"{algo.upper()}:\n{value}\n\n"
            self.status_indicator.setText(output_string)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    driver = QtDriver()
    driver.show()
    sys.exit(app.exec_())