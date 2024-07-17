import requests
import uuid
import os
import base64
import logging

from utils.errors import AccessTokenError, TransactionError, TransferRequestError

class MtnAPIHelper:
    def __init__(self):
        self.endpoint = "sandbox.momodeveloper.mtn.com"

    def get_apiuser(self):
        reference_id = str(uuid.uuid4())

        url = f"https://{self.endpoint}/v1_0/apiuser"

        headers = {
            "X-Reference-Id": reference_id,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_SUBSCRIPTION_KEY", "4813d15be4f94f12bb3a7bd2a3516ee2"
            ),
        }

        data = {
            "providerCallbackHost": "mwape.org",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            return reference_id

        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")

    def create_api_key(self, reference_id):
        url = f"https://{self.endpoint}/v1_0/apiuser/{reference_id}/apikey"

        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_SUBSCRIPTION_KEY", "4813d15be4f94f12bb3a7bd2a3516ee2"
            ),
        }

        data = {
            "providerCallbackHost": "mwape.org",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            if response.text:
                response_data = response.json()
                api_key = response_data.get("apiKey", None)
                return {"api_key": api_key, "api_user": reference_id}
            else:
                print("Empty response received.")
        except requests.exceptions.RequestException as e:
            print(f"Error during API key creation: {e}")
            return None

    def create_access_token(self, api_user_id, api_key):
        url = f"https://{self.endpoint}/collection/token/"

        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{api_user_id}:{api_key}'.encode()).decode()}",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_COLLECTION_SUBSCRIPTION_KEY", "e22d1a41738d4899ad02b602159b5b56"
            ),
            "Content-Type": "application/json",
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error creating access token: {e}")
            return None


class MtnPaymentHelper:
    def __init__(self, api_user_id, api_key):
        self.api_user_id = api_user_id
        self.api_key = api_key
        self.endpoint = "sandbox.momodeveloper.mtn.com"

    def request_to_pay(self, amount, currency, external_id, party_id):
        reference_id = str(uuid.uuid4())

        url = f"https://{self.endpoint}/collection/v1_0/requesttopay"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_COLLECTION_SECONDARY_SUBSCRIPTION_KEY",
                "f1bc2773ffec4fdbb98720b4e227884d",
            ),
        }

        data = {
            "amount": float(amount),
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": party_id,
            },
            "payerMessage": "test message",
            "payeeNote": "test note",
        }

        try:
            response = requests.post(url, headers=headers, json=data)

            response.raise_for_status()
            print(response.status_code)
            print(response.text)

            return reference_id

        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return None

    def check_payment_status(self, transaction_ref):
        url = f"https://{self.endpoint}/collection/v1_0/requesttopay/{transaction_ref}"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_COLLECTION_SECONDARY_SUBSCRIPTION_KEY",
                "f1bc2773ffec4fdbb98720b4e227884d",
            ),
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            if "status" in data:
                amount = data["amount"]
                status = data["status"]

                return status

            elif "reason" in data:
                message = data["message"]
                return message
            else:
                logging.error("Balance information not found in the response.")

        except Exception as e:
            logging.error(f"An error {e} occurred")

    def transfer(self, amount, currency, external_id, payee_party_id):
        reference_id = str(uuid.uuid4())
        url = f"https://{self.endpoint}/disbursement/v1_0/transfer"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_DISBURSEMENT_SUBSCRIPTION_KEY",
                "4813d15be4f94f12bb3a7bd2a3516ee2",
            ),
        }

        data = {
            "amount": float(amount),
            "currency": currency,
            "externalId": external_id,
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": payee_party_id,
            },
            "payerMessage": "Money sent!",
            "payeeNote": "Money transferred to your account!",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            logging.info(
                f"Transfer request successful. Status code: {response.status_code}"
            )
            return reference_id

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error during transfer request: {e}")
            raise TransferRequestError(
                f"Transfer request failed with HTTP error: {e}",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e
        except TransferRequestError as tre:
            logging.error(f"Transfer request failed with status code {tre.status_code}")
            logging.error(f"Response text: {tre.response_text}")

            if hasattr(tre, "response"):
                logging.error(f"HTTP error details: {tre.response}")
            raise

    def transfer_status(self, reference_id):
        url = f"https://{self.endpoint}/disbursement/v1_0/transfer/{reference_id}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_DISBURSEMENT_SUBSCRIPTION_KEY",
                "4813d15be4f94f12bb3a7bd2a3516ee2",
            ),
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            if "status" in data:
                amount = data["amount"]
                status = data["status"]

                return status

            elif "reason" in data:
                message = data["message"]
                return message
            else:
                logging.error("Balance information not found in the response.")

        except Exception as e:
            logging.error(f"An error {e} occurred")

        return None

    def balance(self):
        url = f"https://{self.endpoint}/disbursement/v1_0/account/balance"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_DISBURSEMENT_SUBSCRIPTION_KEY",
                "4813d15be4f94f12bb3a7bd2a3516ee2",
            ),
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            balance_data = response.json()
            if "availableBalance" in balance_data:
                available_balance = balance_data["availableBalance"]
                logging.info(f"Wallet balance: {available_balance}")
                return available_balance
            elif "code" in balance_data:
                message = balance_data["message"]
                return message
            else:
                logging.error("Balance information not found in the response.")

        except Exception as e:
            logging.error(f"An error {e} occurred")

        return None

    def withdraw(self, amount, currency, external_id, party_id):
        url = f"https://{self.endpoint}/collection/v1_0/requesttowithdraw"
        reference_id = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": os.environ.get(
                "MOMO_COLLECTION_SECONDARY_SUBSCRIPTION_KEY",
                "f1bc2773ffec4fdbb98720b4e227884d",
            ),
        }

        data = {
            "amount": float(amount),
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": party_id,
            },
            "payerMessage": "test message",
            "payeeNote": "test note",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            logging.info(
                f"Transaction request successful. Status code: {response.status_code}"
            )
            return reference_id

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error during transaction: {e}")
            raise TransactionError(
                f"Transaction failed with HTTP error: {e}",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e
        except TransactionError as tre:
            logging.error(
                f"Transaction request failed with status code {tre.status_code}"
            )
            logging.error(f"Response text: {tre.response_text}")

            if hasattr(tre, "response"):
                logging.error(f"HTTP error details: {tre.response}")
            raise

    def get_access_token(self):
        api_helper = MtnAPIHelper()
        try:
            return api_helper.create_access_token(self.api_user_id, self.api_key)
        except Exception as e:
            raise AccessTokenError(f"Error obtaining access token: {e}")


def auth_keys():
    mtn_helper = MtnAPIHelper()
    reference_id = mtn_helper.get_apiuser()
    result_hash = mtn_helper.create_api_key(reference_id)
    api_key = result_hash.get("api_key", None)
    api_user = result_hash.get("api_user", None)

    if api_key and api_user:
        return {"api_user": api_user, "api_key": api_key}
    else:
        print("API key not found")
