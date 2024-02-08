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
        class _MyChecksumArchiveCapability(enum.Enum):
            GET_IT = "get-it"
            PUT_IT = "put-it"
            UNUSED = "unused"  # for testing when a capability has no operations

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

            def url_for_put(self, checksum_iri):
                # TODO: how to represent "send a PUT request here"?
                # return RedirectLadle(
                #     HTTPMethod.PUT,
                #     f'https://myarchive.example///{checksum_iri}',
                # )?
                return f"https://myarchive.example///{checksum_iri}"

        self._MyChecksumArchiveImplementation = _MyChecksumArchiveImplementation

    def test_operation_list(self):
        _my_cap = self.my_addon_category.capabilities
        _my_interface_cls = self.my_addon_category.base_interface
        _expected_get_op = AddonOperation(
            operation_fn=_my_interface_cls.url_for_get,
            operation_type=AddonOperationType.REDIRECT,
            capability=_my_cap.GET_IT,
            declaration_cls=_my_interface_cls,
            method_name="url_for_get",
        )
        _expected_put_op = AddonOperation(
            operation_fn=_my_interface_cls.url_for_put,
            operation_type=AddonOperationType.REDIRECT,
            capability=_my_cap.PUT_IT,
            declaration_cls=_my_interface_cls,
            method_name="url_for_put",
        )
        _query_operation = AddonOperation(
            operation_fn=_my_interface_cls.query_relations,
            operation_type=AddonOperationType.PROXY,
            capability=_my_cap.GET_IT,
            declaration_cls=_my_interface_cls,
            method_name="query_relations",
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared()),
            {_expected_get_op, _expected_put_op, _query_operation},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability=_my_cap.GET_IT)),
            {_expected_get_op, _query_operation},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability=_my_cap.PUT_IT)),
            {_expected_put_op},
        )
        self.assertEqual(
            set(self.my_addon_category.operations_declared(capability=_my_cap.UNUSED)),
            set(),
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_implemented(
                    self._MyChecksumArchiveImplementation,
                )
            ),
            {_expected_get_op, _expected_put_op},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_implemented(
                    self._MyChecksumArchiveImplementation,
                    capability=_my_cap.GET_IT,
                )
            ),
            {_expected_get_op},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_implemented(
                    self._MyChecksumArchiveImplementation,
                    capability=_my_cap.PUT_IT,
                )
            ),
            {_expected_put_op},
        )
        self.assertEqual(
            set(
                self.my_addon_category.operations_implemented(
                    self._MyChecksumArchiveImplementation,
                    capability=_my_cap.UNUSED,
                )
            ),
            set(),
        )
