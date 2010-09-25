# coding=utf8
"""
Status of the payment.

See: https://secure.ogone.com/ncol/param_cookbook.asp?CSRFSP=%2Fncol%2Ftest%2Fdownload_docs.asp&CSRFKEY=2FA1BDB2690AAD330CAEF5B9F2F7AC73A44FA90A&CSRFTS=20081004115228

0  - Incomplete or invalid
1  - Cancelled by client
2  - Authorization refused
4  - Order stored
41 - Waiting client payment
5  - Authorized
51 - Authorization waiting
52 - Authorization not known
59 - Author. to get manually
6  - Authorized and canceled
61 - Author. deletion waiting
62 - Author. deletion uncertain
63 - Author. deletion refused
7  - Payment deleted
71 - Payment deletion pending
72 - Payment deletion uncertain
73 - Payment deletion refused
74 - Payment deleted (not accepted)
75 - Deletion processed by merchant
8  - Refund
81 - Refund pending
82 - Refund uncertain
83 - Refund refused
84 - Payment declined by the acquirer (will be debited)
85 - Refund processed by merchant
9  - Payment requested
91 - Payment processing
92 - Payment uncertain
93 - Payment refused
94 - Refund declined by the acquirer
95 - Payment processed by merchant
97 - Being processed (intermediate technical status)
98 - Being processed (intermediate technical status)
99 - Being processed (intermediate technical status)

The table above summarises the possible statuses of the payments.

Statuses in 1 digit are 'normal' statuses:

    * 0 means the payment is invalid (e.g. data validation error) or the processing is not complete either because it is still underway, or because the transaction was interrupted. If the cause is a validation error, an additional error code (*) (NCERROR) identifies the error.
    * 1 means the customer cancelled the transaction.
    * 2 means the acquirer did not authorise the payment.
    * 5 means the acquirer autorised the payment.
    * 9 means the payment was captured.

Statuses in 2 digits correspond either to 'intermediary' situations or to abnormal events. When the second digit is:

    * 1, this means the payment processing is on hold.
    * 2, this means an unrecoverable error occurred during the communication with the acquirer. The result is therefore not determined. You must therefore call the acquirer's helpdesk to find out the actual result of this transaction.
    * 3, this means the payment processing (capture or cancellation) was refused by the acquirer whilst the payment had been authorised beforehand. It can be due to a technical error or to the expiration of the authorisation. You must therefore call the acquirer's helpdesk to find out the actual result of this transaction.
    * 4, this means our system has been notified the transaction was rejected well after the transaction was sent to your acquirer.
    * 5, this means our system hasn’t sent the requested transaction to the acquirer since the merchant will send the transaction to the acquirer himself, like he specified in his configuration.
"""

STATUS_DESCRIPTIONS = {
    0  : 'Incomplete or invalid',
    1  : 'Cancelled by client',
    2  : 'Authorization refused',
    4  : 'Order stored',
    41 : 'Waiting client payment',
    5  : 'Authorized',
    51 : 'Authorization waiting',
    52 : 'Authorization not known',
    59 : 'Author. to get manually',
    6  : 'Authorized and canceled',
    61 : 'Author. deletion waiting',
    62 : 'Author. deletion uncertain',
    63 : 'Author. deletion refused',
    7  : 'Payment deleted',
    71 : 'Payment deletion pending',
    72 : 'Payment deletion uncertain',
    73 : 'Payment deletion refused',
    74 : 'Payment deleted (not accepted)',
    75 : 'Deletion processed by merchant',
    8  : 'Refund',
    81 : 'Refund pending',
    82 : 'Refund uncertain',
    83 : 'Refund refused',
    84 : 'Payment declined by the acquirer (will be debited)',
    85 : 'Refund processed by merchant',
    9  : 'Payment requested',
    91 : 'Payment processing',
    92 : 'Payment uncertain',
    93 : 'Payment refused',
    94 : 'Refund declined by the acquirer',
    95 : 'Payment processed by merchant',
    97 : 'Being processed (intermediate technical status)',
    98 : 'Being processed (intermediate technical status)',
    99 : 'Being processed (intermediate technical status)',
}

SUCCESS_CODES = (5, 4, 9, 41, 51, 91)
SUCCESS_STATUS = 'success'

DECLINE_CODES = (2, 93)
DECLINE_STATUS = 'decline'

EXCEPTION_CODES = (52, 92)
EXCEPTION_STATUS = 'exception'

CANCEL_CODES = (1, )
CANCEL_STATUS = 'cancel'

def get_status_description(status):
    assert isinstance(status, int)

    return STATUS_DESCRIPTIONS[status]

def get_status_category(status):
    """ The Ogone API allows for four kind of results:
        - success
        - decline
        - exception
        - cancel

        In this function we do mapping from the status
        number into one of these categories of results.
    """

    logging.debug('Processing status message %d', status)

    if status in SUCCESS_CODES:
        return SUCCESS_STATUS

    if status in DECLINE_CODES:
        return DECLINE_STATUS

    if status in EXCEPTION_CODES:
        return EXCEPTION_STATUS

    if status in CANCEL_CODES:
        return CANCEL_STATUS

    from django_ogone.exceptions import UnknownStatusException

    raise UnknownStatusException(status)
