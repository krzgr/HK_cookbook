# This Python file uses the following encoding: utf-8
import PySide6.QtWidgets
import PySide6.QtCore
import jsonschema.exceptions
import RecipeDialog
import json
import jsonschema
from enum import Enum
import GenerateCookbook

class RecipeAppGUI(PySide6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.recipe_dialog = RecipeDialog.RecipeDialog(self)
        self.file_dialog = PySide6.QtWidgets.QFileDialog(self)
        self.recipes_data = []
        self.recipe_dialog_state = 'RECIPE_NEW'

        self.recipes_filename = None
        self.cookbook_template = None
        self.recipe_template = None

        self.recipes_data_changed = False

        with open(PySide6.QtCore.QDir.currentPath()+"/recipes_schema.json", 'r') as f:
            self.schema = json.load(f)
        
        self.title_style_sheet = "QLabel { font-size: 28px; font-weight: bold; }"
        self.section_style_sheet = "QLabel { font-size: 16px; font-weight: bold; }"
        self.section_info_style_sheet = "QLabel { font-size: 16px; }"

        self._initUI()

    def _initUI(self):
        self.setWindowTitle("Przepiśnik")
        self.setGeometry(100, 100, 1000, 640)
        self.move(self.screen().geometry().center() - self.frameGeometry().center())

        # RecipeDialog signals
        self.recipe_dialog.accepted.connect(self._onRecipeAccepted)
        self.recipe_dialog.rejected.connect(self._onRecipeRejected)

        # Main container
        self.central_widget = PySide6.QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = PySide6.QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(self.main_layout)

        # Open file with recipes
        self.groupbox_recipes_data = PySide6.QtWidgets.QGroupBox("Przepisy")
        self.groupbox_recipes_data_layout = PySide6.QtWidgets.QHBoxLayout()
        self.groupbox_recipes_data_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.groupbox_recipes_data_layout.addSpacing(5)

        self.open_recipes_file_button = PySide6.QtWidgets.QPushButton("Otwórz")
        self.save_recipes_file_button = PySide6.QtWidgets.QPushButton("Zapisz")
        self.recipes_filename_label = PySide6.QtWidgets.QLabel("")
        self.groupbox_recipes_data_layout.addWidget(self.open_recipes_file_button)
        self.groupbox_recipes_data_layout.addWidget(self.save_recipes_file_button)
        self.groupbox_recipes_data_layout.addWidget(self.recipes_filename_label)
        self.groupbox_recipes_data.setLayout(self.groupbox_recipes_data_layout)
        self.main_layout.addWidget(self.groupbox_recipes_data)

        self.open_recipes_file_button.clicked.connect(self._onOpenRecipesFileClicked)
        self.save_recipes_file_button.clicked.connect(self._onSaveRecipesFileClicked)

        # Open templates
        self.groupbox_templates = PySide6.QtWidgets.QGroupBox("Szablony")
        self.groupbox_templates_layout = PySide6.QtWidgets.QGridLayout()
        self.groupbox_templates_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.groupbox_templates_layout.setSpacing(5)

        self.open_cookbook_template_button = PySide6.QtWidgets.QPushButton("Otwórz szablon przepiśnika")
        self.open_recipe_template_button = PySide6.QtWidgets.QPushButton("Otwórz szablon przepisów")
        self.cookbook_template_label = PySide6.QtWidgets.QLabel("")
        self.recipe_template_label = PySide6.QtWidgets.QLabel("")

        self.groupbox_templates_layout.addWidget(self.open_cookbook_template_button, 1, 1)
        self.groupbox_templates_layout.addWidget(self.cookbook_template_label, 1, 2)
        self.groupbox_templates_layout.addWidget(self.open_recipe_template_button, 2, 1)
        self.groupbox_templates_layout.addWidget(self.recipe_template_label, 2, 2)

        self.groupbox_templates.setLayout(self.groupbox_templates_layout)
        self.main_layout.addWidget(self.groupbox_templates)

        self.open_cookbook_template_button.clicked.connect(self._onOpenCookbookTemplateClicked)
        self.open_recipe_template_button.clicked.connect(self._onOpenRecipeTemplateClicked)

        # Gererate LATEX file
        self.groupbox_latex_generation = PySide6.QtWidgets.QGroupBox("Generowanie pliku Latex")
        self.generate_cookbook_button = PySide6.QtWidgets.QPushButton("Wygeneruj przepiśnik")
        self.groupbox_generate_latex_layout = PySide6.QtWidgets.QHBoxLayout()
        self.groupbox_generate_latex_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.groupbox_generate_latex_layout.addWidget(self.generate_cookbook_button)
        
        self.groupbox_latex_generation.setLayout(self.groupbox_generate_latex_layout)
        self.main_layout.addWidget(self.groupbox_latex_generation)

        self.generate_cookbook_button.clicked.connect(self._onGenerateCookbookClicked)

        # Cookbook info
        self.cookbook_info_layout = PySide6.QtWidgets.QHBoxLayout()
        self.cookbook_info_widget = PySide6.QtWidgets.QWidget()
        self.cookbook_info_widget.setFixedWidth(1000)
        self.cookbook_info_widget.setMinimumHeight(450)
        self.cookbook_info_widget.setLayout(self.cookbook_info_layout)
        self.main_layout.addWidget(self.cookbook_info_widget)

        self.recipe_list = PySide6.QtWidgets.QListWidget()
        self.recipe_list.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, 
                                       PySide6.QtWidgets.QSizePolicy.Policy.Expanding)
        self.recipe_list.setFixedWidth(200)
        self.recipe_list_layout = PySide6.QtWidgets.QVBoxLayout()
        self.recipe_list_layout.addWidget(self.recipe_list)
        self.recipe_info = PySide6.QtWidgets.QVBoxLayout()
        self.cookbook_info_layout.addLayout(self.recipe_list_layout)
        self.cookbook_info_layout.addSpacing(15)
        self.cookbook_info_layout.addLayout(self.recipe_info)
        self.recipe_list.itemSelectionChanged.connect(self._onRecipeListItemSelectionChanged)

        self.recipe_name_label = PySide6.QtWidgets.QLabel('')
        self.recipe_name_label.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.recipe_name_label.setStyleSheet(self.title_style_sheet)
        self.recipe_info.addWidget(self.recipe_name_label)

        self.servings_layout = PySide6.QtWidgets.QHBoxLayout()
        self.servings_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.servings_label = PySide6.QtWidgets.QLabel('')
        self.servings_label.setStyleSheet(self.section_info_style_sheet)
        self.recipe_info.addLayout(self.servings_layout)
        self.servings_text_label = PySide6.QtWidgets.QLabel('Liczba porcji:')
        self.servings_text_label.setStyleSheet(self.section_style_sheet)
        self.servings_layout.addWidget(self.servings_text_label)
        self.servings_layout.addWidget(self.servings_label)

        self.authors_layout = PySide6.QtWidgets.QHBoxLayout()
        self.authors_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.authors_text_label = PySide6.QtWidgets.QLabel('Autorzy:')
        self.authors_text_label.setStyleSheet(self.section_style_sheet)
        self.authors_label = PySide6.QtWidgets.QLabel('')
        self.authors_label.setStyleSheet(self.section_info_style_sheet)
        self.recipe_info.addLayout(self.authors_layout)
        self.authors_layout.addWidget(self.authors_text_label)
        self.authors_layout.addWidget(self.authors_label)

        self.ingredients_label = PySide6.QtWidgets.QLabel('Składniki:')
        self.ingredients_label.setStyleSheet(self.section_style_sheet)
        self.recipe_info.addWidget(self.ingredients_label)
        self.ingredients_items_label = PySide6.QtWidgets.QLabel('')
        self.ingredients_items_label.setStyleSheet(self.section_info_style_sheet)
        self.recipe_info.addWidget(self.ingredients_items_label)

        self.prepration_label = PySide6.QtWidgets.QLabel('Sposób przygotowania:')
        self.prepration_label.setStyleSheet(self.section_style_sheet)
        self.recipe_info.addWidget(self.prepration_label)
        self.prepration_steps_label = PySide6.QtWidgets.QLabel('')
        self.prepration_steps_label.setStyleSheet(self.section_info_style_sheet)
        self.prepration_steps_label.setWordWrap(True)
        self.recipe_info.addWidget(self.prepration_steps_label)

        self.notes_text_label = PySide6.QtWidgets.QLabel('Uwagi:')
        self.notes_text_label.setStyleSheet(self.section_style_sheet)
        self.recipe_info.addWidget(self.notes_text_label)
        self.notes_label = PySide6.QtWidgets.QLabel('')
        self.notes_label.setStyleSheet(self.section_info_style_sheet)
        self.notes_label.setWordWrap(True)
        self.recipe_info.addWidget(self.notes_label)

        self.recipe_button_layout = PySide6.QtWidgets.QHBoxLayout()
        self.recipe_info.addLayout(self.recipe_button_layout)
        self.recipe_button_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.recipe_button_layout.addSpacing(5)
        self.new_recipe_button = PySide6.QtWidgets.QPushButton("Dodaj nowy przepis")
        self.change_recipe_button = PySide6.QtWidgets.QPushButton("Zmień przepis")
        self.remove_recipe_button = PySide6.QtWidgets.QPushButton("Usuń przepis")
        self.move_up_recipe_button = PySide6.QtWidgets.QPushButton("Przesuń w górę")
        self.move_down_recipe_button = PySide6.QtWidgets.QPushButton("Przesuń w dół")
        self.recipe_button_layout.addWidget(self.new_recipe_button)
        self.recipe_button_layout.addWidget(self.change_recipe_button)
        self.recipe_button_layout.addWidget(self.remove_recipe_button)
        self.recipe_button_layout.addWidget(self.move_up_recipe_button)
        self.recipe_button_layout.addWidget(self.move_down_recipe_button)

        self.new_recipe_button.clicked.connect(self._onNewRecipeButtonClicked)
        self.change_recipe_button.clicked.connect(self._onChangeRecipeButtonClicked)
        self.remove_recipe_button.clicked.connect(self._onRemoveRecipeButtonClicked)
        self.move_up_recipe_button.clicked.connect(self._onMoveUpRecipeButtonClicked)
        self.move_down_recipe_button.clicked.connect(self._onMoveDownRecipeButtonClicked)


        spacerItem7 = PySide6.QtWidgets.QSpacerItem(20, 200, PySide6.QtWidgets.QSizePolicy.Minimum, 
                                                    PySide6.QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addItem(spacerItem7)
        #self.main_layout.addStretch()
        self.recipe_info.addStretch()
        

    def loadRecipeData(self, filename):
        recipes_data = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                recipes_data = json.load(file)
        except ValueError:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                   f"Wystąpił błąd podczas otwierania pliku:\n{filename}")
            return

        try:
            jsonschema.validate(instance=recipes_data, schema=self.schema)
            self.recipes_data = recipes_data
            self.updateRecipesList()
            self.recipe_list.setCurrentRow(0)
            self.recipes_filename = filename
            self.recipes_filename_label.setText(filename)
        except jsonschema.exceptions.ValidationError as e:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                   f"Wystąpił błąd podczas otwierania pliku:\n{e.message}")

    def updateRecipesList(self):
        labels = [x['recipe_name'] for x in self.recipes_data]
        self.recipe_list.clear()
        self.recipe_list.addItems(labels)
        self.recipe_list.setHorizontalScrollBarPolicy(PySide6.QtCore.Qt.ScrollBarAlwaysOff)
        #self.recipe_list.setFixedSize(self.recipe_list.sizeHintForColumn(0) + 2 * self.recipe_list.frameWidth() + 50,
        #                              self.recipe_list.sizeHintForRow(0) * self.recipe_list.count() + 2 * self.recipe_list.frameWidth())



    def _onRecipeAccepted(self):
        self.recipes_data_changed = True
        recipe_data = self.recipe_dialog.getRecipeData()

        if self.recipe_dialog_state == 'RECIPE_NEW':
            self.recipes_data.append(recipe_data)
        elif self.recipe_dialog_state == 'RECIPE_CHANGE':
            idx_list = self.recipe_list.selectedIndexes()
            if len(idx_list) == 1:
                idx = idx_list[0].row()
                self.recipes_data[idx] = recipe_data
                self.updateRecipeInfo(idx)

        self.updateRecipesList()

    def _onRecipeRejected(self):
        pass

    def _onOpenRecipesFileClicked(self):
        file_name = self.file_dialog.getOpenFileName(self, "Select a File",
                                                     PySide6.QtCore.QDir.currentPath()+'/..',
                                                     "JSON (*.json)")
        if file_name[0]:
            self.loadRecipeData(file_name[0])
    
    def _onSaveRecipesFileClicked(self):
        if not self.recipes_filename:
            filename = self.file_dialog.getSaveFileName(self, "Create new File",
                                                        PySide6.QtCore.QDir.currentPath()+'/przepisnik.json',
                                                        "JSON (*.json)")
            filename = filename[0]

            if filename:
                self.recipes_filename = filename
            else:
                return
        try:
            with open(self.recipes_filename, 'w', encoding='utf-8') as file:
                self.recipes_filename_label.setText(self.recipes_filename)
                json.dump(self.recipes_data, file)
                self.recipes_data_changed = False
        except ValueError:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd",
                                                   f"Wystąpił błąd podczas zapisywania pliku:\n{self.recipes_filename}")


    def _onRecipeListItemSelectionChanged(self):
        idx_list = self.recipe_list.selectedIndexes()
        if len(idx_list) == 1:
            self.updateRecipeInfo(idx_list[0].row())

    def updateRecipeInfo(self, idx_selected_item):
        recipe_data = self.recipes_data[idx_selected_item]

        self.recipe_name_label.setText(recipe_data['recipe_name'])
        self.servings_label.setText(str(recipe_data['servings']))
        self.authors_label.setText(recipe_data['authors'])

        prepration_steps_label_html = '<ul><li>{}</li></ul>'.format('</li><li>'.join(recipe_data['ingredients']))
        self.ingredients_items_label.setText(prepration_steps_label_html)

        self.prepration_steps_label.setText(recipe_data['preparation'])
        self.notes_label.setText(recipe_data['notes'])
    
    def _onNewRecipeButtonClicked(self):
        self.recipe_dialog_state = 'RECIPE_NEW'
        self.recipe_dialog.clearDialogData()
        self.recipe_dialog.show()

    def _onChangeRecipeButtonClicked(self):
        self.recipe_dialog_state = 'RECIPE_CHANGE'
        idx_list = self.recipe_list.selectedIndexes()
        if len(idx_list) == 1:
            idx = idx_list[0].row()
            self.recipe_dialog.setRecipeData(self.recipes_data[idx])
            self.recipe_dialog.show()

    def _onRemoveRecipeButtonClicked(self):
        self.recipe_dialog_state = 'RECIPE_REMOVE'
        idx_list = self.recipe_list.selectedIndexes()
        if len(idx_list) == 1:
            self.recipes_data_changed = True
            idx = idx_list[0].row()
            del self.recipes_data[idx]
            self.updateRecipesList()

    def _onMoveUpRecipeButtonClicked(self):
        self.recipe_dialog_state = 'RECIPE_MOVE_UP'
        idx_list = self.recipe_list.selectedIndexes()
        if len(idx_list) == 1:
            idx = idx_list[0].row()
            if idx > 0:
                self.recipes_data_changed = True
                self.recipes_data[idx], self.recipes_data[idx-1] = self.recipes_data[idx-1], self.recipes_data[idx]
                self.updateRecipesList()
                self.recipe_list.setCurrentRow(idx-1)

    def _onMoveDownRecipeButtonClicked(self):
        self.recipe_dialog_state = 'RECIPE_MOVE_DOWN'
        idx_list = self.recipe_list.selectedIndexes()
        if len(idx_list) == 1:
            idx = idx_list[0].row()
            if idx < len(self.recipes_data)-1:
                self.recipes_data_changed = True
                self.recipes_data[idx], self.recipes_data[idx+1] = self.recipes_data[idx+1], self.recipes_data[idx]
                self.updateRecipesList()
                self.recipe_list.setCurrentRow(idx+1)

    def _onOpenRecipeTemplateClicked(self):
        filename = self.file_dialog.getOpenFileName(self, "Select a File",
                                                    PySide6.QtCore.QDir.currentPath()+'/..',
                                                    "TEX (*.tex)")
        filename = filename[0]
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    self.recipe_template = file.read()
                self.recipe_template_label.setText(filename)
            except ValueError:
                PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Wystąpił błąd podczas otwierania pliku:\n{filename}")

    def _onOpenCookbookTemplateClicked(self):
        filename = self.file_dialog.getOpenFileName(self, "Select a File",
                                                    PySide6.QtCore.QDir.currentPath()+'/..',
                                                    "TEX (*.tex)")
        filename = filename[0]
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    self.cookbook_template = file.read()
                self.cookbook_template_label.setText(filename)
            except ValueError:
                PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Wystąpił błąd podczas otwierania pliku:\n{filename}")

    def _onGenerateCookbookClicked(self):
        if self.recipes_filename == None:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Aby wygenerować przepiśnik należy otworzyć bazę z przepisami")
            return
        if self.cookbook_template == None:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Aby wygenerować przepiśnik należy otworzyć szablon przepiśnika")
            return
        if self.recipe_template == None:
            PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Aby wygenerować przepiśnik należy otworzyć szablon przepisów")
            return
        
        filename = self.file_dialog.getSaveFileName(self, "Create new File",
                                                    PySide6.QtCore.QDir.currentPath()+'/przepisnik.tex',
                                                    "TEX (*.tex)")
        filename = filename[0]

        if filename:
            g = GenerateCookbook.GenerateCookbook(self.cookbook_template, self.recipe_template, self.recipes_data)
            out = g.generateCookbook()
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(out)
            except ValueError:
                PySide6.QtWidgets.QMessageBox.critical(self, "Błąd", 
                                                    f"Wystąpił błąd podczas zapisywania pliku:\n{filename}")
    def closeEvent(self, event):

        if self.recipes_data_changed:
            reply = PySide6.QtWidgets.QMessageBox.question(
                self,
                "Niezapisane zmiany",
                "Jeżeli zamkniesz to okno zmiany zostaną niezapisane. Czy na pewno chcesz zamknąć okno?",
                PySide6.QtWidgets.QMessageBox.Yes | PySide6.QtWidgets.QMessageBox.No,
                PySide6.QtWidgets.QMessageBox.No  # domyślnie zaznaczony
            )

            if reply == PySide6.QtWidgets.QMessageBox.Yes:
                event.accept()  # pozwól zamknąć
            else:
                event.ignore()  # anuluj zamknięcie

        #super().closeEvent(event)  # nie zapomnij wywołać metody bazowej
