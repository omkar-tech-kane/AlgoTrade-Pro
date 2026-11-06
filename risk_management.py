# =========================================
# RISK MANAGEMENT ENGINE
# Educational Paper Trading Only
# =========================================

INITIAL_CAPITAL = 100000

RISK_PER_TRADE = 0.01

MAX_ALLOCATION = 0.20

STOP_LOSS_PERCENT = 0.02

TAKE_PROFIT_PERCENT = 0.04


# =========================================
# POSITION SIZING
# =========================================

def calculate_position_size(
    capital,
    entry_price
):

    if capital <= 0 or entry_price <= 0:
        raise ValueError("Capital and price must be positive.")

    risk_amount = capital * RISK_PER_TRADE

    stop_distance = (
        entry_price * STOP_LOSS_PERCENT
    )

    risk_quantity = int(
        risk_amount / stop_distance
    )

    allocation_amount = (
        capital * MAX_ALLOCATION
    )

    allocation_quantity = int(
        allocation_amount / entry_price
    )

    quantity = min(
        risk_quantity,
        allocation_quantity
    )

    return {
        "Capital": capital,
        "Entry_Price": entry_price,
        "Risk_Amount": risk_amount,
        "Quantity": quantity,
        "Investment": quantity * entry_price,
        "Stop_Loss": entry_price * (
            1 - STOP_LOSS_PERCENT
        ),
        "Take_Profit": entry_price * (
            1 + TAKE_PROFIT_PERCENT
        )
    }


# =========================================
# EXIT CONDITIONS
# =========================================

def check_exit(
    entry_price,
    current_price
):

    stop_loss = (
        entry_price * (1 - STOP_LOSS_PERCENT)
    )

    take_profit = (
        entry_price * (1 + TAKE_PROFIT_PERCENT)
    )

    if current_price <= stop_loss:

        return "STOP_LOSS"

    elif current_price >= take_profit:

        return "TAKE_PROFIT"

    return "HOLD"


# =========================================
# TEST RISK ENGINE
# =========================================

if __name__ == "__main__":

    result = calculate_position_size(
        INITIAL_CAPITAL,
        1500
    )

    print("\n========== RISK REPORT ==========")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("\n========== EXIT TEST ==========")

    print(
        "Price 1460:",
        check_exit(1500, 1460)
    )

    print(
        "Price 1560:",
        check_exit(1500, 1560)
    )

    print(
        "Price 1520:",
        check_exit(1500, 1520)
    )