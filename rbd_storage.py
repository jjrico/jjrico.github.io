#------------------------------------------------------------------------------
# Filename: rbd_storage.py
# Author(s): Aaron Thompson
# Last Updated: 11/4/2019
#
# Description: This file contains functions that help manage files/folders
#   within a storage.
#------------------------------------------------------------------------------
import boto3
import os
import re

s3 = boto3.resource("s3")
DEFAULT_BUCKET = s3.Bucket("rbddev-test-bucket")
rbddev_test_bucket = s3.Bucket("rbddev-test-bucket")
#------------------------------------------------------------------------------
# Unit (Class)
#------------------------------------------------------------------------------
class Unit:
    user_list = dict()
    group_list = dict()
    name = ""
    path_parent = ""
    path_full = ""
    parent = None
    bucket = None
    
    def __init__(self, name, parent, bucket):
        self.name = name
        self.parent = parent
        self.bucket = bucket
        self.UpdatePath()
    
    def Delete(self):
        if(self.path_full == None):
            self.UpdatePath()
        
        if(self.parent != None):
            self.parent.RemoveChild(self)
        
        s3.Object(self.bucket.name, self.path_full).delete()
    
    def Move(self, parent):
        if(self.parent != None):
            self.parent.RemoveChild(self)
        
        if(self.path_full == None):
            self.UpdatePath()
        old_path = self.path_full
        
        self.parent = parent
        self.UpdatePath()
        self.parent.AddChild(self)
        copy_source = {"Bucket" : self.bucket.name, "Key" : old_path}
        s3.meta.client.copy(copy_source, self.bucket.name, self.path_full)
    
    def Rename(self, name):
        if(self.path_full == None):
            self.UpdatePath()
        old_path = self.path_full
        
        self.name = name
        self.UpdatePath()
        copy_source = {"Bucket" : self.bucket.name, "Key" : old_path}
        s3.meta.client.copy(copy_source, self.bucket.name, self.path_full)
    
    def Download(self, location):
        if(self.path_full == None):
            self.UpdatePath()
        
        s3.download_file(self.bucket.name, self.path, location)
    
    def UpdatePath(self):
        self.path_parent = self.ComputePath(False)
        self.path_full = self.path_parent + self.name
    
    def ComputePath(self, full_path=True):
        if(self.parent == None):
            return self.name
        
        if(full_path):
            return self.ComputePath(self, True) + "/" + self.name
        else:
            return self.ComputePath(self, True) + "/"
    
    def HasPermission(self, user):
        for group in self.group_list:
            if(group.Contains(user)):
                return True
            
        return user in self.user_list
    
    def AddUserPermission(self, user):
        self.user_list[user.name] = user
    
    def RemoveUserPermission(self, user):
        if(user.name in self.user_list):
            del self.user_list[user.name]
    
    def AddGroupPerimission(self, group):
        self.group_list[group.name] = group
        
    def RemoveGroupPerimission(self, group):
        self.group_list[group.name] = group
    
#------------------------------------------------------------------------------
# Folder (Class)
#------------------------------------------------------------------------------
class Folder(Unit):
    children = dict()
    
    def AddChild(self, child):
        self.children[child.name] = child
    
    def RemoveChild(self, child):
        if(child.name in self.children):
            del self.children[child.name]
    
    def Delete(self, start=True):
        for child in self.children:
            child.Delete()
        
        if(start):
            if(self.path == None):
                self.UpdatePath()
            self.bucket.objects.filter(Prefix=self.path).delete()
        
        self.children.clear()
        self.parent.RemoveChild(self)
    
    def Move(self, parent):
        super().Move(parent)
        
        for child in self.children:
            child.Move(self)
    
    def Rename(self, name):
        super().Rename(name)
        
        for child in self.children:
            child.Move(child.name)
    
    def Download(self, location):
        location = location + self.name + '/'
        os.makedirs(location)
        
        for child in self.children:
            child.Download(location)
    
    def UpdatePath(self):
        super().UpdatePath()
        
        for child in self.children:
            child.UpdatePath()
    
    '''def AddUserPermission(self):
        return
    
    def RemoveUserPermission(self):
        return
    
    def AddGroupPerimission(self):
        return
    
    def RemoveGroupPerimission(self, group):
        return
    
    def UpdatePermissions(self):
        return'''

#------------------------------------------------------------------------------
# File (Class)
#------------------------------------------------------------------------------
class File(Unit):
    def Preview():
        return 

#------------------------------------------------------------------------------
# Placeholders
#------------------------------------------------------------------------------
class User:
    def __init__(self, name):
        self.name = name

class Group:
    def __init__(self, user_list = None):
        if(user_list == None):
            self.user_list = dict()
        else:
            self.user_list = user_list
            
    def Contains(self):
        return self.name in self.user_list