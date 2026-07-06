from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from sciens.spectracs.model.databaseEntity.DbBase import DbBaseEntityMixin
from sciens.spectracs.model.databaseEntity.DbServerBase import ServerDbBaseEntity


class Transaction(ServerDbBaseEntity, DbBaseEntityMixin):
    """A payment record — lives on the SERVER DB (spectracsPyServer.db), alongside AppUser. Money is
    server-authoritative; it never lives on the app's on-device DB. The amount is stored as INTEGER
    MINOR UNITS (100 = 1,00 EUR) to avoid float rounding. Table name derives to `transaction`.
    See SPEC_paypal_payment.md §4.1.
    """

    # FK to AppUser (same declarative base / same DB file -> the FK resolves). AppUser -> `app_user`.
    appUserId = Column(String, ForeignKey("app_user.id"))

    provider = Column(String, default="PAYPAL")     # future-proof for other gateways
    providerOrderId = Column(String)                # PayPal order id (from createOrder)
    providerCaptureId = Column(String)              # PayPal capture id (from captureOrder), nullable

    amountMinor = Column(Integer)                   # 100 = 1,00 EUR (integer minor units)
    currency = Column(String, default="EUR")

    status = Column(String)                         # a TransactionStatusType value
    description = Column(String)

    createdAt = Column(DateTime)                    # set server-side at create
    updatedAt = Column(DateTime)                    # set server-side at create + capture
