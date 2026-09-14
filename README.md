# Excel Sheet Validator

A simple Flask app that uploads an Excel file, validates every row,
inserts valid rows into MySQL, and shows a report of what was
accepted or rejected (and why).

## Setup

1. Run `database_setup.sql` in MySQL to create the database and table.
2. Open `database.py` and replace `YOUR_MYSQL_PASSWORD` with your MySQL password.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open `http://127.0.0.1:5000/` in your browser.

## Expected Excel format

| name    | email             | age |
|---------|-------------------|-----|
| Ahmed   | ahmed@gmail.com   | 21  |
| Mohamed | mohamed@gmail.com | 22  |

## Validation rules

- `name`, `email`, `age` are all required (not empty).
- `age` must be a whole number.
- No duplicate emails within the same file.
- No email that already exists in the database.
