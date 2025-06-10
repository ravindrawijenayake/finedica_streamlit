import os
import sys
import json
import mysql.connector
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_avatar(email):
    """Generate and store avatar in database"""
    try:
        # Connect to the database
        with mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="user_reg_db",
            auth_plugin='mysql_native_password'
        ) as conn:
            cursor = conn.cursor(dictionary=True)

            # Fetch user data
            logging.info(f"Fetching data for user: {email}")
            cursor.execute('''
                SELECT i.image_path
                FROM psychometric_test_responses p
                JOIN future_self_responses f USING (email)
                JOIN face_image_responses i USING (email)
                WHERE p.email = %s
            ''', (email,))
            
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"No data found for {email}")

            # Validate image path
            image_path = result['image_path']
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Face image not found at {image_path}")

            # Process image
            logging.info(f"Processing image at: {image_path}")
            with Image.open(image_path).convert('RGBA') as base_img:
                base_img = base_img.resize((512, 512))

                # Ensure avatars directory exists
                avatars_dir = 'avatars'
                os.makedirs(avatars_dir, exist_ok=True)

                # Save the avatar
                avatar_path = os.path.join(avatars_dir, f"{email}_avatar.png")
                base_img.save(avatar_path)

            # Store avatar path in the database
            logging.info(f"Storing avatar path in database: {avatar_path}")
            cursor.execute('''
                INSERT INTO avatars (email, image_path, avatar_path)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE avatar_path = VALUES(avatar_path)
            ''', (email, image_path, avatar_path))
            
            conn.commit()
            logging.info("Avatar generation and storage successful.")
            return avatar_path

    except mysql.connector.Error as db_err:
        logging.error(f"Database error: {str(db_err)}")
        raise
    except Exception as e:
        logging.error(f"Error during avatar generation: {str(e)}")
        raise

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_avatar.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    try:
        avatar_path = generate_avatar(email)
        print(json.dumps({'status': 'ok', 'avatar_path': avatar_path}))
    except Exception as e:
        print(json.dumps({'status': 'error', 'message': str(e)}))
        sys.exit(1)