"""Resource groups mounted on the Webshare clients."""

from webshare.resources.billing import AsyncBilling, Billing
from webshare.resources.download_tokens import AsyncDownloadTokens, DownloadTokens
from webshare.resources.id_verification import AsyncIDVerificationResource, IDVerificationResource
from webshare.resources.invoices import AsyncInvoices, Invoices
from webshare.resources.ip_authorizations import AsyncIPAuthorizations, IPAuthorizations
from webshare.resources.notifications import AsyncNotifications, Notifications
from webshare.resources.payment_methods import AsyncPaymentMethods, PaymentMethods
from webshare.resources.pending_payments import AsyncPendingPayments, PendingPayments
from webshare.resources.plans import AsyncPlans, Plans
from webshare.resources.profile import AsyncProfileResource, ProfileResource
from webshare.resources.proxies import AsyncProxies, Proxies
from webshare.resources.proxy_activity import AsyncProxyActivityResource, ProxyActivityResource
from webshare.resources.proxy_config import AsyncProxyConfigResource, ProxyConfigResource
from webshare.resources.proxy_replacements import AsyncProxyReplacements, ProxyReplacements
from webshare.resources.referral import AsyncReferral, Referral
from webshare.resources.replaced_proxies import AsyncReplacedProxies, ReplacedProxies
from webshare.resources.stats import AsyncStats, Stats
from webshare.resources.subscription import AsyncSubscriptionResource, SubscriptionResource
from webshare.resources.subusers import AsyncSubusers, Subusers
from webshare.resources.transactions import AsyncTransactions, Transactions
from webshare.resources.verification import AsyncVerification, Verification

__all__ = [
    "AsyncBilling",
    "AsyncDownloadTokens",
    "AsyncIDVerificationResource",
    "AsyncIPAuthorizations",
    "AsyncInvoices",
    "AsyncNotifications",
    "AsyncPaymentMethods",
    "AsyncPendingPayments",
    "AsyncPlans",
    "AsyncProfileResource",
    "AsyncProxies",
    "AsyncProxyActivityResource",
    "AsyncProxyConfigResource",
    "AsyncProxyReplacements",
    "AsyncReferral",
    "AsyncReplacedProxies",
    "AsyncStats",
    "AsyncSubscriptionResource",
    "AsyncSubusers",
    "AsyncTransactions",
    "AsyncVerification",
    "Billing",
    "DownloadTokens",
    "IDVerificationResource",
    "IPAuthorizations",
    "Invoices",
    "Notifications",
    "PaymentMethods",
    "PendingPayments",
    "Plans",
    "ProfileResource",
    "Proxies",
    "ProxyActivityResource",
    "ProxyConfigResource",
    "ProxyReplacements",
    "Referral",
    "ReplacedProxies",
    "Stats",
    "SubscriptionResource",
    "Subusers",
    "Transactions",
    "Verification",
]
