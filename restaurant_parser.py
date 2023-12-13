from selenium import webdriver
from bs4 import BeautifulSoup
import datetime


class Meal:
    name = ''
    price = ''
    day = 0

    def __init__(self, name, price, day):
        self.name = name
        self.price = price
        self.day = day

    def get_price(self):
        return self.price


class WeekMenu:
    meals = []

    def __init__(self):
        self.meals = []

    def add_meal(self, new_meal):
        self.meals.append(new_meal)

    def get_meals(self):
        return self.meals


class Restaurant:
    name = ''
    menu = WeekMenu()
    distance = 0
    tags = []

    def __init__(self, name, res_menu, distance, tags_list):
        self.name = name
        self.menu = res_menu
        self.distance = distance
        self.tags = tags_list

    def get_menu(self):
        return self.menu

    def get_name(self):
        return self.name

    def get_distance(self):
        return str(self.distance) + " m"

    def get_tags(self):
        return self.tags

    def add_tag(self, tag):
        self.tags.append(tag)


# open the browser
driver = webdriver.Safari()

url = "https://www.menicka.cz/moje-poloha.html?m=menicka&gps=49.210166676258375_16.599495697430932"
driver.get(url)

# get the page content
content = driver.page_source
soup = BeautifulSoup(content, features="docs.parser")

# get the list of restaurants
restaurants = []
for restaurant in soup.findAll('div', attrs={'class': 'menicka_detail'}):
    # get the name of the restaurant
    restaurant_name = restaurant.find('div', attrs={'class': 'nazev'}).text
    restaurant_distance = 0
    restaurant_unparsed_distance = restaurant.find('span', attrs={'class': 'dist'}).text
    parsed_distance = restaurant_unparsed_distance.split(" ")
    parsed_distance[0] = parsed_distance[0].replace(",", "")
    if parsed_distance[1] == "m":
        restaurant_distance = int(parsed_distance[0])
    elif parsed_distance[1] == "km":
        restaurant_distance = int(float(parsed_distance[0]) * 10)

    # get menu for the restaurant
    # menu is nested in div "menicka_detail" -> div "menicka" -> div "nabidka_1 (or nabidka)" -> element i
    restaurant_menu_items = restaurant.find('div', attrs={'class': 'menicka'}).findAll('div', attrs={
        'class': 'nabidka_1' or 'nabidka'})
    prices = restaurant.find('div', attrs={'class': 'menicka'}).findAll('div', attrs={'class': 'cena'})
    week_menu = WeekMenu()

    restaurant_tags = []

    mealIndex = 0
    for item in restaurant_menu_items:
        meal_item_name = item.text
        # remove possible HTML tags from meal_item_name
        price = prices[mealIndex].text
        week_menu.add_meal(Meal(meal_item_name, price, mealIndex))

        meal_tags = meal_item_name.split(" ")
        meal_tags = [tag.lower() for tag in meal_tags]

        # remove empty tags or tags containing numbers
        for tag in meal_tags:
            # remove numeric chars and non-alphabetic chars from tag
            tag = ''.join([i for i in tag if not i.isdigit() and i.isalpha()])
            if tag == "" or tag == " " or tag == " " or len(tag) < 3:
                continue
            restaurant_tags.append(tag)

        mealIndex += 1
    restaurants.append(Restaurant(restaurant_name, week_menu, restaurant_distance, restaurant_tags))

# sort the restaurants by their distance
restaurants.sort(key=lambda x: x.distance)

# print the menu for all restaurants
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue

    print("------- RESTAURACE: " + restaurant.get_name() + " " + restaurant.get_distance() + "--------")
    #for meal in restaurant.get_menu().get_meals():
        # print in format "meal_index. meal_name - Cena: meal_price" if the meal_price is 0 or null, print ""
    #    price = meal.get_price()
    #    if price == "0" or price == "" or price == " " or price == " ":
    #        price = "0 Kč (nebo neuvedeno)"
    #    print(str(meal.day) + ". " + meal.name + " - Cena: " + price)
driver.quit()

# generate docs file with menu, use utf-8 encoding and czech language
# first generate list with all restaurants, on click on the list item navigate to #restaurant-name (U Karla -> #u-karla) anchor
f = open("../restaurant_menu/TomasZouhar.github.io/index.html", "w", encoding="utf-8")
f.write("<docs><head><meta charset=\"utf-8\"></head><body>")
f.write("<style>")
# make the page pretty
f.write("body { font-family: Arial, Helvetica, sans-serif; }")
f.write("h1 { font-size: 30px; }")
f.write("h2 { font-size: 20px; }")
f.write("p { font-size: 15px; }")
f.write("ul { list-style-type: none; margin: 0; padding: 0; overflow: hidden; background-color: #333; }")
f.write("li { float: left; }")
f.write("li a { display: block; color: white; text-align: center; padding: 14px 16px; text-decoration: none; }")
f.write("li a:hover { background-color: #111; }")
# style for each restaurant, restaurants should be next to each other
f.write(".restaurant { float: left; width: 48%; }")
# style for tags
f.write(".tags { float: left; width: 100%; }")
# style for toggle button so it looks modern and nice
f.write(".toggle-button { background-color: #4CAF50; border: none; color: white; padding: 15px 32px; text-align: "
        "center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }")
f.write("</style>")

f.write("<h1>Menu dne " + str(datetime.date.today()) + "</h1>")
f.write("<ul>")
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue
    f.write("<li><a href=\"#" + restaurant.get_name().replace(" ",
                                                              "-").lower() + "\">" + restaurant.get_name() + "</a></li>")
f.write("</ul>")

# here parse all restaurants and their tags, keep in mind their count and then generate the list of tags where the more
# common tags are bigger. Keep the tags in dictionary with tag name - count
tags = {}
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue
    for tag in restaurant.get_tags():
        if tag in tags:
            tags[tag] += 1
        else:
            tags[tag] = 1

# sort the tags by their count
sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)

# toggle button for toggling visibility of .tags div
f.write("<button class=\"toggle-button\" onclick=\"var x = document.getElementsByClassName('tags')[0]; if ("
        "x.style.display === 'none') { x.style.display = 'block'; } else { x.style.display = 'none'; "
        "}\">Zobrazit/skrýt tagy</button>")

# generate the list of tags, if user clicks the tag, find all restaurants with this tag and show them
f.write("<div style=\"display: none\" class=\"tags\">")
f.write("<h2 class=\"tag\">Tagy</h2>")
f.write("<ul>")
for tag in sorted_tags:
    # a will scroll to first element with class "has-tag-tagname" (javascript function scrollToTag)
    f.write("<li><a onclick=\"scrollToTag('has-tag-" + tag[0] + "')\">" + tag[0] + " (" + str(tag[1]) + ")</a></li>")
f.write("</ul>")
f.write("</div>")

f.write("<div class=\"wrapper\">")
# then write all restaurants with their ids
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue
    f.write("<div class=\"restaurant\">")
    f.write("<h1 id=\"" + restaurant.get_name().replace(" ",
                                                        "-").lower() + "\"")
    f.write("/>" + restaurant.get_name() + " (" + restaurant.get_distance() + ") </h1>")
    for meal in restaurant.get_menu().get_meals():
        # print in format "meal_index. meal_name - Cena: meal_price" if the meal_price is 0 or null, print ""
        price = meal.get_price()
        if price == "0" or price == "" or price == " " or price == " ":
            price = "0 Kč (nebo neuvedeno)"
        f.write("<p ")

        if len(restaurant.get_tags()) > 0:
            f.write(" class=\"tagged has-tag-")
            for tag in restaurant.get_tags():
                # write tag only if meal name contains it
                if tag in meal.name.lower():
                    f.write(tag + " has-tag-")

            f.write("\"")

        f.write(">" + str(meal.day) + ". " + meal.name + " - Cena: " + price + "</p>")
    f.write("</div>")
f.write("</div>")

f.write("</body>")
f.write("<script>")
# function to toggle tags

# script for scrolling to first restaurant with class "has-tag-tagname" (scroll smoothly)
f.write("function scrollToTag(tag) {")
f.write("var element = document.getElementsByClassName(tag)[0];")
# color all elements with classes "tagged" to light blue
f.write("var tagged = document.getElementsByClassName('tagged');")
f.write("for (var i = 0; i < tagged.length; i++) {")
f.write("tagged[i].style.backgroundColor = 'white';")
f.write("}")
# color all elements with class "has-tag-tagname" to lime
f.write("var elements = document.getElementsByClassName(tag);")
f.write("for (var i = 0; i < elements.length; i++) {")
f.write("elements[i].style.backgroundColor = 'lime';")
f.write("}")
f.write("element.scrollIntoView({behavior: 'smooth'});")
f.write("}")
f.write("</script>")
f.write("</docs>")
