#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, \
    url_for, flash, jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, User, Item
# New imports to create a anti-forgery token)
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///sportslist.db')
Base.metadata.bind = engine

# DBSession = sessionmaker(bind=engine)
# session = DBSession()

session = scoped_session(sessionmaker(bind=engine))


@app.teardown_request
def remove_session(ex=None):
    session.remove()


# useful functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id)
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# Create anti-forgery state token###
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    '''
       função de login do Facebook
    '''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?' \
          'grant_type=fb_exchange_token&client_id=%s&' \
          'client_secret=%s&fb_exchange_token=%s' % (
           app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Usando o token para pegar as informações do usuário na API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?' \
          'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Guardando o token, para poder realizar o logout
    login_session['access_token'] = token

    # coletando a imagem do usuário
    url = 'https://graph.facebook.com/v2.8/me/picture?' \
          'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # verificando se o usuário existe
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Bem vindo, '
    output += login_session['username']

    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; border-radius: 150px;"> '

    flash("Logado como %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    '''
       função de logout do Facebook
    '''
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "Desconectado com sucesso"


# Logout facebook
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash("Desconectado com sucesso.")
            return redirect(url_for('show_all'))
    else:
        flash("Realize o login primeiro")
        return redirect(url_for('show_all'))


@app.route('/')
@app.route('/catalog')
def show_all():
    '''
       Show the categories and items added recently
    '''
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id)).limit(6).all()
    return render_template('catalog.html', categories=categories, items=items)
    # 1o eh o usado no html e o 2o a info aqui.


@app.route('/api/v1/catalog/JSON')
def catalog_JSON():
    '''
       JSON API for all dataset
    '''
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id))
    return jsonify(
        categoria=[
            c.serialize for c in categories], item=[
            i.serialize for i in items])


@app.route('/api/v1/catalog/categorias/JSON')
def categories_JSON():
    '''
       JSON API for all categories
    '''
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(
        categoria=[
            c.serialize for c in categories])


@app.route('/api/v1/catalog/item/<int:item_id>/JSON')
def item_JSON(item_id):
    '''
       JSON API for an item
    '''
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/api/v1/catalog/<int:cat_id>/itens/JSON')
def cat_items_JSON(cat_id):
    '''
       JSON API for each category
    '''
    category = session.query(Category).filter_by(id=cat_id)
    item = session.query(Item).filter_by(cat_id=cat_id).all()
    return jsonify(
        categoria=[
            c.serialize for c in category], itens=[
            i.serialize for i in item])


@app.route('/catalog/categoria/<int:cat_id>')
def show_category(cat_id):
    '''
       Show items of the selected category
    '''
    creator = getUserInfo(Item.user_id)
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(Item).filter_by(cat_id=cat_id).all()
    return render_template(
        'categorias.html',
        category=category, items=items, creator=creator)


@app.route('/catalog/categoria/novo_item/<int:cat_id>',
           methods=['GET', 'POST'])
def new_item(cat_id):
    '''
       Allow you to create a new item
    '''
    if 'username' not in login_session:
        return redirect('/login')
    id_session = login_session['user_id']
    nameCategory = session.query(Category).filter_by(id=cat_id).one()
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Item(
            title=request.form['name'],
            description=request.form['description'],
            cat_id=cat_id,
            user_id=id_session
        )
        session.add(newItem)
        session.commit()
        flash(
            'O novo item %s foi criado com sucesso!' %
            (newItem.title))
        return redirect(url_for('show_category', cat_id=cat_id))
    else:
        return render_template('novo_item.html', nameCategory=nameCategory)


@app.route('/item/view/<int:cat_id>/<int:item_id>')
def show_item(cat_id, item_id):
    '''
       Shows the selected item
    '''
    selectItem = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=selectItem)


@app.route('/item/edit/<int:cat_id>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(cat_id, item_id):
    '''
       Edit the selected item
    '''
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=cat_id).one()
    if login_session['user_id'] != editedItem.user_id:
        return "<script>function myFunction() \n" \
                + "{alert('Não autorizado.');}</script> \n" \
                + "<body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.title = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Item editado com sucesso!')
        return redirect(url_for('show_category', cat_id=cat_id))
    else:
        return render_template(
            'editar_item.html',
            category=category,
            item=editedItem)


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(item_id):
    '''
       Delete the selected item
    '''
    if 'username' not in login_session:
        return redirect('/login')
    item_to_delete = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item_to_delete.user_id:
        return "<script>function myFunction() \n" \
                + "{alert('Não autorizado.');}</script> \n" \
                + "<body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash('Item deletado com sucesso!')
        return redirect(url_for('show_category', cat_id=item_to_delete.cat_id))
    else:
        return render_template('deletar_item.html', item=item_to_delete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
