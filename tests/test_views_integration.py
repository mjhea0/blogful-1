import os
import unittest
from urlparse import urlparse

from werkzeug.security import generate_password_hash

# configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        
        # set up the tables in the database
        Base.metadata.create_all(engine)
        
        # create an example user
        self.user = models.User(name="Alice", email="alice@example.com",
                               password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
        
    def tearDown(self):
        """ Test teardown """
        session.close()
        # remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user.id"] = str(self.user.id)
            print self.user.name
            http_session["_fresh"] = True
            
    def testAddPost(self):
        self.simulate_login()
        
        response = self.client.post("/post/add", data={
                "title": "Test Post",
                "content": "Test Content"
            })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)
        
        posts = posts[0]
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "<p>Test content</p>\n")
        self.assertEqual(post.author, self.user)
if __name__ == "__main__":
    unittest.main()