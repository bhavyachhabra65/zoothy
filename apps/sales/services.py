from datetime import date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from sqlalchemy import or_

from apps.customers.models import Customer
from apps.inventory.services import InventoryService
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem
from core.extensions import db


MONEY_QUANT = Decimal("0.01")


def _money(value):
    return Decimal(value or 0).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class SalesService:

    @staticmethod
    def list_sales(user_id, search=""):
        query = Sale.query.filter_by(user_id=user_id)

        search = (search or "").strip()
        if search:
            term = f"%{search}%"
            query = query.outerjoin(
                Customer,
                Customer.id == Sale.customer_id
            ).filter(
                or_(
                    Sale.sale_number.ilike(term),
                    Customer.name.ilike(term)
                )
            )

        return query.order_by(
            Sale.sale_date.desc(),
            Sale.id.desc()
        ).all()

    @staticmethod
    def get_sale(user_id, sale_id):
        return Sale.query.filter_by(
            id=sale_id,
            user_id=user_id
        ).first()

    @staticmethod
    def _next_sale_number(user_id):
        last_sale = Sale.query.filter_by(
            user_id=user_id
        ).order_by(
            Sale.id.desc()
        ).first()

        next_number = (last_sale.id + 1) if last_sale else 1
        return f"SAL-{next_number:06d}"

    @staticmethod
    def create_sale(user_id, customer_id, sale_date, items, notes=""):
        if customer_id:
            customer = Customer.query.filter_by(
                id=customer_id,
                user_id=user_id
            ).first()
            if not customer:
                raise ValueError("Customer not found.")

        sale = Sale(
            user_id=user_id,
            customer_id=customer_id or None,
            sale_number=SalesService._next_sale_number(user_id),
            sale_date=sale_date,
            subtotal=Decimal("0"),
            tax_amount=Decimal("0"),
            total_amount=Decimal("0"),
            notes=notes or None
        )
        db.session.add(sale)
        db.session.flush()

        subtotal = Decimal("0")
        tax_amount = Decimal("0")

        try:
            for item in items:
                product_id = int(item["product_id"])
                quantity = Decimal(str(item["quantity"]))
                unit_price = _money(item["unit_price"])

                product = Product.query.filter_by(
                    id=product_id,
                    user_id=user_id
                ).first()

                if not product:
                    raise ValueError("One of the selected products was not found.")

                gst_rate = Decimal(product.gst_rate or 0)
                line_subtotal = _money(quantity * unit_price)
                line_tax = _money(line_subtotal * gst_rate / Decimal("100"))
                line_total = line_subtotal + line_tax

                InventoryService.stock_out(
                    user_id=user_id,
                    product_id=product.id,
                    quantity=quantity,
                    reason=f"Sale {sale.sale_number}"
                )

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit=product.unit,
                    quantity=quantity,
                    unit_price=unit_price,
                    gst_rate=gst_rate,
                    tax_amount=line_tax,
                    line_total=line_total
                )
                db.session.add(sale_item)

                subtotal += line_subtotal
                tax_amount += line_tax

            sale.subtotal = _money(subtotal)
            sale.tax_amount = _money(tax_amount)
            sale.total_amount = _money(subtotal + tax_amount)

            db.session.commit()
            return sale

        except Exception:
            db.session.rollback()
            raise
