# -*- coding: utf-8 -*-
from .segment import Segment
from .settings import DocumentConfiguration
from .validators import ValidationReport


class Envelope(object):
    def __init__(self) -> None:
        self.header: Segment = Segment()
        self.trailer: Segment = Segment()
        self.body: list = []

    def format_as_edi(self, document_configuration: DocumentConfiguration) -> str:
        """
        Format the envelope as an EDI string.
        :param document_configuration: config for formatting.
        :return: document as a string of EDI.
        """
        document: str = self.header.format_as_edi(document_configuration)
        document += self._format_body_as_edi(document_configuration)
        document += self.trailer.format_as_edi(document_configuration)
        return document

    def _format_body_as_edi(self, document_configuration: DocumentConfiguration) -> str:
        """
        Format the body of the envelope as an EDI string.
        This calls format_as_edi in all the children.
        :param document_configuration: config for formatting.
        :return: document as a string of EDI.
        """
        document = ""
        for item in self.body:
            document += item.format_as_edi(document_configuration)
        return document

    def validate(self, report: ValidationReport) -> None:
        """
        Performs validation of the envelope and its components.
        :param report: the validation report to append errors.
        """
        self.header.validate(report)
        self._validate_body(report)
        self.trailer.validate(report)

    def _validate_body(self, report: ValidationReport) -> None:
        """
        Validates each of the children of the envelope.
        :param report: the validation report to append errors.
        """
        for item in self.body:
            item.validate(report)

    def number_of_segments(self) -> int:
        return len(self.body)

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "trailer": self.trailer.to_dict(),
            "body": [item.to_dict() for item in self.body],
        }


class InterchangeEnvelope(Envelope):
    def __init__(self) -> None:
        Envelope.__init__(self)
        self.groups: list = self.body


class GroupEnvelope(Envelope):
    def __init__(self) -> None:
        Envelope.__init__(self)
        self.transaction_sets: list = self.body


class TransactionSetEnvelope(Envelope):
    def __init__(self) -> None:
        Envelope.__init__(self)
        self.transaction_body: list = self.body

    def number_of_segments(self) -> int:
        header_trailer_count: int = 2
        return len(self.transaction_body) + header_trailer_count