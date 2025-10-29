from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Road Axis Calculator")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label = QLabel("Welcome to the Road Axis Calculator")
        self.layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter axis details...")
        self.layout.addWidget(self.input_field)
        
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_button)
        
        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label)

    def calculate(self):
        # Placeholder for calculation logic
        input_data = self.input_field.text()
        self.result_label.setText(f"Calculated result for: {input_data}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())