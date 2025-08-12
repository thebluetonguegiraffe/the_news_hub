from pathlib import Path
import sqlite3
from datetime import datetime
from collections import defaultdict
import os

class TopicsDBClient:
    def __init__(self, db_path=str):        
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._setup_db()

    def _setup_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            topic TEXT PRIMARY KEY,
            description TEXT,
            date TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def upsert_topic(self, topic, description, date=None):
        if date is None:
            date = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO topics (topic, description, date) VALUES (?, ?, ?)
        ON CONFLICT(topic) DO UPDATE SET date=excluded.date
        ''', (topic, date, description))
        self.conn.commit()

    def get_all_topics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT topic, description, date FROM topics ORDER BY topic")
        return cursor.fetchall()
    
    def get_topics_grouped_by_date(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT topic, date FROM topics")
        rows = cursor.fetchall()
        
        grouped = defaultdict(list)
        for topic, date in rows:
            grouped[date].append(topic)
        return dict(grouped)

    def delete_topic(self, topic):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM topics WHERE topic = ?", (topic,))
        self.conn.commit()
    

    def close(self):
        self.conn.close()

if __name__ == "__main__":

    topics = [""]

    project_root = Path(__file__).resolve().parent.parent
    db_path = "topics.db"
    client = TopicsDBClient(
        db_path=f"{project_root}/db/{db_path}"
    )

    client.get_all_topics()
    # client.delete_topic("history")
    # client.delete_topic("technology", "2025-08-01T09:30:00")
    
    client.close()
