# database.py
import sqlite3
from config import Config
from logger import setup_logger
import datetime

logger = setup_logger()


class DatabaseService:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.initialize_tables()
            logger.info("Database connected successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def initialize_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    student_id TEXT UNIQUE NOT NULL,
                    enrollment_date TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    criteria TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_id INTEGER NOT NULL,
                    achieved_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(achievement_id) REFERENCES achievements(id)
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    topic TEXT,
                    question TEXT,
                    user_answer TEXT,
                    correct_answer TEXT,
                    correct INTEGER,
                    explanation TEXT
                )
            ''')
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                login_time TEXT
            )
        ''')
            self.conn.commit()
            logger.info("Database tables initialized.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing tables: {e}")
            raise

    def create_achievement(self, name, description, criteria):
        try:
            self.cursor.execute('''
                    INSERT INTO achievements (name, description, criteria)
                    VALUES (?, ?, ?)
                ''', (name, description, criteria))
            self.conn.commit()
            logger.info(f"Created achievement: {name}")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity Error creating achievement {name}: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database Error creating achievement {name}: {e}")
            return False

    # Read all achievements
    def read_achievements(self):
        try:
            self.cursor.execute('''
                SELECT id, name, description, criteria FROM achievements
            ''')
            achievements = self.cursor.fetchall()
            logger.info("Fetched all achievements.")
            return achievements
        except sqlite3.Error as e:
            logger.error(f"Database fetch error for achievements: {e}")
            return []

    # Update an existing achievement
    def update_achievement(self, achievement_id, name, description, criteria):
        try:
            self.cursor.execute('''
                UPDATE achievements
                SET name = ?, description = ?, criteria = ?
                WHERE id = ?
            ''', (name, description, criteria, achievement_id))
            self.conn.commit()
            logger.info(f"Updated achievement ID {achievement_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database update error for achievement ID {
                         achievement_id}: {e}")
            return False

    # Delete an achievement
    def delete_achievement(self, achievement_id):
        try:
            self.cursor.execute('''
                DELETE FROM achievements WHERE id = ?
            ''', (achievement_id,))
            self.conn.commit()
            logger.info(f"Deleted achievement ID {achievement_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database deletion error for achievement ID {
                         achievement_id}: {e}")
            return False

    def is_quiz_completed_after_midnight(self, username):
        try:
            self.cursor.execute('''
                SELECT achieved_at FROM user_achievements
                WHERE username = ? ORDER BY achieved_at DESC LIMIT 1
            ''', (username,))
            result = self.cursor.fetchone()
            if result:
                achieved_time = datetime.strptime(
                    result[0], '%Y-%m-%dT%H:%M:%S')
                return achieved_time.hour >= 0 and achieved_time.hour < 6
            return False
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return False

    def get_user_by_username(self, username):
        try:
            self.cursor.execute('''
                SELECT * FROM users WHERE username = ?
            ''', (username,))
            user = self.cursor.fetchone()
            return user  # This will be a tuple representing the user record
        except sqlite3.Error as e:
            logger.error(f"Database fetch error for user {username}: {e}")
            return None

    def insert_user(self, username, display_name=None, student_id=None, enrollment_date=None):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, display_name, student_id, enrollment_date)
                VALUES (?, ?, ?, ?)
            ''', (username, display_name, student_id, enrollment_date))
            self.conn.commit()
            logger.info(f"Inserted new user: {username}")
        except sqlite3.Error as e:
            logger.error(f"Database insertion error: {e}")

    def insert_result(self, username, topic, question, user_answer, correct_answer, correct, explanation):
        try:
            self.cursor.execute('''
                INSERT INTO assessment_results 
                (username, topic, question, user_answer, correct_answer, correct, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, topic, question, user_answer, correct_answer, correct, explanation))
            self.conn.commit()
            logger.info("Inserted assessment result.")
        except sqlite3.Error as e:
            logger.error(f"Database insertion error: {e}")

    def fetch_results(self, username):
        try:
            self.cursor.execute('''
                SELECT topic, question, user_answer, correct_answer, correct, explanation 
                FROM assessment_results WHERE username = ?
            ''', (username,))
            results = self.cursor.fetchall()
            logger.info("Fetched assessment results.")
            return results
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return []

    def update_explanation(self, username, topic, question, explanation):
        try:
            self.cursor.execute('''
                UPDATE assessment_results SET explanation = ?
                WHERE username = ? AND topic = ? AND question = ?
            ''', (explanation, username, topic, question))
            self.conn.commit()
            logger.info("Updated explanation in assessment results.")
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")

    def insert_login_time(self, username, login_time):
        try:
            print(f"Inserting login time for username: {
                username}, login_time: {login_time}")  # Debugging
            self.cursor.execute('''
                INSERT INTO user_logins (username, login_time) VALUES (?, ?)
            ''', (username, login_time))
            self.conn.commit()
            logger.info("Inserted login time for user.")
        except sqlite3.Error as e:
            logger.error(f"Database insertion error: {e}")
            print(f"Database insertion error: {e}")

    def get_login_count(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM user_logins WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched login count for user {username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_total_questions_answered(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total questions answered for user {
                        username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_total_student_count(self):
        try:
            self.cursor.execute('''
                SELECT COUNT(DISTINCT username) FROM assessment_results
            ''')
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total student count: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def select_each_topic(self):
        try:
            self.cursor.execute('''
                SELECT DISTINCT topic FROM assessment_results
            ''')
            result = self.cursor.fetchall()
            topics = [row[0] for row in result]
            logger.info(f"Fetched all topics: {topics}")
            return topics
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return []

    def get_total_correct_answers_without_username(self):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE correct = 1
            ''')
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total correct answers: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")

    def get_total_correct_answers(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ? AND correct = 1
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total correct answers for user {
                        username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_previous_login_time(self, username):
        try:
            self.cursor.execute('''
                SELECT login_time FROM user_logins WHERE username = ? ORDER BY id DESC LIMIT 1 OFFSET 1
            ''', (username,))
            result = self.cursor.fetchone()
            login_time = result[0] if result else None
            logger.info(f"Fetched previous login time for user {
                        username}: {login_time}")
            return login_time
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return None

    def get_student_performance(self, username):
        try:
            # Fetch total questions answered and total correct answers
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ?
            ''', (username,))
            total_answered = self.cursor.fetchone()[0]

            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ? AND correct = 1
            ''', (username,))
            total_correct = self.cursor.fetchone()[0]

            # Fetch topics the student has attempted
            self.cursor.execute('''
                SELECT DISTINCT topic FROM assessment_results WHERE username = ?
            ''', (username,))
            topics_attempted = [row[0] for row in self.cursor.fetchall()]

            # Fetch topics where the student struggled (less than 50% correct)
            topics_struggled = []
            for topic in topics_attempted:
                self.cursor.execute('''
                    SELECT COUNT(*) FROM assessment_results WHERE username = ? AND topic = ?
                ''', (username, topic))
                topic_total = self.cursor.fetchone()[0]

                self.cursor.execute('''
                    SELECT COUNT(*) FROM assessment_results WHERE username = ? AND topic = ? AND correct = 1
                ''', (username, topic))
                topic_correct = self.cursor.fetchone()[0]

                if topic_total > 0 and (topic_correct / topic_total) < 0.5:
                    topics_struggled.append(topic)

            performance_data = {
                'total_answered': total_answered,
                'total_correct': total_correct,
                'topics_attempted': topics_attempted,
                'topics_struggled': topics_struggled
            }
            return performance_data
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return {}

    def add_achievement(self, name, description, criteria):
        try:
            self.cursor.execute('''
                INSERT INTO achievements (name, description, criteria)
                VALUES (?, ?, ?)
            ''', (name, description, criteria))
            self.conn.commit()
            logger.info(f"Added new achievement: {name}")
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity Error adding achievement {name}: {e}")
        except sqlite3.Error as e:
            logger.error(f"Database Error adding achievement {name}: {e}")

    def fetch_all_achievements(self):
        try:
            self.cursor.execute('''
                SELECT id, name, description, criteria FROM achievements
            ''')
            achievements = self.cursor.fetchall()
            logger.info("Fetched all achievements.")
            return achievements
        except sqlite3.Error as e:
            logger.error(f"Database fetch error for achievements: {e}")
            return []

    def assign_achievement_to_user(self, username, achievement_name, achieved_at):
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(
                    f"User {username} not found. Cannot assign achievement.")
                return
            user_id = user[0]

            # Fetch achievement ID
            self.cursor.execute('''
                SELECT id FROM achievements WHERE name = ?
            ''', (achievement_name,))
            achievement = self.cursor.fetchone()
            if not achievement:
                logger.warning(
                    f"Achievement {achievement_name} not found. Cannot assign.")
                return
            achievement_id = achievement[0]

            # Check if already assigned
            self.cursor.execute('''
                SELECT * FROM user_achievements WHERE user_id = ? AND achievement_id = ?
            ''', (user_id, achievement_id))
            if self.cursor.fetchone():
                logger.info(f"User {username} already has achievement {
                            achievement_name}.")
                return

            # Assign achievement
            self.cursor.execute('''
                INSERT INTO user_achievements (user_id, achievement_id, achieved_at)
                VALUES (?, ?, ?)
            ''', (user_id, achievement_id, achieved_at))
            self.conn.commit()
            logger.info(f"Assigned achievement {achievement_name} to user {
                        username} at {achieved_at}")
        except sqlite3.Error as e:
            logger.error(f"Database error assigning achievement {
                         achievement_name} to user {username}: {e}")

    def fetch_user_achievements(self, username):
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(
                    f"User {username} not found. Cannot fetch achievements.")
                return []
            user_id = user[0]
            self.cursor.execute('''
                SELECT a.name, a.description, ua.achieved_at
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = ?
            ''', (user_id,))
            achievements = self.cursor.fetchall()
            logger.info(f"Fetched achievements for user {username}")
            return achievements
        except sqlite3.Error as e:
            logger.error(f"Database fetch error for achievements of user {
                         username}: {e}")
            return []

    def close(self):
        try:
            self.conn.close()
            logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
