#!/usr/bin/env python3

import xml.etree.ElementTree as ET

import os
import copy
import json

#读取序列文件，得到dir处理序列
with open('dirQueue.txt', 'r') as queueFile:
    handleList = queueFile.readlines()

#设置用来做test的图片开始位置和结束位置
testStartId = 1000
testEndId = 6000

strJson = "{\"images\": "
strTestJson = "{\"images\": "
# print(strJson)
#构造单张图片的image结构
imageDict = {
"dataset": "BitVehicle",
"height": 540,
"id": 0,
"width": 960,
"file_name": "",
"coco_url": None,
"license": None,
"flickr_url": None,
"image": "",
"date_captured": None
}
#循环构造imagesList
imagesList = []
imagesTestList = []
id = 0
for line in handleList:
    dirname = os.path.join("./images", line.strip())
    fileNameList = os.listdir(dirname)
    i = 0
    fileListLen = len(fileNameList)
    fileNameList.sort()
    while i < fileListLen:
        imageDictBuffer = imageDict.copy()
        imageDictBuffer["file_name"] = fileNameList[i]
        imageDictBuffer["image"] = os.path.join(dirname, fileNameList[i])
        imageDictBuffer["id"] = id
        if id >= testStartId and id <= testEndId:
            imagesTestList.append(imageDictBuffer)
        else:
            imagesList.append(imageDictBuffer)
        id = id + 1
        i = i + 1

# print(len(imagesList), id)
#get training imageList
strImages = str(imagesList).replace("None", "null")
strImages = strImages.replace("\'", "\"")
strJson = strJson + strImages

#get test imageList
strTestImages = str(imagesTestList).replace("None", "null")
strTestImages = strTestImages.replace("\'", "\"")
strTestJson = strTestJson + strTestImages

# print(strJson)

#构造单个target的注释dict
annotationDict = {
"area": 109512.0,
"id": 0,
"iscrowd": 0,
"category_id": 1,
"is_occluded": False,
"image_id": 0,
"segmentation": None,
"bbox": [604.0, 0.0, 324.0, 338.0],
"attributes": {}
}

#所有图片放在一起的ID
imageSumId = -1
circleSumId = -1
#循环构造annotationsList
annotationsList = []
annotationsTestList = []
for line in handleList:
    #获得本文件夹下有多少张图片
    dirname = os.path.join("./images", line.strip())
    fileNameList = os.listdir(dirname)
    fileListLen = len(fileNameList)
    # print(fileListLen)

    #打开对应的xml文件
    xmlFilePathName = os.path.join("./DETRAC-Train-Annotations-XML", line.strip())
    xmlFilePathName = xmlFilePathName + ".xml"
    #读取，得到根节点
    tree = ET.ElementTree(file=xmlFilePathName)
    root = tree.getroot()

    # print(xmlFilePathName)
    # 循环遍历和解析xml树
    for child_of_root in root:
        #获得frame结点
        if child_of_root.tag == "frame":
            #获得当前frame的target的density,和当前帧是在本文件夹下的第几张图片
            density = int(child_of_root.attrib["density"])
            num = int(child_of_root.attrib["num"])
            # 循环获得该frame中的target参数
            i = 0
            while i < density:
                #生成一个新的annotationDict, 并填充
                annotationDictBuffer = copy.deepcopy(annotationDict)
                annotationDictBuffer["image_id"] = imageSumId + num
                target =  child_of_root[0][i]
                circleSumId = circleSumId + 1
                annotationDictBuffer["id"] = circleSumId
                for attribute in target:
                    if attribute.tag == "box":
                        annotationDictBuffer["bbox"][0] = float(attribute.attrib["left"])
                        annotationDictBuffer["bbox"][1] = float(attribute.attrib["top"])
                        annotationDictBuffer["bbox"][2] = float(attribute.attrib["width"])
                        annotationDictBuffer["bbox"][3] = float(attribute.attrib["height"])
                        annotationDictBuffer["area"] = annotationDictBuffer["bbox"][2] * annotationDictBuffer["bbox"][3]
                        # annotationDictBuffer["area"] = format(annotationDictBuffer["bbox"][2] * annotationDictBuffer["bbox"][3], "0.2f")
                    # if attribute.tag == "attribute":
                        # annotationDictBuffer["attributes"] = attribute.attrib
                    if attribute.tag == "attribute":
                        if attribute.attrib["vehicle_type"] == "car":
                            annotationDictBuffer["category_id"] = 1
                        if attribute.attrib["vehicle_type"] == "bus":
                            annotationDictBuffer["category_id"] = 2
                        if attribute.attrib["vehicle_type"] == "van":
                            annotationDictBuffer["category_id"] = 3
                        if attribute.attrib["vehicle_type"] == "others":
                            annotationDictBuffer["category_id"] = 4
                    if attribute.tag == "occlusion":
                        annotationDictBuffer["is_occluded"] = True
                # print(annotationDictBuffer)
                #把生成的annotationDict追加到annotationsList中
                if annotationDictBuffer["image_id"] >= testStartId and annotationDictBuffer["image_id"] <= testEndId:
                    annotationsTestList.append(annotationDictBuffer)
                else:
                    annotationsList.append(annotationDictBuffer)
                i = i + 1
    imageSumId = imageSumId + fileListLen

# print(annotationsList)
#get Training json
strAnnotations = str(annotationsList).replace("None", "null")
strAnnotations = strAnnotations.replace("False", "false")
strAnnotations = strAnnotations.replace("True", "true")
strAnnotations = strAnnotations.replace("\'", "\"")
strJson = strJson + ", \"annotations\": "
strJson = strJson + strAnnotations
strJson = strJson + ", \"categories\": [{\"id\": 0, \"name\": \"bg\", \"supercategory\": \"\"},{\"id\": 1, \"name\": \"car\", \"supercategory\": \"\"}, {\"id\": 2, \"name\": \"bus\", \"supercategory\": \"\"}, {\"id\": 3, \"name\": \"van\", \"supercategory\": \"\"}, {\"id\": 4, \"name\": \"others\", \"supercategory\": \"\"}]}"
Arr = json.loads(strJson)
js = json.dumps(Arr, sort_keys=True, indent=4, separators=(', ', ': '))

#get Test json
strTestAnnotations = str(annotationsTestList).replace("None", "null")
strTestAnnotations = strTestAnnotations.replace("False", "false")
strTestAnnotations = strTestAnnotations.replace("True", "true")
strTestAnnotations = strTestAnnotations.replace("\'", "\"")
strTestJson = strTestJson + ", \"annotations\": "
strTestJson = strTestJson + strTestAnnotations
strTestJson = strTestJson + ", \"categories\": [{\"id\": 0, \"name\": \"bg\", \"supercategory\": \"\"},{\"id\": 1, \"name\": \"car\", \"supercategory\": \"\"}, {\"id\": 2, \"name\": \"bus\", \"supercategory\": \"\"}, {\"id\": 3, \"name\": \"van\", \"supercategory\": \"\"}, {\"id\": 4, \"name\": \"others\", \"supercategory\": \"\"}]}"
ArrTest = json.loads(strTestJson)
jsTest = json.dumps(ArrTest, sort_keys=True, indent=4, separators=(', ', ': '))

print(js)
print("########Test########")
print(jsTest)
