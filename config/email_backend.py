import ssl

import certifi
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend


class CertifiEmailBackend(DjangoEmailBackend):
    """SMTP backend that uses certifi's CA bundle (fixes macOS Python SSL errors)."""

    @property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            return super().ssl_context

        return ssl.create_default_context(cafile=certifi.where())
