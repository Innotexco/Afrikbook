from django.test import SimpleTestCase

from Stock.forms import is_selected_fk, missing_new_item_required_fields


class NewItemRequiredFieldsTests(SimpleTestCase):
    def test_placeholder_is_not_a_selected_fk(self):
        self.assertFalse(is_selected_fk(""))
        self.assertFalse(is_selected_fk("--Choose An Option--"))
        self.assertFalse(is_selected_fk("---------"))
        self.assertFalse(is_selected_fk("Select Sub Category"))
        self.assertTrue(is_selected_fk("12"))

    def test_empty_post_lists_all_required_fields(self):
        self.assertEqual(
            missing_new_item_required_fields({}),
            [
                "Category",
                "Sub-category",
                "Item Name",
                "Item Code",
                "Purchase Price",
            ],
        )

    def test_sub_category_optional_when_category_has_none(self):
        missing = missing_new_item_required_fields(
            {
                "category": "1",
                "sub_category": "",
                "item_name": "Panel 550W",
                "generated_code": "998877",
                "purchase_price": "150,000",
            },
            sub_category_required=False,
        )
        self.assertEqual(missing, [])

    def test_whitespace_item_name_is_missing(self):
        missing = missing_new_item_required_fields(
            {
                "category": "1",
                "sub_category": "2",
                "item_name": "   ",
                "generated_code": "998877",
                "purchase_price": "0",
            }
        )
        self.assertEqual(missing, ["Item Name"])
