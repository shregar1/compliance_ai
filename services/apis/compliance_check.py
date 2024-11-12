import requests

from bs4 import BeautifulSoup
from google.api_core.exceptions import ResourceExhausted
from http import HTTPStatus
from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, List, Union

from abstractions.service import IService

from constants.api_status import APIStatus

from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.unexpected_response_error import UnexpectedResponseError

from start_utils import conversation_llm

from utilities.dictionary import DictionaryUtility


class ComplianceCheckService(IService):

    def __init__(self, urn: str = None, api_name: str = None) -> None:
        super().__init__(urn, api_name)

        self.dictionary_utility = DictionaryUtility(urn=urn)

    async def __build_chat(self, conversation: List[Dict[str, str]]):

        chat = []
        self.logger.debug("Preparing chat.")
        for message in conversation:
            if "ai" in message:
                chat.append(AIMessage(content=message.get("ai", "")))
            else:
                chat.append(HumanMessage(content=message.get("human", "")))
        self.logger.debug("Prepared chat.")

        return chat

    async def __invoke_conversation_model(self, chat: List[Union[AIMessage, HumanMessage]]) -> str:

        self.logger.debug("Invoking chat llm")
        try:
            
            ai_message: AIMessage = conversation_llm.invoke(chat)
            self.logger.debug("Invoked chat llm")
            
            self.logger.debug("Extracting message content")
            message: str = ai_message.content if getattr(ai_message, "content", None) else ai_message
            self.logger.debug("Extracted message content")

            return message
        
        except ResourceExhausted:
            self.logger.error("RateLimitError occured while invoking llm")
            return "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors."
        
        except Exception as err:
            self.logger.error(f"Error occured while invoking llm: {type(err), err}")
            return "Unexpected Error occured while invoking llm."

    async def __fetch_webpage_text(self, url: str):

        try:

            self.logger.debug("Fetching webpage")
            response = requests.get(url=url)
            response.raise_for_status()
            self.logger.debug("Fetching webpage")

            self.logger.debug("Parsing webpage")
            soup = BeautifulSoup(response.text, "html.parser")
            self.logger.debug("Parsed webpage")

            self.logger.debug("Fetching webpage content")
            webpage_text = soup.get_text(separator="\n")
            self.logger.debug("Fetched webpage content")

            return webpage_text

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch the webpage: {e}")
            raise BadInputError(
                responseMessage="Failed to fetch the webpage",
                responseKey="error_invalid_url",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

    async def __perform_compliance_check(self, webpage_text: str) -> Union[List[str], Dict[str, str], str]:
        compliance_policy = """
        Marketing Treasury-based services
        Create precise messaging for your users that complies with regulations.
        Many states have statutory prohibitions on references to “banking," “banks," and “bank accounts” when the entities making these references are not state- or federally-chartered banks or credit unions. Imprecise terminology of Stripe Treasury accounts might draw scrutiny from regulators.

        Recommended Terms
        For your platform to efficiently leverage Stripe Treasury, you need to brand and communicate the nature of the product while being mindful of regulations. Refer to the following list of recommended terms to use in your messaging when building out your implementation of the product.

        Money management, or money management account or solution
        Cash management, or cash management account or solution
        [Your brand] account
        Financial services
        Financial account
        Financial product
        Financial service product
        Store of funds
        Wallet or open loop wallet
        Stored-value account
        Open-Loop stored-value account
        Prepaid access account
        Eligible for FDIC “pass-through” insurance
        Funds held at [Partner Bank], Member FDIC
        Terms to Avoid
        Avoid the terms in this list for any marketing programs you create because only financial institutions licensed as banks can use them.

        Stripe or [Your Brand] bank
        Bank account
        Bank balance
        Banking
        Banking account
        Banking product
        Banking platform
        Deposits
        Mobile banking
        [Your Brand] pays interest
        [Your Brand] sets interest rates
        [Your Brand] advances funds
        Phrases that suggest your users receive banking products or services directly from bank partners, for example:
        Create a [Bank Partner] bank account
        A better way to bank with [Bank Partner]
        Mobile banking with [Bank Partner]
        Yield compliance marketing guidance
        As a platform, you can provide your customers with yield, calculated as a percentage of their Treasury balance. We understand that this can be a great value proposition as part of your product. When you market and disclose yield to your potential and existing customers, don’t conflate yield with interest. We’ve outlined best practices for your marketing disclosures below. If you have any questions on how to present yield in your marketing, reach out to our compliance team at platform-compliance@stripe.com

        Recommended Terms:
        Always refer to yield as “yield.”
        Always disclose prominently in your marketing materials that the yield percentage is subject to change and the conditions under which it might change.
        Notify your existing customers whenever the yield percentage has changed. Prominently display the most recent yield percentage in their Dashboard.
        Terms to avoid
        Never refer to yield as “interest.”
        Don’t reference the Fed Funds Rate as a benchmark for setting your yield percentage.
        Don’t imply that the yield is pass-through interest from a bank partner.
        How to talk about FDIC insurance eligibility
        Stripe Treasury balances are stored value accounts that are held “for the benefit of” our Stripe Treasury users with our bank partners, Evolve Bank & Trust and Goldman Sachs Bank USA. We disclose to you which of our partners hold your funds. For FDIC insurance to apply to a user’s balance in a “for the benefit of” account, we must satisfy the rules for FDIC pass-through deposit insurance, unlike a bank account directly with an FDIC insured bank.

        We understand that FDIC insurance eligibility can be a valuable feature to your customers. Stripe has approved the variations of the phrase “FDIC Insurance eligible” noted below on marketing materials, as long as certain conditions are met. Specifically, the statement of FDIC insurance eligibility must always be paired with two disclosures:

        Stripe Treasury Accounts are eligible for FDIC pass-through deposit insurance if they meet certain requirements. The accounts are eligible only to the extent pass-through insurance is permitted by the rules and regulations of the FDIC, and if the requirements for pass-through insurance are satisfied. The FDIC insurance applies up to 250,000 USD per depositor, per financial institution, for deposits held in the same ownership capacity.
        You must also disclose that neither Stripe nor you are an FDIC insured institution and that the FDIC’s deposit insurance coverage only protects against the failure of an FDIC insured depository institution.
        The following terms that incorporate the term “eligible” are approved:	Don’t use the following terms:
        “Eligible for FDIC insurance”
        “FDIC insurance-eligible accounts”
        “Eligible for FDIC pass-through insurance”
        “Eligible for FDIC insurance up to the standard maximum deposit insurance per depositor in the same capacity"
        “Eligible for FDIC insurance up to $250K”
        “FDIC insured”
        “FDIC insured accounts”
        “FDIC pass-through insurance guaranteed”
        We have also prepared these FAQs that you can use when your customers have questions about FDIC insurance eligibility or any of the disclosures:

        Is FDIC insurance impacted if a customer holds deposits in other accounts with the same institution?	It can be. It’s your responsibility to know which insured institutions hold your funds. If you have other business-purpose accounts with the same institution where Treasury funds are held, the FDIC might aggregate all of your business account balances with that institution in applying the 250,000 USD limit. The FDIC generally does not, however, aggregate your personal accounts with your business accounts.
        Does FDIC insurance eligibility protect from fraud or financial loss?	No, FDIC insurance eligibility is applicable only in the event of a bank failure.
        How do I know if the requirements for FDIC pass-through insurance are met?	Stripe Treasury accounts are designed to be eligible for FDIC pass-through insurance. The FDIC makes the final determination about the availability of pass-through insurance at the time of a bank’s failure.
        """
        prompt = (
            f"You are a compliance auditor. Check the following webpage content against the compliance policy provided. "
            f"Return a list of non-compliant findings.\n\n"
            f"Compliance Policy:\n{compliance_policy}\n\n"
            f"Webpage Content:\n{webpage_text[:4000]}"
            f"Produce result as a list of bullet points"
        )

        conversation: List[Dict[str, str]] = [
            {
                "human": prompt
            }
        ]

        chat: List[AIMessage | HumanMessage] = await self.__build_chat(
            conversation=conversation
        )

        llm_response: Union[List[str], Dict[str, str], str] = await self.__invoke_conversation_model(
            chat=chat
        )

        return llm_response
    
    async def format_compliance_findings(self, raw_input: str) -> List[str]:
        findings = raw_input.split("\n")
        
        formatted_output = []
        
        for finding in findings:
            finding = finding.replace('\"', "'")
            if finding.strip():

                start_idx = finding.find("**") + 2
                end_idx = finding.find("**", start_idx)
                
                if start_idx != -1 and end_idx != -1:
                    title = finding[start_idx:end_idx]

                    description = finding[end_idx + 2:].strip()
                    formatted_output.append(f"{title} => {description.capitalize()}")
                else:
                    formatted_output.append(f"{finding.strip()}")

        return formatted_output

    async def run(self, data: dict):

        try:
            
            url: str = data.get("url")
            webpage_text: str = await self.__fetch_webpage_text(url=url)

            llm_response = await self.__perform_compliance_check(webpage_text=webpage_text)

            response_data = await self.format_compliance_findings(raw_input=llm_response)

            response_payload: Dict[str, str] = {
                "url": url,
                "findings": response_data
            }

            return BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.SUCCESS,
                responseMessage="Successfully perfomed compliance check.",
                responseKey="success_compliance_check",
                data=self.dictionary_utility.convert_dict_keys_to_camel_case(response_payload)
            )

        except Exception as err:

            self.logger.error(f"Unexpected error occureed while compliance check: {err}")
            raise UnexpectedResponseError(
                responseMessage="Unexpected error occured while compliance check",
                responseKey="error_unexpected_error",
                http_status_code=HTTPStatus.UNPROCESSABLE_ENTITY
            )