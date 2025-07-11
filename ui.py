import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit
from model_thread import ModelThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление моделями Llama")
        self.setFixedSize(300, 200)
        self.running_models = {}

        central_widget = QWidget()
        layout = QGridLayout()

        launch_button = QPushButton("Запуск моделей")
        launch_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        launch_button.clicked.connect(self.open_launch_window)

        interact_button = QPushButton("Общение с моделями")
        interact_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        interact_button.clicked.connect(self.open_interact_window)

        layout.addWidget(launch_button, 0, 0)
        layout.addWidget(interact_button, 1, 0)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_launch_window(self):
        self.launch_window = LaunchModelsWindow(self.running_models)
        self.launch_window.show()

    def open_interact_window(self):
        self.interact_window = InteractWithModelsWindow(self.running_models)
        self.interact_window.show()


class LaunchModelsWindow(QWidget):
    def __init__(self, running_models):
        super().__init__()
        self.setWindowTitle("Запуск моделей")
        self.setFixedSize(300, 400)
        self.running_models = running_models
        self.model_buttons = {}

        layout = QGridLayout()
        models_dir = "models"
        if os.path.exists(models_dir):
            for i, model_file in enumerate(os.listdir(models_dir)):
                if model_file.endswith(".gguf"):
                    model_name = os.path.splitext(model_file)[0]
                    button = QPushButton(f"Запустить {model_name}")
                    button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
                    button.clicked.connect(lambda checked, mn=model_name, mf=os.path.join(models_dir, model_file),
                                                  btn=button: self.toggle_model(mn, mf, btn))
                    layout.addWidget(button, i, 0)
                    self.model_buttons[model_name] = button
        else:
            layout.addWidget(QLabel("Модели в папке 'models' не найдены."), 0, 0)
        self.setLayout(layout)

    def toggle_model(self, model_name, model_path, button):
        if model_name in self.running_models:
            self.running_models[model_name].stop()
            del self.running_models[model_name]
            button.setText(f"Запустить {model_name}")
            button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        else:
            try:
                thread = ModelThread(model_path)
                thread.start()
                self.running_models[model_name] = thread
                button.setText(f"Выключить {model_name}")
                button.setStyleSheet("background-color: #F44336; color: white; padding: 8px;")
            except Exception as e:
                print(f"Ошибка запуска модели {model_name}: {e}")


class InteractWithModelsWindow(QWidget):
    def __init__(self, running_models):
        super().__init__()
        self.setWindowTitle("Общение с моделями")
        self.setFixedSize(300, 400)
        self.running_models = running_models
        self.interaction_windows = []

        layout = QGridLayout()
        if self.running_models:
            for i, model_name in enumerate(self.running_models):
                button = QPushButton(f"Общаться с {model_name}")
                button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
                button.clicked.connect(lambda checked, mn=model_name: self.open_interaction_window(mn))
                layout.addWidget(button, i, 0)
        else:
            layout.addWidget(QLabel("Нет запущенных моделей."), 0, 0)
        self.setLayout(layout)

    def open_interaction_window(self, model_name):
        window = InteractionWindow(model_name, self.running_models[model_name])
        self.interaction_windows.append(window)
        window.show()


class InteractionWindow(QWidget):
    def __init__(self, model_name, model_thread):
        super().__init__()
        self.setWindowTitle(f"Общение с {model_name}")
        self.setFixedSize(400, 500)
        self.model_thread = model_thread

        layout = QGridLayout()
        layout.addWidget(QLabel("Введите запрос:"), 0, 0, 1, 2)

        self.prompt_input = QLineEdit()
        layout.addWidget(self.prompt_input, 1, 0, 1, 2)

        self.send_button = QPushButton("Отправить")
        self.send_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        layout.addWidget(self.send_button, 2, 0)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label, 2, 1)

        layout.addWidget(QLabel("Ответ:"), 3, 0, 1, 2)
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        layout.addWidget(self.response_area, 4, 0, 1, 2)

        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_prompt)
        self.is_waiting = False

    def send_prompt(self):
        if self.is_waiting:
            return

        prompt = self.prompt_input.text()
        if prompt:
            self.is_waiting = True
            self.status_label.setText("Генерация...")
            self.send_button.setEnabled(False)
            self.prompt_input.clear()

            self.model_thread.generate_response(prompt, self.display_response)

    def display_response(self, response):
        self.response_area.append(response)
        self.status_label.setText("")
        self.send_button.setEnabled(True)
        self.is_waiting = False