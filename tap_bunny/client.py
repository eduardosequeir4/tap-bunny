"""GraphQL client handling, including BunnyStream base class."""

from __future__ import annotations

import decimal
import typing as t
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import argparse
import json

import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.streams import GraphQLStream

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
        self._stream = stream
        self._access_token = stream.config.get("access_token")
        self._expires_at = stream.config.get("token_expires_at")
        if not self._access_token or not self._expires_at or datetime.now() >= datetime.fromisoformat(self._expires_at):
            self.update_access_token()

    def is_token_valid(self) -> bool:
        """Check if the current token is valid.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self._access_token or not self._expires_at:
            return False
        return datetime.now() < datetime.fromisoformat(self._expires_at)

    def handle_401_response(self, response: requests.Response) -> None:
        """Handle 401 Unauthorized response by refreshing the token.
        
        Args:
            response: The HTTP response that returned 401
            
        Raises:
            RuntimeError: If token refresh fails
        """
        if response.status_code == 401:
            self.logger.warning("Received 401 Unauthorized response. Attempting to refresh token...")
            try:
                self.update_access_token()
            except Exception as e:
                raise RuntimeError(f"Failed to refresh token after 401 response: {str(e)}")

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
        
        # Calculate expiration time using created_at timestamp
        created_at = datetime.fromtimestamp(auth_data["created_at"])
        expires_at = created_at + timedelta(seconds=auth_data["expires_in"])
        self._expires_at = expires_at.isoformat()
        
        # Update config with new token
        self._stream.update_config({
            "access_token": self._access_token,
            "token_expires_at": self._expires_at
        })

    @property
    def access_token(self) -> str:
        """Return the access token."""
        if not self._access_token or not self._expires_at:
            self.update_access_token()
        else:
            expires_at = datetime.fromisoformat(self._expires_at)
            # Refresh token if it expires in less than 5 minutes
            if datetime.now() + timedelta(minutes=5) >= expires_at:
                self.logger.info("Token expires in less than 5 minutes, refreshing...")
                self.update_access_token()
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        """Set the access token."""
        self._access_token = value


class BunnyStream(GraphQLStream):
    """Bunny stream class."""

    def _request_with_backoff(self, prepared_request: requests.PreparedRequest, context: dict) -> requests.Response:
        """Execute a request with backoff and token refresh handling.
        
        Args:
            prepared_request: The prepared request to execute
            context: The stream context
            
        Returns:
            The HTTP response
            
        Raises:
            RuntimeError: If the request fails after token refresh
        """
        response = super()._request_with_backoff(prepared_request, context)
        
        # If we get a 401, try to refresh the token and retry once
        if response.status_code == 401:
            self.authenticator.handle_401_response(response)
            # Retry the request with the new token
            prepared_request.headers["Authorization"] = f"Bearer {self.authenticator.access_token}"
            response = super()._request_with_backoff(prepared_request, context)
            
        return response

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

    @property
    def incremental_sync(self) -> bool:
        """Return whether incremental sync is enabled.
        
        This property reads the incremental_sync setting from the config.
        If not specified, it defaults to False to use cursor-based pagination only.
        """
        return self.config.get("incremental_sync", False)

    def get_starting_replication_key_value(self, context: dict | None) -> str | None:
        """Get starting replication key value based on config."""
        # Always return None to perform a full sync using cursor-based pagination
        return None

    def get_starting_timestamp(self, context: dict | None) -> datetime | None:
        """Get starting timestamp based on config."""
        # Always return None to perform a full sync using cursor-based pagination
        return None

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages.
        
        This method handles cursor-based pagination for all Bunny streams.
        It extracts the next page token from the GraphQL response's pageInfo.
        
        Args:
            response: The HTTP response object
            previous_token: The previous page token
            
        Returns:
            The next page token if there are more pages, None otherwise
        """
        try:
            data = response.json()
            # Extract the field name based on the stream name
            field_name = self.name
            stream_data = data.get("data", {}).get(field_name, {})
            
            # Handle both connection-style and direct node-style responses
            if isinstance(stream_data, dict):
                page_info = stream_data.get("pageInfo", {})
                if page_info and page_info.get("hasNextPage"):
                    return page_info.get("endCursor")
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing pagination info: {str(e)}")
            return None

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.
        
        This method handles the pagination parameters for all Bunny streams.
        It adds the 'after' parameter when a next page token is available.
        
        Args:
            context: The stream context
            next_page_token: The token for the next page
            
        Returns:
            A dictionary of URL parameters
        """
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def get_graphql_variables(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used as GraphQL variables.
        
        This method standardizes the GraphQL variables across all streams.
        It handles pagination by providing the 'after' cursor when available.
        
        Args:
            context: The stream context
            next_page_token: The token for the next page
            
        Returns:
            A dictionary of GraphQL variables
        """
        variables: dict = {}
        if next_page_token:
            variables["after"] = next_page_token
        # Always use 'id' for sorting to prevent duplicates
        variables["sort"] = "id"
        return variables

    def parse_response(self, response: requests.Response) -> t.Generator[dict, None, None]:
        """Parse the response and yield each record from the source.

        Args:
            response: HTTP response object

        Yields:
            An iterator for each record from the source.

        Raises:
            RuntimeError: If the response is not valid JSON or contains errors.
        """
        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP request failed with status code {response.status_code}: {response.text}"
            )

        try:
            json_data = response.json()
            # Log the first API response for each stream
            self.logger.info(f"First API response for {self.name} stream: {json.dumps(json_data, indent=2)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse JSON response: {str(e)}\nResponse text: {response.text[:1000]}"
            ) from e

        if "errors" in json_data:
            errors = json_data["errors"]
            error_msg = "GraphQL errors occurred:\n"
            for error in errors:
                error_msg += f"- {error.get('message', 'Unknown error')}\n"
                if "path" in error:
                    error_msg += f"  Path: {'.'.join(str(p) for p in error['path'])}\n"
                if "locations" in error:
                    error_msg += f"  Locations: {error['locations']}\n"
                if "extensions" in error:
                    error_msg += f"  Extensions: {error['extensions']}\n"
            if "query" in json_data:
                error_msg += f"\nQuery: {json_data['query']}\n"
            if "variables" in json_data:
                error_msg += f"Variables: {json_data['variables']}\n"
            raise RuntimeError(error_msg)

        if not isinstance(json_data, dict):
            raise RuntimeError(f"Expected dictionary response, got {type(json_data)}")

        if "data" not in json_data:
            raise RuntimeError(f"No 'data' field in response: {json_data}")

        if json_data["data"] is None:
            raise RuntimeError("Response data is null")

        # Convert stream name from snake_case to camelCase for field lookup
        field_name = "".join(word.capitalize() for word in self.name.split("_"))
        field_name = field_name[0].lower() + field_name[1:]  # Make first letter lowercase

        if field_name not in json_data["data"]:
            available_fields = list(json_data["data"].keys())
            raise RuntimeError(
                f"No data found for stream '{self.name}' in response\n"
                f"Available fields: {available_fields}\n"
                f"Response: {json_data}"
            )

        stream_data = json_data["data"][field_name]

        if stream_data is None:
            raise RuntimeError(f"Stream data for '{self.name}' is null")

        # Handle both nodes and edges formats
        if "nodes" in stream_data:
            nodes = stream_data["nodes"]
        elif "edges" in stream_data:
            nodes = [edge["node"] for edge in stream_data["edges"]]
        else:
            raise RuntimeError(
                f"No 'nodes' or 'edges' found in stream data for '{self.name}'\n"
                f"Available fields: {list(stream_data.keys())}\n"
                f"Response: {json_data}"
            )

        if nodes is None:
            raise RuntimeError(f"Nodes array is null for stream '{self.name}'")

        for node in nodes:
            if node is not None:
                yield node

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

    def prepare_request(
        self,
        context: dict,
        next_page_token: Optional[Any] = None,
    ) -> requests.PreparedRequest:
        """Prepare a request object for this stream.
        
        Args:
            context: Stream sync context
            next_page_token: Token for retrieving the next page
            
        Returns:
            A prepared request object
        """
        request = requests.Request(
            "POST",
            self.url_base + self.path,
            headers=self.http_headers,
            json={
                "query": self.query,
                "variables": self.get_graphql_variables(context, next_page_token),
            },
        )
        
        # Debug logging to see the request details
        self.logger.info(f"GraphQL Query for {self.name}: {self.query}")
        self.logger.info(f"GraphQL Variables for {self.name}: {self.get_graphql_variables(context, next_page_token)}")
        
        return request.prepare()
