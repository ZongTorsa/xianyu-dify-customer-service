import unittest

from xianyu_customer_service.dify import build_question


class BuildQuestionTests(unittest.TestCase):
    def test_joins_non_empty_messages_in_order(self) -> None:
        self.assertEqual(build_question(["你好", "  ", "请问有货吗？"]), "你好\n请问有货吗？")

    def test_empty_messages_produce_empty_question(self) -> None:
        self.assertEqual(build_question(["", "  "]), "")


if __name__ == "__main__":
    unittest.main()
