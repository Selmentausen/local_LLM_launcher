from PyQt5.QtCore import QThread
import llama_cpp
import queue
import threading


class ModelThread(QThread):
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.model = None
        self.running = True
        self.task_queue = queue.Queue()

    def run(self):
        try:
            self.model = llama_cpp.Llama(self.model_path)
            threading.Thread(target=self.process_tasks, daemon=True).start()
            while self.running:
                self.msleep(100)
        except Exception as e:
            pass

    def stop(self):
        self.running = False
        self.task_queue.put(None)
        self.wait()

    def generate_response(self, prompt, callback):
        self.task_queue.put((prompt, callback))

    def process_tasks(self):
        while self.running:
            item = self.task_queue.get()
            if item is None:
                break

            prompt, callback = item
            if self.model:
                try:
                    output = self.model(prompt, max_tokens=100, stop=["\n"], echo=False)
                    response = output["choices"][0]["text"]
                    callback(response)
                except Exception as e:
                    callback(f"Ошибка генерации: {e}")
            else:
                callback("Модель не загружена.")