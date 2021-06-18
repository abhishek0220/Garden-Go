from dotenv import load_dotenv
load_dotenv()


def runserver():
    from Garden_Go import app
    return app


app = runserver()
