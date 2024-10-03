import string
import pandas as pd
import subprocess

recipes_data = []
recipe_template = ""
cookbook_template = ""

with open('recipes_data.csv', mode ='r') as f:
    recipes_data = pd.read_csv(f, sep=',')

with open('templates/recipe_template.txt', mode ='r') as f:
    recipe_template = string.Template(f.read())

with open('templates/cookbook_template.txt', mode ='r') as f:
    cookbook_template = string.Template(f.read())


table_lut = {'TIME_SIGNATURE' : 0,
             'TYPE' : 1,
             'RECIPE_NAME' : 2,
             'AUTHORS' : 3,
             'NUMBER_OF_PEOPLE' : 4,
             'INGREDIENTS' : 5,
             'RECIPE' : 6,
             'NOTES' : 7,
             'IMG_FILENAME' : 8,
             'IMG_CAPTION' : 2
             }


#============================================================================
new_filenames = []
for index, row in recipes_data.iterrows():
    img_link = row.iloc[table_lut['IMG_FILENAME']]
    id_idx = img_link.find('id=')
    img_id = img_link[id_idx+3:] 
    subprocess.check_output('gdown {} -O bin/img/a{}'.format(img_id, index), shell=True)
    os_out = subprocess.check_output('file bin/img/a{}'.format(index), shell=True)
    os_out = os_out.decode('utf-8')

    new_extension = ''
    if 'PNG' in os_out:
        new_extension = '.png'
    elif 'JPEG' in os_out:
        new_extension = '.jpeg'
    elif 'PC bitmap' in os_out:
        new_extension = '.bmp'
    elif 'GIF' in os_out:
        new_extension = '.jpeg'
    else:
        print('UNKNOWN EXTENSION FROM FILE a{}'.format(index))
    
    subprocess.check_output('mv bin/img/a{} bin/img/a{}{}'.format(index, index, new_extension), shell=True)
    new_filenames.append('a{}{}'.format(index, new_extension))

recipes_data.iloc[:, table_lut['IMG_FILENAME']] = new_filenames
#============================================================================


cookbook_output = ""
breakfast_recipes_output = ""
diner_recipes_output = ""

for index, row in recipes_data.iterrows():
    ingredients = row.iloc[table_lut['INGREDIENTS']]
    ingredients = '\\item ' + ingredients.replace('\n', '\n\\item ')

    recipe = row.iloc[table_lut['RECIPE']]
    recipe = recipe.replace('\n', ' ')

    recipe_dict = {
        'RECIPE_NAME': row.iloc[table_lut['RECIPE_NAME']],
        'AUTHORS': row.iloc[table_lut['AUTHORS']],
        'INGREDIENTS': ingredients,
        'RECIPE': recipe,
        'CARBS': '?',
        'PROTEIN': '?',
        'FAT': '?',
        'KCAL': '?',
        'KCAL_PER_100G': '?',
        'NOTES': row.iloc[table_lut['NOTES']],
        'IMG_FILENAME': row.iloc[table_lut['IMG_FILENAME']],
        'IMG_CAPTION': row.iloc[table_lut['IMG_CAPTION']]
    }
    if row.iloc[table_lut['TYPE']] == 'Śniadanie':
        breakfast_recipes_output += recipe_template.substitute(recipe_dict)
    else:
        diner_recipes_output += recipe_template.substitute(recipe_dict)

cookbook_dict = {
    'BREAKFAST_RECIPES' : breakfast_recipes_output,
    'DINER_RECIPES' : diner_recipes_output
}

cookbook_output = cookbook_template.substitute(cookbook_dict)

with open('bin/przepisnik_HK.tex', 'w') as f:
    f.write(cookbook_output)
