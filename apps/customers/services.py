from sqlalchemy import or_

from apps.customers.models import Customer
from core.extensions import db


class CustomerService:

    @staticmethod
    def list_customers(user_id, search=""):

        query = Customer.query.filter_by(
            user_id=user_id
        )

        search = (search or "").strip()

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(term),
                    Customer.phone.ilike(term),
                    Customer.email.ilike(term),
                    Customer.gstin.ilike(term)
                )
            )

        return query.order_by(
            Customer.name.asc(),
            Customer.id.asc()
        ).all()

    @staticmethod
    def get_customer(user_id, customer_id):

        return Customer.query.filter_by(
            id=customer_id,
            user_id=user_id
        ).first()

    @staticmethod
    def create_customer(
        user_id,
        name,
        phone,
        email,
        gstin,
        address,
        notes
    ):

        customer = Customer(
            user_id=user_id,
            name=name,
            phone=phone or None,
            email=email or None,
            gstin=gstin or None,
            address=address or None,
            notes=notes or None
        )

        db.session.add(customer)
        db.session.commit()

        return customer

    @staticmethod
    def update_customer(
        customer,
        name,
        phone,
        email,
        gstin,
        address,
        notes
    ):

        customer.name = name
        customer.phone = phone or None
        customer.email = email or None
        customer.gstin = gstin or None
        customer.address = address or None
        customer.notes = notes or None

        db.session.commit()

        return customer

    @staticmethod
    def delete_customer(customer):

        db.session.delete(customer)
        db.session.commit()
