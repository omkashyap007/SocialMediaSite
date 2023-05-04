## **Social Media Site**

Welcome to the Advanced Chat System, a powerful communication platform that allows you to chat with anyone in the world who is logged in. Whether you want to chat publicly or privately, connect with new people, or stay in touch with friends and family, our platform makes it easy and convenient.

## Features

Our chat system comes packed with features to enhance your communication experience, including:

**Public Chat System** : Connect and chat with anyone in the world who is logged in to the application. Choose from multiple chat rooms to join conversations on topics that interest you.

**Private Messaging** : Chat privately with friends you have added on the application. Share confidential information, photos, videos, or just engage in a casual conversation without worrying about others seeing your messages.

**Advanced Profile Management** : Create and update your profile to make it stand out. Add a profile picture, cover photo, bio, and any other information you want others to know about you. You can also find and add friends on the application, create and join groups, and participate in forum discussions.

**Code Sharing** : Share code snippets with other users in the form of messages. Our built-in Markdown editor ensures that your messages are rendered safely and accurately.

**Real-time Notification System** : Never miss an important message or notification again. Our real-time notification system keeps you informed about any new messages, friend requests, group invites, or other updates related to your account.

**Advanced Security** : Our application is built with the latest security protocols to ensure that your data is safe and secure. We use Markdown-it to prevent XSS attacks, ensuring that your messages are rendered safely and accurately.

## Technologies

We have used the following technologies to develop the Advanced Chat System:

1. Django: A high-level Python web framework for rapid development.
2. Django Channels: A Django library that extends WebSockets and handles asynchrony.
3. WebSockets: A protocol for bi-directional, real-time communication between clients and servers.
  ## How to Use

To get started with the Advanced Chat System, follow these simple steps:

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:
```
pip install -r requirements.txt
```
3. Create a database by running the following command:
```
python manage.py migrate
```
4. Start the developement server by running the following command : 

```
python manage.py runserver
```
5. Navigate to http://localhost:8000 in your web browser to access the application.

## Usage
**Public Chat System**
To use the public chat system, follow these steps:

Just login to the application with proper authentication . 
You'll get navigated to the HomePage , you'll see the  public chat section.
Type your message in the message field and hit enter to send it.

## Private Messaging
To use the private messaging system, follow these steps:

Click on the "Chat" button in the header menu.
Search for the friend you wish to message and click on their profile.
Click on the "Send Message" button and type your message in the message field.
Hit enter to send the message.

## Code Sharing
To share code snippets with other users, follow these steps:

Type your code snippet in the message field.
Use Markdown syntax to format your code snippet.
Hit enter to send the message.

Example : 

```
  ```python
  def function() :
      print("This function is run !")    
  ```
```
