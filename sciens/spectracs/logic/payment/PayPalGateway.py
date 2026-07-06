import base64
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple

from sciens.spectracs.logic.config.ServerConfig import ServerConfig


class PayPalError(Exception):
    """Raised on any PayPal REST failure. `detail` holds the parsed error body when available."""

    def __init__(self, message: str, detail=None):
        super().__init__(message)
        self.detail = detail


class PayPalGateway:
    """Thin PayPal Orders v2 (Checkout) client — sandbox first. Credentials come from the server
    `.env` via ServerConfig; the client/APK never sees them (SPEC_paypal_payment.md §4.2 / D4).

    Stdlib-only HTTP (urllib) — no `requests`/`httpx` (not in the app venv the server reuses). The
    OAuth access token is cached in-process until shortly before expiry (RD11).
    """

    _accessToken: Optional[str] = None
    _tokenExpiryEpoch: float = 0.0

    # --- config accessors ---------------------------------------------------
    def apiBase(self) -> str:
        return ServerConfig.get("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com").rstrip("/")

    def _clientId(self) -> str:
        return ServerConfig.get("PAYPAL_CLIENT_ID", "") or ""

    def _clientSecret(self) -> str:
        return ServerConfig.get("PAYPAL_CLIENT_SECRET", "") or ""

    def _payeeEmail(self) -> Optional[str]:
        return ServerConfig.get("PAYPAL_PAYEE_EMAIL", None)

    def _payeeMerchantId(self) -> Optional[str]:
        return ServerConfig.get("PAYPAL_PAYEE_MERCHANT_ID", None)

    def _returnUrl(self) -> str:
        return ServerConfig.get("PAYPAL_RETURN_URL", "https://example.com/paypal/return")

    def _cancelUrl(self) -> str:
        return ServerConfig.get("PAYPAL_CANCEL_URL", "https://example.com/paypal/cancel")

    # --- auth ---------------------------------------------------------------
    def getAccessToken(self) -> str:
        if PayPalGateway._accessToken is not None and time.time() < PayPalGateway._tokenExpiryEpoch:
            return PayPalGateway._accessToken

        clientId = self._clientId()
        clientSecret = self._clientSecret()
        if not clientId or not clientSecret:
            raise PayPalError("PayPal credentials missing (PAYPAL_CLIENT_ID/SECRET in server .env)")

        credentials = base64.b64encode(("%s:%s" % (clientId, clientSecret)).encode("utf-8")).decode("ascii")
        headers = {
            "Authorization": "Basic %s" % credentials,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
        response = self._request("POST", self.apiBase() + "/v1/oauth2/token", headers, data)

        token = response.get("access_token")
        if not token:
            raise PayPalError("PayPal token response had no access_token", response)
        expiresIn = int(response.get("expires_in", 300))
        PayPalGateway._accessToken = token
        PayPalGateway._tokenExpiryEpoch = time.time() + max(0, expiresIn - 60)  # refresh 60s early
        return token

    def _authHeaders(self) -> Dict[str, str]:
        return {"Authorization": "Bearer %s" % self.getAccessToken(), "Content-Type": "application/json"}

    # --- orders -------------------------------------------------------------
    @staticmethod
    def formatAmount(amountMinor: int) -> str:
        # integer minor units -> PayPal 2-decimal string (EUR has 2 minor digits). 100 -> "1.00".
        amountMinor = int(amountMinor)
        sign = "-" if amountMinor < 0 else ""
        amountMinor = abs(amountMinor)
        return "%s%d.%02d" % (sign, amountMinor // 100, amountMinor % 100)

    def createOrder(self, amountMinor: int, currency: str, description: str) -> Tuple[str, str]:
        purchaseUnit = {
            "amount": {"currency_code": currency, "value": self.formatAmount(amountMinor)},
            "description": description,
        }
        if self._payeeEmail() is not None:
            purchaseUnit["payee"] = {"email_address": self._payeeEmail()}
        elif self._payeeMerchantId() is not None:
            purchaseUnit["payee"] = {"merchant_id": self._payeeMerchantId()}

        body = {
            "intent": "CAPTURE",
            "purchase_units": [purchaseUnit],
            "application_context": {
                "return_url": self._returnUrl(),
                "cancel_url": self._cancelUrl(),
                "user_action": "PAY_NOW",
                "brand_name": "Spectracs",
            },
        }
        response = self._request("POST", self.apiBase() + "/v2/checkout/orders",
                                 self._authHeaders(), json.dumps(body).encode("utf-8"))
        orderId = response.get("id")
        if not orderId:
            raise PayPalError("PayPal createOrder returned no id", response)
        approvalUrl = None
        for link in response.get("links", []):
            if link.get("rel") == "approve":
                approvalUrl = link.get("href")
                break
        if approvalUrl is None:
            raise PayPalError("PayPal createOrder returned no approval link", response)
        return orderId, approvalUrl

    def getOrder(self, orderId: str) -> Dict:
        return self._request("GET", self.apiBase() + "/v2/checkout/orders/" + orderId,
                             self._authHeaders(), None)

    def captureOrder(self, orderId: str) -> Dict:
        # Orders v2 capture is a POST with an (empty) JSON body.
        return self._request("POST", self.apiBase() + "/v2/checkout/orders/" + orderId + "/capture",
                             self._authHeaders(), b"{}")

    # --- transport ----------------------------------------------------------
    def _request(self, method: str, url: str, headers: Dict[str, str], data) -> Dict:
        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        context = ssl.create_default_context()
        try:
            with urllib.request.urlopen(request, timeout=20, context=context) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = {"raw": body}
            raise PayPalError("PayPal HTTP %s on %s" % (error.code, url), parsed)
        except urllib.error.URLError as error:
            raise PayPalError("PayPal network error on %s: %s" % (url, error.reason))
        if raw == "":
            return {}
        try:
            return json.loads(raw)
        except Exception:
            raise PayPalError("PayPal returned non-JSON on %s" % url, {"raw": raw})
