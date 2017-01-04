#!/usr/bin/env python



__author__ = 'bsupriadi83@gmail.com'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb


class Pengguna(ndb.Model):   
    client_id       = ndb.StringProperty(required=True)
    client_name     = ndb.StringProperty()
    client_addr     = ndb.StringProperty()
    city            = ndb.StringProperty()
    service         = ndb.StringProperty() 
    sub_service     = ndb.StringProperty()   
    bhp             = ndb.IntegerProperty()
    app_date        = ndb.DateProperty()
    month           = ndb.IntegerProperty()
    send_date       = ndb.DateProperty()
    email_addr      = ndb.StringProperty()

class PenggunaForm(messages.Message):
    client_id       = messages.StringField(1)
    client_name     = messages.StringField(2)
    client_addr     = messages.StringField(3)
    city            = messages.StringField(4)
    service         = messages.StringField(5) 
    sub_service     = messages.StringField(6)   
    bhp             = messages.IntegerField(7, variant=messages.Variant.INT32)
    app_date        = messages.StringField(8)
    send_date       = messages.StringField(9)
    month           = messages.IntegerField(10)
    email_addr      = messages.StringField(11)
    
class updateForm(messages.Message):
    client_id       = messages.StringField(1)
    client_name     = messages.StringField(2)
    client_addr     = messages.StringField(3)
    city            = messages.StringField(4)
    service         = messages.StringField(5) 
    sub_service     = messages.StringField(6)   
    bhp             = messages.IntegerField(7, variant=messages.Variant.INT32)
    app_date        = messages.StringField(8)    
    email_addr      = messages.StringField(9)
    
class PenggunaForms(messages.Message):
    """PenggunaForms -- multiple Conference outbound form message"""
    items = messages.MessageField(PenggunaForm, 1, repeated=True)

class PenggunaQueryForm(messages.Message):
    """ConferenceQueryForm -- Conference query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

class PenggunaQueryForms(messages.Message):
    """ConferenceQueryForms -- multiple ConferenceQueryForm inbound form message"""
    filters = messages.MessageField(PenggunaQueryForm, 1, repeated=True)
    
class GetUpdateForm(messages.Message):
    """String that stores a message."""
    client_id = messages.StringField(1)
