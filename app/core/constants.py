SMALL = 1
MEDIUM = 2
LARGE = 3
ORDER_SIZE = (
    (SMALL, u'Small'),
    (MEDIUM, u'Medium'),
    (LARGE, u'Large')
)

MARGARITA = 1
MARINARA = 2
SALAMI = 3
ORDER_TITLE = (
    (1, u'margarita'),
    (2, u'marinara'),
    (3, u'salami')
)

RECEIVED = 1
IN_PROCESS = 2
OUT_FOR_DELIVERY = 3
DELIVERED = 4
RETURNED = 5

ORDER_STATUS = (
    (RECEIVED, u'Received'),
    (IN_PROCESS, u'In Process'),
    (OUT_FOR_DELIVERY, u'Out For Delivery'),
    (DELIVERED, u'Delivered'),
    (RETURNED, u'Returned')
)
