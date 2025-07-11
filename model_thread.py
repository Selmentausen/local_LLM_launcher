from PyQt5.QtCore import QThread, pyqtSignal
import llama_cpp


class ModelThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.model = None
        self.running = True

    def run(self):
        try:
            self.model = llama_cpp.Llama(self.model_path)
            while self.running:
                self.msleep(100)
        except Exception as e:
            self.response_signal.emit(f"Ошибка загрузки модели: {e}")

    def stop(self):
        self.running = False
        self.wait()

    def generate_response(self, prompt):
        if self.model:
            try:
                output = self.model(prompt, max_tokens=100, stop=["\n"], echo=False)
                response = output["choices"][0]["text"]
                self.response_signal.emit(response)
            except Exception as e:
                self.response_signal.emit(f"Ошибка генерации: {e}")
        else:
            self.response_signal.emit("Модель не загружена.")
