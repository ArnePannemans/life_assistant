import os
import pandas as pd
from datetime import datetime
from phi.tools import Toolkit
from phi.utils.log import logger
from typing import Dict, Any

EXPENSE_DIR = "data/expenses"
CATEGORIES = ["Food", "Rent", "Transportation", "Clothing", "Material", "Event", "Paypal", "Sports"]

class ExpenseTrackerToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="expense_tracker_toolkit")
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.register(self.add_expense)
        self.register(self.list_expenses)
        self.register(self.summarize_expenses)
        self.register(self.delete_expense)
        self.register(self.update_expense)
        self.register(self.run_dataframe_operation)

    def get_current_month_file(self) -> str:
        """
        Get the filename for the current month's expenses CSV file.

        Returns:
            str: The path to the current month's expenses CSV file.
        """
        if not os.path.exists(EXPENSE_DIR):
            os.makedirs(EXPENSE_DIR)
        current_month = datetime.now().strftime("%Y-%m")
        logger.info(f"Retrieving current month file: {current_month}")
        return os.path.join(EXPENSE_DIR, f"expenses_{current_month}.csv")

    def get_month_file(self, year: int, month: int) -> str:
        """
        Get the filename for the specified month's expenses CSV file.

        Args:
            year (int): The year of the expenses.
            month (int): The month of the expenses.

        Returns:
            str: The path to the specified month's expenses CSV file.
        """
        if not os.path.exists(EXPENSE_DIR):
            os.makedirs(EXPENSE_DIR)
        month_str = f"{year}-{month:02d}"
        return os.path.join(EXPENSE_DIR, f"expenses_{month_str}.csv")

    def load_expenses(self, file_path: str) -> pd.DataFrame:
        """
        Load expenses from the specified CSV file.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            pd.DataFrame: A DataFrame containing the expense details.
        """
        logger.info(f"Loading expenses from: {file_path}")
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame(columns=["date", "amount", "category", "description"])

    def save_expenses(self, expenses: pd.DataFrame, file_path: str):
        """
        Save expenses to the specified CSV file.

        Args:
            expenses (pd.DataFrame): A DataFrame containing the expense details to be saved.
            file_path (str): The path to the CSV file.
        """
        logger.info(f"Saving expenses to: {file_path}")
        expenses.to_csv(file_path, index=False)

    def validate_category(self, category: str) -> bool:
        """
        Validate if the given category is in the predefined categories.

        Args:
            category (str): The category to validate.

        Returns:
            bool: True if the category is valid, False otherwise.
        """

        logger.info(f"Validating category '{category}': {valid}")
        return category in CATEGORIES

    def add_expense(self, amount: float, category: str, description: str) -> str:
        """
        Adds an expense to the current month's expense tracker.

        Args:
            amount (float): The amount of the expense.
            category (str): The category of the expense (e.g., "Food", "Transport").
            description (str): A brief description of the expense.

        Returns:
            str: A confirmation message indicating that the expense was added.

        Example:
            add_expense(25.50, "Food", "Lunch at restaurant")
        """
        valid = category in CATEGORIES

        file_path = self.get_current_month_file()
        expenses = self.load_expenses(file_path)
        logger.info(f"Adding expense: {amount}, {category}, {description}")
        new_expense = pd.DataFrame([{
            "date": datetime.now().isoformat(),
            "amount": amount,
            "category": category,
            "description": description
        }])
        expenses = pd.concat([expenses, new_expense], ignore_index=True)
        self.save_expenses(expenses, file_path)
        return f"Expense of {amount} in category '{category}' added."

    def list_expenses(self, year: int = None, month: int = None) -> str:
        """
        Lists all expenses recorded in the specified month. If no month is specified, lists the current month's expenses.

        Args:
            year (int, optional): The year of the expenses to list. Defaults to the current year.
            month (int, optional): The month of the expenses to list. Defaults to the current month.

        Returns:
            str: A formatted string of all expenses.

        Example:
            list_expenses()
            list_expenses(2023, 4)
        """
        if year is None or month is None:
            file_path = self.get_current_month_file()
        else:
            file_path = self.get_month_file(year, month)

        expenses = self.load_expenses(file_path)
        logger.info(f"Listing expenses from: {file_path}")
        if expenses.empty:
            return "You have no recorded expenses for this period."
        return expenses.to_string(index=False)

    def summarize_expenses(self, year: int = None, month: int = None) -> str:
        """
        Provides a summary of expenses by category for the specified month. If no month is specified, summarizes the current month's expenses.

        Args:
            year (int, optional): The year of the expenses to summarize. Defaults to the current year.
            month (int, optional): The month of the expenses to summarize. Defaults to the current month.

        Returns:
            str: A formatted string summarizing the total expenses by category.

        Example:
            summarize_expenses()
            summarize_expenses(2023, 4)
        """

        if year is None or month is None:
            file_path = self.get_current_month_file()
        else:
            file_path = self.get_month_file(year, month)

        expenses = self.load_expenses(file_path)
        logger.info(f"Summarizing expenses from: {file_path}")
        if expenses.empty:
            return "You have no recorded expenses for this period."
        summary = expenses.groupby("category")["amount"].sum().reset_index()
        return summary.to_string(index=False)

    def delete_expense(self, description: str, year: int = None, month: int = None) -> str:
        """
        Deletes an expense from the specified month's expense tracker based on the description. If no month is specified, deletes from the current month's expenses.

        Args:
            description (str): The description of the expense to delete.
            year (int, optional): The year of the expenses to delete from. Defaults to the current year.
            month (int, optional): The month of the expenses to delete from. Defaults to the current month.

        Returns:
            str: A confirmation message indicating that the expense was deleted.

        Example:
            delete_expense("Lunch at restaurant")
            delete_expense("Lunch at restaurant", 2023, 4)
        """
        if year is None or month is None:
            file_path = self.get_current_month_file()
        else:
            file_path = self.get_month_file(year, month)

        expenses = self.load_expenses(file_path)
        expenses = expenses[expenses["description"] != description]
        self.save_expenses(expenses, file_path)
        return f"Expense with description '{description}' has been deleted."

    def update_expense(self, description: str, updated_amount: float, updated_category: str, updated_description: str, year: int = None, month: int = None) -> str:
        """
        Updates an existing expense in the specified month's expense tracker. If no month is specified, updates the current month's expenses.

        Args:
            description (str): The description of the expense to update.
            updated_amount (float): The updated amount of the expense.
            updated_category (str): The updated category of the expense.
            updated_description (str): The updated description of the expense.
            year (int, optional): The year of the expenses to update. Defaults to the current year.
            month (int, optional): The month of the expenses to update. Defaults to the current month.

        Returns:
            str: A confirmation message indicating that the expense was updated.

        Example:
            update_expense("Lunch at restaurant", 30.00, "Food", "Dinner at restaurant")
            update_expense("Lunch at restaurant", 30.00, "Food", "Dinner at restaurant", 2023, 4)
        """

        logger.info(f"Updating expense with description '{description}' to amount {updated_amount}, category {updated_category}, description {updated_description}")
        if not self.validate_category(updated_category):
            return f"Invalid category '{updated_category}'. Valid categories are: {', '.join(CATEGORIES)}."

        if year is None or month is None:
            file_path = self.get_current_month_file()
        else:
            file_path = self.get_month_file(year, month)

        expenses = self.load_expenses(file_path)
        expenses.loc[expenses["description"] == description, ["amount", "category", "description"]] = [
            updated_amount, updated_category, updated_description]
        self.save_expenses(expenses, file_path)
        return f"Expense with description '{description}' has been updated."


    def create_dataframe_from_csv(self, csv_path: str, dataframe_name: str) -> str:
        """
        Creates a pandas dataframe from a specified CSV file and stores it with a given name.

        Args:
            csv_path (str): The path to the CSV file.
            dataframe_name (str): The name to store the dataframe under.

        Returns:
            str: A confirmation message indicating that the dataframe was created.

        Example:
            create_dataframe_from_csv("expenses_2023-04.csv", "april_expenses")
        """
        try:
            dataframe = pd.read_csv(csv_path)
            if dataframe.empty:
                return f"CSV file at {csv_path} is empty."
            self.dataframes[dataframe_name] = dataframe
            return f"Dataframe '{dataframe_name}' created from CSV at {csv_path}."
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return f"Error: {e}"

    def generate_monthly_report(self, year: int, month: int) -> str:
        """
        Generates a monthly financial report for the specified year and month.

        Args:
            year (int): The year of the report.
            month (int): The month of the report.

        Returns:
            str: A formatted string containing the monthly financial report.

        Example:
            generate_monthly_report(2023, 4)
        """
        logger.info(f"Generating monthly report for {year}-{month:02d}")
        file_path = self.get_month_file(year, month)
        expenses = self.load_expenses(file_path)
        if expenses.empty:
            return f"No expenses recorded for {year}-{month:02d}."

        total_expenses = expenses["amount"].sum()
        summary = expenses.groupby("category")["amount"].sum().reset_index()

        report = f"Financial Report for {year}-{month:02d}\n"
        report += "-" * 30 + "\n"
        report += f"Total Expenses: {total_expenses}\n"
        report += "-" * 30 + "\n"
        report += summary.to_string(index=False)

        return report

    def create_monthly_expense_file(self, year: int, month: int) -> str:
        """
        Creates a new CSV file for the specified year and month if it does not yet exist.

        Args:
            year (int): The year for which to create the expense file.
            month (int): The month for which to create the expense file.

        Returns:
            str: A confirmation message indicating that the file was created or already exists.

        Example:
            create_monthly_expense_file(2023, 4)
        """
        file_path = self.get_month_file(year, month)
        if os.path.exists(file_path):
            return f"Expense file for {year}-{month:02d} already exists."
        expenses = pd.DataFrame(columns=["date", "amount", "category", "description"])
        self.save_expenses(expenses, file_path)
        return f"Expense file for {year}-{month:02d} created successfully."

    def run_dataframe_operation(self, year: int, month: int, operation: str, operation_parameters: Dict[str, Any]) -> str:
        """
        Runs an operation `operation` on a pandas dataframe on the expenses from year month with the parameters `operation_parameters`.
        The columns are "date", "amount", "category", and "description".
        For expense information and filtering, look at description column.
        Returns the result of the operation as a string if successful, otherwise returns an error message.

        For Example:
       - To filter rows where the description contains "camp de base" and get the sum of the amounts for April 2023, use: {"year": 2023, "month": 4, "operation": "filter_sum", "operation_parameters": {"description_contains": "camp de base"}}

        :param year: The year of the expenses file.
        :param month: The month of the expenses file.
        :param operation: The operation to run on the dataframe.
        :param operation_parameters: The parameters to pass to the operation.
        :return: The result of the operation if successful, otherwise returns an error message.
        """
        file_path = self.get_month_file(year, month)
        try:
            logger.info(f"Running operation: {operation}")
            logger.info(f"On file: {file_path}")
            logger.info(f"With parameters: {operation_parameters}")

            # Load the dataframe
            dataframe = self.load_expenses(file_path)

            # Run the operation
            result = getattr(dataframe, operation)(**operation_parameters)

            logger.debug(f"Ran operation: {operation}")
            try:
                try:
                    return result.to_string()
                except AttributeError:
                    return str(result)
            except Exception:
                return "Operation ran successfully"
        except Exception as e:
            logger.error(f"Error running operation: {e}")
            return f"Error running operation: {e}"