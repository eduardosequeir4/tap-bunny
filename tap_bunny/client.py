"""GraphQL client handling, including BunnyStream base class."""

from __future__ import annotations

import decimal
import typing as t
from datetime import datetime, timedelta
import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.streams import GraphQLStream
from singer_sdk.helpers.jsonpath import extract_jsonpath
if t.TYPE_CHECKING:
    from singer_sdk.helpers.typing import Context


class BunnyAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Bunny."""

    def __init__(self, stream, auth_url: str) -> None:
        """Init authenticator."""
        super().__init__(
            stream=stream,
            auth_endpoint=auth_url,
        )
        self._access_token = None
        self._expires_at = None
        self.update_access_token()

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body."""
        return {
            "grant_type": "client_credentials",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "scope": "standard:read standard:write product:read product:write billing:read billing:write",
        }

    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`."""
        response = requests.post(
            self.auth_endpoint,
            data=self.oauth_request_body,
        )
        response.raise_for_status()
        auth_data = response.json()
        self._access_token = auth_data["access_token"]
        self._expires_at = datetime.now() + timedelta(seconds=auth_data["expires_in"])

    @property
    def access_token(self) -> str:
        """Return the access token."""
        if not self._access_token or not self._expires_at or datetime.now() >= self._expires_at:
            self.update_access_token()
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        """Set the access token."""
        self._access_token = value


class BunnyStream(GraphQLStream):
    """Bunny stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @property
    def authenticator(self) -> BunnyAuthenticator:
        """Return a new authenticator object."""
        # Use the tap's authenticator if available
        if hasattr(self._tap, "_get_authenticator"):
            return self._tap._get_authenticator()
        return BunnyAuthenticator(self, self.config["auth_url"])

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config["user_agent"]
        headers["Authorization"] = f"Bearer {self.authenticator.access_token}"
        headers["Content-Type"] = "application/json"
        return headers

    def get_starting_replication_key_value(self, context: dict | None) -> str | None:
        """Get starting replication key value based on config."""
        if self.config.get("incremental_sync", True):
            # If incremental sync is enabled, use normal behavior
            return super().get_starting_replication_key_value(context)
        # If full sync is requested, return None to sync all records
        return None

    def get_starting_timestamp(self, context: dict | None) -> datetime | None:
        """Get starting timestamp based on config."""
        if self.config.get("incremental_sync", True):
            # If incremental sync is enabled, use start_date from config or state
            return super().get_starting_timestamp(context)
        # If full sync is requested, return None to sync all records
        return None

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Raises:
            RuntimeError: If the GraphQL response contains errors or invalid data.

        Yields:
            Each record from the source.
        """
        # First check the response status code, even though GraphQL often returns 200
        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP request failed with status code {response.status_code}:\n"
                f"Response: {response.text}"
            )

        try:
            resp_json = response.json(parse_float=decimal.Decimal)
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse JSON response: {str(e)}\n"
                f"Response text: {response.text[:1000]}"  # Include first 1000 chars of response
            ) from e

        # Check for GraphQL errors
        if "errors" in resp_json:
            errors = resp_json["errors"]
            error_messages = []
            
            for error in errors:
                message = error.get("message", "Unknown error")
                path = ".".join(str(p) for p in error.get("path", []))
                locations = error.get("locations", [])
                extensions = error.get("extensions", {})
                
                error_detail = [
                    f"Message: {message}",
                    f"Path: {path}" if path else None,
                    f"Locations: {locations}" if locations else None,
                    f"Extensions: {extensions}" if extensions else None,
                ]
                error_messages.append(
                    "\n".join(detail for detail in error_detail if detail is not None)
                )

            query_info = f"\nQuery: {self.query}" if hasattr(self, "query") else ""
            variables_info = f"\nVariables: {self.vars}" if hasattr(self, "vars") else ""
            
            raise RuntimeError(
                f"GraphQL query failed for stream '{self.name}':"
                f"{query_info}"
                f"{variables_info}\n\n"
                f"Errors:\n" + "\n\n".join(error_messages)
            )

        # Validate response structure
        if not isinstance(resp_json, dict):
            raise RuntimeError(
                f"Invalid GraphQL response structure. Expected dict, got {type(resp_json)}\n"
                f"Response: {resp_json}"
            )
        yield from extract_jsonpath(self.records_jsonpath, resp_json)

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        # TODO: Delete this method if not needed.
        return row
