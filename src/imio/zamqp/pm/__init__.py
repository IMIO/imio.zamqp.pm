from zope.i18nmessageid import MessageFactory
_ = MessageFactory('imio.zamqp.pm')

BARCODE_ATTR_ID = '_barcode_inserted'


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
