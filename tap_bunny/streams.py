"""Stream type classes for tap-bunny."""

from __future__ import annotations

import typing as t
from importlib import resources
from typing import Any, Dict, Optional

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath
import requests
import decimal

from tap_bunny.client import BunnyStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"

class UsersStream(BunnyStream):
    """Define custom stream."""

    name = "users"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("id", th.StringType),
        th.Property("modified", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "modified"
    query = """
        users(first: 100, after: $after) {
            edges {
                cursor
                node {
                    name
                    id
                    modified
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
        """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.users.edges[*].node", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data.get("data", {}).get("users", {}).get("pageInfo", {})
        
        if page_info.get("hasNextPage"):
            return page_info.get("endCursor")
        return None


class GroupsStream(BunnyStream):
    """Define custom stream."""

    name = "groups"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("id", th.StringType),
        th.Property("modified", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "modified"
    query = """
        groups(first: 100, after: $after) {
            edges {
                cursor
                node {
                    name
                    id
                    modified
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
        """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.groups.edges[*].node", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data.get("data", {}).get("groups", {}).get("pageInfo", {})
        
        if page_info.get("hasNextPage"):
            return page_info.get("endCursor")
        return None


class AccountsStream(BunnyStream):
    """Define custom stream."""

    name = "accounts"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountTypeId", th.StringType),
        th.Property("annualRevenue", th.NumberType),
        th.Property("arr", th.NumberType),
        th.Property("billingCity", th.StringType),
        th.Property("billingContactId", th.StringType),
        th.Property("billingCountry", th.StringType),
        th.Property("billingDay", th.IntegerType),
        th.Property("billingState", th.StringType),
        th.Property("billingStreet", th.StringType),
        th.Property("billingZip", th.StringType),
        th.Property("code", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("currencyId", th.StringType),
        th.Property("description", th.StringType),
        th.Property("duns", th.StringType),
        th.Property("employees", th.IntegerType),
        th.Property("entityId", th.StringType),
        th.Property("entityUseCode", th.StringType),
        th.Property("fax", th.StringType),
        th.Property("groupId", th.StringType),
        th.Property("industryId", th.StringType),
        th.Property("invoiceTemplateId", th.StringType),
        th.Property("linkedinUrl", th.StringType),
        th.Property("mrr", th.NumberType),
        th.Property("mur", th.NumberType),
        th.Property("name", th.StringType),
        th.Property("netPaymentDays", th.IntegerType),
        th.Property("ownerUserId", th.StringType),
        th.Property("payingStatus", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("shippingCity", th.StringType),
        th.Property("shippingCountry", th.StringType),
        th.Property("shippingState", th.StringType),
        th.Property("shippingStreet", th.StringType),
        th.Property("shippingZip", th.StringType),
        th.Property("taxNumber", th.StringType),
        th.Property("taxNumberValidated", th.BooleanType),
        th.Property("timezone", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("website", th.StringType),
    ).to_dict()

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    @property
    def query(self) -> str:
        """Return the GraphQL query."""
        return """
        query getAllAccounts ($after: String, $before: String, $first: Int, $last: Int, $filter: String, $viewId: ID, $sort: String){
          accounts (after: $after, before: $before, first: $first, last: $last, filter: $filter, viewId: $viewId, sort: $sort){
            edges {
              node {
                id
                accountTypeId
                annualRevenue
                arr
                billingCity
                billingContactId
                billingCountry
                billingDay
                billingState
                billingStreet
                billingZip
                code
                createdAt
                currencyId
                description
                duns
                employees
                entityId
                entityUseCode
                fax
                groupId
                industryId
                invoiceTemplateId
                linkedinUrl
                mrr
                mur
                name
                netPaymentDays
                ownerUserId
                payingStatus
                phone
                shippingCity
                shippingCountry
                shippingState
                shippingStreet
                shippingZip
                taxNumber
                taxNumberValidated
                timezone
                updatedAt
                website
              }
            }
            totalCount
            pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }
          }
        }
        """

    def get_graphql_variables(self, next_page_token: Optional[Any] = None) -> Dict[str, Any]:
        """Return the variables for the GraphQL query."""
        variables = {
            "first": 100,
            "after": next_page_token if next_page_token else "null",
        }
        return variables

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        resp_json = response.json(parse_float=decimal.Decimal)
        if "errors" in resp_json:
            raise RuntimeError(
                f"GraphQL query failed: {resp_json['errors']}"
            )
        
        # Extract accounts from the nested structure
        accounts = resp_json.get("data", {}).get("accounts", {}).get("edges", [])
        for edge in accounts:
            yield edge.get("node", {})

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        resp_json = response.json()
        page_info = resp_json.get("data", {}).get("accounts", {}).get("pageInfo", {})
        
        if page_info.get("hasNextPage"):
            return page_info.get("endCursor")
        return None


class SubscriptionsStream(BunnyStream):
    """Define custom stream."""

    name = "subscriptions"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("period", th.StringType),
        th.Property("evergreen", th.BooleanType),
        th.Property("state", th.StringType),
        th.Property("currencyId", th.StringType),
        th.Property("priceListId", th.StringType),
        th.Property("provisioningRequired", th.BooleanType),
        th.Property("rampIntervalMonths", th.IntegerType),
        th.Property("startDate", th.DateTimeType),
        th.Property("endDate", th.DateTimeType),
        th.Property("trialStartDate", th.DateTimeType),
        th.Property("trialEndDate", th.DateTimeType),
        th.Property("trialPeriod", th.StringType),
        th.Property("cancellationDate", th.DateTimeType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        subscriptions(first: 100, after: $after) {
            nodes {
                id
                accountId
                name
                period
                evergreen
                state
                currencyId
                priceListId
                provisioningRequired
                rampIntervalMonths
                startDate
                endDate
                trialStartDate
                trialEndDate
                trialPeriod
                cancellationDate
                createdAt
                updatedAt
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.subscriptions.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["subscriptions"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class AccountBalancesStream(BunnyStream):
    """Define custom stream."""

    name = "account_balances"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("balance", th.NumberType),
        th.Property("currencyId", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    query = """
        accountBalances(first: 100, after: $after) {
            nodes {
                id
                accountId
                balance
                currencyId
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.accountBalances.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["accountBalances"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class EntitiesStream(BunnyStream):
    """Define custom stream."""

    name = "entities"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("abbreviation", th.StringType),
        th.Property("accentColor", th.StringType),
        th.Property("baseCurrencyId", th.StringType),
        th.Property("billingCity", th.StringType),
        th.Property("billingCountry", th.StringType),
        th.Property("billingState", th.StringType),
        th.Property("billingStreet", th.StringType),
        th.Property("billingZip", th.StringType),
        th.Property("brandColor", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("customerServiceEmail", th.StringType),
        th.Property("emailSenderName", th.StringType),
        th.Property("emailTemplate", th.StringType),
        th.Property("fax", th.StringType),
        th.Property("fiscalYearStartMonth", th.IntegerType),
        th.Property("invoiceNumberPrefix", th.StringType),
        th.Property("invoiceNumberSeq", th.IntegerType),
        th.Property("invoicesImageUrl", th.StringType),
        th.Property("isDefault", th.BooleanType),
        th.Property("name", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("privacyUrl", th.StringType),
        th.Property("quoteNumberPrefix", th.StringType),
        th.Property("quoteNumberSeq", th.IntegerType),
        th.Property("quotesImageUrl", th.StringType),
        th.Property("refundPolicyUrl", th.StringType),
        th.Property("taxId", th.StringType),
        th.Property("taxType", th.StringType),
        th.Property("termsUrl", th.StringType),
        th.Property("timezone", th.StringType),
        th.Property("topNavImageUrl", th.StringType),
        th.Property("tzIdentifier", th.StringType),
        th.Property("tzOffset", th.IntegerType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("website", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        entities(first: 100, after: $after) {
            nodes {
                id
                abbreviation
                accentColor
                baseCurrencyId
                billingCity
                billingCountry
                billingState
                billingStreet
                billingZip
                brandColor
                createdAt
                customerServiceEmail
                emailSenderName
                emailTemplate
                fax
                fiscalYearStartMonth
                invoiceNumberPrefix
                invoiceNumberSeq
                invoicesImageUrl
                isDefault
                name
                phone
                privacyUrl
                quoteNumberPrefix
                quoteNumberSeq
                quotesImageUrl
                refundPolicyUrl
                taxId
                taxType
                termsUrl
                timezone
                topNavImageUrl
                tzIdentifier
                tzOffset
                updatedAt
                website
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.entities.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["entities"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class InvoicesStream(BunnyStream):
    """Define custom stream."""

    name = "invoices"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("amountDue", th.NumberType),
        th.Property("amountPaid", th.NumberType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("credits", th.NumberType),
        th.Property("currencyId", th.StringType),
        th.Property("description", th.StringType),
        th.Property("dueAt", th.DateTimeType),
        th.Property("issuedAt", th.DateTimeType),
        th.Property("kind", th.StringType),
        th.Property("netPaymentDays", th.IntegerType),
        th.Property("number", th.StringType),
        th.Property("paidAt", th.DateTimeType),
        th.Property("payableId", th.StringType),
        th.Property("poNumber", th.StringType),
        th.Property("portalUrl", th.StringType),
        th.Property("quoteId", th.StringType),
        th.Property("smallUnitAmountDue", th.NumberType),
        th.Property("state", th.StringType),
        th.Property("subtotal", th.NumberType),
        th.Property("taxAmount", th.NumberType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("url", th.StringType),
        th.Property("uuid", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        invoices(first: 100, after: $after) {
            nodes {
                id
                accountId
                amount
                amountDue
                amountPaid
                createdAt
                credits
                currencyId
                description
                dueAt
                issuedAt
                kind
                netPaymentDays
                number
                paidAt
                payableId
                poNumber
                portalUrl
                quoteId
                smallUnitAmountDue
                state
                subtotal
                taxAmount
                updatedAt
                url
                uuid
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.invoices.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["invoices"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class InvoiceItemsStream(BunnyStream):
    """Define custom stream."""

    name = "invoice_items"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("chargeType", th.StringType),
        th.Property("couponId", th.StringType),
        th.Property("currencyId", th.StringType),
        th.Property("discount", th.NumberType),
        th.Property("invoiceId", th.StringType),
        th.Property("kind", th.StringType),
        th.Property("lineText", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("price", th.NumberType),
        th.Property("priceDecimals", th.IntegerType),
        th.Property("prorationRate", th.NumberType),
        th.Property("quantity", th.NumberType),
        th.Property("subtotal", th.NumberType),
        th.Property("taxAmount", th.NumberType),
        th.Property("taxCode", th.StringType),
        th.Property("vatCode", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    query = """
        invoiceItems(first: 100, after: $after) {
            nodes {
                id
                amount
                chargeType
                couponId
                currencyId
                discount
                invoiceId
                kind
                lineText
                position
                price
                priceDecimals
                prorationRate
                quantity
                subtotal
                taxAmount
                taxCode
                vatCode
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.invoiceItems.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["invoiceItems"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class PaymentsStream(BunnyStream):
    """Define custom stream."""

    name = "payments"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("amountUnapplied", th.NumberType),
        th.Property("baseCurrencyCash", th.NumberType),
        th.Property("baseCurrencyId", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("currencyId", th.StringType),
        th.Property("description", th.StringType),
        th.Property("isLegacy", th.BooleanType),
        th.Property("memo", th.StringType),
        th.Property("receivedAt", th.DateTimeType),
        th.Property("state", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        payments(first: 100, after: $after) {
            nodes {
                id
                accountId
                amount
                amountUnapplied
                baseCurrencyCash
                baseCurrencyId
                createdAt
                currencyId
                description
                isLegacy
                memo
                receivedAt
                state
                updatedAt
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.payments.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["payments"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class PaymentMethodsStream(BunnyStream):
    """Define custom stream."""

    name = "payment_methods"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("disabled", th.BooleanType),
        th.Property("expirationDate", th.DateTimeType),
        th.Property("failureCode", th.StringType),
        th.Property("lastSuccess", th.DateTimeType),
        th.Property("paymentType", th.StringType),
        th.Property("pluginId", th.StringType),
        th.Property("state", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        paymentMethods(first: 100, after: $after) {
            nodes {
                id
                accountId
                createdAt
                disabled
                expirationDate
                failureCode
                lastSuccess
                paymentType
                pluginId
                state
                updatedAt
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.paymentMethods.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["paymentMethods"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class ProductsStream(BunnyStream):
    """Define custom stream."""

    name = "products"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("code", th.StringType),
        th.Property("description", th.StringType),
        th.Property("everythingInPlus", th.BooleanType),
        th.Property("internalNotes", th.StringType),
        th.Property("name", th.StringType),
        th.Property("platformId", th.StringType),
        th.Property("productCategoryId", th.StringType),
        th.Property("showProductNameOnLineItem", th.BooleanType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    query = """
        products(first: 100, after: $after) {
            nodes {
                id
                code
                description
                everythingInPlus
                internalNotes
                name
                platformId
                productCategoryId
                showProductNameOnLineItem
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.products.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["products"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class PlansStream(BunnyStream):
    """Define custom stream."""

    name = "plans"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("addon", th.BooleanType),
        th.Property("basePrice", th.NumberType),
        th.Property("code", th.StringType),
        th.Property("contactUsLabel", th.StringType),
        th.Property("contactUsUrl", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("internalNotes", th.StringType),
        th.Property("isVisible", th.BooleanType),
        th.Property("name", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("pricingDescription", th.StringType),
        th.Property("productId", th.StringType),
        th.Property("productPlanName", th.StringType),
        th.Property("selfServiceBuy", th.BooleanType),
        th.Property("selfServiceCancel", th.BooleanType),
        th.Property("selfServiceRenew", th.BooleanType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        plans(first: 100, after: $after) {
            nodes {
                id
                addon
                basePrice
                code
                contactUsLabel
                contactUsUrl
                createdAt
                description
                internalNotes
                isVisible
                name
                position
                pricingDescription
                productId
                productPlanName
                selfServiceBuy
                selfServiceCancel
                selfServiceRenew
                updatedAt
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.plans.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["plans"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class QuotesStream(BunnyStream):
    """Define custom stream."""

    name = "quotes"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("acceptedByName", th.StringType),
        th.Property("acceptedByTitle", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("amountDue", th.NumberType),
        th.Property("applicationDate", th.DateTimeType),
        th.Property("backdatedPeriods", th.IntegerType),
        th.Property("backdatedQuote", th.BooleanType),
        th.Property("billingDay", th.IntegerType),
        th.Property("contactId", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("credits", th.NumberType),
        th.Property("currencyId", th.StringType),
        th.Property("dealId", th.StringType),
        th.Property("discount", th.NumberType),
        th.Property("discountValue", th.NumberType),
        th.Property("evergreen", th.BooleanType),
        th.Property("invoiceImmediately", th.BooleanType),
        th.Property("invoiceImmediatelyAvailable", th.BooleanType),
        th.Property("message", th.StringType),
        th.Property("name", th.StringType),
        th.Property("netPaymentDays", th.IntegerType),
        th.Property("notes", th.StringType),
        th.Property("number", th.StringType),
        th.Property("ownerId", th.StringType),
        th.Property("payableId", th.StringType),
        th.Property("periodAmount", th.NumberType),
        th.Property("poNumber", th.StringType),
        th.Property("smallUnitAmountDue", th.NumberType),
        th.Property("splitInvoice", th.BooleanType),
        th.Property("state", th.StringType),
        th.Property("subtotal", th.NumberType),
        th.Property("taxAmount", th.NumberType),
        th.Property("taxCode", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("uuid", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        quotes(first: 100, after: $after) {
            nodes {
                id
                acceptedByName
                acceptedByTitle
                accountId
                amount
                amountDue
                applicationDate
                backdatedPeriods
                backdatedQuote
                billingDay
                contactId
                createdAt
                credits
                currencyId
                dealId
                discount
                discountValue
                evergreen
                invoiceImmediately
                invoiceImmediatelyAvailable
                message
                name
                netPaymentDays
                notes
                number
                ownerId
                payableId
                periodAmount
                poNumber
                smallUnitAmountDue
                splitInvoice
                state
                subtotal
                taxAmount
                taxCode
                updatedAt
                uuid
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.quotes.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["quotes"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class QuoteChargesStream(BunnyStream):
    """Define custom stream."""

    name = "quote_charges"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("billingPeriod", th.StringType),
        th.Property("chargeType", th.StringType),
        th.Property("couponId", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("currencyId", th.StringType),
        th.Property("currentQuantity", th.NumberType),
        th.Property("discount", th.NumberType),
        th.Property("invoiceLineText", th.StringType),
        th.Property("kind", th.StringType),
        th.Property("name", th.StringType),
        th.Property("price", th.NumberType),
        th.Property("priceDecimals", th.IntegerType),
        th.Property("priceListChargeId", th.StringType),
        th.Property("pricingModel", th.StringType),
        th.Property("prorationRate", th.NumberType),
        th.Property("quantity", th.NumberType),
        th.Property("quantityMax", th.NumberType),
        th.Property("quantityMin", th.NumberType),
        th.Property("quoteChangeId", th.StringType),
        th.Property("subtotal", th.NumberType),
        th.Property("taxAmount", th.NumberType),
        th.Property("taxCode", th.StringType),
        th.Property("tieredAveragePrice", th.NumberType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("vatCode", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        quoteCharges(first: 100, after: $after) {
            nodes {
                id
                amount
                billingPeriod
                chargeType
                couponId
                createdAt
                currencyId
                currentQuantity
                discount
                invoiceLineText
                kind
                name
                price
                priceDecimals
                priceListChargeId
                pricingModel
                prorationRate
                quantity
                quantityMax
                quantityMin
                quoteChangeId
                subtotal
                taxAmount
                taxCode
                tieredAveragePrice
                updatedAt
                vatCode
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.quoteCharges.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["quoteCharges"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class RecurringRevenuesStream(BunnyStream):
    """Define custom stream."""

    name = "recurring_revenues"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("currencyId", th.StringType),
        th.Property("recurringAmount", th.NumberType),
        th.Property("totalAmount", th.NumberType),
        th.Property("usageAmount", th.NumberType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    query = """
        recurringRevenues(first: 100, after: $after) {
            nodes {
                id
                accountId
                currencyId
                recurringAmount
                totalAmount
                usageAmount
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.recurringRevenues.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["recurringRevenues"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class RevenueMovementsStream(BunnyStream):
    """Define custom stream."""

    name = "revenue_movements"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("currencyId", th.StringType),
        th.Property("date", th.DateTimeType),
        th.Property("movementType", th.StringType),
        th.Property("recurringAmount", th.NumberType),
        th.Property("totalAmount", th.NumberType),
        th.Property("usageAmount", th.NumberType),
        th.Property("usageMovementType", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    query = """
        revenueMovements(first: 100, after: $after) {
            nodes {
                id
                accountId
                currencyId
                date
                movementType
                recurringAmount
                totalAmount
                usageAmount
                usageMovementType
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.revenueMovements.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["revenueMovements"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class SubscriptionChargesStream(BunnyStream):
    """Define custom stream."""

    name = "subscription_charges"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("billingPeriod", th.StringType),
        th.Property("chargeType", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("discount", th.NumberType),
        th.Property("discountedPrice", th.NumberType),
        th.Property("invoiceLineText", th.StringType),
        th.Property("kind", th.StringType),
        th.Property("name", th.StringType),
        th.Property("periodPrice", th.NumberType),
        th.Property("price", th.NumberType),
        th.Property("priceDecimals", th.IntegerType),
        th.Property("priceListChargeId", th.StringType),
        th.Property("priceListId", th.StringType),
        th.Property("pricingModel", th.StringType),
        th.Property("prorationRate", th.NumberType),
        th.Property("quantity", th.NumberType),
        th.Property("quantityMax", th.NumberType),
        th.Property("quantityMin", th.NumberType),
        th.Property("selfServiceQuantity", th.BooleanType),
        th.Property("subscriptionId", th.StringType),
        th.Property("tieredAveragePrice", th.NumberType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        subscriptionCharges(first: 100, after: $after) {
            nodes {
                id
                amount
                billingPeriod
                chargeType
                createdAt
                discount
                discountedPrice
                invoiceLineText
                kind
                name
                periodPrice
                price
                priceDecimals
                priceListChargeId
                priceListId
                pricingModel
                prorationRate
                quantity
                quantityMax
                quantityMin
                selfServiceQuantity
                subscriptionId
                tieredAveragePrice
                updatedAt
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.subscriptionCharges.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["subscriptionCharges"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class TransactionsStream(BunnyStream):
    """Define custom stream."""

    name = "transactions"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("amount", th.NumberType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("currencyId", th.StringType),
        th.Property("description", th.StringType),
        th.Property("state", th.StringType),
        th.Property("transactionableId", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "createdAt"
    query = """
        transactions(first: 100, after: $after) {
            nodes {
                id
                accountId
                amount
                createdAt
                currencyId
                description
                state
                transactionableId
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.transactions.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["transactions"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class TenantsStream(BunnyStream):
    """Define custom stream."""

    name = "tenants"
    path = "/graphql"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("code", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("lastLogin", th.DateTimeType),
        th.Property("latestProvisioningChangeId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("platformId", th.StringType),
        th.Property("provisioningRequired", th.BooleanType),
        th.Property("provisioningState", th.StringType),
        th.Property("subdomain", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("userCount", th.IntegerType),
        th.Property("utilizationMetrics", th.StringType),
    ).to_dict()
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    query = """
        tenants(first: 100, after: $after) {
            nodes {
                id
                accountId
                code
                createdAt
                lastLogin
                latestProvisioningChangeId
                name
                platformId
                provisioningRequired
                provisioningState
                subdomain
                updatedAt
                userCount
                utilizationMetrics
            }
            pageInfo {
                startCursor
                endCursor
                hasNextPage
                hasPreviousPage
            }
        }
    """

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath("$.data.tenants.nodes[*]", response.json())

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        data = response.json()
        page_info = data["data"]["tenants"]["pageInfo"]
        if page_info["hasNextPage"]:
            return page_info["endCursor"]
        return None


class ContactsStream(BunnyStream):
    """Define custom stream."""

    name = "contacts"
    path = "/graphql"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updatedAt"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("code", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("email", th.StringType),
        th.Property("entityId", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("fullName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("linkedinUrl", th.StringType),
        th.Property("mailingCity", th.StringType),
        th.Property("mailingCountry", th.StringType),
        th.Property("mailingState", th.StringType),
        th.Property("mailingStreet", th.StringType),
        th.Property("mailingZip", th.StringType),
        th.Property("mobile", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("portalAccess", th.BooleanType),
        th.Property("salutation", th.StringType),
        th.Property("title", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["after"] = next_page_token
        return params

    @property
    def query(self) -> str:
        """Return the GraphQL query."""
        return """
        query contacts ($after: String, $before: String, $first: Int, $last: Int, $filter: String, $viewId: ID, $sort: String) {
          contacts (after: $after, before: $before, first: $first, last: $last, filter: $filter, viewId: $viewId, sort: $sort) {
            edges {
              cursor
              node {
                id
                accountId
                code
                createdAt
                description
                email
                entityId
                firstName
                fullName
                lastName
                linkedinUrl
                mailingCity
                mailingCountry
                mailingState
                mailingStreet
                mailingZip
                mobile
                phone
                portalAccess
                salutation
                title
                updatedAt
              }
            }
            totalCount
            pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }
          }
        }
        """

    def get_graphql_variables(self, next_page_token: Optional[Any] = None) -> Dict[str, Any]:
        """Return the variables for the GraphQL query."""
        variables = {
            "first": 100,
            "after": next_page_token if next_page_token else "null",
        }
        return variables

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        resp_json = response.json(parse_float=decimal.Decimal)
        if "errors" in resp_json:
            raise RuntimeError(
                f"GraphQL query failed: {resp_json['errors']}"
            )
        
        # Extract contacts from the nested structure
        contacts = resp_json.get("data", {}).get("contacts", {}).get("edges", [])
        for edge in contacts:
            yield edge.get("node", {})

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[Any]:
        """Return token for identifying next page or None if no more pages."""
        resp_json = response.json()
        page_info = resp_json.get("data", {}).get("contacts", {}).get("pageInfo", {})
        
        if page_info.get("hasNextPage"):
            return page_info.get("endCursor")
        return None
