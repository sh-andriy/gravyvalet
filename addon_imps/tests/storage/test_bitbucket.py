import unittest
from unittest.mock import (
    AsyncMock,
    Mock,
)

from addon_imps.storage.bitbucket import BitbucketStorageImp
from addon_toolkit.interfaces.storage import (
    ItemResult,
    ItemType,
    StorageConfig,
)


class TestBitbucketStorageImp(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.base_url = "https://api.bitbucket.org/2.0/"
        self.config = StorageConfig(
            external_api_url=self.base_url,
            max_upload_mb=100,
            connected_root_id="",
            external_account_id="",
        )
        self.network = Mock()
        self.network.GET = Mock()
        self.imp = BitbucketStorageImp(config=self.config, network=self.network)

    def _patch_get(self, return_value: dict, status: int = 200):
        mock_response = AsyncMock()
        mock_response.json_content.return_value = return_value
        mock_response.http_status = status

        context_manager_mock = AsyncMock()
        context_manager_mock.__aenter__.return_value = mock_response
        context_manager_mock.__aexit__.return_value = None

        self.network.GET.return_value = context_manager_mock

    def _assert_get(self, endpoint: str, query: dict = None):
        if query is None:
            self.network.GET.assert_called_once_with(endpoint)
        else:
            self.network.GET.assert_called_once_with(endpoint, query=query)

    async def test_get_external_account_id(self):
        mock_response = {"uuid": "{user-uuid}"}
        self._patch_get(mock_response)

        result = await self.imp.get_external_account_id({})

        self.assertEqual(result, "{user-uuid}")
        self._assert_get("user")

    async def test_get_external_account_id_no_uuid(self):
        mock_response = {}
        self._patch_get(mock_response)

        with self.assertRaises(ValueError) as context:
            await self.imp.get_external_account_id({})

        self.assertIn("Failed to retrieve user UUID", str(context.exception))
        self._assert_get("user")

    async def test_list_root_items(self):
        mock_response = {
            "values": [
                {
                    "workspace": {
                        "slug": "workspace1",
                        "name": "Workspace One",
                    }
                },
                {
                    "workspace": {
                        "slug": "workspace2",
                        "name": "Workspace Two",
                    }
                },
            ],
            "next": "https://api.bitbucket.org/2.0/user/permissions/workspaces?page=2",
        }
        self._patch_get(mock_response)
        expected_items = [
            ItemResult(
                item_id="workspace:workspace1",
                item_name="Workspace One",
                item_type=ItemType.FOLDER,
            ),
            ItemResult(
                item_id="workspace:workspace2",
                item_name="Workspace Two",
                item_type=ItemType.FOLDER,
            ),
        ]

        result = await self.imp.list_root_items()

        self.assertEqual(result.items, expected_items)
        self.assertEqual(result.next_sample_cursor, mock_response["next"])
        self._assert_get("user/permissions/workspaces", query={"pagelen": "100"})

    async def test_get_item_info_workspace(self):
        item_id = "workspace:workspace1"
        mock_response = {
            "slug": "workspace1",
            "name": "Workspace One",
        }
        self._patch_get(mock_response)

        result = await self.imp.get_item_info(item_id)

        expected_result = ItemResult(
            item_id=item_id,
            item_name="Workspace One",
            item_type=ItemType.FOLDER,
        )
        self.assertEqual(result, expected_result)
        self._assert_get("workspaces/workspace1")

    async def test_get_item_info_repository(self):
        item_id = "repository:workspace1/repo1"
        mock_response = {
            "full_name": "workspace1/repo1",
            "name": "Repository One",
        }
        self._patch_get(mock_response)

        result = await self.imp.get_item_info(item_id)

        expected_result = ItemResult(
            item_id=item_id,
            item_name="Repository One",
            item_type=ItemType.FOLDER,
        )
        self.assertEqual(result, expected_result)
        self._assert_get("repositories/workspace1/repo1")

    async def test_get_item_info_file(self):
        item_id = "repository:workspace1/repo1/path/to/file.txt"
        mock_response = {
            "type": "commit_file",
            "path": "path/to/file.txt",
        }
        self._patch_get(mock_response)

        result = await self.imp.get_item_info(item_id)

        expected_result = ItemResult(
            item_id=item_id,
            item_name="file.txt",
            item_type=ItemType.FILE,
        )
        self.assertEqual(result, expected_result)
        self._assert_get("repositories/workspace1/repo1/src/HEAD/path/to/file.txt")

    async def test_list_child_items_workspace(self):
        item_id = "workspace:workspace1"
        mock_response = {
            "values": [
                {
                    "full_name": "workspace1/repo1",
                    "name": "Repository One",
                },
                {
                    "full_name": "workspace1/repo2",
                    "name": "Repository Two",
                },
            ],
            "next": "https://api.bitbucket.org/2.0/repositories/workspace1?page=2",
        }
        self._patch_get(mock_response)
        expected_items = [
            ItemResult(
                item_id="repository:workspace1/repo1",
                item_name="Repository One",
                item_type=ItemType.FOLDER,
            ),
            ItemResult(
                item_id="repository:workspace1/repo2",
                item_name="Repository Two",
                item_type=ItemType.FOLDER,
            ),
        ]

        result = await self.imp.list_child_items(item_id)

        self.assertEqual(result.items, expected_items)
        self.assertEqual(result.next_sample_cursor, mock_response["next"])
        expected_query = {"role": "member", "pagelen": "100"}
        self._assert_get("repositories/workspace1", query=expected_query)

    async def test_list_child_items_repository(self):
        item_id = "repository:workspace1/repo1"
        mock_response = {
            "values": [
                {
                    "type": "commit_directory",
                    "path": "src",
                },
                {
                    "type": "commit_file",
                    "path": "README.md",
                },
            ],
            "next": None,
        }
        self._patch_get(mock_response)
        expected_items = [
            ItemResult(
                item_id="repository:workspace1/repo1/src",
                item_name="src",
                item_type=ItemType.FOLDER,
            ),
            ItemResult(
                item_id="repository:workspace1/repo1/README.md",
                item_name="README.md",
                item_type=ItemType.FILE,
            ),
        ]

        result = await self.imp.list_child_items(item_id)

        self.assertEqual(result.items, expected_items)
        self.assertIsNone(result.next_sample_cursor)
        self._assert_get("repositories/workspace1/repo1/src/HEAD/", query={})

    async def test_list_child_items_repository_with_path(self):
        item_id = "repository:workspace1/repo1/src"
        mock_response = {
            "values": [
                {
                    "type": "commit_file",
                    "path": "src/main.py",
                },
                {
                    "type": "commit_file",
                    "path": "src/utils.py",
                },
            ],
            "next": None,
        }
        self._patch_get(mock_response)
        expected_items = [
            ItemResult(
                item_id="repository:workspace1/repo1/src/main.py",
                item_name="main.py",
                item_type=ItemType.FILE,
            ),
            ItemResult(
                item_id="repository:workspace1/repo1/src/utils.py",
                item_name="utils.py",
                item_type=ItemType.FILE,
            ),
        ]

        result = await self.imp.list_child_items(item_id)

        self.assertEqual(result.items, expected_items)
        self.assertIsNone(result.next_sample_cursor)
        self._assert_get("repositories/workspace1/repo1/src/HEAD/src", query={})

    async def test_build_wb_config_repository(self):
        self.imp.config = StorageConfig(
            external_api_url="https://api.bitbucket.org/2.0/",
            max_upload_mb=100,
            connected_root_id="repository:workspace1/repo1",
            external_account_id="",
        )

        result = await self.imp.build_wb_config()

        expected_result = {
            "workspace": "workspace1",
            "repo_slug": "repo1",
            "host": "api.bitbucket.org",
        }
        self.assertEqual(result, expected_result)

    async def test_build_wb_config_workspace(self):
        self.imp.config = StorageConfig(
            external_api_url="https://api.bitbucket.org/2.0/",
            max_upload_mb=100,
            connected_root_id="workspace:workspace1",
            external_account_id="",
        )

        result = await self.imp.build_wb_config()

        expected_result = {
            "workspace": "workspace1",
            "host": "api.bitbucket.org",
        }
        self.assertEqual(result, expected_result)

    async def test_handle_response_success(self):
        mock_response = AsyncMock()
        mock_response.http_status = 200
        mock_response.json_content = AsyncMock(return_value={"key": "value"})

        result = await self.imp._handle_response(mock_response)

        self.assertEqual(result, {"key": "value"})
        mock_response.json_content.assert_awaited_once()

    async def test_handle_response_error(self):
        mock_response = AsyncMock()
        mock_response.http_status = 400
        mock_response.json_content = AsyncMock(
            return_value={"error": {"message": "Bad Request"}}
        )

        with self.assertRaises(ValueError) as context:
            await self.imp._handle_response(mock_response)

        self.assertIn("HTTP Error 400: Bad Request", str(context.exception))
        mock_response.json_content.assert_awaited_once()

    async def test_parse_item_id(self):
        item_id = "repository:workspace1/repo1/path/to/file.txt"
        result = self.imp._parse_item_id(item_id)
        self.assertEqual(result, ("repository", "workspace1/repo1/path/to/file.txt"))

    async def test_make_item_id(self):
        item_type = "repository"
        actual_id = "workspace1/repo1"
        result = self.imp._make_item_id(item_type, actual_id)
        self.assertEqual(result, "repository:workspace1/repo1")

    async def test_split_repo_full_name_and_path(self):
        actual_id = "workspace1/repo1/path/to/file.txt"
        repo_full_name, path_param = self.imp._split_repo_full_name_and_path(actual_id)
        self.assertEqual(repo_full_name, "workspace1/repo1")
        self.assertEqual(path_param, "path/to/file.txt")

    async def test_params_from_cursor(self):
        cursor = (
            "https://api.bitbucket.org/2.0/repositories/workspace1?page=2&pagelen=100"
        )
        result = self.imp._params_from_cursor(cursor)
        self.assertEqual(result, {"page": "2", "pagelen": "100"})

    async def test_params_from_cursor_empty(self):
        cursor = ""
        result = self.imp._params_from_cursor(cursor)
        self.assertEqual(result, {})

    async def test_get_item_info_invalid_item_id(self):
        item_id = "invalid_item_id"
        with self.assertRaises(ValueError) as context:
            await self.imp.get_item_info(item_id)
        self.assertIn("Invalid item_id format", str(context.exception))

    async def test_list_child_items_invalid_item_id(self):
        item_id = "invalid_item_id"
        with self.assertRaises(ValueError) as context:
            await self.imp.list_child_items(item_id)
        self.assertIn("Invalid item_id format", str(context.exception))

    async def test_get_item_info_unknown_item_type(self):
        item_id = "unknown_type:some_id"
        with self.assertRaises(ValueError) as context:
            await self.imp.get_item_info(item_id)
        self.assertIn("Unknown item type: unknown_type", str(context.exception))

    async def test_list_child_items_unknown_item_type(self):
        item_id = "unknown_type:some_id"
        with self.assertRaises(ValueError) as context:
            await self.imp.list_child_items(item_id)
        self.assertIn(
            "Cannot list child items for item type unknown_type", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
