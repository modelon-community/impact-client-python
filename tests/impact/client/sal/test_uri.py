from modelon.impact.client.sal.uri import URI


def test_uri_concat_no_slashes():
    uri = URI('http://modelon.com/impact') / 'api'
    assert 'http://modelon.com/impact/api' == uri.resolve()


def test_uri_concat_base_ends_with_slash():
    uri = URI('http://modelon.com/impact/') / 'api'
    assert 'http://modelon.com/impact/api' == uri.resolve()


def test_uri_concat_relativ_starts_with_slash():
    uri = URI('http://modelon.com/impact') / '/api'
    assert 'http://modelon.com/impact/api' == uri.resolve()


def test_uri_concat_both_base_and_rel_part_have_slashes():
    uri = URI('http://modelon.com/impact/') / '/api'
    assert 'http://modelon.com/impact/api' == uri.resolve()


def test_uri_concat_rel_part_ends_with_slash():
    uri = URI('http://modelon.com/impact') / 'api/'
    assert 'http://modelon.com/impact/api/' == uri.resolve()