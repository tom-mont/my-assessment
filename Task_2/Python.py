import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculates the percent of loans that defaulted as per the type 1 default definition. 
    A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """

    # First, find all loan payments that were less than the scheduled payment
    actual_less_than_scheduled = df_balances[df_balances['ActualRepayment'] < df_balances['ScheduledRepayment']]

    # By the type 1 default definition any payments less than the scheduled payment meet the definition
    ## nununique() selects distinct loans
    count_distinct_loans_type1default = actual_less_than_scheduled['LoanID'].nunique()

    ## nununique() selects all distinct loans:
    count_distinct_loans = df_balances['LoanID'].nunique()

    # Hence type 1 default rate is the proportion that met the type 1 definition. Multiplied by 100 to 
    # make it a number
    default_rate_percent = 100 * count_distinct_loans_type1default / count_distinct_loans

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculates the percent of loans that defaulted as per the type 2 default definition: 
    A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """

    ## Number of scheduled payments for each loan 
    repayments_per_loan = df_scheduled.groupby("LoanID").size()
    
    ## Unpaid payments are defined as a payment being 0
    unpaid_payments = df_balances[df_balances["ActualRepayment"] == 0].groupby("LoanID").size()

    ## Create a new DF that is on a loan-grain
    loans_df = pd.DataFrame({
        'TotalExpectedRepayments': repayments_per_loan,
        'UnpaidPayments': unpaid_payments
    })
    
    ## Update NaN values to 0 for calculcation purposes:
    loans_df['UnpaidPayments'] = loans_df['UnpaidPayments'].fillna(0).astype(int)
    
    ## Calculate percentage of payments in a loan that were not repaid:
    loans_df["PercentUnpaidPayments"] = 100 * loans_df["UnpaidPayments"] / loans_df["TotalExpectedRepayments"]
    
    ## Calculate what % of loans are in type 2 default:
    default_rate_percent = 100 * len(loans_df[loans_df["PercentUnpaidPayments"] > 15]) / len(loans_df)
    
    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """
    
    ## Aggregate portfolio by taking the sums of relevant columns per-month
    portfolio_months = df_balances.groupby("Month").agg({
        "ActualRepayment": "sum",
        "ScheduledRepayment": "sum",
        "LoanBalanceStart": "sum"
    })
    
    ## Unscheduled principal will be any payment that exceeds the expected payment 
    portfolio_months["UnscheduledPrincipal"] = portfolio_months["ActualRepayment"] - portfolio_months["ScheduledRepayment"]
    
    ## UnscheduledPrincipal cannot be less than zero:
    portfolio_months.loc[portfolio_months["UnscheduledPrincipal"] < 0, "UnscheduledPrincipal"] = 0
    
    ## SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    portfolio_months["SMM"] = portfolio_months["UnscheduledPrincipal"] / portfolio_months["LoanBalanceStart"]
    
    ## SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    SMM_mean = (1 + portfolio_months["SMM"]).prod() ** (1/12) - 1
    
    ## CPR is calculated as: 1 - (1- SMM_mean)^12
    cpr_percent = 100 * (1 - (1 - SMM_mean) ** 12)

    return cpr_percent


def question_4(df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """

    ## Need to calculate the total loan balance at the end of year 1
    ## To do this, sum all the loan balances at the end of month 12:
    yearend_loan_balance = df_balances.loc[df_balances["Month"] == 12, "LoanBalanceEnd"].sum()
    
    ## Recovery rate is given to be 0.8
    recovery_rate = 0.8
    
    ## Probabiltiy of default is taken from both questions 1 and 2 
    probability_of_default = 0.15
    
    ## Predicted total loss: probability_of_default * total_loan_balance * (1 - recovery_rate)
    total_loss = probability_of_default * yearend_loan_balance * (1 - recovery_rate)

    return total_loss
