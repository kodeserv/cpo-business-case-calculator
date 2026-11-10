# Hand-checked cases: year 1 of each preset

Worked by hand from the preset inputs in `src/cpo_calc/presets.py`. `tests/test_hand_checked.py`
asserts each figure to the rupee. Utilisation is energy-based: kWh delivered / (installed kW x 8,760 h).
Uptime only caps utilisation; it does not reduce energy a second time.

## Highway DC (2 x 60 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 120 kW x 8,760 h x 8% = 84,096 kWh | |
| Paid by drivers, incl. GST | 84,096 x 22 | 18,50,112 |
| Revenue excl. GST | 18,50,112 / 1.18 | 15,67,892 |
| Payment fees | 2% of 18,50,112 | 37,002 |
| Revenue share to landowner | 10% of 15,67,891.53 | 1,56,789 |
| Energy cost | 84,096 / 0.93 x 7.5 | 6,78,194 |
| Fixed costs | no demand charge (public station); O&M 2 x 50,000; CSMS 2 x 1,000 x 12; staff 30,000 x 12 | 4,84,000 |
| **EBITDA** | | **2,11,907** |
| Net capex | 2 x 11,00,000 + 15,00,000 + 5,00,000 + 1,00,000 | 43,00,000 |

## Apartment society AC (4 x 7.4 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 29.6 kW x 8,760 h x 12% = 31,115.52 kWh | |
| Paid by drivers, incl. GST | 31,115.52 x 14 | 4,35,617 |
| Revenue excl. GST | 4,35,617.28 / 1.18 | 3,69,167 |
| Payment fees | 2% of 4,35,617.28 | 8,712 |
| Energy cost | 31,115.52 / 0.95 x 7 | 2,29,272 |
| Fixed costs | O&M 4 x 5,000; CSMS 4 x 300 x 12 | 34,400 |
| **EBITDA** | | **96,783** |
| Net capex | 4 x 60,000 + 1,50,000 + 50,000 + 20,000 | 4,60,000 |

## Fleet depot DC (4 x 30 kW)

| Line | Working | Rs |
|---|---|---:|
| Energy sold | 120 kW x 8,760 h x 20% = 2,10,240 kWh | |
| Revenue excl. GST | 2,10,240 x 17 / 1.18 | 30,28,881 |
| Energy cost | 2,10,240 / 0.93 x 7 | 15,82,452 |
| Fixed costs | demand 150 x 130 x 12 = 2,34,000; O&M 4 x 30,000; CSMS 4 x 800 x 12; rent 10,000 x 12; staff 20,000 x 12 | 7,52,400 |
| **EBITDA** | | **6,94,030** |
| Net capex | 4 x 6,00,000 + 10,00,000 + 3,00,000 + 80,000 | 37,80,000 |
