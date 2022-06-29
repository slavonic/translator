from data.untitlo import untitlo


def test():

    result = untitlo('гдⷭ҇а')
    assert result == 'го\u0301спода'

def test01():
    result = untitlo('пречⷭ҇томꙋ')
    assert result == 'пречи\u0301стомꙋ'
