import PySide6.QtWidgets
from PySide6.QtCore import Qt
import re

class RecipeDialog(PySide6.QtWidgets.QDialog):
    RECIPE_TYPES = {"breakfast": "Śniadanie",
                    "snack": "Przekąska",
                    "dinner": "Obiadokolacja"}

    def __init__(self, args):
        super().__init__(args)

        self.recipe_data = {}
        self._initUI()

    def _initUI(self):
        self.setWindowFlags(self.windowFlags() & ~PySide6.QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Dodaj Nowy Przepis")
        self.setGeometry(100, 100, 600, 800)
        self.setModal(True)

        # Main container
        self.layout = PySide6.QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Fields for the form

        # Dish Type
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Rodzaj dania:"))
        self.dish_type = PySide6.QtWidgets.QComboBox()

        for type in self.RECIPE_TYPES:
            self.dish_type.addItem(self.RECIPE_TYPES[type], type)

        self.layout.addWidget(self.dish_type)

        # Dish Name
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Nazwa dania:"))
        self.dish_name = PySide6.QtWidgets.QLineEdit()
        self.layout.addWidget(self.dish_name)

        # Author
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Autor przepisu:"))
        self.author_name = PySide6.QtWidgets.QLineEdit()
        self.layout.addWidget(self.author_name)

        # Servings
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Porcje (na ile osób):"))
        self.servings = PySide6.QtWidgets.QSpinBox()
        self.servings.setMinimum(1)
        self.servings.setMaximum(4)
        self.layout.addWidget(self.servings)

        # Preparation time
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Czas przygotowania:"))
        self.preparation_time = PySide6.QtWidgets.QSpinBox()
        self.preparation_time.setMinimum(1)
        self.preparation_time.setMaximum(60)
        self.layout.addWidget(self.preparation_time)

        # Ingredients
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Składniki:"))
        self.ingredients_list = PySide6.QtWidgets.QListWidget()
        self.layout.addWidget(self.ingredients_list)

        self.ingredient_input = PySide6.QtWidgets.QLineEdit()
        self.ingredient_input.setPlaceholderText("Dodaj składnik")
        self.ingredient_input.returnPressed.connect(self.add_ingredient)
        self.layout.addWidget(self.ingredient_input)

        self.ingredient_buttons_layout = PySide6.QtWidgets.QHBoxLayout()

        self.add_ingredient_button = PySide6.QtWidgets.QPushButton("Dodaj składnik")
        self.add_ingredient_button.clicked.connect(self.add_ingredient)
        self.ingredient_buttons_layout.addWidget(self.add_ingredient_button)

        self.remove_ingredient_button = PySide6.QtWidgets.QPushButton("Usuń zaznaczony składnik")
        self.remove_ingredient_button.clicked.connect(self.remove_ingredient)
        self.ingredient_buttons_layout.addWidget(self.remove_ingredient_button)

        self.move_up_button = PySide6.QtWidgets.QPushButton("Przesuń w górę")
        self.move_up_button.clicked.connect(self.move_ingredient_up)
        self.ingredient_buttons_layout.addWidget(self.move_up_button)

        self.move_down_button = PySide6.QtWidgets.QPushButton("Przesuń w dół")
        self.move_down_button.clicked.connect(self.move_ingredient_down)
        self.ingredient_buttons_layout.addWidget(self.move_down_button)

        self.layout.addLayout(self.ingredient_buttons_layout)

        # Nutrition
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Wartości odżywcze:"))
        self.nutrition_grid_layout = PySide6.QtWidgets.QGridLayout()

        nutrition_headers = ["Węglowdany [g]", "Białko [g]", "Tłuszcze [g]",
                             "kcal/porcje", "kcal/100g"]

        self.carbs = PySide6.QtWidgets.QSpinBox()
        self.carbs.setMinimum(0)
        self.carbs.setMaximum(10000)

        self.protein = PySide6.QtWidgets.QSpinBox()
        self.protein.setMinimum(0)
        self.protein.setMaximum(10000)

        self.fats = PySide6.QtWidgets.QSpinBox()
        self.fats.setMinimum(0)
        self.fats.setMaximum(10000)

        self.kcal = PySide6.QtWidgets.QSpinBox()
        self.kcal.setMinimum(0)
        self.kcal.setMaximum(10000)

        self.kcal_per_100g = PySide6.QtWidgets.QSpinBox()
        self.kcal_per_100g.setMinimum(0)
        self.kcal_per_100g.setMaximum(10000)

        for col, header in enumerate(nutrition_headers):
            item = PySide6.QtWidgets.QLabel(header)
            item.setAlignment(Qt.AlignCenter)
            self.nutrition_grid_layout.addWidget(item, 0, col)

        self.nutrition_grid_layout.addWidget(self.carbs, 1, 0)
        self.nutrition_grid_layout.addWidget(self.protein, 1, 1)
        self.nutrition_grid_layout.addWidget(self.fats, 1, 2)
        self.nutrition_grid_layout.addWidget(self.kcal, 1, 3)
        self.nutrition_grid_layout.addWidget(self.kcal_per_100g, 1, 4)

        self.layout.addLayout(self.nutrition_grid_layout)

        # Preparation
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Sposób przygotowania:"))
        self.preparation = PySide6.QtWidgets.QTextEdit()
        self.layout.addWidget(self.preparation)

        # Notes
        self.layout.addWidget(PySide6.QtWidgets.QLabel("Uwagi (opcjonalne):"))
        self.notes = PySide6.QtWidgets.QTextEdit()
        self.layout.addWidget(self.notes)

        # Action buttons
        self.buttons_layout = PySide6.QtWidgets.QHBoxLayout()
        self.save_button = PySide6.QtWidgets.QPushButton("Zapisz przepis")
        self.save_button.clicked.connect(self._onRecipeAccepted)
        self.cancel_button = PySide6.QtWidgets.QPushButton("Anuluj")
        self.cancel_button.clicked.connect(self._onRecipeRejected)

        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

    def add_ingredient(self):
        ingredient = self.ingredient_input.text()
        if ingredient:
            self.ingredients_list.addItem(ingredient)
            self.ingredient_input.clear()
        else:
            PySide6.QtWidgets.QMessageBox.warning(self, "Błąd", "Składnik nie może być pusty")

    def remove_ingredient(self):
        selected_items = self.ingredients_list.selectedItems()
        if not selected_items:
            PySide6.QtWidgets.QMessageBox.warning(self, "Błąd", "Nie zaznaczono składnika do usunięcia")
            return

        for item in selected_items:
            self.ingredients_list.takeItem(self.ingredients_list.row(item))

    def move_ingredient_up(self):
        current_row = self.ingredients_list.currentRow()
        if current_row > 0:
            current_item = self.ingredients_list.takeItem(current_row)
            self.ingredients_list.insertItem(current_row - 1, current_item)
            self.ingredients_list.setCurrentRow(current_row - 1)

    def move_ingredient_down(self):
        current_row = self.ingredients_list.currentRow()
        if current_row < self.ingredients_list.count() - 1:
            current_item = self.ingredients_list.takeItem(current_row)
            self.ingredients_list.insertItem(current_row + 1, current_item)
            self.ingredients_list.setCurrentRow(current_row + 1)

    def _onRecipeAccepted(self):
        recipe_type_str = self.dish_type.currentText().strip()
        recipe_type = "".join([key for key, val in self.RECIPE_TYPES.items() if val == recipe_type_str])
        dish_name = self.dish_name.text()
        author = self.author_name.text()
        servings = self.servings.value()
        preparation_time = self.preparation_time.value()
        ingredients = [self.ingredients_list.item(i).text() for i in range(self.ingredients_list.count())]
        preparation = self.preparation.toPlainText()
        notes = self.notes.toPlainText()

        if not dish_name or not author or not ingredients or not preparation:
            PySide6.QtWidgets.QMessageBox.warning(self, "Błąd", "Wszystkie wymagane pola muszą być wypełnione")
        else:
            self.accept()

    def _onRecipeRejected(self):
        self.reject()

    def setRecipeData(self, recipe_data):
        if 'type' in recipe_data:
            idx = self.dish_type.findData(recipe_data['type'])
            if idx != -1:
                self.dish_type.setCurrentIndex(idx)
        if 'recipe_name' in recipe_data:
            self.dish_name.setText(recipe_data['recipe_name'])
        if 'authors' in recipe_data:
            self.author_name.setText(recipe_data['authors'])
        if 'servings' in recipe_data:
            self.servings.setValue(recipe_data['servings'])
        if 'preparation_time' in recipe_data:
            self.preparation_time.setValue(recipe_data['preparation_time'])
        if 'ingredients' in recipe_data:
            self.ingredients_list.clear()
            for ingredient in recipe_data['ingredients']:
                self.ingredients_list.addItem(ingredient)
        if 'carbs' in recipe_data:
            self.carbs.setValue(recipe_data['carbs'])
        if 'protein' in recipe_data:
            self.protein.setValue(recipe_data['protein'])
        if 'fats' in recipe_data:
            self.fats.setValue(recipe_data['fats'])
        if 'kcal' in recipe_data:
            self.kcal.setValue(recipe_data['kcal'])
        if 'kcal_per_100g' in recipe_data:
            self.kcal_per_100g.setValue(recipe_data['kcal_per_100g'])
        if 'preparation' in recipe_data:
            self.preparation.setText(recipe_data['preparation'])
        if 'notes' in recipe_data:
            self.notes.setText(recipe_data['notes'])


    def getRecipeData(self):
        recipe_type_str = self.dish_type.currentText().strip()
        recipe_type = "".join([key for key, val in self.RECIPE_TYPES.items() if val == recipe_type_str])
        recipe_name = self.dish_name.text().strip()
        authors = self.author_name.text().strip()
        servings = self.servings.value()
        preparation_time = self.preparation_time.value()
        ingredients = [self.ingredients_list.item(i).text().strip() for i in range(self.ingredients_list.count())]
        carbs = self.carbs.value()
        protein = self.protein.value()
        fats = self.fats.value()
        kcal = self.kcal.value()
        kcal_per_100g = self.kcal_per_100g.value()
        preparation = self.preparation.toPlainText().strip()
        notes = self.notes.toPlainText().strip()

        rgx = re.compile(r"\s+", re.MULTILINE)
        repl = " "

        return {"type": rgx.sub(repl, recipe_type),
                "recipe_name": rgx.sub(repl, recipe_name),
                "authors": rgx.sub(repl, authors),
                "servings": servings,
                "preparation_time": preparation_time,
                "ingredients": [rgx.sub(repl, item) for item in ingredients],
                "carbs": carbs,
                "protein": protein,
                "fats": fats,
                "kcal": kcal,
                "kcal_per_100g": kcal_per_100g,
                "preparation": rgx.sub(repl, preparation),
                "notes": rgx.sub(repl, notes)}

    def clearDialogData(self):
        self.dish_name.setText('')
        self.author_name.setText('')
        self.servings.setValue(1)
        self.preparation_time.setValue(15)
        self.ingredients_list.clear()
        self.carbs.setValue(0)
        self.protein.setValue(0)
        self.fats.setValue(0)
        self.kcal.setValue(0)
        self.kcal_per_100g.setValue(0)
        self.preparation.setText('')
        self.notes.setText('')
