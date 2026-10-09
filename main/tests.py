from decimal import Decimal

from django.http import QueryDict
from django.test import RequestFactory, SimpleTestCase

from main.money import format_money, parse_money, sanitize_mapping, strip_money_commas


class MoneyHelpersTests(SimpleTestCase):
    def test_parse_strips_commas_and_currency(self):
        self.assertEqual(parse_money("1,234.50"), Decimal("1234.50"))
        self.assertEqual(parse_money("₦8,011,975.00"), Decimal("8011975.00"))
        self.assertEqual(parse_money("N1,000"), Decimal("1000.00"))
        self.assertEqual(parse_money(8011975), Decimal("8011975.00"))

    def test_format_adds_commas(self):
        self.assertEqual(format_money("8011975"), "8,011,975.00")
        self.assertEqual(format_money("1,234.5"), "1,234.50")
        self.assertEqual(format_money(0), "0.00")

    def test_strip_leaves_non_money_text(self):
        self.assertEqual(strip_money_commas("Lagos, Nigeria"), "Lagos, Nigeria")
        self.assertEqual(strip_money_commas("12, 13"), "12, 13")
        self.assertEqual(strip_money_commas("8,011,975.00"), "8011975.00")

    def test_sanitize_querydict(self):
        data = QueryDict(mutable=True)
        data.setlist("amount[]", ["1,500.00", "2,000"])
        data["customer"] = "Chukwuma, Fidelis"
        data["total"] = "8,011,975.00"
        sanitize_mapping(data)
        self.assertEqual(data.getlist("amount[]"), ["1500.00", "2000"])
        self.assertEqual(data["customer"], "Chukwuma, Fidelis")
        self.assertEqual(data["total"], "8011975.00")

    def test_middleware_strips_post(self):
        from main.middleware import SanitizeMoneyMiddleware

        factory = RequestFactory()
        request = factory.post("/new-sales/", {"total": "1,250,000.50", "name": "Ada, Okon"})
        SanitizeMoneyMiddleware(lambda r: None).process_request(request)
        self.assertEqual(request.POST["total"], "1250000.50")
        self.assertEqual(request.POST["name"], "Ada, Okon")

    def test_aged_payment_fields_parse(self):
        self.assertEqual(parse_money("2,411,975.00"), Decimal("2411975.00"))
        self.assertEqual(parse_money("0"), Decimal("0.00"))
        payload = QueryDict(mutable=True)
        payload["Discount"] = "1,000.00"
        payload["cost"] = "2,411,975.00"
        payload["transfer_amount"] = "1,200,000.50"
        payload["cash_amount"] = "1,211,974.50"
        sanitize_mapping(payload)
        self.assertEqual(parse_money(payload["Discount"]), Decimal("1000.00"))
        self.assertEqual(parse_money(payload["cost"]), Decimal("2411975.00"))
        self.assertEqual(parse_money(payload["transfer_amount"]), Decimal("1200000.50"))
        self.assertEqual(parse_money(payload["cash_amount"]), Decimal("1211974.50"))

