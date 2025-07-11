from PyQt5.QtCore import QThread, pyqtSignal
import llama_cpp
import queue
import threading


class ModelThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.model = None
        self.running = True
        self.task_queue = queue.Queue()

    def run(self):
        try:
            self.model = llama_cpp.Llama(self.model_path)

            # Запускаем отдельный поток обработки запросов
            threading.Thread(target=self.process_tasks, daemon=True).start()

            while self.running:
                self.msleep(100)  # Ожидание в основном QThread (можно оставить)
        except Exception as e:
            self.response_signal.emit(f"Ошибка загрузки модели: {e}")

    def stop(self):
        self.running = False
        self.task_queue.put(None)  # Останавливаем поток задач
        self.wait()

    def generate_response(self, prompt):
        # Просто добавляем задачу в очередь
        self.task_queue.put(prompt)

    def process_tasks(self):
        while self.running:
            prompt = self.task_queue.get()
            if prompt is None:
                break

            if self.model:
                try:
                    output = self.model(prompt, max_tokens=100, stop=["\n"], echo=False)
                    response = output["choices"][0]["text"]
                    self.response_signal.emit(response)
                except Exception as e:
                    self.response_signal.emit(f"Ошибка генерации: {e}")
            else:
                self.response_signal.emit("Модель не загружена.")