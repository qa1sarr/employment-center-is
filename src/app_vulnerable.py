from app import create_app

if __name__ == "__main__":
    create_app(demo=True, forced_mode="vulnerable").run(port=5001, debug=True)
