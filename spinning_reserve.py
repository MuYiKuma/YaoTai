"""Utilities for spinning reserve revenue calculations.

This module provides a helper function for estimating annual spinning
reserve revenue after applying an optional aggregator fee.
"""


def calculate_spinning_reserve_revenue(input_data, aggregator_fee=0):
    """Calculate annual spinning reserve revenue after aggregator fees.

    Parameters
    ----------
    input_data : dict
        A mapping that must contain the following numeric fields:
        - ``sr_capacity_kw``: Spinning reserve capacity in kilowatts.
        - ``sr_hours_per_day``: Number of spinning reserve service hours per day.
        - ``sr_price``: Revenue rate per kilowatt-hour (or the pricing unit used
          consistently by your model).
        - ``sr_execution_rate``: Annual execution/realization rate, expressed as
          a decimal. For example, use ``0.9`` for 90%.
    aggregator_fee : float, optional
        Aggregator fee percentage to deduct from the gross annual revenue.
        This value should be provided as a percentage, not a decimal.
        For example:
        - ``0`` means no fee deduction.
        - ``5`` means a 5% fee.
        Default is ``0``.

    Returns
    -------
    dict
        A dictionary with one key:
        - ``annual_sr_revenue``: The final annual spinning reserve revenue after
          deducting the aggregator fee.

    Notes
    -----
    Calculation logic:

    1. Daily revenue = ``sr_capacity_kw × sr_hours_per_day × sr_price``
    2. Gross annual revenue = ``daily revenue × 365 × sr_execution_rate``
    3. Net annual revenue = ``gross annual revenue × (1 - aggregator_fee / 100)``

    Examples
    --------
    >>> calculate_spinning_reserve_revenue(
    ...     {
    ...         "sr_capacity_kw": 1000,
    ...         "sr_hours_per_day": 2,
    ...         "sr_price": 3,
    ...         "sr_execution_rate": 0.8,
    ...     },
    ...     aggregator_fee=5,
    ... )
    {'annual_sr_revenue': 1664400.0}
    """
    # Read the required spinning reserve parameters from the input dictionary.
    # These values are expected to be numeric and should already use a
    # consistent unit system in the caller's business logic.
    sr_capacity_kw = input_data["sr_capacity_kw"]
    sr_hours_per_day = input_data["sr_hours_per_day"]
    sr_price = input_data["sr_price"]
    sr_execution_rate = input_data["sr_execution_rate"]

    # Step 1:
    # Calculate the daily spinning reserve revenue.
    # Formula:
    #   daily revenue = capacity (kW) × service hours per day × price
    daily_sr_revenue = sr_capacity_kw * sr_hours_per_day * sr_price

    # Step 2:
    # Convert the daily revenue to annual gross revenue.
    # The business rule specifies multiplying by 365 days and then by the
    # execution rate to reflect the proportion of revenue actually realized.
    gross_annual_sr_revenue = daily_sr_revenue * 365 * sr_execution_rate

    # Step 3:
    # Convert the aggregator fee from a percentage into a deduction factor.
    # Example:
    #   aggregator_fee = 5  -> net factor = 0.95
    #   aggregator_fee = 0  -> net factor = 1.00
    net_revenue_factor = 1 - (aggregator_fee / 100)

    # Step 4:
    # Apply the aggregator fee deduction to obtain the final annual revenue.
    annual_sr_revenue = gross_annual_sr_revenue * net_revenue_factor

    # Return the final result in the requested output structure.
    return {"annual_sr_revenue": annual_sr_revenue}
