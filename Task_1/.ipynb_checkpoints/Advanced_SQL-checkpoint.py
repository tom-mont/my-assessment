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
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """  
        -- we first need to dedupe the data as both tables contain 
        -- duplicate customer ids
        with customers_deduped as (
            select *
            from customers
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        -- credit table also contains customerid duplicates and needs to be deduped
        credit_deduped as (
            select *
            from credit
            qualify row_number() over (partition by customerid order by customerid) = 1
        )
        select 
            credit_deduped.CustomerClass
            ,avg(customers_deduped.income) as AverageIncome
        from credit_deduped
        left join customers_deduped
            on customers_deduped.customerid = credit_deduped.customerid
        group by credit_deduped.customerclass
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """  
        -- we first need to dedupe the data as both tables contain 
        -- duplicate customer ids. Here we will also ensure consistent
        -- naming of the provinces
        with customers_deduped as (
            select 
                *
                -- Ensure province naming is consistent:
                ,case when region in ('NC', 'NorthernCape') then 'NorthernCape'
                    when region in ('EC', 'EasternCape') then 'EasternCape'
                    when region in ('WC', 'WesternCape') then 'WesternCape'
                    when region in ('FS', 'FreeState') then 'FreeState'
                    when region in ('GT', 'Gauteng') then 'Gauteng'
                    when region in ('LP', 'Limpopo') then 'Limpopo'
                    when region in ('NW', 'NorthWest') then 'NorthWest'
                    when region in ('KZN', 'KwaZulu-Natal') then 'KwaZulu-Natal'
                    when region in ('MP', 'Mpumalanga') then 'KwaZulu-Natal'
                    end
                as province
            from customers
        -- Deduplication of customers:
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        rejected_loans_deduped as (
            select *
            from loans
            where approvalstatus = 'Rejected'
        -- there are duplicate customer IDs in the loan table, hence need to be deduped:
            qualify row_number() over (partition by customerid order by customerid) = 1
        )
        select 
            customers_deduped.province as Province
            ,count(*) as RejectedApplications
        from customers_deduped
        left join rejected_loans_deduped
            on customers_deduped.customerid = rejected_loans_deduped.customerid
        group by customers_deduped.province
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
        create or replace table financing (
            CustomerID INT
            ,Income INT
            ,LoanAmount INT
            ,LoanTerm INT
            ,InterestRate FLOAT
            ,ApprovalStatus VARCHAR(100)
            ,CreditScore INT
        );

        insert into financing (
            CustomerID
            ,Income
            ,LoanAmount
            ,LoanTerm
            ,InterestRate
            ,ApprovalStatus
            ,CreditScore
        )
        with customers_deduped as (
            select *
            from customers
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        loans_deduped as (
            select *
            from loans
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        -- credit table also contains customerid duplicates and needs to be deduped
        credit_deduped as (
            select *
            from credit
            qualify row_number() over (partition by customerid order by customerid) = 1
        )
        select 
            customers_deduped.customerid as CustomerID
            ,customers_deduped.income as Income
            ,loans_deduped.loanamount as LoanAmount
            ,loans_deduped.loanterm as LoanTerm
            ,loans_deduped.interestrate as InterestRate
            ,loans_deduped.approvalstatus as ApprovalStatus
            ,credit_deduped.creditscore as CreditScore
        from customers_deduped
        left join loans_deduped
            on customers_deduped.customerid = loans_deduped.customerid
        left join credit_deduped
            on customers_deduped.customerid = credit_deduped.customerid
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    qry = """
        create or replace table timeline (
            CustomerID INT
            ,MonthName varchar(100)
            ,NumberOfRepayments INT
            ,AmountTotal INT
        );

        insert into timeline (CustomerID, MonthName, NumberOfRepayments, AmountTotal)
        with customers_deduped as (
            select *
            from customers
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        -- Below 
        repayments_london_conversion as (
            select
                customerid
                ,repaymentdate at time zone timezone at time zone 'Europe/London' as london_time
                ,extract(hour from london_time) as london_hour
                ,extract(month from london_time) as london_month
                ,amount
            from repayments
        -- Repayments should only occur between 6am and 6pm London Time:
            where london_hour between 6 and 17
        ),
        repayments_per_month as (
            select 
                customerid
                ,london_month
                ,count(*) as numberofrepayments
                ,sum(amount) as amounttotal
            from repayments_london_conversion
            group by customerid, london_month
        ),
        customer_months as (
            select 
                customers_deduped.customerid
                ,months.monthname
                ,months.monthid
            from customers_deduped
            cross join months
        )
        select 
            customer_months.customerid
            ,customer_months.monthname as MonthName
        -- If a customer does not make a repayment the repayments_per_month will fail to join 
        -- and the value for NumberOfRepayments and AmountTotal will be null. We coalesce this 
        -- to 0 to represent that a payment has not been made:
            ,coalesce(repayments_per_month.numberofrepayments, 0) as NumberOfRepayments
            ,coalesce(repayments_per_month.amounttotal, 0) as AmountTotal
        from customer_months
        left join repayments_per_month
            on customer_months.monthid = repayments_per_month.london_month
            and customer_months.customerid = repayments_per_month.customerid
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
        select
            CustomerId
            ,cast(sum(case when monthname = 'January' then numberofrepayments else 0 end) as int)
            as JanuaryRepayments
            ,cast(sum(case when monthname = 'January' then amounttotal else 0 end) as int)
            as JanuaryTotal
            ,cast(sum(case when monthname = 'February' then numberofrepayments else 0 end) as int)
            as FebruaryRepayments
            ,cast(sum(case when monthname = 'February' then amounttotal else 0 end) as int)
            as FebruaryTotal
            ,cast(sum(case when monthname = 'March' then numberofrepayments else 0 end) as int)
            as MarchRepayments
            ,cast(sum(case when monthname = 'March' then amounttotal else 0 end) as int)
            as MarchTotal
            ,cast(sum(case when monthname = 'April' then numberofrepayments else 0 end) as int)
            as AprilRepayments
            ,cast(sum(case when monthname = 'April' then amounttotal else 0 end) as int)
            as AprilTotal
            ,cast(sum(case when monthname = 'May' then numberofrepayments else 0 end) as int)
            as MayRepayments
            ,cast(sum(case when monthname = 'May' then amounttotal else 0 end) as int)
            as MayTotal
            ,cast(sum(case when monthname = 'June' then numberofrepayments else 0 end) as int)
            as JuneRepayments
            ,cast(sum(case when monthname = 'June' then amounttotal else 0 end) as int)
            as JuneTotal
            ,cast(sum(case when monthname = 'July' then numberofrepayments else 0 end) as int)
            as JulyRepayments
            ,cast(sum(case when monthname = 'July' then amounttotal else 0 end) as int)
            as JulyTotal
            ,cast(sum(case when monthname = 'August' then numberofrepayments else 0 end) as int)
            as AugustRepayments
            ,cast(sum(case when monthname = 'August' then amounttotal else 0 end) as int)
            as AugustTotal
            ,cast(sum(case when monthname = 'September' then numberofrepayments else 0 end) as int)
            as SeptemberRepayments
            ,cast(sum(case when monthname = 'September' then amounttotal else 0 end) as int)
            as SeptemberTotal
            ,cast(sum(case when monthname = 'October' then numberofrepayments else 0 end) as int)
            as OctoberRepayments
            ,cast(sum(case when monthname = 'October' then amounttotal else 0 end) as int)
            as OctoberTotal
            ,cast(sum(case when monthname = 'November' then numberofrepayments else 0 end) as int)
            as NovemberRepayments
            ,cast(sum(case when monthname = 'November' then amounttotal else 0 end) as int)
            as NovemberTotal
            ,cast(sum(case when monthname = 'December' then numberofrepayments else 0 end) as int)
            as DecemberRepayments
            ,cast(sum(case when monthname = 'December' then amounttotal else 0 end) as int)
            as DecemberTotal
        from timeline
        group by customerid
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
        create or replace table corrected_customers as
        -- Note: we continue to assume that it is correct to deduplicate the table:
        with customers_deduped as (
            select *
            from customers
            qualify row_number() over (partition by customerid order by customerid) = 1
        ),
        corrected_customers as ( 
            select
                customerid as CustomerId
                ,age as Age
                ,gender as Gender
                -- Manual input for overflowing customers:
                ,case 
                -- first two female customers:
                    when customerid = 1 then 52
                    when customerid = 2 then 71
                -- first two male customers:
                    when customerid = 7 then 39
                    when customerid = 8 then 51
            -- Function will assign the age of two customers "above" the customer:
                    else lag(age, 2) 
                        over (partition by gender order by customerid asc) end
                as CorrectedAge
            from customers_deduped
        )
        select *
        from corrected_customers
        ;

        select *
        from corrected_customers
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """
        with age_category_customers as (
        select 
            *
            ,case 
                when CorrectedAge < 20 then 'Teen'
                when (20 <= CorrectedAge) and (CorrectedAge < 30) then 'Young Adult'
                when (30 <= CorrectedAge) and (CorrectedAge  < 60) then 'Adult'
                else 'Pensioner' end
            as AgeCategory
        from corrected_customers
        ),
        repayments_per_customer as (
            select
                customerid
                ,coalesce(count(*), 0) 
                as repayment_count
            from repayments
            group by customerid
        )
        select 
            age_category_customers.CustomerID
            ,age_category_customers.Age
            ,age_category_customers.CorrectedAge
            ,age_category_customers.Gender
            ,age_category_customers.AgeCategory
        -- dense_rank ensures that customers with an equal repayment_count are given 
        -- the same rank and rankings are not skipped
            ,case when repayments_per_customer.repayment_count is NULL 
                    or repayments_per_customer.repayment_count = 0 then 0 
                else dense_rank() 
                    over (partition by AgeCategory order by repayments_per_customer.repayment_count desc)
                    end
            as Rank
        from age_category_customers
        left join repayments_per_customer
            on age_category_customers.customerid = repayments_per_customer.customerid
    """

    return qry
