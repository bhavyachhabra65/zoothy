from apps.settings.models import Business
from core.extensions import db


class SettingsService:

    @staticmethod
    def get_business(user_id):

        return Business.query.filter_by(
            user_id=user_id
        ).first()

    @staticmethod
    def save_business(
        user_id,
        business_name,
        phone,
        gstin,
        address
    ):

        business = Business.query.filter_by(
            user_id=user_id
        ).first()

        if not business:

            business = Business(
                user_id=user_id
            )

            db.session.add(business)

        business.business_name = business_name
        business.phone = phone
        business.gstin = gstin
        business.address = address

        db.session.commit()

        return business