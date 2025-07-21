import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).parent))

from app.gui_controller import GUIController

def main():
    app = QApplication(sys.argv)
    controller = GUIController(app)
    controller.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()