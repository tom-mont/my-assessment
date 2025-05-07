"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)


NOTE:
Each question in this section is isolated, for example, you do not need to consider how Q5 may affect Q4.
Remember to clean your data.

"""


def question_1():
    # Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    # Return the `Name`, `Surname` and `CustomerID`

    qry = """____________________"""
    # deleteing starts here
    qry = """
    SELECT Name, Surname, CustomerID
    FROM CUSTOMERS
    GROUP BY Name, Surname, CustomerID
    HAVING COUNT(*) > 1;
    """

    # deleteing ends here

    return qry


def question_2():
    # Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income

    qry = """____________________"""
    # deleteing starts here
    qry = """SELECT Name, Surname, Income
             FROM (SELECT DISTINCT * FROM customers)
             WHERE Gender = 'Female'
             ORDER BY CustomerID, Income DESC;"""
    # deleteing ends here

    return qry


def question_3():
    # Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    # ie 50 not 0.5
    # There is only 1 loan per customer ID.

    qry = """____________________"""
    # deleteing starts here
    qry = """SELECT LoanTerm, 
             (SUM(CASE WHEN ApprovalStatus = 'Approved' THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS ApprovalPercentage,
             FROM (SELECT DISTINCT * FROM loans)
             GROUP BY LoanTerm"""
    # deleteing ends here

    return qry


def question_4():
    # Return a breakdown of the number of customers per CustomerClass in the credit data
    # Return columns `CustomerClass` and `Count`

    qry = """____________________"""
    # deleteing starts here
    qry = """SELECT CustomerClass, COUNT(DISTINCT CustomerID) as Count 
             FROM (SELECT DISTINCT * FROM credit)
             GROUP BY CustomerClass"""
    # deleteing ends here

    return qry


def question_5():
    # Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.

    qry = """____________________"""
    # deleteing starts here
    qry = """UPDATE credit SET CustomerClass = 'C' WHERE CreditScore BETWEEN 600 AND 650;"""
    # deleteing ends here

    return qry
