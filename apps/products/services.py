from decimal import Decimal

from sqlalchemy import or_

from apps.products.models import Product
from core.extensions import db


class ProductService:

    @staticmethod
    def list_products(user_id, search=""):

        query = Product.query.filter_by(
            user_id=user_id
        )

        search = (search or "").strip()

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(term),
                    Product.sku.ilike(term),
                    Product.hsn_sac.ilike(term),
                    Product.unit.ilike(term)
                )
            )

        return query.order_by(
            Product.name.asc(),
            Product.id.asc()
        ).all()

    @staticmethod
    def get_product(user_id, product_id):

        return Product.query.filter_by(
            id=product_id,
            user_id=user_id
        ).first()

    @staticmethod
    def create_product(
        user_id,
        name,
        sku,
        hsn_sac,
        unit,
        purchase_price,
        selling_price,
        gst_rate,
        description,
        opening_stock="0"
    ):

        opening_stock = Decimal(opening_stock or 0)

        product = Product(
            user_id=user_id,
            name=name,
            sku=sku or None,
            hsn_sac=hsn_sac or None,
            unit=unit,
            purchase_price=purchase_price or 0,
            selling_price=selling_price or 0,
            gst_rate=gst_rate or 0,
            opening_stock=opening_stock,
            description=description or None
        )

        db.session.add(product)
        db.session.flush()

        # Opening stock is recorded in Inventory at product creation time.
        # The import is intentionally local to avoid a module-level circular import.
        if opening_stock > 0:
            from apps.inventory.services import InventoryService

            InventoryService.initialize_opening_stock(
                user_id=user_id,
                product_id=product.id,
                quantity=opening_stock
            )

        db.session.commit()

        return product

    @staticmethod
    def update_product(
        product,
        name,
        sku,
        hsn_sac,
        unit,
        purchase_price,
        selling_price,
        gst_rate,
        description
    ):

        product.name = name
        product.sku = sku or None
        product.hsn_sac = hsn_sac or None
        product.unit = unit
        product.purchase_price = purchase_price or 0
        product.selling_price = selling_price or 0
        product.gst_rate = gst_rate or 0
        product.description = description or None

        db.session.commit()

        return product

    @staticmethod
    def delete_product(product):

        db.session.delete(product)
        db.session.commit()
