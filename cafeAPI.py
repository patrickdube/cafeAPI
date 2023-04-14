###############################################################################
## {Description du programme}
###############################################################################
## Auteur: {auteur}
## Copyright: Copyright {année}, {nom_du_projet}
## Licence: {licence[MIT,GNU GPL,Apache License 2.0,ISC,BSD]}
## Version: {majeur}.{mineur}.{patch}
## Date: {date_dernier_changement}
## Email: {contact_email}
###############################################################################

# Déclaration des imports et dépendances
#import requests
import os
import json

# Déclaration des variables globales, constantes
ACCOUNTS_PATH = "data\comptes.csv"
ORDERS_PATH = "data\commandes.csv"
MENU_PATH = "data\menu.json"

# Déclaration des fonctions internes et calculs 
# avec commentaires détaillés nécessaires seulement (optionnel)
def get_user_serial_number():
    serial_number = input("Entrez votre matricule: ")
    while not serial_number.isdecimal() or len(serial_number) > 8:
        print("Format de matricule invalide.")
        serial_number = input("Entrez votre matricule: ")
    return serial_number

def get_user_password():
    password = input("Entrez votre mot de passe: ")
    return password

def get_menu_data():
    with open(MENU_PATH, "rb") as data:
        return json.load(data)

def get_orders_data():
    with open(ORDERS_PATH) as data:
        content = data.read().splitlines()
    
    orders = []
    for order_unsplit in content:
        order_split = order_unsplit.split(" | ")
        items_bought = []
        for item in order_split[2]:
            items = item.split(", ")
            for _ in items:
                items = items.split("x")
                items_bought.append(items)
        
        current_order = {
            "id" : order_split[0],
            "customer_serial_number" : order_split[1],
            "items_bought" : items_bought,
            "purchase_date" : order_split[3],
            "price_total" : order_split[4]
        }
        orders.append(current_order)

    return orders

def get_accounts_data():
    with open(ACCOUNTS_PATH) as data:
        content = data.read().splitlines()

    accounts = []
    for account_unsplit in content:
        account_split = account_unsplit.split(" | ")
        current_account = {
            "serial_number" : account_split[0],
            "second_name" : account_split[1],
            "first_name" : account_split[2],
            "password" : account_split[3],
            "email" : account_split[4],
            "role" : account_split[5],
            "activity" : account_split[6]
        }
        accounts.append(current_account)
    
    return accounts

def verify_account(serial_number, password):
    accounts = get_accounts_data()
    for account in accounts:
        if serial_number == account["serial_number"] and password == account["password"]:
            return True
    return False

def authentification(user_serial_number=None, user_password=None):
    if user_serial_number == None:
        user_serial_number = get_user_serial_number()
    if user_password == None:
        user_password = get_user_password()
    if verify_account(user_serial_number, user_password):
        authenticated = True
    else:
        authenticated = False
    return authenticated

def request_items():
    menu = get_menu_data()

    
    
    pass

def request_category_items(category):
    pass

def main():
    authenticated = authentification()

    while authenticated:
        request = input()
        request_split = request.split("/")
        
        #if request_split[3] in 

        match request:
            case "GET /api/menu/items":
                request_items()

            case "FIN":
                authenticated = False
            
            case _:
                print("Not a valid request.")

#def request_
# Déclaration du code principal et Affichage
main()

#################################################################################
# Tests (optionnel)
#################################################################################