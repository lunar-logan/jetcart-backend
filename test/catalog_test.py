import unittest
from mongoengine import connect

from jetcart.domain import catalog
from jetcart.domain.catalog import NotEnoughInventory

connect('jetcarttest', host='mongomock://localhost')


class TestCatalog(unittest.TestCase):
    def setUp(self) -> None:
        inv = catalog.Inventory(
            sku='abc',
            product="fake",
            warehouse="fake",
            quantity=3,
            buyer_limit=5
        )
        inv.save()

    def tearDown(self) -> None:
        pass

    def test_block_inventory(self):
        inv = catalog.get_inventory_by_id("abc")
        self.assertIsNotNone(inv)

        blocked_inv_id = catalog.block_inventory("abc", 2)
        self.assertIsNotNone(blocked_inv_id)

        blocked_inv = catalog.get_blocked_inventory_by_id(blocked_inv_id)
        self.assertIsNotNone(blocked_inv)
        self.assertEqual(blocked_inv.sku, "abc")

        inv = catalog.get_inventory_by_id("abc")
        self.assertEqual(inv.quantity, 1)

        with self.assertRaises(NotEnoughInventory):
            catalog.block_inventory("abc", 1)

    def test_block_inventory_invalid_input(self):
        with self.assertRaises(ValueError):
            catalog.block_inventory("123", 10)

        with self.assertRaises(ValueError):
            catalog.block_inventory("abc", 50)

        with self.assertRaises(NotEnoughInventory):
            catalog.block_inventory("abc", 5)

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
