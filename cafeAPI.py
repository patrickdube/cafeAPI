###############################################################################
## Programme qui simule une version simplifiée d'un API pour un café étudiant.
###############################################################################
## Auteurs: Patrick Dubé, Johann Sourou
## Copyright: Copyright 2023, cafeAPI_20031977_20227958.py
## Version: 1.0.0
## Date: 01/05/23
## Email: patrick.dube.3@umontreal.ca
###############################################################################

# Déclaration des imports et dépendances

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
PUT_ACTIVITY_BY_ID = re.compile(r'PUT /api/comptes/\w+ \[[0-1]\]')

# Déclaration des fonctions internes et calculs
# avec commentaires détaillés nécessaires seulement (optionnel)

"""Cette fonction retourne une str qui représente le matricule de l'usager.

    Returns:
        str: matricule entré par l'usager.
    """
def get_user_serial_number():
    serial_number = input("Entrez votre matricule: ")
    while not serial_number.isdecimal() or len(serial_number) > 8:
        print("Format de matricule invalide.")
        serial_number = input("Entrez votre matricule: ")
    return serial_number

"""Cette fonction retourne une str qui représente le password de l'usager.

    Returns:
        str: password entré par l'usager.
    """
def get_user_password():
    password = input("Entrez votre mot de passe: ")
    return password

"""Cette fonction retourne un BufferedReader qui représente le menu contenu dans le fichier menu.json.

    Returns:
        BufferedReader: menu chargé par le module json.
    """
def get_menu_data():
    try:
        with open(MENU_PATH, "rb") as data:
            return json.load(data)
    except:
        print("Une erreur est survenue lors de l’ouverture du fichier.")

"""Cette fonction retourne une liste qui contient toutes les commandes du fichier commandes.csv.

    Returns:
        list[str]: liste de commandes.
    """
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

"""Cette fonction retourne une liste qui contient tous les comptes du fichier comptes.csv.

    Returns:
        list[str]: liste de comptes.
    """
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


"""Cette fonction retourne un booléen qui indique si le compte est valide (actif et la combinaison de matricule et password est valide),
    puis retourne le role de l'usager en vérification.

    Args:
        serial_number (str): Matricule de l'usager.
        password (str): Password de l'usager.
    Returns:
        bool: Booléen qui dit si le compte est valide ou non.
        str: str qui indique le role de l'usager.
    """
def verify_account(serial_number, password):
    accounts = get_accounts_data()
    for account in accounts:
        if serial_number == account["serial_number"] and password == account["password"] and int(account["activity"]) == 1:
            user_role = account["role"].strip()
            return True, user_role
    return False, None

"""Cette fonction retourne un booléen qui indique si le compte est connecté, 
    un str qui indique le matricule de l'usager et un autre str qui indique son role.

    Args:
        serial_number (str): Matricule de l'usager.
        user_password (str): Password de l'usager.
    Returns:
        bool: Booléen qui dit si le compte est valide ou non.
        str: str qui indique le matricule de l'usager.
        str: str qui indique le role de l'usager.
    """
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

"""Cette fonction récursive retourne une liste qui contient tous les items que l'on peut retrouver dans le menu (par défaut menu.json).

    Args:
        menu (BufferedReader): menu provenant par défaut du fichier menu.json.
    Returns:
        list: liste qui contient tous les items que l'on peut retrouver dans le menu.
    """
def get_all_items(menu=get_menu_data()):
    items = []
    for value in menu.values():
        if isinstance(value, list):
            for i in value:
                items.append(i)
        else:
            items.extend(get_all_items(value))
    return items

"""Cette fonction affiche tous les items d'une liste donnée.

    Args:
        items (list): liste d'items à afficher.
    """
def print_items(items):
    for item in items:
        item_id = item['id']
        item_name = item['nom']
        print(item_id, item_name)

"""Cette fonction récursive affiche:
                1. Tous les items du menu si item_id = None.
                2. Les informations de l'item ayant item_id comme id.
                3. Tous les items de la catégorie mentionnée (category) du menu.

    Args:
        item_id (str): liste d'items à afficher.
        menu (any) (BufferedReader par défaut): menu contenant les items.
    """
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

"""Cette fonction affiche seulement si l'usager est staff ou admin:
                1. Toutes les commandes du fichier commandes.csv.
                2. Les informations de la commande ayant order_id_ comme id.

    Args:
        user_role (str): role de l'usager.
        order_id_ (str): identifiant de la commande.
    """
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

"""Cette fonction ajoute une commande au fichier commandes.csv.

    Args:
        items_ (list[str]): liste contenant les items et leur quantité à ajouter.
        user_serial_number (str): matricule de l'usager qui fait la commande.
    """
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

"""Cette fonction modifie la disponibilité d'un item seulement si l'usager est staff ou admin

    Args:
        user_role (str): role de l'usager.
        item_id (str): identifiant de l'item à modifier.
        dispo (str): nouvelle disponibilité de l'item.
    """
def update_item(user_role, item_id, dispo):
    if user_role.strip() in ["staff", "admin"]:

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

"""Cette fonction affiche seulement si l'usager est admin:
                1. Tous le comptes du fichier comptes.csv.
                2. Toutes les informations du compte ayant user_id comme matricule.

    Args:
        user_role (str): role de l'usager.
        user_id (str): matricule du compte à afficher.
    """
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

"""Cette fonction modifie l'activité d'un compte selon son matricule seulement si l'usager est admin.

    Args:
        user_role (str): role de l'usager.
        account_id (str): matricule du compte à modifier.
        activity (str): valeur qui vient modifier la section activité du compte.
    """
def update_account(user_role, account_id, activity):

    if user_role.strip() == "admin":

        accounts = get_accounts_data()

        with open(ACCOUNTS_PATH, "r+") as file:

            try:
                file.truncate(0)

            except:
                print("Erreur de modification du fichier.")

            for account in accounts:

                account_serial_number = account['serial_number']
                account_second_name = account['second_name']
                account_first_name = account['first_name']
                account_password = account['password']
                account_email = account['email']
                account_role = account['role']

                if account_id == account['serial_number']:
                    account['activity'] = activity

                account_activity = account['activity']

                try:

                    file.write(
                        f"{account_serial_number} | {account_second_name} | {account_first_name} | {account_password} | {account_email} | {account_role} | {account_activity}\n")

                except:
                    print("Erreur de modification du fichier.")

"""Cette fonction prend un str ou un regex et retourne un str approprié qui sera utilisé pour un match case.

    Args:
        request (str): role de l'usager.

    Returns:
        str: version str de la requête qui va passer dans le match case.
    """
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
    test_verify_account()
    test_type_request()
    test_authentification()

def test_verify_account():
    assert verify_account("20031977", "pdPass_17") == (True, "public"), "Combinaison valide, user_role = public."
    assert verify_account("20031977", "asdasds") == (False, None), "Password n'existe pas, user_role = None."
    assert verify_account("20458102", "pdPass_17") == (False, None), "Combinaison invalide (matricule et password existent), user_role = None."
    assert verify_account("93852095723053", "pdPass_17") == (False, None), "Matricule n'existe pas, user_role = None."
    assert verify_account("93852095723053", "1111123123") == (False, None), "Matricule et password n'existent pas."

def test_type_request():
    assert type_request("GET /api/comptes") == "get_accounts", "GET /api/comptes mal détecté."
    assert type_request("GET /api/comptes/20238163") == "get_accounts_by_id", "GET /api/comptes/matricule mal détecté."
    assert type_request("PUT /api/menu/items/3 disponible=0") == "put_items_by_id", "PUT /api/menu/items/id disponible mal détecté."
    assert type_request("POST /api/commandes 3x1 4x2") == "post_orders", "POST /api/commandes mal détecté."
    assert type_request("GET /api/menu/cafe/items") == "get_items_by_category", "GET /api/menu/categorie/items mal détecté."

def test_authentification():
    assert authentification("20031977", "pdPass_17") == (True, "20031977", "public"), "Combinaison valide."
    assert authentification("20031977", "asdasds") == (False, None, None), "Password n'existe pas."
    assert authentification("20458102", "pdPass_17") == (False, None, None), "Combinaison invalide (matricule et password existent)."
    assert authentification("93852095723053", "pdPass_17") == (False, None, None), "Matricule n'existe pas."
    assert authentification("93852095723053", "1111123123") == (False, None, None), "Matricule et password n'existent pas."

def main():
    authenticated, user_serial_number, user_role = authentification("20458102", "rlPass_30")

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
                account_id = request_split[3].split(" ")[0]
                activity = request_split[3].split(" ")[1].strip("[").strip("]")
                update_account(user_role, account_id, activity)

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

# tests()
