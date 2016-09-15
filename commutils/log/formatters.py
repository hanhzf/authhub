import logging


class CEWLogFilter(logging.Filter):
    '''
        this filter will get logs for critical, error and warning
    '''
    def filter(self, record):
        return (record.levelno > logging.INFO)
