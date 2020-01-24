import unittest
from TwitchCubieBot.CubieBot import CubieBot

class TestCheckForText(unittest.TestCase):

    def setUp(self):
        self.bot = CubieBot()
        self.bot.update_settings()
        self.sender = "Cubie"

    def test_dial(self):
        message = "D I A L"
        self.assertFalse(self.bot.check_for_text(message, self.sender))

    def test_aaaaa(self):
        message = "aaaaa"
        self.assertTrue(self.bot.check_for_text(message, self.sender))

    def test_AAAAA(self):
        message = "AAAAA"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_A(self):
        message = "A"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_a(self):
        message = "a"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_I_will(self):
        message = "I will do that"
        self.assertFalse(self.bot.check_for_text(message, self.sender))
    
    def test_I_wish(self):
        message = "I wish"
        self.assertFalse(self.bot.check_for_text(message, self.sender))
    
    def test_a_a_a_a_a(self):
        message = "a a a a a"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_A_A_A_A_A(self):
        message = "A A A A A"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_A_please(self):
        message = "A please"
        self.assertTrue(self.bot.check_for_text(message, self.sender))
    
    def test_A_sentence(self):
        message = "A win for me please"
        self.assertTrue(self.bot.check_for_text(message, self.sender))

class TestCheckForNumbers(unittest.TestCase):
    
    def setUp(self):
        self.bot = CubieBot()
        self.bot.update_settings()
        self.sender = "Cubie"
    
    def test_12(self):
        message = "12"
        result = 12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_12_0(self):
        message = "12.0"
        result = 12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_neg_12(self):
        message = "-12"
        result = -12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_neg_12_0(self):
        message = "-12.0"
        result = -12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_12_percentage(self):
        message = "12%"
        result = 12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_12_0_percentage(self):
        message = "12.0%"
        result = 12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_neg_12_percentage(self):
        message = "-12%"
        result = -12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_neg_12_0_percentage(self):
        message = "-12.0%"
        result = -12
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_8_div_10(self):
        message = "8/10"
        result = 8
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_neg_8_div_10(self):
        message = "-8/10"
        result = -8
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_text_div_10(self):
        message = "text/10"
        result = False
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_8_div_text(self):
        message = "8/text"
        result = 8
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_text(self):
        message = "hello"
        result = False
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_sentence(self):
        message = "hello, this is a sentence"
        result = False
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_sentence_clean(self):
        message = "hello this is a sentence without punctuation"
        result = False
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))
    
    def test_sentence_messy(self):
        message = "hello, this .is /a sentence with a% lot of / random punctuation."
        result = False
        self.assertEqual(result, self.bot.check_for_numbers(message, self.sender))

if __name__ == "__main__":
    unittest.main()