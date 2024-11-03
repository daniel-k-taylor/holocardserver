from unittest import TestCase, mock
import logging
logger = logging.getLogger('app.card_database')

from tests.helpers import *

class Test_CardDatabase(TestCase):

  def test_alternate_cards_are_loaded(self):
    all_cards = card_db.all_cards
    self.assertGreater(len(all_cards), 0)
    
    # gather all original cards with alternates
    originals = list(card for card in all_cards if "alternates" in card)
    
    # assert that all originals generated alternate entries
    for original in originals:
      self.assertTrue(original["alt_id"])
      self.assertGreater(len(original["alternates"]), 0)

      for rarity in original["alternates"]:
        alt_card_id = original["card_id"] + "_" + rarity.upper()
        alt_card = next((alt_card for alt_card in all_cards if alt_card_id == alt_card["card_id"]), None)
        
        self.assertIsNotNone(alt_card)
        self.assertEqual(alt_card["alt_id"], original["card_id"])
        self.assertEqual(alt_card["rarity"], rarity)
        self.assertFalse("alternates" in alt_card)


  def test_original_cards_correct_alternates_property(self):
    all_cards = card_db.all_cards
    self.assertGreater(len(all_cards), 0)

    # gather all cards with `alternates` property
    originals = list(card for card in all_cards if "alternates" in card)

    for original in originals:
      self.assertIsInstance(original["alternates"], list)
      self.assertGreater(len(original["alternates"]), 0)


  @mock.patch.object(logger, "info")
  def test_validate_oshi_id(self, mock_logger: mock.Mock):
      # invalid oshi id
      self.assertFalse(card_db.validate_deck("INVALID OSHI", None, None))
      mock_logger.assert_called_once_with("--Deck Invalid: Oshi")
      mock_logger.reset_mock()

      # not an oshi card (hBP01-009: debut Kanata)
      self.assertFalse(card_db.validate_deck("hBP01-009", None, None))
      mock_logger.assert_called_once_with("--Deck Invalid: Oshi")

      # PASSED OSHI CARD VALIDATION


  @mock.patch.object(logger, "info")
  def test_validate_deck(self, mock_logger: mock.Mock):
    # card not found
    result = card_db.validate_deck("hBP01-006", { "hBP01-006xxx": 1 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Card not found hBP01-006xxx")
    mock_logger.reset_mock()

    # wrong card type (hBP01-006: Kiara oshi)
    result = card_db.validate_deck("hBP01-006", { "hBP01-006": 1 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: oshi not allowed")
    mock_logger.reset_mock()

    # more than allowed copies (hBP01-070: 1st bloom Polka)
    result = card_db.validate_deck("hBP01-006", { "hBP01-070": 10 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Too many cards")
    mock_logger.reset_mock()

    # more than unli debut possible (hBP01-070: debut Kanata)
    result = card_db.validate_deck("hBP01-006", { "hBP01-009": 51 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Too many cards")
    mock_logger.reset_mock()

    # too many total copies for original and alt arts (hBP01-071: 1st buzz Polka)
    result = card_db.validate_deck("hBP01-006", { "hBP01-071": 3, "hBP01-071_UR": 3 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Too many cards")
    mock_logger.reset_mock()

    # higher than required deck count (hBP01-009: debut Kanata, hBP01-071: 1st buzz Polka)
    result = card_db.validate_deck("hBP01-006", { "hBP01-009": 50, "hBP01-071": 1 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Not enough cards")
    mock_logger.reset_mock()

    # lower than required deck count (hBP01-009: debut Kanata)
    result = card_db.validate_deck("hBP01-006", { "hBP01-009": 49 }, None)
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Not enough cards")
    mock_logger.reset_mock()

    # PASSED MAIN DECK VALIDATION


  @mock.patch.object(logger, 'info')
  def test_validate_cheer_deck(self, mock_logger: mock.Mock):
    # zero cards in cheer deck
    result = card_db.validate_deck("hBP01-006", { "hBP01-009": 50 }, {})
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Cheer deck count wrong")
    mock_logger.reset_mock()

    # invalid card type in cheer deck
    result = card_db.validate_deck("hBP01-006", { "hBP01-009": 50 }, { "hBP01-006": 20 })
    self.assertFalse(result)
    mock_logger.assert_called_once_with("--Deck Invalid: Cheer deck wrong")
    mock_logger.reset_mock()

    # PASSED CHEER DECK VALIDATION


  @mock.patch.object(logger, 'info')
  def test_successful_full_deck_validation(self, mock_logger: mock.Mock):
    # complete deck
    result = card_db.validate_deck("hBP01-006", {
      "hBP01-009": 38,    # debut Kanata
      "hBP01-071": 3,     # 1st buzz Polka
      "hBP01-071_UR": 1,  # 1st buzz Polka Alt
      "hBP01-014": 4,     # 2nd bloom Kanata
      "hBP01-051": 4,     # 1st buzz Iroha Alt
    }, { "hY01-001": 10, "hY02-001": 10 })
    self.assertTrue(result)
    mock_logger.assert_not_called()