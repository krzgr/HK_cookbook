import sys
import PySide6.QtWidgets
import RecipeAppGUI

if __name__ == "__main__":
    app = PySide6.QtWidgets.QApplication(sys.argv)
    window = RecipeAppGUI.RecipeAppGUI()
    window.show()
    sys.exit(app.exec())
 