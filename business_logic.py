def calculate_share(amount, number_of_people):
    if number_of_people <= 0:
        return 0
    return round(amount / number_of_people, 2)


def validate_expense_amount(amount):
    return amount > 0


def validate_group_name(group_name):
    return group_name is not None and len(group_name.strip()) >= 2


def validate_member_name(member_name):
    return member_name is not None and len(member_name.strip()) >= 2


def validate_member_count(member_count):
    return member_count >= 2


def calculate_total_expenses(expenses):
    total = 0

    for expense in expenses:
        total += expense["amount"]

    return round(total, 2)


def calculate_group_summary(expenses):
    summary = []

    for expense in expenses:
        share = calculate_share(expense["amount"], expense["split_count"])

        summary.append({
            "title": expense["title"],
            "amount": expense["amount"],
            "paid_by": expense["paid_by"],
            "split_count": expense["split_count"],
            "share": share
        })

    return summary