#!/usr/bin/env python3
# coding=UTF-8

import os
import pytest
from clearurl.clearurl import Filter, Url

# Testfunktionen für grundlegende URL-Funktionalitäten
def test_url_parsing():
    url = Url("https://www.example.com/path?param1=value1&param2=value2#fragment")
    assert url.scheme == "https"
    assert url.netloc == "www.example.com"
    assert url.host == "www.example.com"
    assert url.path == "/path"
    assert url.query == "param1=value1&param2=value2"
    assert url.fragment == "fragment"
    assert url.query_dict == {"param1": ["value1"], "param2": ["value2"]}

def test_url_modification():
    url = Url("https://www.example.com/path?param1=value1&param2=value2#fragment")
    url.query_dict.pop("param1")
    assert url.get_url() == "https://www.example.com/path?param2=value2#fragment"
    
    url.fragment = None
    assert url.get_url() == "https://www.example.com/path?param2=value2"

# Tests für die Filterung mit Standardregeln
def test_filter_url_default():
    filter = Filter()
    
    # Google Analytics Parameter
    assert filter.filter_url("http://test.com/index.php?utm_source=test") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?utm_medium=email") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?utm_campaign=newsletter") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?fbclid=123abc") == "http://test.com/index.php"
    
    # Parameter mit Wert behalten
    assert filter.filter_url("http://test.com/index.php?id=123&utm_source=test") == "http://test.com/index.php?id=123"

# Tests für spezifische Host-Regeln
def test_filter_url_host_specific():
    filter = Filter()
    
    # Douban
    assert filter.filter_url("https://www.douban.com/annual/2019?source=broadcast&dt_dapp=1") == "https://www.douban.com/annual/2019"
    assert filter.filter_url("https://movie.douban.com/annual/2019?source=broadcast&dt_dapp=1") == "https://movie.douban.com/annual/2019"
    assert filter.filter_url("https://www.douban.com/annual/2019#test") == "https://www.douban.com/annual/2019"
    
    # Twitter
    assert filter.filter_url("https://twitter.com/username/status/1234567890?s=12") == "https://twitter.com/username/status/1234567890"
    
    # Bilibili
    assert filter.filter_url("https://www.bilibili.com/video/12345?share_source=more&share_medium=ipad&bbid=XYZ&ts=1575632820") == "https://www.bilibili.com/video/12345"

# Tests für den Rule-Modus
def test_filter_url_rule_mode():
    filter = Filter()
    url = "https://www.example.com/page?param1=value1&utm_source=newsletter"
    
    # Nur Regeln anwenden
    assert filter.filter_url(url, mode="rule") == "https://www.example.com/page?param1=value1"

# Test für Wildcard-Matching in Host-Regeln
def test_filter_url_wildcard():
    filter = Filter()
    
    # Manuelles Hinzufügen einer Wildcard-Regel für Tests
    filter.rules["hosts"]["*.example.com"] = {"query": ["test_param"], "fragment": False}
    
    assert filter.filter_url("https://subdomain.example.com/page?test_param=123&id=456#fragment") == "https://subdomain.example.com/page?id=456"

# Überschreibe die auto-Methode für den Test
class MockFilter(Filter):
    def filter_auto(self):
        # Für den Test: keine automatische Filterung durchführen
        return False

# Test für den Auto-Modus mit einer überschriebenen Methode
def test_filter_url_auto_mode():
    # Verwende die Mock-Klasse statt der originalen
    filter = MockFilter(self_study=False)
    
    url = "https://www.example.com/page?param1=value1&param2=value2"
    # Da unsere Mock-Klasse filter_auto überschreibt und False zurückgibt,
    # sollte die URL unverändert bleiben
    assert filter.filter_url(url, mode="auto") == url

# Teardown
def teardown_module(module):
    pass

if __name__ == "__main__":
    pytest.main()#!/usr/bin/env python3
# coding=UTF-8

import os
import pytest
from clearurl.clearurl import Filter, Url

# Testfunktionen für grundlegende URL-Funktionalitäten
def test_url_parsing():
    url = Url("https://www.example.com/path?param1=value1&param2=value2#fragment")
    assert url.scheme == "https"
    assert url.netloc == "www.example.com"
    assert url.host == "www.example.com"
    assert url.path == "/path"
    assert url.query == "param1=value1&param2=value2"
    assert url.fragment == "fragment"
    assert url.query_dict == {"param1": ["value1"], "param2": ["value2"]}

def test_url_modification():
    url = Url("https://www.example.com/path?param1=value1&param2=value2#fragment")
    url.query_dict.pop("param1")
    assert url.get_url() == "https://www.example.com/path?param2=value2#fragment"
    
    url.fragment = None
    assert url.get_url() == "https://www.example.com/path?param2=value2"

# Tests für die Filterung mit Standardregeln
def test_filter_url_default():
    filter = Filter()
    
    # Google Analytics Parameter
    assert filter.filter_url("http://test.com/index.php?utm_source=test") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?utm_medium=email") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?utm_campaign=newsletter") == "http://test.com/index.php"
    assert filter.filter_url("http://test.com/index.php?fbclid=123abc") == "http://test.com/index.php"
    
    # Parameter mit Wert behalten
    assert filter.filter_url("http://test.com/index.php?id=123&utm_source=test") == "http://test.com/index.php?id=123"

# Tests für spezifische Host-Regeln
def test_filter_url_host_specific():
    filter = Filter()
    
    # Douban
    assert filter.filter_url("https://www.douban.com/annual/2019?source=broadcast&dt_dapp=1") == "https://www.douban.com/annual/2019"
    assert filter.filter_url("https://movie.douban.com/annual/2019?source=broadcast&dt_dapp=1") == "https://movie.douban.com/annual/2019"
    assert filter.filter_url("https://www.douban.com/annual/2019#test") == "https://www.douban.com/annual/2019"
    
    # Twitter
    assert filter.filter_url("https://twitter.com/username/status/1234567890?s=12") == "https://twitter.com/username/status/1234567890"
    
    # Bilibili
    assert filter.filter_url("https://www.bilibili.com/video/12345?share_source=more&share_medium=ipad&bbid=XYZ&ts=1575632820") == "https://www.bilibili.com/video/12345"

# Tests für den Rule-Modus
def test_filter_url_rule_mode():
    filter = Filter()
    url = "https://www.example.com/page?param1=value1&utm_source=newsletter"
    
    # Nur Regeln anwenden
    assert filter.filter_url(url, mode="rule") == "https://www.example.com/page?param1=value1"

# Test für Wildcard-Matching in Host-Regeln
def test_filter_url_wildcard():
    filter = Filter()
    
    # Manuelles Hinzufügen einer Wildcard-Regel für Tests
    filter.rules["hosts"]["*.example.com"] = {"query": ["test_param"], "fragment": False}
    
    assert filter.filter_url("https://subdomain.example.com/page?test_param=123&id=456#fragment") == "https://subdomain.example.com/page?id=456"

# Erstelle eine Mock-Funktion für get_url_content, um nicht tatsächlich Netzwerkanfragen zu stellen
import clearurl.clearurl as clearurl
original_get_url_content = clearurl.get_url_content

def mock_get_url_content(url):
    # Unterschiedliche Inhalte zurückgeben, um automatische Filterung zu verhindern
    if "param1" in url and "param2" in url:
        return b"Mock content with both params"
    elif "param1" in url:
        return b"Different content with only param1"
    elif "param2" in url:
        return b"Different content with only param2"
    else:
        return b"Different content with no params"

# Test für den Auto-Modus mit Mock
def test_filter_url_auto_mode(monkeypatch):
    # Setze den Mock für get_url_content
    monkeypatch.setattr(clearurl, "get_url_content", mock_get_url_content)
    
    filter = Filter(self_study=False)  # Deaktiviere self_study, um die Regeldatei nicht zu ändern
    
    # Da wir jetzt unterschiedliche Inhalte für verschiedene URLs zurückgeben,
    # sollte der Filter die Parameter behalten
    url = "https://www.example.com/page?param1=value1&param2=value2"
    assert filter.filter_url(url, mode="auto") == url

# Stelle die ursprüngliche Funktion nach den Tests wieder her
def teardown_module(module):
    clearurl.get_url_content = original_get_url_content

if __name__ == "__main__":
    pytest.main()