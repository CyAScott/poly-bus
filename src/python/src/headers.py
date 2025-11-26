"""
Common header names used in PolyBus.
"""


class Headers:
    """
    Common header names used in PolyBus.
    """

    #: The correlation id header name used for specifying the correlation identifier for tracking related messages.
    CORRELATION_ID = "correlation-id"

    #: The content type header name used for specifying the message content type (e.g., "application/json").
    CONTENT_TYPE = "content-type"

    #: The message type header name used for specifying the type of the message.
    MESSAGE_TYPE = "x-type"

    #: The message id header name used for specifying the unique identifier of the message.
    REQUEST_ID = "request-id"