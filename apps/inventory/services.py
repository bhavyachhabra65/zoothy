from decimal import Decimal

from sqlalchemy import or_

from apps.inventory.models import InventoryMovement, InventoryStock
from apps.products.models import Product
from core.extensions import db


class InventoryService:

    @staticmethod
    def list_inventory(user_id, search=""):

        query = (
            db.session.query(Product, InventoryStock)
            .outerjoin(
                InventoryStock,
                (InventoryStock.product_id == Product.id)
                & (InventoryStock.user_id == user_id)
            )
            .filter(
                Product.user_id == user_id
            )
        )

        search = (search or "").strip()

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(term),
                    Product.sku.ilike(term),
                    Product.unit.ilike(term)
                )
            )

        rows = query.order_by(
            Product.name.asc(),
            Product.id.asc()
        ).all()

        return [
            {
                "product": product,
                "stock": stock,
                "quantity": Decimal(stock.quantity if stock else 0),
                "low_stock_level": Decimal(
                    stock.low_stock_level if stock else 0
                )
            }
            for product, stock in rows
        ]

    @staticmethod
    def get_product_inventory(user_id, product_id):

        product = Product.query.filter_by(
            id=product_id,
            user_id=user_id
        ).first()

        if not product:
            return None

        stock = InventoryStock.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        return {
            "product": product,
            "stock": stock,
            "quantity": Decimal(stock.quantity if stock else 0),
            "low_stock_level": Decimal(
                stock.low_stock_level if stock else 0
            )
        }

    @staticmethod
    def get_movements(user_id, product_id):

        return (
            InventoryMovement.query
            .filter_by(
                user_id=user_id,
                product_id=product_id
            )
            .order_by(
                InventoryMovement.created_at.desc(),
                InventoryMovement.id.desc()
            )
            .all()
        )

    @staticmethod
    def initialize_opening_stock(user_id, product_id, quantity):
        """Create the initial inventory balance and opening movement.

        This method intentionally does not commit. Product creation and
        inventory initialization must be committed together by the caller.
        """

        quantity = Decimal(quantity or 0)

        if quantity <= 0:
            return None

        product = Product.query.filter_by(
            id=product_id,
            user_id=user_id
        ).first()

        if not product:
            raise ValueError("Product not found.")

        stock = InventoryStock.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).with_for_update().first()

        if stock:
            raise ValueError(
                "Opening stock has already been initialized for this product."
            )

        opening_movement = InventoryMovement.query.filter_by(
            user_id=user_id,
            product_id=product_id,
            movement_type="opening"
        ).first()

        if opening_movement:
            raise ValueError(
                "Opening stock has already been initialized for this product."
            )

        stock = InventoryStock(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            low_stock_level=Decimal("0")
        )

        movement = InventoryMovement(
            user_id=user_id,
            product_id=product_id,
            movement_type="opening",
            quantity=quantity,
            resulting_quantity=quantity,
            reason="Opening stock"
        )

        db.session.add(stock)
        db.session.add(movement)
        db.session.flush()

        return stock

    @staticmethod
    def adjust_stock(
        user_id,
        product_id,
        movement_type,
        quantity,
        reason,
        low_stock_level
    ):

        product = Product.query.filter_by(
            id=product_id,
            user_id=user_id
        ).first()

        if not product:
            return None

        quantity = Decimal(quantity)
        low_stock_level = Decimal(low_stock_level or 0)

        stock = InventoryStock.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).with_for_update().first()

        if not stock:
            stock = InventoryStock(
                user_id=user_id,
                product_id=product_id,
                quantity=Decimal("0"),
                low_stock_level=low_stock_level
            )
            db.session.add(stock)
            db.session.flush()

        current_quantity = Decimal(stock.quantity or 0)

        if movement_type == "add":
            new_quantity = current_quantity + quantity
        else:
            new_quantity = current_quantity - quantity

        if new_quantity < 0:
            raise ValueError(
                f"Only {current_quantity} {product.unit} is available."
            )

        stock.quantity = new_quantity
        stock.low_stock_level = low_stock_level

        movement = InventoryMovement(
            user_id=user_id,
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            resulting_quantity=new_quantity,
            reason=reason
        )

        db.session.add(movement)
        db.session.commit()

        return stock

    @staticmethod
    def stock_out(user_id, product_id, quantity, reason):
        """Remove stock inside the caller's transaction; never commit here."""
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if not product:
            raise ValueError("Product not found.")
        quantity = Decimal(quantity)
        if quantity <= 0:
            raise ValueError("Stock-out quantity must be greater than zero.")
        stock = InventoryStock.query.filter_by(user_id=user_id, product_id=product_id).with_for_update().first()
        if not stock:
            raise ValueError(f"Only 0 {product.unit} is available for {product.name}.")
        current_quantity = Decimal(stock.quantity or 0)
        new_quantity = current_quantity - quantity
        if new_quantity < 0:
            raise ValueError(f"Only {current_quantity} {product.unit} is available for {product.name}.")
        stock.quantity = new_quantity
        db.session.add(InventoryMovement(user_id=user_id, product_id=product_id, movement_type="remove", quantity=quantity, resulting_quantity=new_quantity, reason=reason))
        db.session.flush()
        return stock

    @staticmethod
    def stock_in(user_id, product_id, quantity, reason=None):
        quantity = Decimal(str(quantity))

        if quantity <= 0:
            raise ValueError("Stock-in quantity must be greater than zero.")

        stock = (
            InventoryStock.query
            .filter_by(
                user_id=user_id,
                product_id=product_id
            )
            .with_for_update()
            .first()
        )

        if not stock:
            stock = InventoryStock(
                user_id=user_id,
                product_id=product_id,
                quantity=Decimal("0")
            )
            db.session.add(stock)
            db.session.flush()

        stock.quantity = stock.quantity + quantity

        movement = InventoryMovement(
            user_id=user_id,
            product_id=product_id,
            movement_type="add",
            quantity=quantity,
            resulting_quantity=stock.quantity,
            reason=reason
        )

        db.session.add(movement)

        return stock

    @staticmethod
    def update_low_stock_level(
        user_id,
        product_id,
        low_stock_level
    ):

        stock = InventoryStock.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        if not stock:
            stock = InventoryStock(
                user_id=user_id,
                product_id=product_id,
                quantity=Decimal("0"),
                low_stock_level=Decimal(low_stock_level or 0)
            )
            db.session.add(stock)
        else:
            stock.low_stock_level = Decimal(low_stock_level or 0)

        db.session.commit()

        return stock
