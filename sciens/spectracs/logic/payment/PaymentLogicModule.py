from datetime import datetime
from typing import Dict, List

from sciens.spectracs.logic.config.ServerConfig import ServerConfig
from sciens.spectracs.logic.payment.PayPalGateway import PayPalGateway, PayPalError
from sciens.spectracs.logic.persistence.database.payment.PersistTransactionLogicModule import \
    PersistTransactionLogicModule
from sciens.spectracs.logic.persistence.database.user.PersistUserLogicModule import PersistUserLogicModule
from sciens.spectracs.model.databaseEntity.application.payment.Transaction import Transaction
from sciens.spectracs.model.databaseEntity.application.payment.TransactionStatusType import TransactionStatusType


class PaymentLogicModule:
    """Server-side payment orchestration (PayPal Orders v2, sandbox). The amount is
    server-authoritative — the client never sends it (anti-tampering, D7). Returns plain dicts only,
    never a Transaction entity. Milestone 1 = a single one-off payment; see SPEC_paypal_payment.md.
    """

    DEFAULT_AMOUNT_MINOR = 100          # 1,00 EUR
    DEFAULT_CURRENCY = "EUR"
    DESCRIPTION = "Spectracs SaaS - sandbox test payment"

    def createPayment(self, userId) -> Dict:
        appUser = PersistUserLogicModule().findUserById(userId)
        if appUser is None:
            return {"ok": False, "message": "user not found"}
        if not appUser.enabled:
            return {"ok": False, "message": "user is disabled"}

        amountMinor = ServerConfig.getInt("PAYPAL_AMOUNT_MINOR", self.DEFAULT_AMOUNT_MINOR)
        currency = ServerConfig.get("PAYPAL_CURRENCY", self.DEFAULT_CURRENCY)

        try:
            orderId, approvalUrl = PayPalGateway().createOrder(amountMinor, currency, self.DESCRIPTION)
        except PayPalError as error:
            print("PaymentLogicModule.createPayment PayPal error: %s (%s)" % (error, error.detail))
            return {"ok": False, "message": "payment provider error: %s" % error}

        now = datetime.utcnow()
        transaction = Transaction()
        transaction.appUserId = appUser.id
        transaction.provider = "PAYPAL"
        transaction.providerOrderId = orderId
        transaction.amountMinor = amountMinor
        transaction.currency = currency
        transaction.status = TransactionStatusType.CREATED.value
        transaction.description = self.DESCRIPTION
        transaction.createdAt = now
        transaction.updatedAt = now
        PersistTransactionLogicModule().saveTransaction(transaction)

        return {"ok": True, "orderId": orderId, "approvalUrl": approvalUrl,
                "transactionId": transaction.id, "amountMinor": amountMinor,
                "currency": currency, "message": None}

    def capturePayment(self, userId, orderId) -> Dict:
        persist = PersistTransactionLogicModule()
        transaction = persist.findByOrderId(orderId)
        if transaction is None:
            return {"ok": False, "status": None, "message": "transaction not found"}
        if transaction.appUserId != userId:
            return {"ok": False, "status": None, "message": "transaction does not belong to user"}
        if transaction.status == TransactionStatusType.CAPTURED.value:
            return {"ok": True, "status": transaction.status, "message": None}  # idempotent

        try:
            response = PayPalGateway().captureOrder(orderId)
        except PayPalError as error:
            issue = self.__firstIssue(error.detail)
            if issue == "ORDER_ALREADY_CAPTURED":
                return self.__markCaptured(persist, transaction, captureId=None)
            if issue in ("ORDER_NOT_APPROVED", "PAYER_ACTION_REQUIRED"):
                # user has not approved in the browser yet -> keep CREATED so they can retry (RD3)
                return {"ok": False, "status": transaction.status, "message": "not approved yet"}
            print("PaymentLogicModule.capturePayment PayPal error: %s (%s)" % (error, error.detail))
            transaction.status = TransactionStatusType.FAILED.value
            transaction.updatedAt = datetime.utcnow()
            persist.updateTransaction(transaction)
            return {"ok": False, "status": transaction.status, "message": "capture failed"}

        if response.get("status") == "COMPLETED":
            return self.__markCaptured(persist, transaction, self.__extractCaptureId(response))

        transaction.updatedAt = datetime.utcnow()
        persist.updateTransaction(transaction)
        return {"ok": False, "status": transaction.status,
                "message": "unexpected status: %s" % response.get("status")}

    def listTransactions(self, userId) -> List[Dict]:
        return [self.__toDto(t) for t in PersistTransactionLogicModule().listByUser(userId)]

    # --- helpers ------------------------------------------------------------
    def __markCaptured(self, persist, transaction, captureId) -> Dict:
        transaction.status = TransactionStatusType.CAPTURED.value
        if captureId is not None:
            transaction.providerCaptureId = captureId
        transaction.updatedAt = datetime.utcnow()
        persist.updateTransaction(transaction)
        return {"ok": True, "status": transaction.status, "message": None}

    def __firstIssue(self, detail):
        if isinstance(detail, dict):
            details = detail.get("details")
            if isinstance(details, list) and details and isinstance(details[0], dict):
                return details[0].get("issue")
        return None

    def __extractCaptureId(self, response: Dict):
        try:
            return response["purchase_units"][0]["payments"]["captures"][0]["id"]
        except (KeyError, IndexError, TypeError):
            return None

    def __toDto(self, transaction: Transaction) -> Dict:
        createdAt = transaction.createdAt.isoformat() if transaction.createdAt is not None else None
        return {"id": transaction.id, "provider": transaction.provider,
                "providerOrderId": transaction.providerOrderId,
                "providerCaptureId": transaction.providerCaptureId,
                "amountMinor": transaction.amountMinor, "currency": transaction.currency,
                "status": transaction.status, "description": transaction.description,
                "createdAt": createdAt}
