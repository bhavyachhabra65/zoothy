from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_required
)


from apps.settings.services import (
    SettingsService
)

from apps.settings.validators import (
    validate_business_settings
)


settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


# ==========================================================
# SETTINGS
# ==========================================================

@settings_bp.get("/")
@login_required
def index():

    business = SettingsService.get_business(
        current_user.id
    )

    return render_template(
        "settings/settings.html",
        business=business
    )


@settings_bp.post("/")
@login_required
def save():

    business_name = request.form.get(
        "business_name",
        ""
    )

    phone = request.form.get(
        "phone",
        ""
    )

    gstin = request.form.get(
        "gstin",
        ""
    )

    address = request.form.get(
        "address",
        ""
    )

    error = validate_business_settings(
        business_name,
        phone,
        gstin,
        address
    )

    if error:

        business = SettingsService.get_business(
            current_user.id
        )

        return render_template(
            "settings/settings.html",
            business=business,
            error=error,
            form_data={
                "business_name": business_name,
                "phone": phone,
                "gstin": gstin,
                "address": address
            }
        ), 400


    SettingsService.save_business(
        current_user.id,
        business_name.strip(),
        phone.strip(),
        gstin.strip().upper(),
        address.strip()
    )

    flash(
        "Your information was saved successfully.",
        "success"
    )

    return redirect(
        url_for("settings.index")
    )