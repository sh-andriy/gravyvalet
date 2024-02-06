from addon_toolkit import (
    AddonCapability,
    BaseAddonInterface,
    proxy_operation,
    redirect_operation,
)


class TestBaseAddonInterface(unittest.TestCase):
    def setUp(self):
        class _MyChecksumStorageInterface(BaseAddonInterface):
            """this is a docstring for _MyChecksumStorageInterface

            it should find its way to browsable docs somewhere
            """

            @redirect_operation(capability=AddonCapability.OBSERVE)
            def download_url(self, checksum_iri) -> str:
                """this download_url docstring should find its way to docs"""
                return f"https://myarchive.example///{checksum_iri}"

            @proxy_operation(capability=AddonCapability.OBSERVE)
            async def query_relations(self, checksum_iri, query=None):
                """this query_relations docstring should find its way to docs"""
                # yields rdf triples (or twoples with implicit subject)
                yield ("http://purl.org/dc/terms/references", "checksum:foo:bar")

            @redirect_operation(capability=AddonCapability.PUBLISH)
            def upload_url(self, checksum_iri):
                """this upload_url docstring should find its way to docs"""
                # TODO: how to represent "send a PUT request here"?
                # return RedirectLadle(
                #     HTTPMethod.PUT,
                #     f'https://myarchive.example///{checksum_iri}',
                # )?
                return f"https://myarchive.example///{checksum_iri}"

    def test_operation_list(self):
        self.assertEqual(
            self._MyChecksumStorageInterface.supported_capabilities(),
            {
                AddonCapability.OBSERVE,
                AddonCapability.PUBLISH,
            },
        )
        self.assertEqual(
            self._MyChecksumStorageInterface.capability_operations(
                AddonCapability.OBSERVE
            ),
            set(),  # TODO
        )
        _interface = _MyChecksumStorageInterface(
            # TODO: account, addon
        )
        self.assertEqual(
            self._interface.(),
            {
                AddonCapability.OBSERVE,
                AddonCapability.PUBLISH,
            },
        )
