import pytest
from backend_projeto.utils.sanitization import (
    sanitize_ticker,
    sanitize_tickers,
    validate_date_format,
    sanitize_date,
    validate_weights,
    validate_alpha,
    sanitize_string,
)


class TestSanitizeTicker:
    def test_valid_ticker(self):
        assert sanitize_ticker("PETR4.SA") == "PETR4.SA"
        assert sanitize_ticker("AAPL") == "AAPL"
        assert sanitize_ticker("^BVSP") == "^BVSP"
    
    def test_ticker_with_spaces(self):
        assert sanitize_ticker("  PETR4.SA  ") == "PETR4.SA"
    
    def test_ticker_with_invalid_chars(self):
        # Remove caracteres inválidos
        assert sanitize_ticker("PETR4@SA") == "PETR4SA"
    
    def test_empty_ticker_raises(self):
        with pytest.raises(ValueError, match="vazio"):
            sanitize_ticker("")
    
    def test_ticker_too_long_raises(self):
        with pytest.raises(ValueError, match="muito longo"):
            sanitize_ticker("A" * 25)


class TestSanitizeTickers:
    def test_valid_list(self):
        result = sanitize_tickers(["PETR4.SA", "VALE3.SA"])
        assert result == ["PETR4.SA", "VALE3.SA"]
    
    def test_removes_duplicates(self):
        result = sanitize_tickers(["PETR4.SA", "VALE3.SA", "PETR4.SA"])
        assert result == ["PETR4.SA", "VALE3.SA"]
    
    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="vazia"):
            sanitize_tickers([])
    
    def test_invalid_ticker_in_list_raises(self):
        with pytest.raises(ValueError, match="inválido"):
            sanitize_tickers(["PETR4.SA", ""])


class TestValidateDate:
    def test_valid_date(self):
        assert validate_date_format("2024-01-15") is True
        assert validate_date_format("2023-12-31") is True
    
    def test_invalid_format(self):
        assert validate_date_format("2024/01/15") is False
        assert validate_date_format("15-01-2024") is False
        assert validate_date_format("2024-1-5") is False
    
    def test_sanitize_date_valid(self):
        assert sanitize_date("2024-01-15") == "2024-01-15"
        assert sanitize_date("  2024-01-15  ") == "2024-01-15"
    
    def test_sanitize_date_invalid_format_raises(self):
        with pytest.raises(ValueError, match="formato"):
            sanitize_date("2024/01/15")
    
    def test_sanitize_date_invalid_values_raises(self):
        with pytest.raises(ValueError, match="Mês inválido"):
            sanitize_date("2024-13-01")
        with pytest.raises(ValueError, match="Dia inválido"):
            sanitize_date("2024-01-32")


class TestValidateWeights:
    def test_none_returns_none(self):
        assert validate_weights(None, 3) is None
    
    def test_valid_weights(self):
        result = validate_weights([0.3, 0.4, 0.3], 3)
        assert len(result) == 3
        assert abs(sum(result) - 1.0) < 1e-9
    
    def test_normalizes_weights(self):
        result = validate_weights([1, 2, 3], 3)
        assert abs(sum(result) - 1.0) < 1e-9
        assert abs(result[0] - 1/6) < 1e-9
        assert abs(result[1] - 2/6) < 1e-9
        assert abs(result[2] - 3/6) < 1e-9
    
    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="difere"):
            validate_weights([0.5, 0.5], 3)
    
    def test_negative_weights_raises(self):
        with pytest.raises(ValueError, match="negativos"):
            validate_weights([0.5, -0.2, 0.7], 3)
    
    def test_zero_sum_raises(self):
        with pytest.raises(ValueError, match="soma"):
            validate_weights([0, 0, 0], 3)


class TestValidateAlpha:
    def test_valid_alpha(self):
        assert validate_alpha(0.95) == 0.95
        assert validate_alpha(0.99) == 0.99
    
    def test_alpha_out_of_range_raises(self):
        with pytest.raises(ValueError, match="entre 0 e 1"):
            validate_alpha(0.0)
        with pytest.raises(ValueError, match="entre 0 e 1"):
            validate_alpha(1.0)
        with pytest.raises(ValueError, match="entre 0 e 1"):
            validate_alpha(1.5)


class TestSanitizeString:
    def test_valid_string(self):
        assert sanitize_string("Hello World") == "Hello World"
    
    def test_strips_whitespace(self):
        assert sanitize_string("  test  ") == "test"
    
    def test_removes_control_chars(self):
        result = sanitize_string("test\x00\x01string")
        assert result == "teststring"
    
    def test_empty_raises(self):
        with pytest.raises(ValueError, match="vazia"):
            sanitize_string("")
    
    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="muito longa"):
            sanitize_string("A" * 150, max_length=100)
