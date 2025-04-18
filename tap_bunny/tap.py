"""Bunny tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_bunny import streams
from tap_bunny.client import BunnyAuthenticator

STREAM_TYPES = [
    streams.AccountsStream,
    streams.ContactsStream,
    streams.SubscriptionsStream,
]

class TapBunny(Tap):
    """Bunny tap class."""

    name = "tap-bunny"
    tap_name = "tap-bunny"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,
            title="Client ID",
            description="The OAuth2 client ID for authentication",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,
            title="Client Secret",
            description="The OAuth2 client secret for authentication",
        ),
        th.Property(
            "api_url",
            th.StringType,
            title="API URL",
            required=True,
            description="The base URL for the Bunny API service",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
        th.Property(
            "incremental_sync",
            th.BooleanType,
            default=True,
            description="Whether to perform incremental sync (True) or full sync (False)",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.BunnyStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.AccountsStream(self),
            streams.SubscriptionsStream(self),
            streams.ContactsStream(self),
            streams.AccountBalancesStream(self),
            streams.EntitiesStream(self),
            streams.InvoicesStream(self),
            streams.InvoiceItemsStream(self),
            streams.PaymentsStream(self),
            streams.PaymentMethodsStream(self),
            streams.ProductsStream(self),
            streams.PlansStream(self),
            streams.QuotesStream(self),
            streams.QuoteChargesStream(self),
            streams.RecurringRevenuesStream(self),
            streams.RevenueMovementsStream(self),
            streams.SubscriptionChargesStream(self),
            streams.TransactionsStream(self),
            streams.TenantsStream(self),
        ]

    def _get_auth_url(self) -> str:
        """Get the auth URL by appending /oauth/token to the API URL."""
        api_url = self.config.get("api_url")
        if not api_url:
            raise ValueError("api_url is required in the configuration")
        return f"{api_url.rstrip('/')}/oauth/token"

    def _get_authenticator(self) -> BunnyAuthenticator:
        """Get the authenticator instance."""
        auth_url = self._get_auth_url()
        return BunnyAuthenticator(self, auth_url=auth_url)


if __name__ == "__main__":
    TapBunny.cli()
