# -*- coding: utf-8 -*-
from app import App 
app = App()
realapp = app.app

if __name__ == '__main__':
    app.manager.run()

