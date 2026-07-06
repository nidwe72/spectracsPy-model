from typing import List, Optional

from sciens.spectracs.model.databaseEntity.DbServerBase import server_session_factory
from sciens.spectracs.model.databaseEntity.application.payment.Transaction import Transaction
# Ensure the FK target `app_user` is registered on the ServerDbBaseEntity metadata before
# create_all() builds the `transaction` table (Transaction.appUserId -> app_user.id). Without this
# import the FK could fail to resolve if no user code has been loaded yet. (noqa: F401 — import for
# side effect / metadata registration only.)
from sciens.spectracs.model.databaseEntity.application.user.AppUser import AppUser  # noqa: F401


class PersistTransactionLogicModule:
    """Server-DB persistence for Transaction. Importing Transaction here registers it on the
    ServerDbBaseEntity metadata, so `server_session_factory()`'s create_all() builds the table
    (mirrors PersistUserLogicModule). SPEC_paypal_payment.md §4.1/§4.2.
    """

    def saveTransaction(self, transaction: Transaction):
        session = server_session_factory()
        session.add(transaction)
        session.commit()

    def updateTransaction(self, transaction: Transaction):
        session = server_session_factory()
        session.merge(transaction)
        session.commit()

    def findByOrderId(self, providerOrderId: str) -> Optional[Transaction]:
        session = server_session_factory()
        return session.query(Transaction).filter(
            Transaction.providerOrderId == providerOrderId).first()

    def listByUser(self, appUserId: str) -> List[Transaction]:
        # Newest first (createdAt desc) for the account-screen table.
        session = server_session_factory()
        return session.query(Transaction).filter(
            Transaction.appUserId == appUserId).order_by(Transaction.createdAt.desc()).all()
