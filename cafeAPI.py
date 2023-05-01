###############################################################################
# {Description du programme}
###############################################################################
# Auteur: {auteur}
# Copyright: Copyright {année}, {nom_du_projet}
# Licence: {licence[MIT,GNU GPL,Apache License 2.0,ISC,BSD]}
# Version: {majeur}.{mineur}.{patch}
# Date: {date_dernier_changement}
# Email: {contact_email}
###############################################################################

# Déclaration des imports et dépendances
# import requests

from datetime import date
import json
import re

# Déclaration des variables globales, constantes

ACCOUNTS_PATH = "data\comptes.csv"
ORDERS_PATH = "data\commandes.csv"
MENU_PATH = "data\menu.json"

# Public requests
GET_ITEMS_REQUEST_BY_CATEGORY_REGEX = re.compile(r'GET /api/menu/\w*/items')
GET_ITEMS_REQUEST_BY_ID_REGEX = re.compile(r'GET /api/menu/items/\w*')
POST_ORDERS_REQUEST = re.compile(r'POST /api/commandes (\w+x\w+)')

# Staff requests
GET_ORDERS_BY_ID_REGEX = re.compile(r'GET /api/commandes/\w+')
PUT_ITEMS_BY_ID_REGEX = re.compile(r'PUT /api/menu/items/\w+ disponible=\w+')

# Admin requests
GET_ACCOUNTS_BY_ID = re.compile(r'GET /api/comptes/\w+')
PUT_ACTIVITY_BY_ID = re.compile(r'PUT /api/comptes/\w+')

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
    try:
        with open(MENU_PATH, "rb") as data:
            return json.load(data)
    except:
        print("Une erreur est survenue lors de l’ouverture du fichier.")


def get_orders_data():
    try:
        with open(ORDERS_PATH) as data:
            content = data.read().splitlines()
    except:
        print("Une erreur est survenue lors de l’ouverture du fichier.")

    orders = []
    for order_unsplit in content:
        order_split = order_unsplit.split(" | ")
        items_bought = []
        order_split_split = order_split[2].split(", ")
        for item in order_split_split:
            items = item.split("x")
            items_bought.append(items)

        current_order = {
            "id": order_split[0],
            "customer_serial_number": order_split[1],
            "items_bought": items_bought,
            "purchase_date": order_split[3],
            "price_total": order_split[4]
        }
        orders.append(current_order)

    return orders


def get_accounts_data():
    try:
        with open(ACCOUNTS_PATH) as data:
            content = data.read().splitlines()
    except:
        print("Une erreur est survenue lors de l’ouverture du fichier.")

    accounts = []
    for account_unsplit in content:
        account_split = account_unsplit.split(" | ")
        current_account = {
            "serial_number": account_split[0],
            "second_name": account_split[1],
            "first_name": account_split[2],
            "password": account_split[3],
            "email": account_split[4],
            "role": account_split[5],
            "activity": account_split[6]
        }
        accounts.append(current_account)

    return accounts


def verify_account(serial_number, password):
    accounts = get_accounts_data()
    for account in accounts:
        if serial_number == account["serial_number"] and password == account["password"] and int(account["activity"]) == 1:
            user_role = account["role"]
            return True, user_role
    return False, None


def authentification(user_serial_number=None, user_password=None):
    if user_serial_number == None:
        user_serial_number = get_user_serial_number()
    if user_password == None:
        user_password = get_user_password()

    account_validity, user_role = verify_account(
        user_serial_number, user_password)

    if account_validity:
        print(f"Connecté en tant que {user_serial_number}.")
        return True, user_serial_number, user_role
    return False, None, None


def get_all_items(menu=get_menu_data()):
    items = []
    for value in menu.values():
        if isinstance(value, list):
            for i in value:
                items.append(i)
        else:
            items.extend(get_all_items(value))
    return items


def print_items(items):
    for item in items:
        item_id = item['id']
        item_name = item['nom']
        print(item_id, item_name)


def request_items(item_id=None, category=None, menu=get_menu_data()):
    if item_id is None and isinstance(menu, dict):
        for key, value in menu.items():
            if category is None:
                print_items(get_all_items())
            elif key == category:
                print_items(get_all_items(value))
                break
            else:
                request_items(category=category, menu=value)
    else:
        for item in get_all_items():
            if item['id'] == item_id:
                item_name = item['nom']
                item_price = item['prix']
                item_availability = item['disponible']
                print(
                    f'nom: {item_name}\nprix: {item_price}\ndispo: {item_availability}')
                break


def request_orders(user_role, order_id_=None):
    if user_role.strip() in ["staff", "admin"]:

        orders = get_orders_data()
        all_items = get_all_items()

        if order_id_ is None:
            for order in orders:
                order_id = order['id']
                order_date = order['purchase_date']
                order_total = order['price_total']
                print(
                    f'id: {order_id} | date achat: {order_date} | prix total: {order_total}$')
        else:
            order_items = ""
            for order in orders:
                if order['id'].strip() == order_id_:
                    order_date = order['purchase_date']
                    order_total = order['price_total'].strip()
                    for i, item_bought in enumerate(order['items_bought']):
                        for item in all_items:
                            if item['id'] == int(item_bought[0]):
                                if i == len(order['items_bought'])-1:
                                    order_items += item['nom'] + \
                                        " x" + item_bought[1]
                                else:
                                    order_items += item['nom'] + \
                                        " x" + item_bought[1] + ", "
                                break
                    print(
                        f'items: {order_items} | date achat: {order_date} | prix total: {order_total}$')
                break
    else:
        print("Vous n'avez pas les droits pour cette requête.")


def post_orders(items_, user_serial_number):
    orders = get_orders_data()
    all_items = get_all_items()

    with open(ORDERS_PATH, "a") as file:

        items = ""
        total_price = 0
        for i, item in enumerate(items_):
            item_split = item.split("x")
            item_id = item_split[0]
            item_quantity = item_split[1]
            for item_2 in all_items:
                if item_2['id'] == int(item_id):
                    total_price += int(item_quantity) * item_2['prix']
                    break
            if i == len(items_)-1:
                items += item
            else:
                items = item + ", "
        last_order_id = orders[-1]['id']

        formatted_total_price = "{:.2f}".format(round(total_price, 2))

        try:
            file.write(
                f"\n{int((last_order_id).strip())+1}  | {user_serial_number} | {items} | {date.today()} | {formatted_total_price}")
        except:
            print("Une erreur est survenue lors de la modification du fichier.")


def update_item(user_role, item_id, dispo):
    if user_role in ["staff", "admin"]:

        all_items = get_all_items()

        for item in all_items:
            if int(item_id) == item['id']:

                if int(dispo) == 1:
                    item['disponible'] = True
                if int(dispo) == 0:
                    item['disponible'] = False

                break
    else:
        print("Vous n'avez pas les droits pour cette requête.")


def request_accounts(user_role, user_id=None):
    if user_role.strip() == "admin":

        accounts = get_accounts_data()

        for account in accounts:

            account_serial_number = account['serial_number'].strip()
            account_second_name = account['second_name'].strip()
            account_first_name = account['first_name'].strip()
            account_password = account['password'].strip()
            account_email = account['email'].strip()
            account_role = account['role'].strip()
            account_activity = account['activity'].strip()

            if user_id is None:

                print(f"matricule: {account_serial_number} | nom: {account_second_name} | prénom: {account_first_name} | password: {account_password} | email: {account_email} | role: {account_role} | activité: {account_activity}")

            elif user_id == account_serial_number:

                print(f"matricule: {account_serial_number} | nom: {account_second_name} | prénom: {account_first_name} | password: {account_password} | email: {account_email} | role: {account_role} | activité: {account_activity}")

                break

    else:
        print("Vous n'avez pas les droits administrateurs.")


def type_request(request):
    if GET_ITEMS_REQUEST_BY_CATEGORY_REGEX.search(request) is not None:
        return "get_items_by_category"
    if GET_ITEMS_REQUEST_BY_ID_REGEX.search(request) is not None:
        return "get_items_by_id"
    if POST_ORDERS_REQUEST.search(request) is not None:
        return "post_orders"
    if GET_ORDERS_BY_ID_REGEX.search(request) is not None:
        return "get_orders_by_id"
    if PUT_ITEMS_BY_ID_REGEX.search(request) is not None:
        return "put_items_by_id"
    if GET_ACCOUNTS_BY_ID.search(request) is not None:
        return "get_accounts_by_id"
    if PUT_ACTIVITY_BY_ID.search(request) is not None:
        return "put_activity_by_id"
    if request == "FIN":
        return "FIN"
    if request == "GET /api/commandes":
        return "get_orders"
    if request == "GET /api/menu/items":
        return "get_items"
    if request == "GET /api/comptes":
        return "get_accounts"
    else:
        return "invalid"


def tests():
    pass


def main():
    authenticated, user_serial_number, user_role = authentification(
        "20250710", "rlPass_30")

    while authenticated:
        request = input()
        request_split = request.split("/")

        match type_request(request):

            # ADMIN REQUESTS
            case "get_accounts":
                request_accounts(user_role=user_role)

            case "get_accounts_by_id":
                request_accounts(user_role, request_split[3])

            case "put_activity_by_id":
                print("put_activity_by_id")

            # STAFF REQUESTS
            case "get_orders":
                request_orders(user_role)

            case "get_orders_by_id":
                request_orders(user_role, request_split[3])

            case "put_items_by_id":
                id_and_dispo = request_split[4].split(" ")
                item_id = id_and_dispo[0]
                dispo = id_and_dispo[1].split("=")[1]
                update_item(user_role, item_id, dispo)

            # STANDARD REQUESTS
            case "get_items":
                request_items()

            case "get_items_by_category":
                request_items(category=request_split[3])

            case "get_items_by_id":
                request_items(item_id=int(request_split[4]))

            case "post_orders":
                items_and_quantities = request_split[2].split(" ")[1:]
                post_orders(items_and_quantities, user_serial_number)

            case "FIN":
                authenticated = False

            case "invalid":
                print("Not a valid request.")


# Déclaration du code principal et Affichage

main()

#################################################################################
# Tests (optionnel)
#################################################################################

tests()
