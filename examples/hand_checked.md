# Hand-checked cases: year 1 of each preset

Worked by hand from the preset inputs in `src/cpo_calc/presets.py`. `tests/test_hand_checked.py`
asserts each figure to the rupee. Utilisation and uptime apply to installed power over 8,760 hours.

## Highway DC (2 x 60 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 120 kW x 8,760 h x 8% x 95% = 79,891.2 kWh | |
| Paid by drivers, incl. GST | 79,891.2 x 22 | 17,57,606 |
| Revenue excl. GST | 17,57,606.4 / 1.18 | 14,89,497 |
| Payment fees | 2% of 17,57,606.4 | 35,152 |
| Revenue share to landowner | 10% of 14,89,496.95 | 1,48,950 |
| Energy cost | 79,891.2 / 0.93 x 7.5 | 6,44,284 |
| Fixed costs | demand 200 x 140 x 12 = 3,36,000; O&M 2 x 50,000; CSMS 2 x 1,000 x 12; staff 30,000 x 12 | 8,20,000 |
| **EBITDA** | | **-1,58,889** |
| Net capex | 2 x 11,00,000 + 15,00,000 + 5,00,000 + 1,00,000 | 43,00,000 |

## Apartment society AC (4 x 7.4 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 29.6 kW x 8,760 h x 12% x 95% = 29,559.744 kWh | |
| Paid by drivers, incl. GST | 29,559.744 x 14 | 4,13,836 |
| Revenue excl. GST | 4,13,836.42 / 1.18 | 3,50,709 |
| Payment fees | 2% of 4,13,836.42 | 8,277 |
| Energy cost | 29,559.744 / 0.95 x 7 | 2,17,809 |
| Fixed costs | O&M 4 x 5,000; CSMS 4 x 300 x 12 | 34,400 |
| **EBITDA** | | **90,223** |
| Net capex | 4 x 60,000 + 1,50,000 + 50,000 + 20,000 | 4,60,000 |

## Fleet depot DC (4 x 30 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 120 kW x 8,760 h x 20% x 95% = 1,99,728 kWh | |
| Revenue excl. GST | 1,99,728 x 15 / 1.18 | 25,38,915 |
| Energy cost | 1,99,728 / 0.93 x 7.5 | 16,10,710 |
| Fixed costs | demand 200 x 130 x 12 = 3,12,000; O&M 4 x 30,000; CSMS 4 x 800 x 12; rent 25,000 x 12; staff 20,000 x 12 | 10,10,400 |
| **EBITDA** | | **-82,194** |
| Net capex | 4 x 6,00,000 + 10,00,000 + 3,00,000 + 80,000 | 37,80,000 |
