import string
import copy


class GenerateCookbook:
    def __init__(self, cookbook_template, recipe_template, recipes_data):
        self.cookbook_template = string.Template(cookbook_template)
        self.recipe_template = string.Template(recipe_template)
        self.recipes_data = copy.deepcopy(recipes_data)

    def generateCookbook(self):
        
        recipes_data_grouped = dict()

        for x in self.recipes_data:
            new_type = x['type']
            if new_type in recipes_data_grouped:
                recipes_data_grouped[new_type].append(x)
            else:
                recipes_data_grouped[new_type] = [x]

        for recipe_type in recipes_data_grouped:
            recipe_tmp = ""
            for idx, x in enumerate(recipes_data_grouped[recipe_type]):
                x['servings'] = "{} porcj{}".format(x['servings'], "a" if x['servings'] < 2 else "e")
                x['authors'] = "Autor{}: \\\\ {}".format(("zy" if "," in x['authors'] else ""), x['authors'])
                x['ingredients'] = "\n".join(['\\item {}'.format(i) for i in x['ingredients']])
                x['img_filename'] = "{}{}.png".format(recipe_type, idx)
                recipe_tmp += self.recipe_template.substitute(x)
            
            recipes_data_grouped[recipe_type] = recipe_tmp

        return self.cookbook_template.substitute(recipes_data_grouped)
