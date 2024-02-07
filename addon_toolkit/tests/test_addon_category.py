import unittest

from primitive_metadata import primitive_rdf as rdf

from addon_toolkit import (
    AddonCapabilities,
    AddonCapability,
    AddonCategory,
    AddonInterface,
    AddonOperation,
    AddonOperationType,
    proxy_operation,
    redirect_operation,
)


class TestAddonCategory(unittest.TestCase):
    def setUp(self):
        self.namespace = rdf.IriNamespace("http://checksum-storage.example/")

        class _MyChecksumArchiveCapabilities(AddonCapabilities):
            GET = AddonCapability(
                iri=self.namespace.get_thing,
                label=rdf.literal("get a thing", language="en"),
                comment=rdf.literal("can read", language="en"),
            )
            PUT = AddonCapability(
                iri=self.namespace.put_thing,
                label=rdf.literal("put a thing", language="en"),
                comment=rdf.literal("can write", language="en"),
            )

        class _MyChecksumArchiveInterface(AddonInterface):
            """this is a docstring for _MyChecksumArchiveInterface

            it should find its way to browsable docs somewhere
            """

            @redirect_operation(capability=_MyChecksumArchiveCapabilities.GET)
            def url_for_get(self, checksum_iri) -> str:
                """this url_for_get docstring should find its way to docs"""
                return f"https://myarchive.example///{checksum_iri}"

            @proxy_operation(capability=_MyChecksumArchiveCapabilities.GET)
            async def query_relations(self, checksum_iri, query=None):
                """this query_relations docstring should find its way to docs"""
                # yields rdf triples (or twoples with implicit subject)
                yield ("http://purl.org/dc/terms/references", "checksum:foo:bar")

            @redirect_operation(capability=_MyChecksumArchiveCapabilities.PUT)
            def url_for_put(self, checksum_iri):
                """this url_for_put docstring should find its way to docs"""
                # TODO: how to represent "send a PUT request here"?
                # return RedirectLadle(
                #     HTTPMethod.PUT,
                #     f'https://myarchive.example///{checksum_iri}',
                # )?
                return f"https://myarchive.example///{checksum_iri}"

        self.my_addon_category = AddonCategory(
            capabilities=_MyChecksumArchiveCapabilities,
            base_interface=_MyChecksumArchiveInterface,
        )

        class _MyChecksumArchiveImplementation(_MyChecksumArchiveInterface):
            def url_for_get(self, checksum_iri) -> str:
                return f"https://myarchive.example///{checksum_iri}"

            async def query_relations(self, checksum_iri, query=None):
                # yields rdf triples (or twoples with implicit subject)
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
            capability=self.my_addon_category.capabilities.GET,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="url_for_get",
        )
        _put_operation = AddonOperation(
            operation_type=AddonOperationType.REDIRECT,
            capability=self.my_addon_category.capabilities.PUT,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="url_for_put",
        )
        _query_operation = AddonOperation(
            operation_type=AddonOperationType.PROXY,
            capability=self.my_addon_category.capabilities.GET,
            declaration_cls=self.my_addon_category.base_interface,
            method_name="query_relations",
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared()),
            {_get_operation, _put_operation, _query_operation},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_declared(
                    capability_iri=self.namespace.get_thing,
                )
            ),
            {_get_operation, _query_operation},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_declared(
                    capability_iri=self.namespace.put_thing,
                )
            ),
            {_put_operation},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_declared(
                    capability_iri="http://nothing.example/",
                )
            ),
            set(),
        )
