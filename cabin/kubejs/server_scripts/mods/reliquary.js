if(Platform.isLoaded("reliquary")) {
    ServerEvents.recipes(event => {
        event.forEachRecipe({id: /alkahestry/}, recipe => {
            recipe.id(recipe.getId() + "_manual_only")
        })

        // Alkahestry

        // Remove silver and tin alkahestry recipes
        event.remove({ id: "reliquary:alkahestry/crafting/tin_ingot"})
        event.remove({ id: "reliquary:alkahestry/crafting/silver_ingot"})

        /**
         * @param {string} ingredient
         * @param {number} charge
         * @param {number} outputCount
         * @returns {Internal.RecipesEventJS}
         */
        function createAlkahestryRecipe(ingredient, charge, outputCount) {
            return event.custom({
                "type": "forge:conditional",
                "recipes": [
                    {
                        "conditions": [
                            {
                                "type": "reliquary:alkahestry_enabled"
                            }
                        ],
                        "recipe": {
                            "type": "reliquary:alkahestry_crafting",
                            "charge": charge,
                            "ingredient": ingredient.charAt(0) == "#" ? {
                                "tag": ingredient.slice(1)
                            } : {
                                "item": ingredient
                            },
                            "result_count": outputCount
                        }
                    }
                ]
            })
        }
        let recipePath = "kubejs:alkahestry/crafting/"
        let manualOnly = "_manual_only"

        // Add alkahestry recipes for modded ore metals and gems found in CABIN
        createAlkahestryRecipe("#forge:ingots/zinc", 8, 3).id(recipePath + "zinc_ingot" + manualOnly)
        createAlkahestryRecipe("#forge:ingots/nickel", 32, 2).id(recipePath + "nickel_ingot" + manualOnly)
        createAlkahestryRecipe("#forge:ingots/lead", 32, 2).id(recipePath + "lead_ingot" + manualOnly)

        createAlkahestryRecipe("#forge:gems/apatite", 8, 5).id(recipePath + "apatite" + manualOnly)
        createAlkahestryRecipe("#forge:gems/niter", 8, 3).id(recipePath + "niter" + manualOnly)
        createAlkahestryRecipe("#forge:gems/sulfur", 8, 3).id(recipePath + "sulfur" + manualOnly)
        createAlkahestryRecipe("#forge:gems/cinnabar", 16, 2).id(recipePath + "cinnabar" + manualOnly)
        createAlkahestryRecipe("#forge:gems/ruby", 64, 2).id(recipePath + "ruby" + manualOnly)
        createAlkahestryRecipe("#forge:gems/sapphire", 64, 2).id(recipePath + "sapphire" + manualOnly)
    })
}
