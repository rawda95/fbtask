import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import  facebook
from models import Base, User, Post

engine = create_engine('postgresql://admin:admin@localhost/v3fbdb',)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


token= 'EAAEyVtgNn6YBAJmCk0eVq4u8ZAQmZAjgvyc7Bnaky5MW9E8SypwKG1ZAE20EV95FhZBw14TASK943ctc9A9s6Erpzf2eBktvOl4ADRTH6AwcGVjRhkF3Gz13cmkANnUQfCU84CDoBHTZCoR73oacxLXIzjeXbiakGXU2hCzAM06TMQrPgdFHFdDBB51mlBDd7Gml5Sel8GXRDlLAkOUxMJLlpRzDG6qEZD'
graph = facebook.GraphAPI(access_token=token, version=2.7)


def dleteExtraPost(userId):
    lastPosts = session.query(Post).order_by('created_time desc').limit(25).all()
    posts = session.query(Post).filter_by(user_id=userId)
    print(posts)
    print(lastPosts)
    dlpost =list( set(posts) - set(lastPosts))
    for post in dlpost:
        session.delete(post)
        session.commit()


@app.route('/users/<string:facebookId>')
def SaveUser(facebookId):
    if request.args.get('local') == 'true':
        user = session.query(User).filter_by(id=facebookId).first()
        if user is not None:
            return jsonify(user=user.serialize,local='true')
    fbuser = graph.request(str(facebookId))
    print(fbuser)
    existUser = session.query(User).filter_by(id=fbuser['id']).first()
    if existUser is not None:
        if not existUser.name == fbuser['name']:
            existUser.name = fbuser['name']
            session.commit()

        return jsonify(user=existUser.serialize)

    else:
        user = User(name=fbuser['name'], id=fbuser['id'])
        session.add(user)
        session.commit()
        return jsonify(user=user.serialize,massge='saved')


@app.route('/users/<string:facebookId>/posts')
def GetPosts(facebookId):
    if request.args.get('local') == 'true':
        posts = session.query(Post).filter_by(user_id=facebookId)
        if posts is not None:
            return jsonify(posts=[i.serialize for i in posts])
    else:
        fbposts = graph.request(str(facebookId)+'/posts?limit=25')
        allposts =[]
        if session.query(User).filter_by(id=facebookId).first()is None:
            SaveUser(facebookId)
        for fbpost in fbposts['data']:
            post= session.query(Post).filter_by(id=fbpost['id']).first()
            if post is None :
                post = Post(id=fbpost['id'],
                            created_time=fbpost['created_time'],
                            user_id=facebookId)
                if 'message'in fbpost :
                    post.content=fbpost['message']
                session.add(post)
                allposts.append(post)
                session.commit()
            else:
                post.created_time = fbpost['created_time']
                if 'message'in fbpost :
                    post.content = fbpost['message']
                allposts.append(post)
                session.commit()
        dleteExtraPost(facebookId)
        return jsonify(posts=[i.serialize for i in allposts])


@app.route('/users')
def UserList():
    users = session.query(User).all()
    return jsonify(users=[i.serialize for i in users])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    port = int(os.environ.get('PORT', 8000))  # Use PORT if it's there.
    app.run(host='0.0.0.0', port=port)
