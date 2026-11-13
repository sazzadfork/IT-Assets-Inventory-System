from flask import Flask, render_template, request, redirect, send_file
import sqlite3

app = Flask(__name__)


# ==============================
# Status Options
# ==============================

STATUS_OPTIONS = [
    "Assigned",
    "Available",
    "Maintenance",
    "Damaged",
    "Retired"
]


# ==============================
# Initialize Database
# ==============================

def init_db():

    conn = sqlite3.connect("assets.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            serial_number TEXT NOT NULL,
            employee_id TEXT,
            department TEXT,
            assigned_to TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(assets)")
    columns = [column[1] for column in cursor.fetchall()]


    # Add Employee ID column
    if "employee_id" not in columns:

        cursor.execute(
            "ALTER TABLE assets ADD COLUMN employee_id TEXT"
        )


    # Add Department column
    if "department" not in columns:

        cursor.execute(
            "ALTER TABLE assets ADD COLUMN department TEXT"
        )


    # Add Status column
    if "status" not in columns:

        cursor.execute(
            "ALTER TABLE assets ADD COLUMN status TEXT DEFAULT 'Available'"
        )


    conn.commit()
    conn.close()


# ==============================
# Home Page
# ==============================

# Home Page
@app.route("/")
def home():

    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()

    conn = sqlite3.connect("assets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Asset List Query
    query = "SELECT * FROM assets WHERE 1=1"
    params = []

    if search:
        query += """
            AND (
                asset_name LIKE ?
                OR serial_number LIKE ?
                OR employee_id LIKE ?
                OR assigned_to LIKE ?
                OR department LIKE ?
                OR status LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if department:
        query += " AND department = ?"
        params.append(department)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)

    assets = cursor.fetchall()


    # Dashboard Counts
    cursor.execute("SELECT COUNT(*) FROM assets")
    total_assets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assets WHERE status = ?",
        ("Assigned",)
    )
    assigned = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assets WHERE status = ?",
        ("Available",)
    )
    available = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assets WHERE status = ?",
        ("Maintenance",)
    )
    maintenance = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assets WHERE status = ?",
        ("Damaged",)
    )
    damaged = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM assets WHERE status = ?",
        ("Retired",)
    )
    retired = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "index.html",
        assets=assets,
        search=search,
        department=department,
        status=status,
        status_options=STATUS_OPTIONS,

        # Dashboard Data
        total_assets=total_assets,
        assigned=assigned,
        available=available,
        maintenance=maintenance,
        damaged=damaged,
        retired=retired
    )


# ==============================
# Add Asset
# ==============================

@app.route("/add", methods=["POST"])
def add_asset():

    asset_name = request.form["asset_name"]
    asset_type = request.form["asset_type"]
    serial_number = request.form["serial_number"]
    employee_id = request.form["employee_id"]
    department = request.form["department"]
    assigned_to = request.form["assigned_to"]
    status = request.form["status"]


    # Validate Status

    if status not in STATUS_OPTIONS:

        status = "Available"


    conn = sqlite3.connect("assets.db")

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO assets
        (
            asset_name,
            asset_type,
            serial_number,
            employee_id,
            department,
            assigned_to,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        asset_name,
        asset_type,
        serial_number,
        employee_id,
        department,
        assigned_to,
        status
    ))


    conn.commit()
    conn.close()


    return redirect("/")

#View Asset

@app.route("/view/<int:id>")
def view_asset(id):

    conn = sqlite3.connect("assets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM assets WHERE id = ?",(id,)
    )
    asset = cursor.fetchone()
    conn.close()

    if asset is None:
        return "Asset not found"

    return render_template(
        "view.html",
        asset=asset
    )


# ==============================
# Delete Asset
# ==============================

@app.route("/delete/<int:id>")
def delete_asset(id):

    conn = sqlite3.connect("assets.db")

    cursor = conn.cursor()


    cursor.execute(
        "DELETE FROM assets WHERE id = ?",
        (id,)
    )


    conn.commit()
    conn.close()


    return redirect("/")


# ==============================
# Edit Asset
# ==============================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_asset(id):

    conn = sqlite3.connect("assets.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    if request.method == "POST":

        asset_name = request.form["asset_name"]
        asset_type = request.form["asset_type"]
        serial_number = request.form["serial_number"]
        employee_id = request.form["employee_id"]
        department = request.form["department"]
        assigned_to = request.form["assigned_to"]
        status = request.form["status"]


        # Validate Status

        if status not in STATUS_OPTIONS:

            status = "Available"


        cursor.execute("""
            UPDATE assets
            SET
                asset_name = ?,
                asset_type = ?,
                serial_number = ?,
                employee_id = ?,
                department = ?,
                assigned_to = ?,
                status = ?
            WHERE id = ?
        """, (
            asset_name,
            asset_type,
            serial_number,
            employee_id,
            department,
            assigned_to,
            status,
            id
        ))


        conn.commit()
        conn.close()


        return redirect("/")


    cursor.execute(
        "SELECT * FROM assets WHERE id = ?",
        (id,)
    )


    asset = cursor.fetchone()

    conn.close()


    return render_template(
        "edit.html",
        asset=asset,
        status_options=STATUS_OPTIONS
    )


# ==============================
# Initialize Database
# ==============================

init_db()

# Export Assets to Excel
@app.route("/export")
def export_assets():

    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    conn = sqlite3.connect("assets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            asset_name,
            asset_type,
            serial_number,
            assigned_to,
            employee_id,
            department,
            status
        FROM assets
        ORDER BY id DESC
    """)

    assets = cursor.fetchall()

    conn.close()


    # Create Excel Workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Asset List"


    # Header
    headers = [
        "ID",
        "Asset Name",
        "Asset Type",
        "Serial Number",
        "Assigned To",
        "Employee ID",
        "Department",
        "Status"
    ]

    sheet.append(headers)


    # Asset Data
    for asset in assets:

        sheet.append([
            asset["id"],
            asset["asset_name"],
            asset["asset_type"],
            asset["serial_number"],
            asset["assigned_to"],
            asset["employee_id"] or "",
            asset["department"] or "",
            asset["status"] or "Available"
        ])


    # Header Style
    for cell in sheet[1]:

        cell.font = Font(bold=True)
        cell.fill = PatternFill(
            "solid",
            fgColor="1F2937"
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )


    # Column Width
    for column in sheet.columns:

        max_length = 0

        column_letter = get_column_letter(
            column[0].column
        )

        for cell in column:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        sheet.column_dimensions[
            column_letter
        ].width = max_length + 3


    # Save Excel File
    file_path = "assets_export.xlsx"

    workbook.save(file_path)


    return send_file(
        file_path,
        as_attachment=True,
        download_name="IT_Assets_Report.xlsx"
    )

# Database Backup
@app.route("/backup")
def backup_database():

    return send_file(
        "assets.db",
        as_attachment=True,
        download_name="IT_Assets_Backup.db"
    )


# ==============================
# Run Flask
# ==============================

if __name__ == "__main__":

    app.run(debug=True)

    