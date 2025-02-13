from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database only if it doesn't exist
        db_path = 'service_platform.db'
        if not os.path.exists(db_path):
            db.create_all()
            print("Database created.")
    app.run(debug=True,port=8001)
