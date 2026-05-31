import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business_logic import (
    calculate_share,
    validate_expense_amount,
    validate_group_name,
    validate_member_name,
    validate_member_count,
    calculate_total_expenses,
    calculate_group_summary
)


def test_calculate_share():
    assert calculate_share(300, 3) == 100
    assert calculate_share(100, 4) == 25
    assert calculate_share(100, 0) == 0


def test_validate_expense_amount():
    assert validate_expense_amount(100) == True
    assert validate_expense_amount(0) == False
    assert validate_expense_amount(-50) == False


def test_validate_group_name():
    assert validate_group_name("Home") == True
    assert validate_group_name("A") == False
    assert validate_group_name("") == False
    assert validate_group_name(None) == False


def test_validate_member_name():
    assert validate_member_name("Amr") == True
    assert validate_member_name("A") == False
    assert validate_member_name("") == False
    assert validate_member_name(None) == False


def test_validate_member_count():
    assert validate_member_count(2) == True
    assert validate_member_count(3) == True
    assert validate_member_count(1) == False
    assert validate_member_count(0) == False


def test_calculate_total_expenses():
    expenses = [
        {"amount": 100},
        {"amount": 250},
        {"amount": 50}
    ]

    assert calculate_total_expenses(expenses) == 400


def test_calculate_group_summary():
    expenses = [
        {
            "id": 1,
            "title": "Dinner",
            "amount": 300,
            "paid_by": "Amr",
            "split_count": 3
        }
    ]

    summary = calculate_group_summary(expenses)

    assert summary[0]["id"] == 1
    assert summary[0]["title"] == "Dinner"
    assert summary[0]["amount"] == 300
    assert summary[0]["paid_by"] == "Amr"
    assert summary[0]["split_count"] == 3
    assert summary[0]["share"] == 100