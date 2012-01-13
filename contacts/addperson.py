import wx
from wxPython.lib.rcsizer import RowColSizer
from utilities import *

ADD=wx.NewId()
CANCEL=wx.NewId()


class addperson(wx.Dialog):
    def __init__(self,parent,id,title,edit,idu,**kwds):
        
        #initialisation
        
        self.title = title
        self.edit = edit
        self.idu = 0
        self.parms = {
          'fname':'',
          'lname':'',
          'profession':'',
          'salutation':'',
           }
        salutations = ['Dr','Mr','Ms']
        professions = ['Doctor','Lawyer','Engineer']
        if edit:
            self.parms = getpersonparms(idu)
            self.idu = idu
            
        wx.Dialog.__init__(self,parent,id,title,**kwds)
        
        #create the widgets
        
        self.Salute = wx.RadioBox(self, -1,"Salutation: ",
            wx.DefaultPosition,wx.DefaultSize,salutations,1,wx.RA_SPECIFY_ROWS)
        self.Salute.SetStringSelection(self.parms['salutation'])
        self.labfname = wx.StaticText(self, -1, "First Name:")
        self.Fname = wx.TextCtrl(self, -1, self.parms['fname'])
        self.lablname = wx.StaticText(self, -1, "Last Name:")
        self.Lname = wx.TextCtrl(self, -1, self.parms['lname'])
        self.labprofession = wx.StaticText(self, -1,"Profession:")
        self.Profession = wx.ComboBox(self, -1, choices=professions,
              style=wx.CB_DROPDOWN)
        self.Profession.SetValue(self.parms['profession'])
        self.butsave = wx.Button(self, ADD, "Save")
        self.butcancel = wx.Button(self, CANCEL, "Cancel")
        self.Fname.SetSize((320, 26))
        self.Fname.SetMaxLength(40)
        self.Lname.SetSize((320, 26))
        self.Lname.SetMaxLength(40)

        self.__do_layout()


    def __do_layout(self):
        
        self.SetPosition([300,250])
        boxl = RowColSizer()
        boxl.Add(self.Salute, row=1, col=1, colspan=2)
        boxl.Add(self.labfname, row=2, col=1)
        boxl.Add(self.Fname, row=2, col=2)
        boxl.Add(self.lablname, row=3, col=1)
        boxl.Add(self.Lname, row=3, col=2)
        boxl.Add(self.labprofession, row=4, col=1)
        boxl.Add(self.Profession, row=4, col=2)
       
        
        boxb = wx.BoxSizer(wx.HORIZONTAL)
        boxb.Add(self.butsave, 0, 
         wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        boxb.Add(50,10,0)
        boxb.Add(self.butcancel, 0, 
         wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        boxl.Add(boxb, row=5, col=2)
        
        for x in range(1,5):
            boxl.AddSpacer(75,30, pos=(x,1))
            boxl.AddSpacer(380,1, pos=(x,2))
            
        boxl.AddSpacer(75,30,pos=(5,1))
        self.SetAutoLayout(1)
        self.SetSizer(boxl)
        boxl.Fit(self)
        boxl.SetSizeHints(self)
        self.Layout()
        wx.EVT_BUTTON(self, ADD, self.add)
        wx.EVT_BUTTON(self, CANCEL, self.cancel)
 
    def cancel(self,event):
        self.EndModal(0)
        
    def add(self, event):
        ok = True
        msg = ''
        parms = self.parms
        parms['lname'] = self.Lname.GetValue().strip()
        #strip to get rid of leading and trailing spaces
        parms['fname'] = self.Fname.GetValue()
        parms['profession'] = self.Profession.GetValue()
        parms['salutation'] = self.Salute.GetStringSelection()
        
        #check that all fields are filled
        for k,v in parms.items():
            if v == '':
                msg += "Fill in %s" %(k.capitalize())
                ok = False
        #if edit mode
        if self.edit:
            #check for duplicates
                msg,ok = duplicedit(parms['fname'],
                                    parms['lname'],self.idu,msg,ok)
                if ok:
                    updateperson(parms,self.idu) #external program
                    self.EndModal(1)
                else:
                    #display error message
                    error = wx.MessageDialog(self,msg,'Error',wx.OK)
                    error.ShowModal()
                    error.Destroy()    
        #if add mode    
        else:
            msg,ok = duplic(parms['fname'],parms['lname'],msg,ok)
            if ok:
                enterperson(parms) #external program
                self.EndModal(1)
            else:
                error = wx.MessageDialog(self,msg,'Error',wx.OK)
                error.ShowModal()
                error.Destroy()
