import logging
# Logging设计，前端显示进度条，函数，后端输入日志文件

class Logger:
    def __init__(self,filename:str):
        # to be completed, it can be used as functions
        self.logger = logging.getLogger()
        self.format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.handler = logging.FileHandler(filename)

    def initlogger(self):
        self.logger.setLevel(logging.INFO)
        self.handler.setLevel(logging.INFO)
        self.handler.Formatter = logging.Formatter(self.format)


    def
