from sqlalchemy import or_

from apps.suppliers.models import Supplier
from core.extensions import db


class SupplierService:

    @staticmethod
    def list_suppliers(user_id, search=""):

        query = Supplier.query.filter_by(
            user_id=user_id
        )

        search = (search or "").strip()

        if search:

            term = f"%{search}%"

            query = query.filter(
                or_(
                    Supplier.name.ilike(term),
                    Supplier.phone.ilike(term),
                    Supplier.email.ilike(term),
                    Supplier.gstin.ilike(term)
                )
            )

        return query.order_by(
            Supplier.name.asc(),
            Supplier.id.asc()
        ).all()

    @staticmethod
    def get_supplier(user_id, supplier_id):

        return Supplier.query.filter_by(
            id=supplier_id,
            user_id=user_id
        ).first()

    @staticmethod
    def create_supplier(
        user_id,
        name,
        phone,
        email,
        gstin,
        address,
        notes
    ):

        supplier = Supplier(
            user_id=user_id,
            name=name,
            phone=phone or None,
            email=email or None,
            gstin=gstin or None,
            address=address or None,
            notes=notes or None
        )

        db.session.add(supplier)
        db.session.commit()

        return supplier

    @staticmethod
    def update_supplier(
        supplier,
        name,
        phone,
        email,
        gstin,
        address,
        notes
    ):

        supplier.name = name
        supplier.phone = phone or None
        supplier.email = email or None
        supplier.gstin = gstin or None
        supplier.address = address or None
        supplier.notes = notes or None

        db.session.commit()

        return supplier

    @staticmethod
    def delete_supplier(supplier):

        db.session.delete(supplier)
        db.session.commit()
