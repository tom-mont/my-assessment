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
    """
    Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    Return the `Name`, `Surname` and `CustomerID`
    """

    qry = """  
        -- we use a select distinct so that only one 
        -- row is returned per duplicated customer id:
        select distinct name, surname, customerid
        from customers
        where customerid in 
            -- subquery to identify duplicates:
            (
            select customerid
            from customers
            group by customerid
            having count(*) > 1
            )
    """

    return qry


def question_2():
    """
    Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income
    """

    qry = """  
    -- We know there are duplicates in this table, hence we use a select distinct
        select distinct name, surname, income
        from customers
        where gender = 'Female'
        order by income desc
    """

    return qry


def question_3():
    """
    Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    ie 50 not 0.5
    There is only 1 loan per customer ID.
    """

    qry = """
        -- for the calculation we determine the total approved loans in the numerator 
        -- and divide this by total loans in the denominator. We use distinct customerids 
        -- as there should only be 1 loan per customer id
        select
            (select count(distinct customerid) from loans where approvalstatus = 'Approved')
            /count(distinct customerid)
        from loans
    """

    return qry


def question_4():
    """
    Return a breakdown of the number of customers per CustomerClass in the credit data
    Return columns `CustomerClass` and `Count`
    """

    qry = """
        -- there are duplicate customerids, we deduplicate using count distinct:
        select customerclass, count(distinct customerid) as count
        from credit
        group by customerclass
    """

    return qry


def question_5():
    """
    Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.
    """

    qry = """  
        update credit
        set customerclass = 'C'
        -- "between" is inclusive of both the lower and upper bounds:
        where creditscore between 600 and 650
    """

    return qry
