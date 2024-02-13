import enum
import unittest

from addon_toolkit import (
    addon_interface,
    get_operation_declarations,
    get_operation_implementations,
    proxy_operation,
    redirect_operation,
)
from addon_toolkit.interface import AddonOperationImplementation
from addon_toolkit.operation import (
    AddonOperationDeclaration,
    AddonOperationType,
)


class TestAddonInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ###
        # declare the capabilities and interface for a category of addons

        class _MyCapability(enum.Enum):
            GET_IT = "get-it"
            PUT_IT = "put-it"
            UNUSED = "unused"  # for testing when a capability has no operations

        @addon_interface(capability_enum=_MyCapability)
        class _MyInterface:
            """this _MyInterface docstring should find its way to browsable docs somewhere"""

            @redirect_operation(capability=_MyCapability.GET_IT)
            def url_for_get(self, checksum_iri) -> str:
                """this url_for_get docstring should find its way to docs"""
                raise NotImplementedError

            @proxy_operation(capability=_MyCapability.GET_IT)
            async def query_relations(self, checksum_iri, query=None):
                """this query_relations docstring should find its way to docs"""
                raise NotImplementedError

            @redirect_operation(capability=_MyCapability.PUT_IT)
            def url_for_put(self, checksum_iri):
                """this url_for_put docstring should find its way to docs"""
                raise NotImplementedError

        ###
        # implement (some of) the interface's declared operations

        class _MyImplementation(_MyInterface):
            def url_for_get(self, checksum_iri) -> str:
                """this url_for_get docstring could contain implementation-specific caveats"""
                return f"https://myarchive.example///{checksum_iri}"

            def url_for_put(self, checksum_iri):
                """this url_for_put docstring could contain implementation-specific caveats"""
                # TODO: how to represent "send a PUT request here"?
                # return RedirectLadle(
                #     HTTPMethod.PUT,
                #     f'https://myarchive.example///{checksum_iri}',
                # )?
                return f"https://myarchive.example///{checksum_iri}"

        cls._MyCapability = _MyCapability
        cls._MyInterface = _MyInterface
        cls._MyImplementation = _MyImplementation

        cls._expected_get_op = AddonOperationDeclaration(
            operation_type=AddonOperationType.REDIRECT,
            capability=_MyCapability.GET_IT,
            operation_fn=_MyInterface.url_for_get,
        )
        cls._expected_put_op = AddonOperationDeclaration(
            operation_type=AddonOperationType.REDIRECT,
            capability=_MyCapability.PUT_IT,
            operation_fn=_MyInterface.url_for_put,
        )
        cls._expected_query_op = AddonOperationDeclaration(
            operation_type=AddonOperationType.PROXY,
            capability=_MyCapability.GET_IT,
            operation_fn=_MyInterface.query_relations,
        )

        cls._expected_get_imp = AddonOperationImplementation(
            operation=cls._expected_get_op,
            implementation_cls=_MyImplementation,
        )
        cls._expected_put_imp = AddonOperationImplementation(
            operation=cls._expected_put_op,
            implementation_cls=_MyImplementation,
        )

    def test_get_operation_declarations(self):
        self.assertEqual(
            set(get_operation_declarations(self._MyInterface)),
            {self._expected_get_op, self._expected_put_op, self._expected_query_op},
        )
        self.assertEqual(
            set(
                get_operation_declarations(
                    self._MyInterface, capability=self._MyCapability.GET_IT
                )
            ),
            {self._expected_get_op, self._expected_query_op},
        )
        self.assertEqual(
            set(
                get_operation_declarations(
                    self._MyInterface, capability=self._MyCapability.PUT_IT
                )
            ),
            {self._expected_put_op},
        )
        self.assertEqual(
            set(
                get_operation_declarations(
                    self._MyInterface, capability=self._MyCapability.UNUSED
                )
            ),
            set(),
        )

    def test_get_implemented_operations(self):
        self.assertEqual(
            set(get_operation_implementations(self._MyImplementation)),
            {self._expected_get_imp, self._expected_put_imp},
        )
        self.assertEqual(
            set(
                get_operation_implementations(
                    self._MyImplementation,
                    capability=self._MyCapability.GET_IT,
                )
            ),
            {self._expected_get_imp},
        )
        self.assertEqual(
            set(
                get_operation_implementations(
                    self._MyImplementation,
                    capability=self._MyCapability.PUT_IT,
                )
            ),
            {self._expected_put_imp},
        )
        self.assertEqual(
            set(
                get_operation_implementations(
                    self._MyImplementation,
                    capability=self._MyCapability.UNUSED,
                )
            ),
            set(),
        )
