#!/usr/bin/env python

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.api import taskqueue

from datetime import datetime
from emailnotif import emailnotifAPI
from models import Pengguna
from google.appengine.ext import ndb

class SetTaskHandler (webapp2.RequestHandler):
    def get(self):
        tgl_sekarang = datetime.now()
        _tgl_skrg = datetime.strptime(str(tgl_sekarang)[:10], "%Y-%m-%d")
        tahun_skrg = tgl_sekarang.year        
        
        q = Pengguna.query()
        for data in q :
            #tgl_jatuhtempo = datetime.strptime(str(data.app_date)[:10], "%Y-%m-%d")
            #cek dec15th and above
            dec15 = datetime.strptime(str(tahun_skrg)+"-12-15", "%Y-%m-%d")
            delta_dec = (_tgl_skrg - dec15).days
          
            if delta_dec >=0 and delta_dec<=21 :
                tgl_jatuhtempo_thn_ini = datetime.strptime(str(tahun_skrg+1)+"-"+str(data.app_date)[6:10], "%Y-%m-%d")
                long_date = tgl_jatuhtempo_thn_ini.strftime("%d-%b-%Y")
            else:
                tgl_jatuhtempo_thn_ini = datetime.strptime(str(tahun_skrg)+"-"+str(data.app_date)[6:10], "%Y-%m-%d")
                long_date = tgl_jatuhtempo_thn_ini.strftime("%d-%b-%Y")
            #bln_tgl_jatuhtempo = datetime.strptime(str(tgl_jatuhtempo)[6:10], "%m-%d")
            delta = (tgl_jatuhtempo_thn_ini - _tgl_skrg).days
            tgl_kirim= datetime.strptime(str(tgl_sekarang)[:10],"%Y-%m-%d").date()
            #tahun_kirim = tgl_kirim.year
          
        
            if data.send_date == None:   
               
                if delta >=0 and delta <=21 :  
                    taskqueue.add(params={'email': str(data.email_addr),
                                                  'nama': str(data.client_name),
                                                  'tgl_jthtempo': str(long_date),},
                                          url='/tasks/send_notifmail'
                                          )
                        
                    p_key = ndb.Key (Pengguna,data.client_id)
                    save_data = p_key.get()          
                    setattr(save_data,'send_date',tgl_kirim)
                    save_data.put()
                  
                  
            else :
                tgl_kirim = datetime.strptime(str(data.send_date)[:10], "%Y-%m-%d")
                delta_kirim = (tgl_jatuhtempo_thn_ini - tgl_kirim).days
               
                if delta_kirim >=300 and (delta >=0 and delta <=21):
                    taskqueue.add(params={'email': str(data.email_addr),
                                                  'nama': str(data.client_name),
                                                  'tgl_jthtempo': str(long_date),},
                                          url='/tasks/send_notifmail'
                                          )
        
                    p_key = ndb.Key (Pengguna,data.client_id)
                    save_data = p_key.get()          
                    setattr(save_data,'send_date',tgl_kirim)
                    save_data.put()
                                       
          

class SendNotificationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email notification."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),             # from
            self.request.get('email'),                           # to
            '[Pengingat] Tagihan BHP Frek. Radio!',             # subj
            'Yth. Pelanggan, %s \n'  %(self.request.get('nama')) +        # body
            '\n Diberitahukan bahwa kewajiban tahunan anda atas penggunaan frekuensi radio '+
            'akan berakhir pada tanggal: \n %s \n'% (self.request.get('tgl_jthtempo')) +
            'Silahkan melakukan pembayaran untuk menghindari denda. \n\n' +
            'Abaikan email ini jika anda sudah melakukan pembayaran\n\n' +
            'Terimakasih\n'+
            'Balmon Kelas II Batam, Ditjen SDPPI\n'+
            'Kementerian Komunikasi dan Informatika\n'
             
        )

        
app = webapp2.WSGIApplication([    
    ('/crons/set_task', SetTaskHandler),                         
    ('/tasks/send_notifmail', SendNotificationEmailHandler),
   
], debug=True)


