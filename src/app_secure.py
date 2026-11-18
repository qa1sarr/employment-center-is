from app import create_app

if __name__ == "__main__":
    create_app(demo=False, forced_mode="secure").run(port=5002, debug=True)
