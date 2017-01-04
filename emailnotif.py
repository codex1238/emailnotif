#!/usr/bin/env python


from datetime import datetime
from google.appengine.api import mail
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext import ndb

from models import Pengguna
from models import PenggunaForm
from models import PenggunaForms
from models import GetUpdateForm
from models import PenggunaQueryForms
from models import updateForm

from google.appengine.api import taskqueue

from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
OPERATORS = {
            'EQ':   '=',
            'GT':   '>',
            'GTEQ': '>=',
            'LT':   '<',
            'LTEQ': '<=',
            'NE':   '!='
            }

FIELDS =    {
            'CITY': 'city',
            'NAMA': 'client_name',
            'ID': 'client_id',
            }

@endpoints.api( name='emailnotif',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class emailnotifAPI(remote.Service):
    """Email Notification API v1"""

# - - - Pengguna objects - - - - - - - - - - - - - - - - - - -

    def _Object_inputPengguna(self, request):
        
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        client_key = ndb.Key(Pengguna, getattr(request, 'client_id'))
        data['key'] = client_key
        if data['app_date'] :
            data['app_date'] = datetime.strptime(data['app_date'][:10], "%Y-%m-%d").date()
            data['month'] = data['app_date'].month
            
        Pengguna(**data).put()
              
        return request
 
    @endpoints.method(PenggunaForm, PenggunaForm, path='input',
            http_method='POST', name='inputPengguna')
    def inputPengguna(self, request):
        """Input Data Pengguna Frekuensi Radio di Kepulauan Riau."""
        return self._Object_inputPengguna(request)
    
    
    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Pengguna.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Pengguna.client_name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Pengguna.client_name)

        for filtr in filters:
            #if filtr["field"] in ["month", "maxAttendees"]:
            #    filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q
    
    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)
    
    def _copyPenggunaToForm(self, conf):
        """Copy relevant fields from Conference to ConferenceForm."""
        pf = PenggunaForm()
        for field in pf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('date'):
                    setattr(pf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(pf, field.name, getattr(conf, field.name))
                    
        pf.check_initialized()
        return pf
    
    @endpoints.method(PenggunaQueryForms, PenggunaForms,
            path='pengguna',
            http_method='POST',
            name='queryPengguna')
    def queryPengguna(self, request):
        """Query for pengunna."""
        pengguna = self._getQuery(request)
        return PenggunaForms(
                items=[self._copyPenggunaToForm(conf) for conf in \
                pengguna]
        )
    
    def _getUpdate(self, request):
        p_key = ndb.Key(Pengguna,request.client_id)
        data = p_key.get()
        return self._copyPenggunaToForm(data)
    
    @endpoints.method(GetUpdateForm, PenggunaForm,
            path='getupdate',
            http_method='GET',
            name='getupdatePengguna')
    def getupdatePengguna(self, request):
        """Query for pengunna."""
        return self._getUpdate(request)
    
 
    def _updatePengguna(self, request):
    
        client_key = ndb.Key(Pengguna, getattr(request, 'client_id'))
        dataStore = client_key.get()
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['send_date']
                                      
        data['app_date'] = datetime.strptime(data['app_date'][:10], "%Y-%m-%d").date()
        data['month'] = data['app_date'].month
        for item in data  :                  
            setattr(dataStore, item, data[item])
        dataStore.put()    
        return request
 
    @endpoints.method(PenggunaForm, PenggunaForm, path='update',
            http_method='POST', name='updatePengguna')
    def updatePengguna(self, request):
        """Update Data Pengguna Frekuensi Radio di Kepulauan Riau."""
        return self._updatePengguna(request)  
    
    
    
        
              
            
  
# registers API
api = endpoints.api_server([emailnotifAPI]) 
