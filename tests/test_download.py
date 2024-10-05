import pytest
import requests
from io import BytesIO
from project0.main import fetchincidents


# Mock requests.get to simulate a successful PDF download
class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.RequestException(f"Error code: {self.status_code}")

# Mock function to simulate downloading a PDF
def mock_requests_get(url):
    if url == "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf":
        return MockResponse(b'%PDF-1.4\n%Test content\n%%EOF', 200)
    else:
        return MockResponse(b'', 404)


# Test if fetchincidents can download a PDF from a URL
def test_fetchincidents(monkeypatch):
    monkeypatch.setattr(requests, 'get', mock_requests_get)

    # Test with a valid URL
    result = fetchincidents("https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf")
    assert isinstance(result, BytesIO), "fetchincidents did not return a BytesIO object"
    assert result.getvalue().startswith(b'%PDF-1.4'), "The PDF header is incorrect"

    # Test with an invalid URL
    with pytest.raises(Exception, match=r"PDF retrieval failed"):
        fetchincidents("https://invalid-url.com")

