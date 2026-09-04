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
    def _validate_customer(user_id, customer_id):
        if not customer_id:
            return None

        customer = Customer.query.filter_by(
            id=customer_id,
            user_id=user_id
        ).first()

        if not customer:
            raise ValueError("Customer not found.")

        return customer

    @staticmethod
    def _build_item(product, item, sale_number):
        try:
            quantity = Decimal(str(item["quantity"]))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Enter a valid quantity for {product.name}.")

        if quantity <= 0:
            raise ValueError(f"Quantity must be greater than zero for {product.name}.")

        try:
            unit_price = _money(item["unit_price"])
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Enter a valid selling price for {product.name}.")

        if unit_price < 0:
            raise ValueError(f"Selling price cannot be negative for {product.name}.")

        gst_rate = Decimal(product.gst_rate or 0)
        line_subtotal = _money(quantity * unit_price)
        line_tax = _money(line_subtotal * gst_rate / Decimal("100"))
        line_total = _money(line_subtotal + line_tax)

        return {
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "gst_rate": gst_rate,
            "line_subtotal": line_subtotal,
            "line_tax": line_tax,
            "line_total": line_total,
        }

    @staticmethod
    def create_sale(user_id, customer_id, sale_date, items, notes=""):
        SalesService._validate_customer(user_id, customer_id)

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
                product = Product.query.filter_by(
                    id=product_id,
                    user_id=user_id
                ).first()

                if not product:
                    raise ValueError("One of the selected products was not found.")

                calculated = SalesService._build_item(
                    product,
                    item,
                    sale.sale_number
                )

                InventoryService.stock_out(
                    user_id=user_id,
                    product_id=product.id,
                    quantity=calculated["quantity"],
                    reason=f"Sale {sale.sale_number}"
                )

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit=product.unit,
                    quantity=calculated["quantity"],
                    unit_price=calculated["unit_price"],
                    gst_rate=calculated["gst_rate"],
                    tax_amount=calculated["line_tax"],
                    line_total=calculated["line_total"]
                )
                db.session.add(sale_item)

                subtotal += calculated["line_subtotal"]
                tax_amount += calculated["line_tax"]

            sale.subtotal = _money(subtotal)
            sale.tax_amount = _money(tax_amount)
            sale.total_amount = _money(subtotal + tax_amount)

            db.session.commit()
            return sale

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_sale(user_id, sale_id, customer_id, sale_date, items, notes=""):
        sale = SalesService.get_sale(user_id, sale_id)
        if not sale:
            raise ValueError("Sale not found.")

        SalesService._validate_customer(user_id, customer_id)

        # Lock the parent row so two edits cannot safely mutate the same sale
        # at the same time.
        sale = (
            Sale.query
            .options(db.lazyload(Sale.customer))
            .filter_by(id=sale_id, user_id=user_id)
            .with_for_update(of=Sale)
            .first()
        )
        if not sale:
            raise ValueError("Sale not found.")

        try:
            # Validate and calculate everything before changing inventory.
            calculated_items = []
            subtotal = Decimal("0")
            tax_amount = Decimal("0")

            for item in items:
                product_id = int(item["product_id"])
                product = Product.query.filter_by(
                    id=product_id,
                    user_id=user_id
                ).first()

                if not product:
                    raise ValueError("One of the selected products was not found.")

                calculated = SalesService._build_item(
                    product,
                    item,
                    sale.sale_number
                )
                calculated_items.append(calculated)
                subtotal += calculated["line_subtotal"]
                tax_amount += calculated["line_tax"]

            # Return the previous sale quantities first. This makes an edit
            # from 10 -> 15 work correctly even when only 10 were originally
            # available before the sale.
            old_items = list(sale.items)
            for old_item in old_items:
                InventoryService.stock_in(
                    user_id=user_id,
                    product_id=old_item.product_id,
                    quantity=Decimal(old_item.quantity),
                    reason=f"Edit Sale {sale.sale_number} - return previous quantity"
                )

            # Remove stock for the new version of the sale.
            for calculated in calculated_items:
                InventoryService.stock_out(
                    user_id=user_id,
                    product_id=calculated["product"].id,
                    quantity=calculated["quantity"],
                    reason=f"Edit Sale {sale.sale_number}"
                )

            sale.customer_id = customer_id or None
            sale.sale_date = sale_date
            sale.notes = notes or None
            sale.subtotal = _money(subtotal)
            sale.tax_amount = _money(tax_amount)
            sale.total_amount = _money(subtotal + tax_amount)

            # Replace the old item snapshots with the new version.
            sale.items.clear()

            for calculated in calculated_items:
                sale.items.append(
                    SaleItem(
                        product_id=calculated["product"].id,
                        product_name=calculated["product"].name,
                        unit=calculated["product"].unit,
                        quantity=calculated["quantity"],
                        unit_price=calculated["unit_price"],
                        gst_rate=calculated["gst_rate"],
                        tax_amount=calculated["line_tax"],
                        line_total=calculated["line_total"]
                    )
                )

            db.session.commit()
            return sale

        except Exception:
            db.session.rollback()
            raise
