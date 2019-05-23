#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Item

engine = create_engine('sqlite:///sportslist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
Criação das categorias iniciais
'''

games = Category(id=1, name="Chuteiras")
session.add(games)
session.commit()


filmes = Category(id=2, name="Bolas")
session.add(filmes)
session.commit()


livros = Category(id=3, name="Meioes")
session.add(livros)
session.commit()


user = User(
    id=1,
    name="Admin",
    email="igor.rocha@ee.ufcg.edu.br",
    picture="encurtador.com.br/LQR45")
session.add(user)
session.commit()


'''
Criação dos itens iniciais
'''

item1 = Item(
    id=1,
    title="Chuteira Society Kappa Torpedo",
    description=(
        "A Chuteira Kappa eh feita de material sintetico e cravos"
        "de borracha que dao velocidade e aderencia na passada."),
    cat_id=1,
    user_id=1)
session.add(item1)
session.commit()


item2 = Item(
    id=2,
    title="Bola de Futebol Society Nike CBF",
    description=(
        "A Bola de Futebol de Campo da Nike eh para aquela"
        "partidinha com os amigos ou ate mesmo virar item de colecionador."
        "Com o escudo da Selecao Brasileira e cores marcantes, ela"
        "eh ideal para melhor visualizacao em campo."),
    cat_id=2,
    user_id=1)
session.add(item2)
session.commit()


item3 = Item(
    id=3,
    title="Meiao Milano 16 Adidas Masculino",
    description=(
        "Na pelada do final de semana, o meiao nao pode faltar."
        " Com o Meiao Milano 16 Adidas Masculino confeccionado em"
        " nylon, voce se sente confortavel durante a partida."),
    cat_id=3,
    user_id=1)
session.add(item3)
session.commit()

print "todos os itens foram adicionados"
