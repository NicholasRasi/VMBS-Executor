import platform
import os
import sys
import psutil


class Server():
    SIZE_UNITS = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    @staticmethod
    def get_all():
        return {"platform": Server.get_platform(),
                "processor": Server.get_processor(),
                "memory": Server.get_memory(),
                "machine": Server.get_machine(),
                "hostname": Server.get_hostname(),
                "version": Server.get_version(),
                "username": Server.get_username()}

    @staticmethod
    def get_platform():
        return platform.platform()

    @staticmethod
    def get_processor():
        return platform.processor()

    @staticmethod
    def get_memory():
        return Server.format_size(psutil.virtual_memory()[0], binary=True)

    @staticmethod
    def get_machine():
        return platform.machine()

    @staticmethod
    def get_hostname():
        return platform.node()

    @staticmethod
    def get_version():
        return sys.version

    @staticmethod
    def get_username():
        return os.getlogin()

    @staticmethod
    def format_size(num_bytes, binary=False, strip=True):
        """
        Format a number of bytes as a human readable size.

        Parameters
        ----------
        num_bytes : int
            The size to format.
        binary : bool, optional
            The base to group the number of bytes.
        strip : bool, optional
            If trailing zeros should be keeped or stripped.

        Returns
        -------
        str
            The human readable file size.

        Examples
        --------
        >>> format_size(42)
        42 bytes
        >>> format_size(1000)
        1 kB
        >>> format_size(1080)
        1.08 kB
        >>> format_size(1810782348)
        1.81 GB
        >>> format_size(1810782348, binary=True)
        1.69 GB
        """
        if binary:
            base = 2 ** 10
        else:
            base = 10 ** 3

        for i, unit in reversed(list(enumerate(Server.SIZE_UNITS))):
            divider = base ** i
            if num_bytes >= divider:
                formatted = '{:0.2f}'.format(num_bytes / divider, unit)
                if strip:
                    formatted = formatted.rstrip('0').rstrip('.')
                formatted = '{} {}'.format(formatted, unit)

                return formatted

        # Failed to match a unit
        return '0 {}'.format(Server.SIZE_UNITS[0])
