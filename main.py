from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Slot
from datetime import datetime, timedelta
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Results")

        self.label = QLabel("Результаты")
        self.button_load = QPushButton("Загрузить файлы")
        self.button_calculate = QPushButton("Вычислить результаты")
        self.button_save = QPushButton("Сохранить результаты")

        self.res_table = QTableWidget()
        self.res_table.setRowCount(5)
        self.res_table.setColumnCount(5)
        self.res_table.setColumnWidth(1,150)
        self.res_table.setHorizontalHeaderLabels(["Место", "Нагрудный номер", "Имя", "Фамилия", "Результат"])

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button_load)
        layout.addWidget(self.button_calculate)
        layout.addWidget(self.button_save)
        layout.addWidget(self.res_table)



        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.button_load.clicked.connect(self.load_files)
        self.button_calculate.clicked.connect(self.calculate_results)
        self.button_save.clicked.connect(self.save_results)

        self.res_data = []
        self.comp_data = {}
        self.results = {}


    @Slot()
    def load_files(self):
        comp_filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл с результатами",
                                                      filter="JSON Files (*.json)")
        res_filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл со спортсменами",
                                                       filter="Text Files (*.txt)")

        if comp_filename and res_filename:
            with open(comp_filename, "r", encoding="utf-8") as comp_file:
                json_str = comp_file.read().strip("\ufeff")
                self.comp_data = json.loads(json_str)

            with open(res_filename, "r", encoding="utf-8-sig") as res_file:
                res_uncounted = res_file.readlines()

        res_counted = []

        for i in range(0, len(res_uncounted), 2):
            start_time_str, finish_time_str = res_uncounted[i].split()[2][:-7], res_uncounted[i + 1].split()[2][:-7]

            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
            finish_time = datetime.strptime(finish_time_str, "%H:%M:%S").time()

            run_time = timedelta(hours=finish_time.hour, minutes=finish_time.minute, seconds=finish_time.second) - timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)

            run_time_str = f"{run_time.seconds // 60:02}:{run_time.seconds % 60:02}"

            self.res_data.append(res_uncounted[i].split()[0] + "." + run_time_str + "," + res_uncounted[i + 1].split()[2][-6:-4])


    @Slot()
    def calculate_results(self):
        sorted_run_results = sorted(self.res_data, key=self.extract_time)
        for i in range(len(sorted_run_results)):
            sorted_run_results[i] = f"{i + 1}." + sorted_run_results[i]

        for element in sorted_run_results:
            athlete_id = element.split(".")[1]
            athlete_time = element.split(".")[2]
            self.results.update({element.split(".")[0]: {"Нагрудный номер": athlete_id,
                                                         "Имя": self.comp_data[athlete_id]["Surname"],
                                                         "Фамилия": self.comp_data[athlete_id]["Name"],
                                                         "Результат": athlete_time}})

        self.display_results()




    @Slot()
    def display_results(self):
        self.res_table.setRowCount(len(self.results))
        for row, key in enumerate(self.results.keys()):
            key_item = QTableWidgetItem(str(key))
            key_item.setTextAlignment(Qt.AlignCenter)
            self.res_table.setItem(row, 0, key_item)
            row_data = self.results[key]
            for col, value in enumerate(row_data.values()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.res_table.setItem(row, col + 1, item)




    @staticmethod
    def extract_time(element):
        return element.split(".")[1]



    @Slot()
    def save_results(self):
        with open("results.json", "w", encoding="utf-8") as write_file:
            json.dump(self.results, write_file, ensure_ascii=False, indent=4)




app = QApplication([])
main_window = MainWindow()
main_window.resize(800,300)
main_window.show()
main_window.res_table.verticalHeader().setVisible(False)
main_window.res_table.show()
app.exec()

