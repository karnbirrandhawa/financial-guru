# adapted from 340 flask-starter-app

from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
from MySQLdb import IntegrityError

app = Flask(__name__)


# app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
# app.config["MYSQL_USER"] = "********"
# app.config["MYSQL_PASSWORD"] = "********"
# app.config["MYSQL_DB"] = "********"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# Routes
@app.route("/")
def home():
    return redirect("/accounts")


# Routes
@app.route("/error")
def error():
    return render_template("error.j2")


# route for accounts page
@app.route("/accounts", methods=["POST", "GET"])
def accounts():
    # Grab accounts data to send to template to display
    if request.method == "GET":
        query = "SELECT account_id AS id, \
                        account_name AS 'Account Name', \
                        account_number AS 'Account Number' \
                    FROM Accounts"

        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        return render_template("accounts.j2", data=data)

    # insert an account into the Accounts entity
    if request.method == "POST":
        # action when user presses the Add Account button
        if request.form.get("Add_Account"):
            account_name_input = request.form["name"]
            account_number_input = request.form["number"]

            # account for null account number
            if account_number_input == "":
                query = "INSERT INTO Accounts (account_name) VALUES (%s)"
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(query, (account_name_input,))
                except IntegrityError:
                    return redirect("/error")

                mysql.connection.commit()
                return redirect("/accounts")

            # no null inputs
            else:
                query = "INSERT INTO Accounts (account_name, account_number) \
                            VALUES (%s, %s)"
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(query, (account_name_input, account_number_input))
                except IntegrityError:
                    return redirect("/error")

                mysql.connection.commit()
                return redirect("/accounts")


@app.route("/delete_account", methods=["POST"])
def delete_account():
    if request.form.get("Delete_Account"):
        account_id_input = request.form["account"]
        query = "DELETE FROM Accounts WHERE account_id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (account_id_input,))
        mysql.connection.commit()

    return redirect("/accounts")


# route for household-members page
@app.route("/household-members", methods=["POST", "GET"])
def members():
    # Grab member data so we send it to our template to display
    if request.method == "GET":
        query = "SELECT member_id AS 'id', \
                        member_name AS 'Member Name' \
                    FROM Household_members \
                    ORDER BY member_id ASC"

        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        return render_template("household-members.j2", data=data)

    #  insert a member into the Household_members entity
    if request.method == "POST":
        # fire off if user presses the Add Member button
        if request.form.get("Add_Member"):
            # grab user form inputs
            member_name_input = request.form["name"]

            # account for null member input
            if member_name_input == "":
                query = "INSERT INTO Household_members (member_name) VALUES (%s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name_input,))
                mysql.connection.commit()

            # no null inputs
            else:
                query = "INSERT INTO Household_members (member_name) VALUES (%s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name_input,))
                mysql.connection.commit()

            # redirect back to household-members page
            return redirect("/household-members")


@app.route("/edit-household-members/", methods=["POST"])
def edit_household_members():

    # fire off if user clicks the 'Update Member' button
    if request.form.get("Update_Member"):
        # grab user form inputs
        member_id = request.form["member_id"]
        member_name = request.form["update_name"]

        query = "UPDATE Household_members \
                    SET member_name = %s \
                    WHERE member_id = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (member_name, member_id))
        mysql.connection.commit()

        # redirect back to members page after we execute the update query
        return redirect("/household-members")


# route for transactions page
@app.route("/transactions", methods=["POST", "GET"])
def transactions():
    # Grab transactions data to display
    if request.method == "GET":
        data_query = "SELECT date AS Date, description AS Description, Accounts.account_name AS 'Account Name', \
                        Budget_categories.category_name AS Category, \
                        CONCAT('$ ', FORMAT(amount, 2)) AS Amount \
                     FROM Transactions \
                 INNER JOIN Accounts ON Transactions.account_id=Accounts.account_id \
                 INNER JOIN Budget_categories ON Transactions.category_id = Budget_categories.category_id \
                 ORDER BY date DESC;"
        cur = mysql.connection.cursor()
        cur.execute(data_query)
        data = cur.fetchall()

        # populate account dropdown
        account_query = "SELECT account_id, account_name \
                            FROM Accounts \
                            ORDER BY account_name;"
        cur = mysql.connection.cursor()
        cur.execute(account_query)
        account_data = cur.fetchall()

        # populate categories dropdown
        category_query = "SELECT category_id, category_name \
                            FROM Budget_categories \
                            ORDER BY category_name;"
        cur = mysql.connection.cursor()
        cur.execute(category_query)
        category_data = cur.fetchall()

        return render_template("transactions.j2", data=data, account_data=account_data, category_data=category_data)

    # insert a transaction into the Transactions entity
    if request.method == "POST":
        # action when the Add Transaction button is pressed
        if request.form.get("Add_Transaction"):
            transaction_date_input = request.form["date"]
            transaction_description_input = request.form["description"]
            transaction_account_input = request.form["account"]
            transaction_category_input = request.form["category"]
            transaction_amount_input = request.form["amount"]

            # account for null account input
            if transaction_account_input == "Null":
                return redirect("/error")

            # account for null category input
            elif transaction_category_input == "Null":
                return redirect("/error")

            # no null inputs
            else:
                query = "INSERT INTO Transactions (date, description, account_id, category_id, amount) \
                             VALUES (%s, %s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (transaction_date_input, transaction_description_input, transaction_account_input,
                                    transaction_category_input, transaction_amount_input))
                mysql.connection.commit()

            # redirect back to transactions page
            return redirect("/transactions")


# route for categories page
@app.route("/categories", methods=["POST", "GET"])
def categories():
    # Grab category data so we send it to our template to display
    if request.method == "GET":
        query = "SELECT category_id AS id, \
                        category_name AS 'Category Name', \
                        CONCAT('$ ', FORMAT(category_budget, 2)) AS 'Budget Amount' \
                    FROM Budget_categories"

        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        return render_template("categories.j2", data=data)

    # insert an account into the Budget_categories entity
    if request.method == "POST":
        # fire off if user presses the Add Category button
        if request.form.get("Add_Category"):
            # grab user form inputs
            category_name_input = request.form["name"]
            category_budget_input = request.form["number"]

            # account for null account number
            if category_budget_input == "":
                query = "INSERT INTO Budget_categories (category_name) VALUES (%s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (category_name_input,))
                mysql.connection.commit()

            # no null inputs
            else:
                query = "INSERT INTO Budget_categories (category_name, category_budget) \
                            VALUES (%s, %s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (category_name_input, category_budget_input))
                mysql.connection.commit()

            # redirect back to accounts page
            return redirect("/categories")


@app.route("/delete_category", methods=["POST"])
def delete_category():
    if request.form.get("Delete_Category"):
        category_id_input = request.form["category"]
        query = "DELETE FROM Budget_categories WHERE category_id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (category_id_input,))
        mysql.connection.commit()

    return redirect("/categories")


# route for household-member-accounts page
@app.route("/household-members-accounts", methods=["POST", "GET"])
def member_accounts():
    # Grab household-members-accounts data to display
    if request.method == "GET":
        data_query = ("SELECT Household_members_accounts.household_members_accounts as ID, \
                      Accounts.account_name AS Account, Household_members.member_name AS Member \
                            FROM Household_members_accounts \
                        INNER JOIN Accounts ON Household_members_accounts.account_id=Accounts.account_id \
                        INNER JOIN Household_members ON \
                            Household_members_accounts.member_id = Household_members.member_id;")
        cur = mysql.connection.cursor()
        cur.execute(data_query)
        data = cur.fetchall()

        # populate account dropdown
        account_query = "SELECT account_id, account_name \
                            FROM Accounts \
                         ORDER BY account_name;"
        cur = mysql.connection.cursor()
        cur.execute(account_query)
        account_data = cur.fetchall()

        # populate member dropdown
        member_query = "SELECT member_id, member_name \
                            FROM Household_members \
                         ORDER BY member_name;"
        cur = mysql.connection.cursor()
        cur.execute(member_query)
        member_data = cur.fetchall()

        member_account_query = "SELECT household_members_accounts \
                                    FROM Household_members_accounts;"
        cur = mysql.connection.cursor()
        cur.execute(member_account_query)
        member_account_data = cur.fetchall()

        return render_template(
            "household-members-accounts.j2", data=data, account_data=account_data,
            member_data=member_data, member_account_data=member_account_data)

    # insert a household-members-accounts row
    if request.method == "POST":
        # if user presses the Assign button
        if request.form.get("Add_Assignment"):
            account_input = request.form["account"]
            household_member_input = request.form["member"]

            # account for null account inputs
            if account_input == "Null":
                return redirect("/error")

            # account for null member inputs
            elif household_member_input == "Null":
                return redirect("/error")

            # no null inputs
            else:
                query = "INSERT INTO Household_members_accounts (account_id, member_id) \
                            VALUES (%s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (account_input, household_member_input))
                mysql.connection.commit()

            # redirect back to transactions page
            return redirect("/household-members-accounts")


@app.route("/edit-member-account", methods=["POST"])
def edit_member_account():

    if request.form.get("Edit_Member_Account"):
        account_member_id_input = request.form["account_member"]
        account_input = request.form["account"]
        member_input = request.form["member"]

        if account_member_id_input == "Null" or account_input == "Null" or member_input == "Null":
            return redirect("/error")

        query = ("UPDATE Household_members_accounts \
                    SET account_id = %s, member_id = %s \
                    WHERE household_members_accounts = %s;")
        cur = mysql.connection.cursor()
        cur.execute(query, (account_input, member_input, account_member_id_input,))
        mysql.connection.commit()

    return redirect("/household-members-accounts")


@app.route("/delete_member_account", methods=["POST"])
def delete_member_account():
    if request.form.get("Delete_Member_Account"):

        account_member_input = request.form["account_member"]

        # handle null id inputs
        if account_member_input == "Null":
            return redirect("/error")

        query = "DELETE FROM Household_members_accounts \
                    WHERE Household_members_accounts = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (account_member_input,))
        mysql.connection.commit()

        return redirect("/household-members-accounts")


# Listener
# change the port number if deploying on the flip servers
# app is displaying on http://flip2.engr.oregonstate.edu:50121 when on the VPN and using above credentials  
if __name__ == "__main__":
    app.run(port=50121, debug=True)
