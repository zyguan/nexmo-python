import pytest

from nexmo.core import Sling, IllegalStateError


def test_empty_sling():
    s = Sling()
    assert s is not None
    assert s._headers == {}


def test_base():
    s = Sling().base("https://rest.nexmo.com/")
    assert s._raw_url == "https://rest.nexmo.com/"

    s = Sling().base("https://rest.nexmo.com/path")
    assert s._raw_url == "https://rest.nexmo.com/path"


def test_path():
    s = Sling().base("https://rest.nexmo.com/").path("first")
    assert s._raw_url == "https://rest.nexmo.com/first", "Append to root should set the path."

    s = Sling().base("https://rest.nexmo.com/first").path("replace/this")
    assert s._raw_url == "https://rest.nexmo.com/replace/this", "Setting a path on a url which does not end with / should replace the last element."

    s = Sling().base("https://rest.nexmo.com/replace/this").path("me")
    assert s._raw_url == "https://rest.nexmo.com/replace/me", "Setting a path on a url which does not end with / should replace ONLY the last element."

    s = Sling().base("https://rest.nexmo.com/replace/me").path("/only")
    assert s._raw_url == "https://rest.nexmo.com/only", "Setting a path which starts with / should replace the whole path."


def test_path_on_empty_base():
    s = Sling().path("first")
    assert s._raw_url == "first"

    s = Sling().path("first").base("https://rest.nexmo.com/")
    assert s._raw_url == "https://rest.nexmo.com/"

    s = Sling().base("https://rest.nexmo.com/sms").base(
        "https://api.nexmo.com")
    assert s._raw_url == "https://api.nexmo.com"


def test_new():
    a = Sling().base("https://api.nexmo.com/sms/").headers({
        'a': 'b'
    }).params({
        'type': 'text'
    })
    b = a.new().path("send").headers({
        'b': 'c'
    }).params({
        'format': 'mp3',
    }).method('PUT')

    assert a is not b
    assert a._raw_url == "https://api.nexmo.com/sms/"
    assert b._raw_url == "https://api.nexmo.com/sms/send"

    assert a._headers == {'a': 'b'}
    assert b._headers == {
        'a': 'b',
        'b': 'c',
    }

    assert a._params == {
        'type': 'text',
    }
    assert b._params == {
        'type': 'text',
        'format': 'mp3',
    }

    assert a._method == "GET"
    assert b._method == "PUT"
