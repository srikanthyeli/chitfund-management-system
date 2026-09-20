from src.shared.common.utils.mobile_utils import normalize_indian_mobile


def test_ten_digit_number_starting_with_91_is_kept():
    assert normalize_indian_mobile("9110770030") == "9110770030"
    assert normalize_indian_mobile("9182758096") == "9182758096"


def test_standard_ten_digit_mobile():
    assert normalize_indian_mobile("9876543210") == "9876543210"
    assert normalize_indian_mobile("6987654321") == "6987654321"


def test_country_code_prefix_is_stripped_only_when_extra_digits():
    assert normalize_indian_mobile("919876543210") == "9876543210"
    assert normalize_indian_mobile("+919876543210") == "9876543210"
    assert normalize_indian_mobile("+91 9110770030") == "9110770030"
    assert normalize_indian_mobile("09876543210") == "9876543210"
    assert normalize_indian_mobile("91-9876543210") == "9876543210"


def test_invalid_mobiles_return_none():
    assert normalize_indian_mobile("12345") is None
    assert normalize_indian_mobile("5110770030") is None
    assert normalize_indian_mobile("") is None
    assert normalize_indian_mobile(None) is None
