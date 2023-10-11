from selenium import webdriver
from bs4 import BeautifulSoup

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

    def add_meal(self, meal):
        self.meals.append(meal)

    def get_meals(self):
        return self.meals


class Restaurant:
    name = ''
    menu = WeekMenu()

    def __init__(self, name, res_menu):
        self.name = name
        self.menu = res_menu

    def get_menu(self):
        return self.menu

    def get_name(self):
        return self.name


# open the browser
driver = webdriver.Safari()

url = "https://www.menicka.cz/moje-poloha.html?m=menicka&gps=49.210166676258375_16.599495697430932"
driver.get(url)

# get the page content
content = driver.page_source
soup = BeautifulSoup(content, features="html.parser")

# get the list of restaurants
restaurants = []
for restaurant in soup.findAll('div', attrs={'class': 'menicka_detail'}):
    # get the name of the restaurant
    restaurant_name = restaurant.find('div', attrs={'class': 'nazev'}).text
    # get menu for the restaurant
    # menu is nested in div "menicka_detail" -> div "menicka" -> div "nabidka_1 (or nabidka)" -> element i
    restaurant_menu_items = restaurant.find('div', attrs={'class': 'menicka'}).findAll('div', attrs={'class': 'nabidka_1' or 'nabidka'})
    prices = restaurant.find('div', attrs={'class': 'menicka'}).findAll('div', attrs={'class': 'cena'})
    week_menu = WeekMenu()

    mealIndex = 0
    for item in restaurant_menu_items:
        meal_item_name = item.text
        # remove possible HTML tags from meal_item_name
        price = prices[mealIndex].text
        week_menu.add_meal(Meal(meal_item_name, price, mealIndex))
        mealIndex += 1

    restaurants.append(Restaurant(restaurant_name, week_menu))

# print the menu for all restaurants
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue

    print ("------- RESTAURACE: "+ restaurant.get_name() +" --------")
    for meal in restaurant.get_menu().get_meals():
        # print in format "meal_index. meal_name - Cena: meal_price" if the meal_price is 0 or null, print ""
        price = meal.get_price()
        if price == "0" or price == "" or price == " " or price == " ":
            price = "0 Kč (nebo neuvedeno)"
        print(str(meal.day) + ". " + meal.name + " - Cena: " + price)
driver.quit()

# generate html file with menu, use utf-8 encoding and czech language
f = open("./html/menu.html", "w", encoding="utf-8")
f.write("<html><head><meta charset=\"utf-8\"></head><body>")
for restaurant in restaurants:
    # if restaurant has no menu, skip it
    if len(restaurant.get_menu().get_meals()) == 0:
        continue

    f.write("<h1>" + restaurant.get_name() + "</h1>")
    for meal in restaurant.get_menu().get_meals():
        # print in format "meal_index. meal_name - Cena: meal_price" if the meal_price is 0 or null, print ""
        price = meal.get_price()
        if price == "0" or price == "" or price == " " or price == " ":
            price = "0 Kč (nebo neuvedeno)"
        f.write("<p>" + str(meal.day) + ". " + meal.name + " - Cena: " + price + "</p>")
