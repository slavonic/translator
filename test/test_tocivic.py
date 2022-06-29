from data.tocivic import tocivic


def test():
    result = tocivic('тѵ́хѡнъ')
    assert result == 'ти\u0301хон'

    result = tocivic('еси́')
    assert result == 'еси́'


def test01():
    result = tocivic('а҆леѯ')
    assert result == 'а\u0301лекс'


def test02():
    result = tocivic('ѿрасль')
    assert result == 'о\u0301трасль'