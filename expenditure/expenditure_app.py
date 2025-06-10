from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB = "expenditure/database.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Income
                salary REAL, dividends REAL, state_pension REAL, pension REAL, benefits REAL, other_income REAL,

                -- Home
                gas REAL, electric REAL, oil REAL, water REAL, council_tax REAL, phone REAL, internet REAL, mobile_phone REAL, food REAL, other_home REAL,

                -- Travel
                petrol REAL, car_tax REAL, car_insurance REAL, maintenance REAL, public_transport REAL, other_travel REAL,

                -- Misc
                social REAL, holidays REAL, gym REAL, clothing REAL, other_misc REAL,

                -- Children
                nursery REAL, childcare REAL, school_fees REAL, uni_costs REAL, child_maintenance REAL, other_children REAL,

                -- Insurance
                life REAL, critical_illness REAL, income_protection REAL, buildings REAL, contents REAL, other_insurance REAL,

                -- Deductions
                pension_ded REAL, student_loan REAL, childcare_ded REAL, travel_ded REAL, sharesave REAL, other_deductions REAL
            )
        ''')
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        with sqlite3.connect(DB) as conn:
            conn.execute('''
                INSERT INTO expenses VALUES (
                    NULL, -- id

                    -- Income
                    ?, ?, ?, ?, ?, ?,

                    -- Home
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,

                    -- Travel
                    ?, ?, ?, ?, ?, ?,

                    -- Misc
                    ?, ?, ?, ?, ?,

                    -- Children
                    ?, ?, ?, ?, ?, ?,

                    -- Insurance
                    ?, ?, ?, ?, ?, ?,

                    -- Deductions
                    ?, ?, ?, ?, ?, ?
                )
            ''', tuple(float(data.get(field, 0)) for field in [
                "salary", "dividends", "statePension", "pension", "benefits", "otherIncome",
                "gas", "electric", "oil", "water", "councilTax", "phone", "internet", "mobilePhone", "food", "otherHome",
                "petrol", "carTax", "carInsurance", "maintenance", "publicTransport", "otherTravel",
                "social", "holidays", "gym", "clothing", "otherMisc",
                "nursery", "childcare", "schoolFees", "uniCosts", "childMaintenance", "otherChildren",
                "life", "criticalIllness", "incomeProtection", "buildings", "contents", "otherInsurance",
                "pensionDed", "studentLoan", "childcareDed", "travelDed", "sharesave", "otherDeductions"
            ]))

        return redirect(url_for("results"))

    return render_template("index.html")

@app.route("/results")
def results():
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 1").fetchone()
        if not row:
            return "No data found"

        # Income = fields 1-6
        income = sum(row[1:7])

        # Expense categories
        home = sum(row[7:18])
        travel = sum(row[18:24])
        misc = sum(row[24:29])
        children = sum(row[29:35])
        insurance = sum(row[35:41])
        deductions = sum(row[41:47])

        # Total expenditure
        total_expenses = home + travel + misc + children + insurance + deductions
        surplus = income - total_expenses

        def pct(x): return round((x / income) * 100, 2) if income > 0 else 0

        # Calculations
        percentages = {
            "income": income,
            "home": home,
            "travel": travel,
            "misc": misc,
            "children": children,
            "insurance": insurance,
            "deductions": deductions,
            "total": total_expenses,
            "surplus": surplus,
            "pct_surplus": pct(surplus),
            "pct_home": pct(home),
            "pct_travel": pct(travel),
            "pct_misc": pct(misc),
            "pct_children": pct(children),
            "pct_insurance": pct(insurance),
            "pct_deductions": pct(deductions),
        }

        # Target calculations
        essentials = home + travel + children + insurance + deductions
        percentages["essentials"] = essentials
        percentages["luxuries_pct"] = pct(misc)
        percentages["savings_pct"] = round(100 - pct(essentials) - pct(misc), 2)

    return render_template("results.html", **percentages)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
