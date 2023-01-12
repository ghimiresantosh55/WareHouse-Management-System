from src.core_app.models import Country, FiscalSessionAD, FiscalSessionBS
from src.core_app.models import OrganizationSetup, OrganizationRule, PaymentMode
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs


def check_setup() -> bool:
    current_fiscal_session_short_ad = get_fiscal_year_code_ad()
    current_fiscal_session_short_bs = get_fiscal_year_code_bs()
    try:
        fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
        fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
        country = Country.objects.first()
        organization_rule = OrganizationRule.objects.first()
        organization_setup = OrganizationSetup.objects.first()
        payment_mode = PaymentMode.objects.first()
        if country and organization_rule and organization_setup and payment_mode:
            return True
        else:
            return False
    except Exception as e:
        return False
