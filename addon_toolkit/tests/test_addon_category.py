import enum
import unittest

from addon_toolkit import (
    AddonCategory,
    AddonInterface,
    AddonOperation,
    AddonOperationType,
    proxy_operation,
    redirect_operation,
)


class TestAddonCategory(unittest.TestCase):
    def setUp(self):
        class _MyChecksumArchiveCapability(enum.StrEnum):
            GET_IT = "get-it"
            PUT_IT = "put-it"

        class _MyChecksumArchiveInterface(AddonInterface):
            """this is a docstring for _MyChecksumArchiveInterface

            it should find its way to browsable docs somewhere
            """

            @redirect_operation(capability=_MyChecksumArchiveCapability.GET_IT)
            def url_for_get(self, checksum_iri) -> str:
                """this url_for_get docstring should find its way to docs"""
                raise NotImplementedError

            @proxy_operation(capability=_MyChecksumArchiveCapability.GET_IT)
            async def query_relations(self, checksum_iri, query=None):
                """this query_relations docstring should find its way to docs"""
                raise NotImplementedError

            @redirect_operation(capability=_MyChecksumArchiveCapability.PUT_IT)
            def url_for_put(self, checksum_iri):
                """this url_for_put docstring should find its way to docs"""
                raise NotImplementedError

        self.my_addon_category = AddonCategory(
            capabilities=_MyChecksumArchiveCapability,
            base_interface=_MyChecksumArchiveInterface,
        )

        class _MyChecksumArchiveImplementation(_MyChecksumArchiveInterface):
            def url_for_get(self, checksum_iri) -> str:
                return f"https://myarchive.example///{checksum_iri}"

            async def query_relations(self, checksum_iri, query=None):
                # maybe yield rdf triples (or twoples with implicit subject)
                yield ("http://purl.org/dc/terms/references", "checksum:foo:bar")

            def url_for_put(self, checksum_iri):
                # TODO: how to represent "send a PUT request here"?
                # return RedirectLadle(
                #     HTTPMethod.PUT,
                #     f'https://myarchive.example///{checksum_iri}',
                # )?
                return f"https://myarchive.example///{checksum_iri}"

        self._MyChecksumArchiveImplementation = _MyChecksumArchiveImplementation

    def test_operation_list(self):
        _get_operation = AddonOperation(
            operation_type=AddonOperationType.REDIRECT,
            capability_id=self.my_addon_category.capabilities.GET_IT,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="url_for_get",
        )
        _put_operation = AddonOperation(
            operation_type=AddonOperationType.REDIRECT,
            capability_id=self.my_addon_category.capabilities.PUT_IT,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="url_for_put",
        )
        _query_operation = AddonOperation(
            operation_type=AddonOperationType.PROXY,
            capability_id=self.my_addon_category.capabilities.GET_IT,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="query_relations",
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared()),
            {_get_operation, _put_operation, _query_operation},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability_id="get-it")),
            {_get_operation, _query_operation},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability_id="put-it")),
            {_put_operation},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability_id="nothing")),
            set(),
        )
