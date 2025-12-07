from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pathlib import Path as path
from datetime import date, datetime



db_name = "expense_tracker_db.sqlite"
this_file = path(__file__)
this_dir = this_file.parent
db_path = this_dir / db_name

db_url = f"sqlite:///{db_path.as_posix()}"
print(f"File -> {this_file}\nCurrent Dir -> {this_dir}\ndb path -> {db_path}\n db url -> {db_url}")

engine = create_engine(url=db_url)
sessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)
Base = declarative_base()

class old_User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # You can seed dummy values for dev
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    expenses = relationship(argument="Expense", back_populates="users", cascade="all, delete-orphan")

class old_Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    amount =  Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(type_=Text, nullable=True)
    date = Column(Date, nullable=False, index=True)

    users = relationship(argument="User", back_populates="expenses")

def expense_pretty_print_record(records:Expense):
    for record in records:
        print(f"id -> {record.id}, amount -> {record.amount}, description -> {record.description}, category -> {record.category}, date -> {record.date}")

def pretty_print_record(records):
    for record in records:
        print_str = ""
        for key, value in record.__dict__.items():
            print_str += f"{key} -> {value}, "
        print(print_str)

User.__table__.drop(engine)
Expense.__table__.drop(engine)
Base.metadata.create_all(bind = engine)

sample_data = [
    {"user_id": 1, "category": "food", "amount": 120.50, "description": "Lunch", "date": date(2025,1,3)},
    {"user_id": 2, "category": "transport", "amount": 50.00, "description": "Bus ticket", "date": date(2025,1,3)},
    {"user_id": 3, "category": "fuel", "amount": 900.00, "description": "Bike petrol", "date": date(2025,1,4)},
    {"user_id": 4, "category": "entertainment", "amount": 300.00, "description": "Movie", "date": date(2025,1,4)},
    {"user_id": 5, "category": "groceries", "amount": 550.25, "description": "Vegetables", "date": date(2025,1,5)},

    {"user_id": 1, "category": "food", "amount": 200.00, "description": "Snacks", "date": date(2025,1,6)},
    {"user_id": 2, "category": "shopping", "amount": 1200.00, "description": "Clothes", "date": date(2025,1,7)},
    {"user_id": 3, "category": "mobile", "amount": 599.00, "description": "Recharge", "date": date(2025,1,7)},
    {"user_id": 4, "category": "internet", "amount": 950.00, "description": "JioFiber", "date": date(2025,1,8)},
    {"user_id": 5, "category": "gift", "amount": 400.00, "description": "Birthday gift", "date": date(2025,1,9)},

    {"user_id": 1, "category": "health", "amount": 150.00, "description": "Medicines", "date": date(2025,1,9)},
    {"user_id": 2, "category": "fuel", "amount": 600.00, "description": "Car petrol", "date": date(2025,1,10)},
    {"user_id": 3, "category": "food", "amount": 180.00, "description": "Breakfast", "date": date(2025,1,10)},
    {"user_id": 4, "category": "transport", "amount": 60.00, "description": "Metro ticket", "date": date(2025,1,11)},
    {"user_id": 5, "category": "food", "amount": 450.00, "description": "Dinner", "date": date(2025,1,11)},

    {"user_id": 1, "category": "shopping", "amount": 799.00, "description": "Headphones", "date": date(2025,1,12)},
    {"user_id": 2, "category": "groceries", "amount": 340.00, "description": "Fruits", "date": date(2025,1,12)},
    {"user_id": 3, "category": "entertainment", "amount": 500.00, "description": "Arcade games", "date": date(2025,1,13)},
    {"user_id": 4, "category": "health", "amount": 2000.00, "description": "Doctor visit", "date": date(2025,1,14)},
    {"user_id": 5, "category": "misc", "amount": 100.00, "description": "Tea & snacks", "date": date(2025,1,14)},
]
sample_users = [
    {"email": "user1@example.com", "password_hash": None},
    {"email": "user2@example.com", "password_hash": None},
    {"email": "user3@example.com", "password_hash": None},
    {"email": "user4@example.com", "password_hash": None},
    {"email": "user5@example.com", "password_hash": None},
]



db = sessionLocal()
for usr in sample_users:
    db.add(User(**usr))

for exp in sample_data:
    db.add(Expense(**exp))

db.commit()

# all users
all_users = db.query(User).all()
pretty_print_record(all_users)

# select records
print("\n\n")
all_expenses = db.query(Expense).all()
pretty_print_record(records=all_expenses)

print("\n\n")
# join tables
all_user_emails = (db.query(
            User.id.label("user_id"),
            User.email,
            Expense.id.label("expense_id"),
            Expense.description,
            Expense.amount
    ).join(Expense, onclause=User.id==Expense.user_id)
                   .order_by(Expense.amount.desc()).all())

for row in all_user_emails:
    print(row.user_id, row.email, row.expense_id, row.description, float(row.amount))
"""
print("\n\n")
food_expenses = db.query(Expense).filter(Expense.category == "food").all()
pretty_print_record(records=food_expenses)

print("\n\n")
date_expenses = db.query(Expense).filter(Expense.date >= date(2025, 1, 10)).all()
pretty_print_record(records=date_expenses)

print("\n\n")
food_date_expenses = db.query(Expense).filter(Expense.category == "food" and Expense.date >= date(2025, 1, 10)).all()
pretty_print_record(records=food_date_expenses)
"""