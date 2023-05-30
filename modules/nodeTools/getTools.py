import os
import threading
import shutil

import json

import modules.sftp.sftp_tools as sftp_tools
import modules.nodeTools.getTools as NodeGetTools
import modules.RAIDmod as raid_module
import modules.sqlite3.serverDButil as serverDButil

from CVSMS.models import  Files,storageNodeInfo


def get_start_of_file(fileSize):
    pass

def filter_node_list():
    pass


#---------------GET MAXIMUM FILE TO STOR IN THE NODE------------------
def getMaxFile(mdList, storSize):
    fragments = fragmentCheck(mdList, storSize)
    largest = 0
    for i in fragments:
        if i[1] - i[0] > largest:
            largest = i[1] - i[0]
    return largest



#-----------------Fragmented Check-----------------------
def fragmentCheck(mdList, storSize):
    #sort json list based on start point to sort the files
    if mdList:
        jsonList = sorted(mdList, key=lambda k: k["start"])
    else:
        jsonList = mdList
    
    
    prev_end = 0
    spaceBetweenFiles  = []
    
    for file in jsonList:
        # Calculate the end byte of the current file
        endByte = file["start"] + file["actualSize"]
        
        #calculate if there is a gap between the previous file and the current file
        if file["start"] != 0:
            space_start = prev_end
            space_end = file["start"]
            
            #if there is a gap append the gap to the list of gaps
            if (space_end - space_start) != 0:
                spaceBetweenFiles.append((space_start,space_end))
        
        prev_end = endByte
    
    #get the size between the last file and the storage location
    space_start = prev_end
    space_end = storSize
    spaceBetweenFiles.append((space_start,space_end))
    
    return spaceBetweenFiles




def get_storage_nodes(partNames,cwd):
    
    allNodes = serverDButil.getAllStorageNodes()
    file_and_node_tuple_list = []
    # file_and_node_tuple_list = []
    # for partName in partNames:

    #     file_size = os.path.getsize(os.path.join(cwd, partName))
        
    #     storage_node = None
        
    #     for storage_node in allNodes:
            
    #         #SKIP THE NODE IF THE NODE IS OFFLINE OR IF THE NODE HAS A SMALLER MAXIMUM SIZE THAT CAN BE STORED
    #         if storage_node["status"] == False:
    #             continue
    #         elif storage_node["maxSize"] < file_size:
    #             continue
            
    #         files_in_node = serverDButil.get_all_files_by_sid(storage_node["SID"])
    ##         node_allocated_size = serverDButil.get_all_files_by_sid(storage_node["allocSize"])
    #         gap_list = fragmentCheck(files_in_node, node_allocated_size)
            
            
    #         #FIND THE SMALLES SPACE IN THE NODE
    #         newSmallestSpace = None
    #         for space in gap_list:
    #             if space[1]-space[0] >= file_size:
    #                 #CHECK IF THE NEW FOUND SPACE IS SMALLER THAN THE PREVIOUS SPACE
    #                 if newSmallestSpace is None or space[1]-space[0] < smallestSpaceBetween:
    #                     newSmallestSpace = space
    #                     smallestSpaceBetween = space[1]-space[0]
            
    #         #CHECK IF NEW FOUND SPACE IN THE NEW NODE IS SMALLER THAN PREVIOUSLY FOUND SPACE            
    #         if smallestSpaceBetween is None or (newSmallestSpace[1] - newSmallestSpace[0]) < (storage_node["Gap"][0] - storage_node["Gap"][1]):  
    #             storage_node = {"storageNode": storage_node , "Gap": newSmallestSpace}
        
    #     #IF THERE WAS NO NODE FOUND END FUNCTION AND RETURN NONE
    #     if storage_node == None:
    #         return None
        
    #     file_and_node_tuple_list.append({"fName":partName, 
    #                                      "storage_info":storage_node})

    #     #REMOVE SELECTED NODE FROM THE LIST OF POSSIBLE NODES
    #     allNodes = [item for item in allNodes if item["SID"] != storage_node["SID"]]

    
    # return file_and_node_tuple_list
            
    file_and_node_tuple_list = []
    for partName in partNames:

        file_size = os.path.getsize(os.path.join(cwd, partName))
        
        storageNode = None
        
        for node in allNodes:
            print(node)
            if node["maxSize"] < file_size:
                continue
            elif node["status"] == False:
                continue
            
            if node["maxSize"] >= file_size:
                
                storageNode = node
      
            
        if storageNode == None:
            return None
            
        allNodes = [item for item in allNodes if item["SID"] != storageNode["SID"]]
        file_and_node_tuple_list.append({"fName":partName, 
                                          "storage_info":storageNode})
        
    return file_and_node_tuple_list
    

            



    
    
    
  