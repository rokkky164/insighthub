from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE,
    SET_NULL,
    DecimalField,
    IntegerField,
    TextField,
    EmailField,
)
from django.core.validators import MinValueValidator
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from common.models import GenericModel
from products.models import Product


class Sale(GenericModel):
    customer = ForeignKey(
        "Customer", on_delete=SET_NULL, null=True, blank=True, related_name="sales"
    )
    sale_date = DateTimeField(auto_now_add=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("card", "Card"), ("online", "Online Payment")],
    )

    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"

    def create_journal_entry(self):
        """Auto create a journal entry for this sale"""

        # 1. Get business via customer
        business = self.customer.business if self.customer else None
        if not business:
            return

        # 2. Create journal entry
        journal = JournalEntry.objects.create(
            business=business,
            description=f"Sale #{self.id} - {self.payment_method}",
            reference=f"sale_{self.id}",
        )

        # 3. Choose accounts
        # NOTE: in real-world SaaS, these accounts should be configurable per business
        if self.payment_method == "cash":
            debit_account = Account.objects.get(business=business, code="1001")  # Cash
        elif self.payment_method == "card":
            debit_account = Account.objects.get(
                business=business, code="1002"
            )  # Bank/Card Clearing
        else:
            debit_account = Account.objects.get(
                business=business, code="1003"
            )  # Online Wallet/Payment Gateway

        credit_account = Account.objects.get(
            business=business, code="4001"
        )  # Sales Revenue

        # 4. Create ledger entries (double entry)
        LedgerEntry.objects.create(
            journal_entry=journal,
            account=debit_account,
            debit=self.total_amount,
            credit=0,
        )
        LedgerEntry.objects.create(
            journal_entry=journal,
            account=credit_account,
            debit=0,
            credit=self.total_amount,
        )


class SaleItem(GenericModel):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name="items")
    product = ForeignKey(
        Product, on_delete=SET_NULL, null=True, blank=True, related_name="sale_items"
    )
    quantity = IntegerField(default=1, validators=[MinValueValidator(1)])
    price = DecimalField(
        max_digits=12, decimal_places=2
    )  # unit price at the time of sale
    subtotal = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])  # quantity * price

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Invoice(GenericModel):
    sale = OneToOneField(Sale, on_delete=CASCADE, related_name="invoice")
    invoice_number = CharField(max_length=50, unique=True)
    issued_on = DateTimeField(auto_now_add=True)
    due_date = DateTimeField(null=True, blank=True)
    status = CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
            ("partially_paid", "Partially Paid"),
        ],
        default="paid",
    )


class Payment(GenericModel):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name="payments")
    amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    method = CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("card", "Card"), ("online", "Online Payment")],
    )
    paid_on = DateTimeField(auto_now_add=True)


class Discount(GenericModel):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name="discounts")
    description = CharField(max_length=100)
    amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])


class Tax(GenericModel):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name="taxes")
    name = CharField(max_length=50)
    rate = DecimalField(max_digits=5, decimal_places=2)  # %
    amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])


class SaleReturn(GenericModel):
    sale_item = ForeignKey(SaleItem, on_delete=CASCADE, related_name="returns")
    quantity = IntegerField()
    reason = TextField(blank=True, null=True)
    refunded_amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])


class Account(GenericModel):
    business = ForeignKey("Business", on_delete=CASCADE, related_name="accounts")
    name = CharField(max_length=100)
    code = CharField(max_length=20, unique=True)  # e.g., 1001 = Cash
    type = CharField(
        max_length=20,
        choices=[
            ("asset", "Asset"),
            ("liability", "Liability"),
            ("equity", "Equity"),
            ("income", "Income"),
            ("expense", "Expense"),
        ],
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(GenericModel):
    business = ForeignKey("Business", on_delete=CASCADE, related_name="journal_entries")
    date = DateTimeField(auto_now_add=True)
    description = CharField(max_length=255, blank=True, null=True)
    reference = CharField(
        max_length=100, blank=True, null=True
    )  # e.g., Sale ID, Invoice No.

    def __str__(self):
        return f"JournalEntry #{self.id} - {self.date.date()}"


class LedgerEntry(GenericModel):
    journal_entry = ForeignKey(JournalEntry, on_delete=CASCADE, related_name="entries")
    account = ForeignKey(Account, on_delete=CASCADE, related_name="entries")
    debit = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    credit = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.account.name} | Debit: {self.debit} | Credit: {self.credit}"


class Purchase(GenericModel):
    business = ForeignKey("Business", on_delete=CASCADE, related_name="purchases")
    purchase_date = DateTimeField(auto_now_add=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    description = CharField(max_length=255, blank=True, null=True)
    payment_method = CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("credit", "Credit"), ("online", "Online Payment")],
    )

    def __str__(self):
        return f"Purchase #{self.id} - {self.total_amount}"

    def create_journal_entry(self):
        journal = JournalEntry.objects.create(
            business=self.business,
            description=f"Purchase #{self.id} - {self.payment_method}",
            reference=f"purchase_{self.id}",
        )

        # Debit: Inventory (Asset)
        debit_account = Account.objects.get(
            business=self.business, code="1201"
        )  # Inventory

        # Credit: Cash/Bank/Payables
        if self.payment_method == "cash":
            credit_account = Account.objects.get(business=self.business, code="1001")
        elif self.payment_method == "online":
            credit_account = Account.objects.get(business=self.business, code="1003")
        else:  # credit purchase
            credit_account = Account.objects.get(business=self.business, code="2001")

        # Double entry
        LedgerEntry.objects.create(
            journal_entry=journal,
            account=debit_account,
            debit=self.total_amount,
            credit=0,
        )
        LedgerEntry.objects.create(
            journal_entry=journal,
            account=credit_account,
            debit=0,
            credit=self.total_amount,
        )


class Expense(GenericModel):
    business = ForeignKey("Business", on_delete=CASCADE, related_name="expenses")
    expense_date = DateTimeField(auto_now_add=True)
    description = CharField(max_length=255)
    amount = DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    category = CharField(
        max_length=50,
        choices=[
            ("rent", "Rent"),
            ("salary", "Salary"),
            ("utilities", "Utilities"),
            ("other", "Other"),
        ],
    )
    payment_method = CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("card", "Card"), ("online", "Online Payment")],
    )

    def __str__(self):
        return f"Expense #{self.id} - {self.amount}"

    def create_journal_entry(self):
        """Auto create a journal entry for this expense"""

        try:
            with transaction.atomic():
                journal = JournalEntry.objects.create(
                    business=self.business,
                    description=f"Expense {self.category} - {self.amount}",
                    reference=f"expense_{self.id}",
                )

                # Debit: Expense Account (5002)
                try:
                    debit_account = Account.objects.get(business=self.business, code="5002")
                except ObjectDoesNotExist:
                    raise ValueError("Expense account (5002) not configured for this business.")
                except MultipleObjectsReturned:
                    raise ValueError("Multiple expense accounts (5002) found for this business.")

                # Credit: Cash/Bank/Other
                try:
                    if self.payment_method == "cash":
                        credit_account = Account.objects.get(business=self.business, code="1001")
                    elif self.payment_method == "card":
                        credit_account = Account.objects.get(business=self.business, code="1002")
                    else:
                        credit_account = Account.objects.get(business=self.business, code="1003")
                except ObjectDoesNotExist:
                    raise ValueError(f"Payment method account not configured for {self.payment_method}.")
                except MultipleObjectsReturned:
                    raise ValueError(f"Multiple accounts found for {self.payment_method} payments.")

                # Double-entry postings
                LedgerEntry.objects.create(
                    journal_entry=journal, account=debit_account, debit=self.amount, credit=0
                )
                LedgerEntry.objects.create(
                    journal_entry=journal, account=credit_account, debit=0, credit=self.amount
                )

                return journal

        except Exception as e:
            # Log error or re-raise
            raise RuntimeError(f"Failed to create journal entry for expense {self.id}: {e}")