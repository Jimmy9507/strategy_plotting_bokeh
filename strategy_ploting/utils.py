from __future__ import division

APPROX_BDAYS_PER_MONTH = 21
APPROX_BDAYS_PER_YEAR = 252

APPROX_DAYS_PER_YR=365
APPROX_DAYS_PER_MON=APPROX_DAYS_PER_YR/12

MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52

MM_DISPLAY_UNIT = 1000000.

DAILY = 'daily'
WEEKLY = 'weekly'
MONTHLY = 'monthly'
YEARLY = 'yearly'

ANNUALIZATION_FACTORS = {
    DAILY: APPROX_BDAYS_PER_YEAR,
    WEEKLY: WEEKS_PER_YEAR,
    MONTHLY: MONTHS_PER_YEAR
}

YIELD_CURVE_TENORS = [
    (0, 'S0'),
    (30, 'M1'),
    (60, 'M2'),
    (90, 'M3'),
    (180, 'M6'),
    (270, 'M9'),
    (365, 'Y1'),
    (365 * 2, 'Y2'),
    (365 * 3, 'Y3'),
    (365 * 4, 'Y4'),
    (365 * 5, 'Y5'),
    (365 * 6, 'Y6'),
    (365 * 7, 'Y7'),
    (365 * 8, 'Y8'),
    (365 * 9, 'Y9'),
    (365 * 10, 'Y10'),
    (365 * 15, 'Y15'),
    (365 * 20, 'Y20'),
    (365 * 30, 'Y30'),
    (365 * 40, 'Y40'),
    (365 * 50, 'Y50'),
]

